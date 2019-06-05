# -*- coding: utf-8 -*-
"""
Created on Wed May 15 22:10:18 2019
@author: George Pan

"""
import pandas as pd
import csv
from collections import Counter
from sklearn.feature_selection import chi2
import numpy as np
from joblib import load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import chi2
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC

model = load('./data/model.joblib')
class FeatureWorker(object): 
    def get_top_weights(self,class_num):
        #model = load('./data/model.joblib')
        tfidf = load('./data/tfidf.joblib')
        indices = np.argsort(model.coef_[class_num,])[-20:]
        tracker = []
        feat = tfidf.get_feature_names()
        for i in indices:
            gram = feat[i]
            if len(gram.split()) == 1:
                tracker.append(gram)
            else:
                pass
        return(tracker)

    def get_category(self,file, tweets):
        df = pd.read_csv(file)
        df.columns = ['tweet','show']
        df = df[pd.notna(df['tweet'])]
        
        tfidf = TfidfVectorizer(sublinear_tf=True, norm='l2', encoding='latin-1', ngram_range=(1, 2), stop_words='english')
        features = tfidf.fit_transform(df.tweet)
        labels = df.show

        #model = load('./data/model.joblib')
        test = tfidf.transform(tweets)
        ans = model.predict(test)
        
        final = Counter(ans)
        best = final.most_common(3)
        npans = np.array(ans)
        indices = []
        indices.append(np.where(npans==best[0][0]))
        indices.append(np.where(npans==best[1][0]))
        indices.append(np.where(npans==best[2][0]))
        

        return (final.most_common(3),indices)