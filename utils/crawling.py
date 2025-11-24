from utils.crawler import Crawler, Updater, ROOTDATA, ALLDATA
from utils import crawler
import os

# 설정 상수
STARTPAGE = 1

def crawlDetail(start, filters=None, file_name=None, test_mode=False):
    if file_name is None:
        file_name = ALLDATA
    crawl = Crawler()
    max_page = 10 if test_mode else None
    while True:
        ids = crawler.getIds(start, filters)
        if not ids:
            print('complete')
            break
        crawl.crawlAll(ids)
        start += 1
        if start % 10 == 0:
            print('----------------------{} pages crawled----------------------'.format(start))
            # 10페이지마다 JSON 저장
            crawl.saveJson(file_name)
        if test_mode and start > max_page:
            print(f'테스트 모드: {max_page}페이지까지 크롤링 완료')
            break
    
    # 마지막에 한 번 더 저장 (10페이지 단위가 아닌 경우를 위해)
    if (start - 1) % 10 != 0:
        crawl.saveJson(file_name)
    

def crawl(option, filters=None, file_name=None, test_mode=False):
    if filters is None:
        filters = {}
    if file_name is None:
        file_name = ALLDATA
    
    start = STARTPAGE
    
    if option == 'ca':
        crawlDetail(start, filters, file_name, test_mode)
        
    elif option == 'un':
        file_path = os.path.join(ROOTDATA, file_name)
        assert os.path.isfile(file_path), \
            f'{file_path} 파일이 존재하지 않습니다. 먼저 전체 데이터를 크롤링하세요.'
        updater = Updater(file_name)
        max_page = 10 if test_mode else None
        while True:
            ids = crawler.getIds(start, filters)
            if not updater.isCompleteUpdate(ids) or not ids:
                break
            start += 1
            if test_mode and start > max_page:
                print(f'테스트 모드: {max_page}페이지까지 크롤링 완료')
                break
        updater.makeNewJson(file_name)
        print('complete')
    
    elif option == 'ad':
        if not filters.get('start_date'):
            print('오류: ad 옵션 사용 시 -d 또는 --date로 시작 날짜를 지정해야 합니다.')
            return
        crawlDetail(start, filters, file_name, test_mode)
        
    else:
        print('retry')
