
import requests
import time
import datetime
import pickle
import pandas as pd

from bs4 import BeautifulSoup
from sqlalchemy import *
start  = time.time()



url = 'https://www.classtok.net/modoo/start_now'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
elements = soup.select('body > div.main_wrap > div > div > ul > div > li > div > a.product_info')

links = []
for i in range(len(elements)):
    links.append('https://classtok.net' + str(elements[i]).replace('<a class="product_info" href="', '').split('">\n<span>')[0])

classtok_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])

onetime = []

for element in elements:
    
    site = '클래스톡'
    try:
        likes = element.select_one('.product_star').text.split()[0]
    except:
        likes = '평가 없음'
    
    onetime.append({
        "site" : site,
        "title" : element.select_one('h2').text,
        "category_2" : element.select_one('span').text.split(' · ')[0],
        "teacher" : element.select_one('span').text.split(' · ')[1],
        "s_price" : element.select_one('.price_info').text.split('\n')[1],
        "discount" : element.select_one('.price_info').text.split('\n')[2].replace(' 할인',''),
        "contentment" : likes,
        "link" : 'https://www.classtok.net' + element.get('href'),
    })
classtok_df = classtok_df.append(onetime)

print('time: ', round((time.time() - start)/60, 1), '분', sep='')
print('\n')

# 모델 열기
with open('/home/ubuntu/notebooks/crawling-repo-6/model_cat1_210315194501.pkl', 'rb') as file:
    load_model = pickle.load(file)

classtok_df['category_1'] = load_model.predict(classtok_df['title'])
classtok_df['crawling_time'] = datetime.datetime.now().strftime("%y%m%d%H%M%S")
classtok_df = classtok_df.reset_index(drop=True)
classtok_df.to_csv(f'/home/ubuntu/notebooks/crawling-repo-6/datas/classtok_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.csv', encoding='utf-8')


print('전체')
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
print('\n')
print('total: ', len(classtok_df), sep='')


# mysql 저장하기
print('mysql db 저장 시작')

engine = create_engine("mysql://root:dss@52.78.38.124/crawled?charset=utf8mb4")

# 1. search table : 검색대상 table

# 1-1. 기존 classtok 데이터 삭제
QUERY = """
    SELECT *
    FROM crawled.search
"""
search_df = pd.read_sql(QUERY, engine, index_col=['index'])
search_df.reset_index(drop=True)
compare_df = search_df[search_df['site'] == '클래스톡']
search_df = search_df[search_df['site'] != '클래스톡']
compare_df.reset_index(drop=True)
search_df.reset_index(drop=True)



# 1-2. 신규 classtok 데이터 추가
search_df = search_df.append(classtok_df)
search_df.reset_index(drop=True)
search_df.to_sql(name='search', con=engine, if_exists='replace')


# 2. save table : 데이터 저장 table

# 2-1. 신규 classtok 데이터 저장
classtok_df.reset_index(drop=True)
classtok_df.to_sql(name='save', con=engine, if_exists='append')





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
for i in range(len(classtok_df)):
    if classtok_df['title'].tolist()[i] not in compare_df['title'].tolist():
        new_class_df = new_class_df.append(classtok_df.iloc[i])

new_class_df.reset_index(drop=True)

# 3-3. 신규강좌 데이터 저장
new_class_df = new_class_df.append(old_class_df)
new_class_df.reset_index(drop=True)
new_class_df.to_sql(name='new_class', con=engine, if_exists='replace')


print('db저장완료')
print('search_df:', len(search_df))
print('classtok_df:', len(classtok_df))
print('new_class_df:', len(new_class_df))
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
