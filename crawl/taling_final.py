import requests
import pandas as pd
import time
import math
import datetime

from bs4 import BeautifulSoup
from sqlalchemy import *
start = time.time()

cat1_beauty_health = list(zip([28, 32, 31, 33, 27], ['메이크업', '퍼스털컬러', '패션', '셀프케어', 'PT/GX']))
cat1_activity = list(zip([78, 235, 123, 217, 240], ['방송', '댄스', '연기/무용', '스포츠/레저', '이색 액티비티']))
cat1_life = list(zip([233, 246, 88, 248, 80, 127, 103], ['인문/교양', '인테리어', '반려동물', '부모/육아', '출판/글쓰기', '사주/타로', '심리상담']))
cat1_hobby = list(zip([81, 79, 222, 232, 84, 83, 60, 59, 61, 76, 125, 249, 126], ['이색취미/공예', '사진', '취미미술', '디지털드로잉', '요리/베이킹', '커피/차/술', '보컬',
                      '악기', '작곡/디제잉','캘리그래피', '플라워', '조향/캔들/비누', '가죽/목공/도예']))
cat1_money = list(zip([214, 188, 116, 244, 213, 15], ['투잡', '마케팅', '주식투자', '부동산', '금융지식', '창업']))
cat1_career = list(zip([239, 250, 17, 13, 12, 14, 11, 34, 35, 54, 182], ['실무역량', '마케팅', '취업/이직/진로', '엑셀', '파워포인트', '스피치', '데이터분석',
                      '웹개발', '앱개발', '컴퓨터공학', '자격증/시험']))
cat1_design = list(zip([3, 201, 206, 209, 193, 199], ['건축', '그래픽디자인', 'UX/UI디자인', '제품디자인', '영상편집', '영상제작']))

cat1_language = list(zip([41, 42, 43, 44, 51], ['영어회화', '중국어회화', '일본어회화', '어학자격증', '기타 외국어']))
cat1s = [cat1_beauty_health, cat1_activity, cat1_life, cat1_hobby, cat1_money, cat1_career, cat1_design, cat1_language]
cat1s_ko = ['뷰티/헬스', '액티비티', '라이프', '취미/공예', '머니', '커리어', '디자인/영상', '외국어']
taling_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])

soldout = 0
end_pages = []

for cat1, j in zip(cat1s, range(len(cat1s))):
    end_page = []
    for sub, _ in cat1:
        first_page = f'https://taling.me/Home/Search/?page=1&cateSub={sub}'
        response = requests.get(first_page)
        soup = BeautifulSoup(response.text, 'html.parser')
        end_page.append(math.ceil(int(soup.select_one('#container > div.main3_cont > div.filter_head > div').text.strip().split('개')[0]) / 15))
    end_pages.append(end_page)

    for x in range(len(cat1)):
        pages = range(1, end_pages[j][x] + 1)
        urls = [f'https://taling.me/Home/Search/?page={page}&cateSub={cat1[x][0]}' for page in pages]
        
        
        for url in urls:
            onetime= []
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            for i in range(0, len(soup.select('#top-space > div > div > a > div.img'))):
                if 'SOLD OUT' not in str(soup.select('#top-space > div > div > a > div.img')[i]):
                    link = 'https://taling.me/' + soup.select('#top-space > div > div > a')[i]['href']
                    site = '탈잉'
                    category_2 = cat1[x][1]
                    category_1 = cat1s_ko[j]
                    try:
                        location = soup.select('#top-space > div > div > a > div.info > div > div.location')[i].text.strip()
                        title = '[' + location + ']' + soup.select('#top-space > div > div> a > div.title')[i].text.strip()
                    except:
                        location = ''
                        title = soup.select('#top-space > div > div> a > div.title')[i].text.strip()
                    try:
                        s_price = '월 ' + soup.select('#top-space > div > div > a > div.price > div > span > span > span')[i].text.strip() + '원'
                    except:
                        s_price = '링크 참조' 
                    try:
                        contentment = len(soup.select('#top-space > div > div > a > div.info > div > div.star')[i].text.strip())
                    except:
                        contentment = '평가 없음'
                    name_nick = soup.select('#top-space > div > div > a > div.profile_box > div.nick')[i].text.strip()
                    name_real = soup.select('#top-space > div > div > a > div.profile_box > div.name')[i].text.strip()
                    teacher = name_nick + '[' + name_real + ']'
                    discount = "0"
                    
                    row = {
                        'site': site,
                        'link': link,
                        'title': title,
                        'teacher': teacher,
                        'category_1': category_1,
                        'category_2': category_2,
                        's_price': s_price,
                        'discount': discount,
                        'contentment': contentment,
                        }

                    onetime.append(row)
                else:
                    soldout += 1
                
            taling_df = taling_df.append(onetime)
taling_df['crawling_time'] = datetime.datetime.now().strftime("%y%m%d%H%M%S")
taling_df = taling_df.reset_index(drop=True)
taling_df.to_csv(f'/home/ubuntu/notebooks/crawling-repo-6/datas/taling_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.csv', encoding='utf-8')
                
print('개수: ', len(taling_df), ' ', 'soldout: ', soldout, sep='')
print(round((time.time() - start)/60, 1), '분', sep='')

# mysql 저장하기
print('mysql db 저장 시작')

engine = create_engine("mysql://root:dss@52.78.38.124/crawled?charset=utf8mb4")

# 1. search table : 검색대상 table

# 1-1. 기존 class101 데이터 삭제
QUERY = """
    SELECT *
    FROM crawled.search
"""
search_df = pd.read_sql(QUERY, engine, index_col=['index'])
search_df.reset_index(drop=True)
compare_df = search_df[search_df['site'] == '탈잉']
search_df = search_df[search_df['site'] != '탈잉']
search_df.reset_index(drop=True)
compare_df.reset_index(drop=True)




# 1-2. 신규 taling 데이터 추가
search_df = search_df.append(taling_df)
search_df.reset_index(drop=True)
search_df.to_sql(name='search', con=engine, if_exists='replace')


# 2. save table : 데이터 저장 table

# 2-1. 신규 taling 데이터 저장
taling_df.reset_index(drop=True)
taling_df.to_sql(name='save', con=engine, if_exists='append')





# 3. new_class table : 3일 내 새로운 강좌 table

# 3-1. new_class에서 3일이 지난 데이터 삭제
days_ago = (datetime.datetime.now() - datetime.timedelta(days=3)).strftime("%y%m%d%H%M%S")
QUERY = """
    SELECT *
    FROM crawled.new_class
"""
old_class_df = pd.read_sql(QUERY, engine, index_col=['index'])
old_class_df.reset_index(drop=True)
old_class_df = old_class_df[old_class_df['crawling_time'].astype(str) > days_ago]
old_class_df.reset_index(drop=True)


# 3-2. 지난 데이터에 없는 신규강좌 데이터 확인
new_class_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])
for i in range(len(taling_df)):
    if taling_df['title'].tolist()[i] not in compare_df['title'].tolist():
        new_class_df = new_class_df.append(taling_df.iloc[i])

new_class_df.reset_index(drop=True)

# 3-3. 신규강좌 데이터 저장
new_class_df = new_class_df.append(old_class_df)
new_class_df.reset_index(drop=True)
new_class_df.to_sql(name='new_class', con=engine, if_exists='replace')


print('db저장완료')
print('search_df:', len(search_df))
print('taling_df:', len(taling_df))
print('new_class_df:', len(new_class_df))
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
