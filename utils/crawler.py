from bs4 import BeautifulSoup
import requests

import json
import time
import os
import sys
from collections import OrderedDict
import warnings

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
warnings.filterwarnings('ignore')

# 설정 상수
ROOT = os.path.dirname(os.path.dirname(__file__))
ROOTDATA = os.path.join(ROOT, 'db')
LOSTURL = 'https://www.lost112.go.kr'
ALLDATA = 'all.json'
DEFAULT_START_YMD = '20250118'


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


def getIds(page, filters=None):
    """
    페이지에서 유실물 ID 목록을 가져옵니다.
    
    Args:
        page: 페이지 번호
        filters: 필터링 옵션 딕셔너리
            - start_date: 시작 날짜 (YYYYMMDD)
            - end_date: 종료 날짜 (YYYYMMDD)
            - category: 물품 분류명
            - category_code: 물품 대분류 코드
            - region: 습득 시군구
            - place_code: 장소 구분 코드
    """
    if filters is None:
        filters = {}
    
    # URL 파라미터 구성
    params = []
    
    # 시작 날짜 (필수)
    start_date = filters.get('start_date') or DEFAULT_START_YMD
    params.append(f'START_YMD={start_date}')
    
    # 종료 날짜
    if filters.get('end_date'):
        params.append(f'END_YMD={filters["end_date"]}')
    
    # 장소 구분 코드
    if filters.get('place_code'):
        params.append(f'PLACE_SE_CD={filters["place_code"]}')
    
    # 물품 분류명
    if filters.get('category'):
        params.append(f'PRDT_CL_NM={filters["category"]}')
    
    # 물품 대분류 코드
    if filters.get('category_code'):
        params.append(f'PRDT_CL_CD01={filters["category_code"]}')
    
    # 습득 시군구
    if filters.get('region'):
        params.append(f'FD_SIGUNGU={filters["region"]}')
    
    # 습득 장소 코드
    if filters.get('location_code'):
        params.append(f'FD_LCT_CD={filters["location_code"]}')
    
    params.append(f'pageIndex={page}')
    
    url = f'https://www.lost112.go.kr/find/findList.do?{"&".join(params)}'
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
                'image': LOSTURL + soup.find('p', {'class': 'lost_img'}).find('img').get('src'),
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
        'image': LOSTURL + soup.find('p', {'class': 'lost_img'}).find('img').get('src'),
        'source': 'lost112',
        'page': url
    }


def toJson(file_name, data):
    # 중복 유실물 제거
    unique_data = list(OrderedDict((item['ID'], item) for item in data).values())
    
    # db 폴더가 없으면 생성
    os.makedirs(ROOTDATA, exist_ok=True)
    
    # 로컬 파일에 저장
    file_path = os.path.join(ROOTDATA, file_name)
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
    
    def saveJson(self, file_name=None):
        if file_name is None:
            file_name = ALLDATA
        toJson(file_name, self.info)


class Updater:
    def __init__(self, file_name=None):
        if file_name is None:
            file_name = ALLDATA
        # 로컬 파일에서 all.json 읽기
        file_path = os.path.join(ROOTDATA, file_name)
        
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
    
    
    def makeNewJson(self, file_name=None):
        if file_name is None:
            file_name = ALLDATA
        # 기존 데이터와 새 데이터 합치기
        updated_all_data = self.data + self.new_datas
        toJson(file_name, updated_all_data)
