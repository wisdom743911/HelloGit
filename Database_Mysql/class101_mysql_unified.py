
import requests
import time
import datetime
import pandas as pd
start  = time.time()


# def rmEmoji(inputData):
#     return inputData.encode('utf-8', 'ignore').decode('utf-8')#.encode('ascii', 'ignore').decode('ascii')


offset = 28 * 0
limit = 28 * 38
url_graphql = 'https://cdn-gql-prod2.class101.net/graphql'

cat_ko_ls = ['취미', '수익창출', '직무교육']
cat_eng_ls = ['creative', 'money', 'career']
brands = ["original", "money", "professional"]
categories = list(zip(cat_ko_ls, cat_eng_ls, brands))

req = requests.get('https://class101.net/robots.txt')
prohibit_url = []
for txt in req.text.split('\n'):
    if 'Disallow: ' in txt:
        prohibit_url.append('https://class101.net' + txt.replace('Disallow: ', ''))
        

class101_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])

for cat_ko, cat_eng, brand in categories:
    print(f'{cat_ko} / {cat_eng}')
    query = [{"operationName":"InfiniteProductCardsWithLastUpdatedInformation","variables":{"brand":[brand],"offset":offset,"limit":limit},"query":"query InfiniteProductCardsWithLastUpdatedInformation($brand: [ProductBrand!], $limit: Int, $offset: Int, $categoryIds: [String!]) {\n  products(\n    limit: $limit\n    offset: $offset\n    productFilter: {brand: $brand, isHidden: false, isLastManagement: true, state: [funding, sales], type: \"klass\", categoryIds: $categoryIds}\n    sort: [{managedAt: -1}]\n  ) {\n    ...ProductCardWithLastUpdatedInformation\n    __typename\n  }\n  productsCount(\n    productFilter: {brand: $brand, categoryIds: $categoryIds, isHidden: false, isLastManagement: true, state: [funding, sales], type: \"klass\"}\n  )\n}\n\nfragment ProductCardWithLastUpdatedInformation on Product {\n  _id\n  categoryId\n  categoryIds\n  coverImageUrl\n  firestoreId\n  title\n  titlePrefixes\n  type\n  state\n  packagePricePreview {\n    listPrice\n    netPrice\n    __typename\n  }\n  ...CategoryAndCreatorTag\n  ...ProductBadge\n  ...LastUpdatedInformation\n  ...HeartAndFeedbackCountLabel\n  __typename\n}\n\nfragment CategoryAndCreatorTag on Product {\n  _id\n  category {\n    _id\n    title\n    __typename\n  }\n  categoryTitleDetail\n  difficulty\n  author {\n    _id\n    firestoreId\n    name\n    nickName\n    photoUrl\n    channels {\n      type\n      url\n      channelId\n      __typename\n    }\n    createdAt\n    __typename\n  }\n  __typename\n}\n\nfragment ProductBadge on Product {\n  productBadge {\n    text\n    imageUrl\n    backgroundColor\n    fontColor\n    __typename\n  }\n  __typename\n}\n\nfragment LastUpdatedInformation on Product {\n  _id\n  lastManagement {\n    managedAt\n    content\n    __typename\n  }\n  __typename\n}\n\nfragment HeartAndFeedbackCountLabel on Product {\n  _id\n  feedbackCount\n  feedbackGoodCount\n  reservationCount\n  wishlistedCount\n  __typename\n}\n"}]
    req = requests.post(url_graphql, json=query, )
    datas = req.json()


    onetime = []
    for i in range(len(datas[0]['data']['products'])):
        
        site = '클래스101'
        
        url_detail = datas[0]['data']['products'][i]['_id']
        link = 'https://class101.net/products/' + url_detail
        if link in prohibit_url:
            continue
            
        state = datas[0]['data']['products'][i]['state']
        title = '[' + state + ']' + datas[0]['data']['products'][i]['title']
        
        category_1 = cat_ko
        category_2 = datas[0]['data']['products'][i]['category']['title']

        try:
            o_price_int = datas[0]['data']['products'][i]['packagePricePreview']['listPrice']
            o_pirce = '총 ' + str(f'{o_price_int:,}') + '원'
        except:
            o_price = '링크 참조'
            print('o_price', link, i)
        try:
            s_price_int = datas[0]['data']['products'][i]['packagePricePreview']['netPrice']
            s_price = '총 ' + str(f'{s_price_int:,}') + '원'
        except:
            s_price = '링크 참조'
            print('s_price', link, i)
        try:
            discount = round((s_price_int / o_price_int) * 100, 1) + '%'
        except:
            discount = '0'
            
        teacher_nick = datas[0]['data']['products'][i]['author']['nickName']
        teacher_real = datas[0]['data']['products'][i]['author']['name']
        if teacher_nick != None:
            if teacher_real != None:
                teacher = teacher_nick + '[' + datas[0]['data']['products'][i]['author']['name'] + ']'
            else:
                teacher = teacher_nick
        else:
            teacher = teacher_real
            
        feedback_count = int(datas[0]['data']['products'][i]['feedbackCount'])
        feedback_good = int(datas[0]['data']['products'][i]['feedbackGoodCount'])
        if feedback_count != 0:
            contentment = str(round((feedback_good / feedback_count) * 100, 1)) + '%'
        else:
            contentment = '평가 없음'
#         reservation = datas[0]['data']['products'][i]['reservationCount']
#         heart = datas[0]['data']['products'][i]['wishlistedCount']


        row = {
#             'url_detail': url_detail, 
            'site': site,
            'link': link,
            'title': title,
            'teacher': teacher,
            'category_1': category_1,
            'category_2': category_2,
            's_price': s_price,
            'discount': discount,
            'contentment': contentment,
#             'reservation': reservation, 
#             'heart': heart
            }
        onetime.append(row)
        
        
    class101_df = class101_df.append(onetime)

    print('time: ', round((time.time() - start)/60, 1), '분', sep='')
    print('\n')

class101_df['crawling_time'] = datetime.datetime.now().strftime("%y%m%d%H%M%S")
class101_df = class101_df.reset_index(drop=True)
class101_df.to_csv(f'/home/ubuntu/notebooks/crawl-repo-6/datas/class101_{datetime.datetime.now().strftime("%y%m%d%H%M%S")}.csv', encoding='utf-8')


print('전체')
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
print('\n')

print('total: ', len(class101_df), sep='')
for cat_ko in cat_ko_ls:
    print(f'{cat_ko}: ', len(class101_df[class101_df['category_1']==cat_ko]), sep='')

# url_detail, title, category_1, category_2, state, o_price, s_price, teacher, teacher_nick, feedback_count, feedback_good, reservation, heart


print('\n')
print('musql db 저장 시작')


from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine("mysql://root:dss@*****/crawling_project?charset=utf8mb4")

# 테이블 객체 생성을 위한 클래스 작성
Base = declarative_base()

class User(Base):
    
    __tablename__ = "class101" # 테이블 이름
    
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

class101_df.to_sql(name='class101', con=engine, if_exists='replace')

print('db저장완료, ', 'time: ', round((time.time() - start)/60, 1), '분', sep='')
