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

# requests header
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
p_n = 0

# time 랜덤
def pick_ran():
    numbers = [2, 3, 4]
    secure_random = random.SystemRandom()  # 시스템 난수 생성기 사용
    chosen_number = secure_random.choice(numbers) 
    return chosen_number

# 게시글 목록과 각 게시글의 URL 수집
def session1():
    ran = pick_ran()
    page_urls = []
    global p_n
    for p_n in range(143, 808):  # 스퀘어 게시판을 글 리젠 빠름 143, 808
        response = requests.get(f'https://theqoo.net/square?page={p_n}', headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for l in range(12, 33):
            # 게시글 목록에서 각 게시글의 URL 추출
            posts = soup.select('#bd_24759_0 > div > table > tbody > tr:nth-child({}) > td.title > a:first-child'.format(l))  # 타이틀 URL 속성 가져오기
            for post in posts:
                href = post.get('href')
                page_urls.append(href)
            p_n += 1
        time.sleep(ran)
    return page_urls

# 게시글 접속 및 시간 데이터 수집
def session2(urls):
    ran = pick_ran()
    base_url = 'https://theqoo.net'
    for url in urls: # 수집된 urls 횟수만큼 반복
        full_url = f"{base_url}{url}"  # # url은 '/'까지 포함하니 '/' 삭제
        # # 게시물 접속
        response = requests.get(full_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # # 게시물 번호만 추출
        match = re.search(r'/(\d+)\?', full_url)
        article_number = match.group(1)  # 첫 번째 그룹에 해당하는 숫자만 추출

        # # 시간 데이터 가져오기
        tr = soup.select_one('#bd_24759_{} > div.rd.rd_nav_style2.clear > div.rd_hd.clear > div.board.clear > div > div.side.fr > span'.format(article_number))
        article_time = tr.text.split()
        article_date = article_time[0].split('.')[1:3]
        article_date = '.'.join(article_date)
        article_hour = article_time[1].split(':')[0]

        # 시간데이터 다시 확인
        print(f"Extracted Date: {article_date}, Hour: {article_hour}")
        
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

# 판다스 DataFrame 생성
df = pd.DataFrame({'weekday': dicHour1, 'weekend': dicHour2})

# CSV 파일로 저장
df.to_csv('output.csv', index_label='Hour')

print('Fin')
