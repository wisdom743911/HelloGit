
import requests
from bs4 import BeautifulSoup
import time
import datetime
import pandas as pd

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

classtok_df['crawling_time'] = datetime.datetime.now().strftime("%y%m%d%H%M%S")
classtok_df = classtok_df.reset_index(drop=True)
classtok_df.to_csv(f'/home/ubuntu/notebooks/crawl-repo-6/datas/classtok_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.csv', encoding='utf-8')


print('전체')
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
print('\n')
print('total: ', len(classtok_df), sep='')


print('mysql db저장 시작')

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql://root:dss@*****/crawling_project?charset=utf8mb4")

# 테이블 객체 생성을 위한 클래스 작성
Base = declarative_base()

class User(Base):
    
    __tablename__ = "classtok" # 테이블 이름
    
    # 컬럼 데이터 작성
    site = Column(String(30))
    link = Column(String(30), primary_key=True)
    title = Column(String(30))
    teacher = Column(String(20))
    category_1 = Column(String(20))
    category_2 = Column(String(20))
    s_price = Column(String(20))
    discount = Column(String(20))
    contentment = Column(String(20))
    crawling_time = Column(String(20))
    
    # 생성자 함수
    def __init__(self, site, link, title, category_1, category_2, s_price, discount, contentment, crawling_time):
        self.site = site
        self.link = link
        self.title = title
        self.category_1 = category_1
        self.category_2 = category_2
        self.s_price = s_price
        self.discount = discount
        self.contentment = contentment
        self.crawling_time = crawling_time
        
    # repr 함수
    def __repr__(self):
        return "<User {}, {}, {}, {}, {}, {}, {}, {}, {}>".format(
        self.site, self.link, self.title, self.category_1, 
        self.category_2, self.s_price, self.discount, self.contentment, self.crawling_time)
    

# engine에 연결된 데이터 베이스(test)에 테이블 생성
Base.metadata.create_all(engine)

# 데이터 베이스에 session 연결
Session = sessionmaker(engine)
session = Session()
session

classtok_df.to_sql(name='classtok', con=engine, if_exists='replace')
print('db저장완료, ', 'time: ', round((time.time() - start)/60, 1), '분', sep='')
