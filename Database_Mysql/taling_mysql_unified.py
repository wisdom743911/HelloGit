import requests
import pandas as pd
import time
import math
import datetime

from bs4 import BeautifulSoup

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
                    link = soup.select('#top-space > div > div > a')[i]['href']
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
                        s_price = '가격미정'
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
taling_df.to_csv(f'/home/ubuntu/notebooks/crawl-repo-6/datas/taling_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.csv', encoding='utf-8')
                
print('개수: ', len(taling_df), ' ', 'soldout: ', soldout, sep='')
print(round((time.time() - start)/60, 1), '분', sep='')


print('mysql db 저장 시작')

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql://root:dss@*****/crawling_project?charset=utf8mb4")

# 테이블 객체 생성을 위한 클래스 작성
Base = declarative_base()

class User(Base):
    
    __tablename__ = "taling" # 테이블 이름
    
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

taling_df.to_sql(name='taling', con=engine, if_exists='replace')
print('db저장완료, ', 'time: ', round((time.time() - start)/60, 1), '분', sep='')
