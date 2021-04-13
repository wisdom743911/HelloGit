import pickle
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

df = pd.read_csv('./crawling-repo-6/datas/taling_210315194501.csv', index_col=0)

train_x, test_x, train_y, test_y = train_test_split(
    df.title, df.category_1, test_size=0.1, random_state=13)

clf = Pipeline([
    ('vect', TfidfVectorizer()),
    ('clf', MultinomialNB(alpha=0.003))
])

model = clf.fit(train_x, train_y)

pred_y = model.predict(test_x)

with open('./model_cat1_210315194501.pkl', 'wb') as file:
    pickle.dump(model, file)
