#IMPORTING LIBRARIES////////////////////////////////
import io
import re
import json
import pandas as pd
import numpy as np
import operator
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer,TfidfVectorizer
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from collections import Counter
from textblob import TextBlob
from string import digits
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import seaborn as sns

#READING THE INPUT DATASET////////////////////////////////
df = pd.read_csv('DATA.csv', index_col=None,encoding= 'unicode_escape' )

#PRE PROSSEING THE TEXT ////////////////////////////////
df['text'] = df['text'].apply(lambda x: " ".join(x.lower() for x in x.split()))#CHANGING COLUMN NAMED "text" TO LOWERCASE
df['text'] = df['text'].apply(lambda x: " ".join(x.replace("'", "") for x in x.split()))#REMOVING SINGLE QUOTE
df['text'] = df['text'].str.replace('[^\w\s]','')#REMOVING PUNCTUATIONS
freq = pd.Series(' '.join(df['text']).split()).value_counts()[:10]#REMOCING COMMON WORDS
freq = list(freq.index)
df['text'] = df['text'].apply(lambda x: " ".join(x for x in x.split() if x not in freq))
freq = pd.Series(' '.join(df['text']).split()).value_counts()[-10:]#REMOVING RARE WORDS
freq = list(freq.index)
df['text'] = df['text'].apply(lambda x: " ".join(x for x in x.split() if x not in freq))

#TOKENIZING ////////////////////////////////
def identify_tokens(row):
    text = str(row['text'])
    tokens = nltk.word_tokenize(text)
    token_words = [w for w in tokens if w.isalpha()]
    return token_words
df['words'] = df.apply(identify_tokens, axis=1)

#LEMMATIZING ////////////////////////////////
from textblob import Word
def lemm_list(row):
    my_list = row['words']#over the tokenization
    lemmatized_list = [Word(word).lemmatize()for word in my_list]
    return (lemmatized_list)
df['lemmatized_words'] = df.apply(lemm_list, axis=1)

#PROSSESING DONE ////////////////////////////////
def rejoin_words(row):
    my_list = row['lemmatized_words']
    joined_words = ( " ".join(my_list))
    return joined_words
df['processed'] = df.apply(rejoin_words, axis=1)
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

stopwords = set(STOPWORDS)
stopwords.update(['we','will','aren', 'couldn', 'didn', 'doesn', 'don', 'hadn',
                  'dont','doesnt','cant','couldnt','couldve','im','ive','isnt',
                  'theres','wasnt','wouldnt','a','also','like',
                  'hasn', 'haven', 'isn', 'let', 'll', 'mustn', 're', 'shan', 'shouldn',
                  've', 'wasn', 'weren', 'won', 'wouldn','ha','wa','ldnont'])
                  
#VECTORIZING ////////////////////////////////
bow_vectorizer = CountVectorizer(max_df=0.90, min_df=2, max_features=1000, stop_words=stopwords)
bow = bow_vectorizer.fit_transform(df['processed'])
top_sum=bow.toarray().sum(axis=0)
top_sum_cv=[top_sum]
columns_cv = bow_vectorizer.get_feature_names()
x_traincvdf = pd.DataFrame(top_sum_cv,columns=columns_cv)
tfidf_vectorizer = TfidfVectorizer(max_df=0.90, min_df=2, max_features=1000,stop_words=stopwords)
text_content = df['processed']
from nltk.corpus import stopwords

#GENERATING TF-IDF FEATURE MATRIX ////////////////////////////////
stops= ['we','this','at','will','can','be','are','cant','our','on','is','an','are','by','all','it']
text_content = [word for word in text_content if not any(stop in word for stop in stops )]
tfidf = tfidf_vectorizer.fit_transform(text_content)
top_sum=tfidf.toarray().sum(axis=0)
top_sum_tfidf=[top_sum]
columns_tfidf = tfidf_vectorizer.get_feature_names()
x_traintfidf_df = pd.DataFrame(top_sum_tfidf,columns=columns_tfidf)
dic = {}
for i in range(len(top_sum_tfidf[0])):
    dic[columns_cv[i]]=top_sum_tfidf[0][i]
sorted_dic=sorted(dic.items(),reverse=True,key=operator.itemgetter(1))

#WRITING CSV FILE FOR TF-IDF OUTPUT ////////////////////////////////
df1= pd.DataFrame(sorted_dic[1:], columns=['keywords', 'Frequency'])
df1.to_csv('tfidf_DATA.csv')



#REFRENCES:
#1-https://www.kaggle.com/gangakrish/keyword-extraction-from-tweets/notebook
#2-https://www.kaggle.com/amar09/sentiment-analysis-on-scrapped-tweets

