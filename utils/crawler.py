from bs4 import BeautifulSoup
import requests

import json
import time
import os
import sys
from collections import OrderedDict
import warnings

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import config as cfg
warnings.filterwarnings('ignore')


def wait(url):
    isEscapeLoop = False
    while True:
        try:
            req = requests.get(url, verify=False)
            soup = BeautifulSoup(req.text, 'html.parser')
            if isEscapeLoop:
                print('Successfully connect in page {}'.format(url))
            return soup
        except Exception as e:
            print('"{}" error occurred in page {}, reconnect ... '.format(e, url))
            time.sleep(3)
            isEscapeLoop = True


def getIds(page):
    url = f'https://www.lost112.go.kr/find/findList.do?START_YMD={cfg.START_YMD}&PLACE_SE_CD=LL1003&pageIndex={page}'
    soup = wait(url)
    ids = [i.find('td').text for i in soup.find('table', {'class': 'type01'}).find('tbody').find_all('tr')]
    return ids if ids != ['검색 결과가 없습니다.'] else []


def getInfo(id):
    def getText(soup):
        div = soup.find('div', {'class': 'find_info_txt'})
        try:
            text = [div.find('br').previous_sibling.strip()] + [br.nextSibling.strip() for br in div.find_all('br')]
            return ' '.join([i for i in text if i != ''])
        
        except AttributeError:
            return div.text.strip()


    url = f'https://www.lost112.go.kr/find/findDetail.do?ATC_ID={id}&FD_SN=1'
    soup = wait(url)
    infos = [i.text.strip() for i in soup.find_all('p', {'class': 'find02'})]
    title = soup.find('p', {'class': 'find_info_name'}).text.split(':')[-1].strip()

    return {
                'ID': id,
                'title': title,
                'personName': infos[1],
                'getDate': infos[2],
                'getPlace': infos[3],
                'type': infos[4],
                'receiptPlace': infos[5],
                'storagePlace': infos[6],
                'lostStatus': infos[7],
                'phone': infos[8],
                'context': getText(soup),
                'image': cfg.LOSTURL + soup.find('p', {'class': 'lost_img'}).find('img').get('src'),
                'source': 'lost112',
                'page': url
            } if len(infos) == 9 else \
     {  
        'ID': id,
        'title': title,
        'getDate': infos[1],
        'getPlace': infos[2],
        'type': infos[3],
        'receiptPlace': infos[4],
        'storagePlace': infos[5],
        'lostStatus': infos[6],
        'phone': infos[7],
        'context': getText(soup),
        'image': cfg.LOSTURL + soup.find('p', {'class': 'lost_img'}).find('img').get('src'),
        'source': 'lost112',
        'page': url
    }


def toJson(file_name, data):
    # 중복 유실물 제거
    unique_data = list(OrderedDict((item['ID'], item) for item in data).values())
    
    # db 폴더가 없으면 생성
    os.makedirs(cfg.ROOTDATA, exist_ok=True)
    
    # 로컬 파일에 저장
    file_path = os.path.join(cfg.ROOTDATA, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(unique_data, f, ensure_ascii=False, indent=4)
    
    print(f'Data saved to {file_path}')


class Crawler:
    def __init__(self):
        self.info = []
        
        
    def crawlAll(self, ids):
        for id in ids:
            info = getInfo(id)
            self.info.append(info)
    
    def saveJson(self):
        toJson(cfg.ALLDATA, self.info)


class Updater:
    def __init__(self):
        # 로컬 파일에서 all.json 읽기
        file_path = os.path.join(cfg.ROOTDATA, cfg.ALLDATA)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'{file_path} 파일이 존재하지 않습니다. 먼저 전체 데이터를 크롤링하세요.')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # ID 목록 추출
        self.keys = [item['ID'] for item in self.data]
        self.new_datas = []
   
    def isCompleteUpdate(self, ids):
        for id in ids:
            if id in self.keys: return False
            info = getInfo(id)
            self.new_datas.append(info)

        return True
    
    
    def makeNewJson(self):
        # 기존 데이터와 새 데이터 합치기
        updated_all_data = self.data + self.new_datas
        toJson(cfg.ALLDATA, updated_all_data)
