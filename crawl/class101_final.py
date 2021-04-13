
import requests
import time
import datetime
import pandas as pd

from sqlalchemy import *
start  = time.time()

offset = 0
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
        
        
    class101_df = class101_df.append(onetime)

    print('time: ', round((time.time() - start)/60, 1), '분', sep='')
    print('\n')

current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S")
class101_df['crawling_time'] = current_time
class101_df = class101_df.reset_index(drop=True)
class101_df.to_csv(f'/home/ubuntu/notebooks/crawling-repo-6/datas/class101_{current_time}.csv', encoding='utf-8')


print('전체')
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
print('\n')

print('total: ', len(class101_df), sep='')
for cat_ko in cat_ko_ls:
    print(f'{cat_ko}: ', len(class101_df[class101_df['category_1']==cat_ko]), sep='')

print('\n')

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
compare_df = search_df[search_df['site'] == '클래스101']
search_df = search_df[search_df['site'] != '클래스101']
compare_df.reset_index(drop=True)
search_df.reset_index(drop=True)



# 1-2. 신규 class101 데이터 추가
search_df = search_df.append(class101_df)
search_df.reset_index(drop=True)
search_df.to_sql(name='search', con=engine, if_exists='replace')


# 2. save table : 데이터 저장 table

# 2-1. 신규 class101 데이터 저장
class101_df.reset_index(drop=True)
class101_df.to_sql(name='save', con=engine, if_exists='append')





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
for i in range(len(class101_df)):
    if class101_df['title'].tolist()[i] not in compare_df['title'].tolist():
        new_class_df = new_class_df.append(class101_df.iloc[i])

new_class_df.reset_index(drop=True)

# 3-3. 신규강좌 데이터 저장
new_class_df = new_class_df.append(old_class_df)
new_class_df.reset_index(drop=True)
new_class_df.to_sql(name='new_class', con=engine, if_exists='replace')


print('db저장완료')
print('search_df:', len(search_df))
print('class101_df:', len(class101_df))
print('new_class_df:', len(new_class_df))
print('time: ', round((time.time() - start)/60, 1), '분', sep='')
