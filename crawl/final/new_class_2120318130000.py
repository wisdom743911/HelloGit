import pandas as pd
from sqlalchemy import *

# old_df
old_df_class101 = pd.read_csv('./crawling-repo-6/datas/class101_210314230107.csv', index_col=0)
old_df_classtok = pd.read_csv('./crawling-repo-6/datas/classtok_210314232004.csv', index_col=0)
old_df_taling = pd.read_csv('./crawling-repo-6/datas/taling_210314234509.csv', index_col=0)

old_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])
old_df = old_df.append([old_df_class101, old_df_classtok, old_df_taling])
print('old_crawled_df:', len(old_df))

# new_df
new_df_class101 = pd.read_csv('./crawling-repo-6/datas/class101_210318140113.csv', index_col=0)
new_df_classtok = pd.read_csv('./crawling-repo-6/datas/classtok_210318132006.csv', index_col=0)
new_df_taling = pd.read_csv('./crawling-repo-6/datas/taling_210318134511.csv', index_col=0)

new_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])
new_df = new_df.append([new_df_class101, new_df_classtok, new_df_taling])
print('new_crawled:', len(new_df))

# new_class_df
new_class_df = pd.DataFrame(columns=['site', 'link', 'title', 'teacher', 'category_1', 'category_2', 's_price', 'discount', 'contentment', 'crawling_time'])
new_df.reset_index
old_df.reset_index
for i in range(len(new_df)):
    if new_df['title'].tolist()[i] not in old_df['title'].tolist():
        new_class_df = new_class_df.append(new_df.iloc[i])



# upload to sql_new_class
engine = create_engine("mysql://root:dss@52.78.38.124/crawled?charset=utf8mb4")
new_class_df.reset_index
new_class_df.to_sql(name='new_class', con=engine, if_exists='replace')
print('신규_클래스101:', len(new_class_df[new_class_df['site']=='클래스101']))
print('신규_클래스톡:', len(new_class_df[new_class_df['site']=='클래스톡']))
print('신규_탈잉:', len(new_class_df[new_class_df['site']=='탈잉']))
print('new_class_df:', len(new_class_df))
