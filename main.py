from utils import crawling
import argparse

parser = argparse.ArgumentParser(description='lost112 유실물 크롤링')
parser.add_argument('-o', '--option', type=str, required=True,
                    help='ca: 전체 크롤링, un: 새 데이터만, ad: 특정 날짜 이후')
parser.add_argument('-d', '--date', type=str, 
                    help='시작 날짜 (YYYYMMDD 형식, ad 옵션 사용 시 필수)')
parser.add_argument('--end-date', type=str,
                    help='종료 날짜 (YYYYMMDD 형식)')
parser.add_argument('--category', type=str,
                    help='물품 분류명 (예: 지갑)')
parser.add_argument('--category-code', type=str,
                    help='물품 대분류 코드 (예: PRH000)')
parser.add_argument('--region', type=str,
                    help='습득 시군구 (예: 경기도)')
parser.add_argument('--place-code', type=str,
                    help='장소 구분 코드 (예: LL1003 지하철, 지정 안하면 전체)')
args = parser.parse_args()

# 필터링 옵션 딕셔너리 생성
filters = {
    'start_date': args.date,
    'end_date': args.end_date,
    'category': args.category,
    'category_code': args.category_code,
    'region': args.region,
    'place_code': args.place_code
}

print("Start Crawling")
if args.category or args.category_code or args.region:
    print(f"필터링 옵션: 분류={args.category or args.category_code}, 지역={args.region}, 장소={args.place_code or '전체'}")

crawling.crawl(args.option, filters)
