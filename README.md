## ahachul_data
더욱 쾌적한 지하철을 위해서, 아! 하철이형 서비스의 Data 레포입니다
***
### 1. git clone
- 해당 repository clone 후, root directory에 위치

### 2. 필요 라이브러리 설치
```
pip install -r requirements.txt
```
### 3. 유실물 크롤링 실행
cmd에서 세 가지 옵션으로 크롤링 가능

#### 기본 옵션
1. **전체 크롤링**
   ```bash
   python main.py -o ca
   ```
   - lost112의 모든 데이터를 크롤링합니다

2. **새 데이터만 크롤링**
   ```bash
   python main.py -o un
   ```
   - 기존 db/all.json에 없는 새로 업데이트된 데이터만 크롤링합니다
   - db/all.json 파일이 존재해야 합니다

3. **특정 날짜 이후 크롤링**
   ```bash
   python main.py -o ad -d YYYYMMDD
   ```
   - 입력한 날짜(포함) 이후 데이터만 크롤링합니다
   - 예: `python main.py -o ad -d 20241117`

#### 필터링 옵션
모든 옵션에 필터링을 추가할 수 있습니다:

- `--category`: 물품 분류명 (예: `--category 지갑`)
- `--category-code`: 물품 대분류 코드 (예: `--category-code PRH000`)
- `--region`: 습득 시군구 (예: `--region 경기도`)
- `--place-code`: 장소 구분 코드 (예: `--place-code LL1003` 지하철, 지정 안하면 전체)
- `--end-date`: 종료 날짜 (예: `--end-date 20241124`)

#### 사용 예시
```bash
# 경기도에서 잃어버린 지갑 찾기
python main.py -o ca --category 지갑 --region 경기도 -d 20241117

# 특정 기간의 지하철 유실물 크롤링
python main.py -o ad -d 20241117 --end-date 20241124 --place-code LL1003

# 새로 업데이트된 경기도 지갑 데이터만 크롤링
python main.py -o un --category 지갑 --region 경기도
```

### 4. 뉴스 기사 크롤링 실행
cmd에서 세 가지 옵션으로 크롤링 가능
- 최상단 디렉토리에서 하위 명령어 실행
    ```
    python utils/news_crawling.py
    ```
- 결과 파일 경로
    ```
    datas folder > subway_news_data.json
    ```
- 뉴스 기사 수집 키워드
    ```
  서울 지하철 n호선 +
  "지연", "운행 중단", "고장", "사고", "혼잡", "폭행", "도난", "파업"
  ```