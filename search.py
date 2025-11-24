import json
import os
import argparse
from utils.crawler import ROOTDATA, ALLDATA

def search_wallet(person_name=None, keywords=None):
    """
    유실물 데이터에서 지갑을 검색합니다.
    
    Args:
        person_name: 이름 (부분 일치)
        keywords: context에서 검색할 키워드 리스트 (쉼표로 구분된 문자열)
    """
    # 데이터 파일 경로
    file_path = os.path.join(ROOTDATA, ALLDATA)
    
    if not os.path.exists(file_path):
        print(f'오류: {file_path} 파일이 존재하지 않습니다. 먼저 데이터를 크롤링하세요.')
        return
    
    # JSON 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 키워드 리스트로 변환
    keyword_list = []
    if keywords:
        keyword_list = [k.strip() for k in keywords.split(',')]
    
    # 검색 결과
    results = []
    
    for item in data:
        # 지갑인지 확인
        if '지갑' not in item.get('type', ''):
            continue
        
        match = False
        match_reasons = []
        
        # personName으로 검색
        if person_name:
            item_person_name = item.get('personName', '')
            if person_name in item_person_name:
                match = True
                match_reasons.append(f"이름 일치: {item_person_name}")
        
        # context에서 키워드 검색
        if keyword_list:
            context = item.get('context', '')
            found_keywords = []
            for keyword in keyword_list:
                if keyword in context:
                    found_keywords.append(keyword)
            if found_keywords:
                match = True
                match_reasons.append(f"키워드 일치: {', '.join(found_keywords)}")
        
        # personName이나 키워드 중 하나라도 일치하면 결과에 추가
        if match:
            results.append({
                'item': item,
                'reasons': match_reasons
            })
    
    # 결과 출력
    if not results:
        print("검색 결과가 없습니다.")
        return
    
    print(f"\n총 {len(results)}개의 지갑을 찾았습니다.\n")
    print("=" * 80)
    
    for idx, result in enumerate(results, 1):
        item = result['item']
        reasons = result['reasons']
        
        print(f"\n[{idx}]")
        print(f"ID: {item.get('ID', 'N/A')}")
        print(f"제목: {item.get('title', 'N/A')}")
        if item.get('personName'):
            print(f"이름: {item.get('personName')}")
        print(f"습득일: {item.get('getDate', 'N/A')}")
        print(f"습득장소: {item.get('getPlace', 'N/A')}")
        print(f"분류: {item.get('type', 'N/A')}")
        print(f"보관장소: {item.get('storagePlace', 'N/A')}")
        print(f"연락처: {item.get('phone', 'N/A')}")
        print(f"상태: {item.get('lostStatus', 'N/A')}")
        print(f"매칭 이유: {' | '.join(reasons)}")
        print(f"상세 내용: {item.get('context', 'N/A')[:200]}...")  # 처음 200자만
        print(f"링크: {item.get('page', 'N/A')}")
        print("-" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='유실물 지갑 검색')
    parser.add_argument('--name', type=str,
                        help='이름 (부분 일치)')
    parser.add_argument('--keywords', type=str,
                        help='context에서 검색할 키워드 (쉼표로 구분, 예: 국민카드,운전면허증)')
    
    args = parser.parse_args()
    
    if not args.name and not args.keywords:
        parser.print_help()
        print("\n오류: --name 또는 --keywords 중 하나 이상을 입력해야 합니다.")
    else:
        search_wallet(args.name, args.keywords)

