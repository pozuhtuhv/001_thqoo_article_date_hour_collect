import requests
from bs4 import BeautifulSoup
import time
import random
import re
import pandas as pd

# 날짜 데이터
day1 = ['04.01', '04.02', '04.03', '04.04', '04.05', '04.08', '04.09', '04.10', '04.11', '04.12']
day2 = ['04.06', '04.07', '04.13', '04.14']
dicHour1 = {f"{i:02}": 0 for i in range(24)} # 평일 데이터 시간 두자리수표시 '00, 01, 02...'
dicHour2 = {f"{i:02}": 0 for i in range(24)} # 주말 데이터 시간 두자리수표시 '00, 01, 02...'
data_accumulate = []

# requests header
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}

# 작업중 인터넷 연결 확인
def wait_for_internet_connection():
    while True:
        try:
            response = requests.get('http://www.google.com', timeout=5)
            if response.status_code == 200:
                print("Internet connection is back.") # 정상일시 다시 넘기고
                return
        except requests.RequestException: # 오류일시 다시 기다려본다
            print("No internet connection, retrying in 10 seconds...") 
            time.sleep(10)

def fetch_data(url, headers):
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except (requests.ConnectionError, requests.Timeout):
            print("Connection error or timeout, checking connection...")
            wait_for_internet_connection()
            return fetch_data(url, headers)  # 진행중인 주소 다시 시도
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                print(f"404 Not Found Error for URL: {url}")
            else:
                print(f"HTTP Error {e.response.status_code} for URL: {url}")
            return None  # 오류 발생 시 None 반환

# time 랜덤
def pick_ran():
    numbers = [3, 4, 5]
    secure_random = random.SystemRandom()  # 시스템 난수 생성기 사용
    chosen_number = secure_random.choice(numbers) 
    return chosen_number

# 게시글 목록과 각 게시글의 URL 수집
def session1():
    ran = pick_ran()
    page_urls = []
    for p_n in range(194, 856):  # 스퀘어 게시판을 글 리젠 빠름 143, 808
        response = fetch_data(f'https://theqoo.net/square?page={p_n}', headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for l in range(12, 33): # 한페이지 공지제외 게시글 갯수 (공지갯수, + 20)
            # 게시글 목록에서 각 게시글의 URL 추출
            posts = soup.select('#bd_24759_0 > div > table > tbody > tr:nth-child({}) > td.title > a:first-child'.format(l))  # 타이틀 URL 속성 가져오기
            for post in posts:
                href = post.get('href')
                page_urls.append(href)
                print(href)
        time.sleep(ran)
    return page_urls

# 게시글 접속 및 제목, 조회수, 작성시간 데이터 수집
def session2(urls):
    ran = pick_ran()
    base_url = 'https://theqoo.net'
    for url in urls: # 수집된 urls 횟수만큼 반복
        full_url = f"{base_url}{url}" # url은 '/'까지 포함하니 '/' 삭제
        # 주소 접속
        response = fetch_data(full_url, headers)
        if response is None:  # 오류가 발생했으면 건너뛰기 외에 다른 오류시 continue로 넘기기
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 게시물 번호만 추출
        match = re.search(r'/(\d+)\?', full_url)
        article_number = match.group(1)  # 첫 번째 그룹에 해당하는 숫자만 추출

        if article_number: # 존재할경우 
            # 타이틀
            title = soup.select_one(f'#bd_24759_{article_number} > div.rd.rd_nav_style2.clear > div.rd_hd.clear > div.theqoo_document_header > span').text
            # 시간 데이터
            tr = soup.select_one(f'#bd_24759_{article_number} > div.rd.rd_nav_style2.clear > div.rd_hd.clear > div.board.clear > div > div.side.fr > span')
            article_time = tr.text.split()
            article_date = article_time[0].split('.')[1:3]
            article_date = '.'.join(article_date)
            article_hour = article_time[1].split(':')[0]
            # 조회수, 댓글 데이터
            view = soup.select_one(f'#bd_24759_{article_number} > div.rd.rd_nav_style2.clear > div.rd_hd.clear > div.theqoo_document_header > div > i.far.fa-eye').next_sibling.strip()
            comment = soup.select_one(f'#bd_24759_{article_number} > div.rd.rd_nav_style2.clear > div.rd_hd.clear > div.theqoo_document_header > div > i.far.fa-comment-dots').next_sibling.strip()

            # 시간데이터 다시 확인
            print(f"Extracted Date: {article_date}, Hour: {article_hour}, title : {title}")
            
            # 데이터 누적에 저장 
            data_accumulate.append({
                'title':  title,
                'link': full_url,
                'view': view,
                'comment': comment,
                'date': article_time,
                'Hour': article_hour
            })

            if article_date in day1:
                dicHour1[str(article_hour)] += 1
            elif article_date in day2:
                dicHour2[str(article_hour)] += 1
            else:
                print(f"Date {article_date} not found in day1 or day2 lists.")
        time.sleep(ran)
        

urls = session1()
print(urls)
session2(urls)

print(dicHour1)  # 평일결과
print(dicHour2)  # 주말결과

# 판다스로 수집데이터 데이터프레임설정
df = pd.DataFrame({'weekday': dicHour1, 'weekend': dicHour2})
# CSV 파일로 저장
df.to_csv('articletime.csv', index_label='Hour', encoding='utf-8-sig')

# 판다스로 수집데이터 데이터프레임설정
df = pd.DataFrame(data_accumulate)
# CSV 파일로 저장 utf-8-sig 인식
df.to_csv('articleinfo.csv', index=False, encoding='utf-8-sig')

print('Fin')
