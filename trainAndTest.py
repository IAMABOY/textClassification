#-*- coding:utf8 -*-

import random
import jieba
import pandas as pd
import csv
from sklearn.feature_extraction.text import TfidfVectorizer, HashingVectorizer,CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import numpy as np
from sklearn.svm import SVC
from sklearn import tree

def csvReader(dataPath,dataArray):
	dataReader = csv.reader(open(dataPath,'r'))	
	for row in dataReader:
		dataArray.append(row[0])

def preprocess_text(content_lines, sentences, label):
	for line in content_lines:
		try:
			lineLower = line.lower()#全部转化为小写，排除大小写的干扰
			segs=jieba.lcut(lineLower)
			segs = [v for v in segs if not str(v).isdigit()]#去数字
			segs = list(filter(lambda x:x.strip(), segs))   #去左右空格
			segs = list(filter(lambda x:len(x)>1, segs)) #长度为1的字符
			segs = list(filter(lambda x:x not in stopwords, segs)) #去掉停用词
			#print(segs)
			sentences.append((" ".join(segs), label))# 打标签
		except Exception:
			#print(line)
			continue

def dataSpliter(sentences):
	x, y = zip(*sentences)
	trainData,testData,trainLabel,testLabel = train_test_split(x, y, test_size=0.3, random_state=0)
	return trainData,testData,trainLabel,testLabel


#加载停用词
stopwords=pd.read_csv('stopWords.txt',index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
stopwords=stopwords['stopword'].values

#print (stopwords)

commonSiteTitle = []
adultSiteTitle = []
#加载语料
csvReader("oldData/commonSiteDescription.csv",commonSiteTitle)
csvReader("oldData/adultSiteDescription.csv",adultSiteTitle)

adultSiteSentences = []
preprocess_text(adultSiteTitle, adultSiteSentences, 0)
random.shuffle(adultSiteSentences)
adultSiteTrainData,adultSiteTestData,adultSiteTrainLabel,adultSiteTestLabel = dataSpliter(adultSiteSentences)
#print(adultSiteTestLabel)

commonSiteSentences = []
preprocess_text(commonSiteTitle, commonSiteSentences,1)
random.shuffle(commonSiteSentences)
commonSiteTrainData,commonSiteTestData,commonSiteTrainLabel,commonSiteTestLabel = dataSpliter(commonSiteSentences)

trainData = []
trainLabel = []
testData = []
testLabel = []

trainData = adultSiteTrainData + commonSiteTrainData
trainLabel = adultSiteTrainLabel + commonSiteTrainLabel
testData = adultSiteTestData + commonSiteTestData
#testData = adultSiteTestData
testLabel = adultSiteTestLabel + commonSiteTestLabel
#testLabel = adultSiteTestLabel

vec = CountVectorizer(analyzer='word',max_features=4000,)
#vec = TfidfVectorizer(analyzer='word',max_features=4000,)
#vec = HashingVectorizer(n_features=2)
vec.fit(trainData)
print(vec.transform(testData))
#print(vec.transform(testData).toarray())
#print(vec.get_feature_names())
classifier = MultinomialNB()
classifier = SVC(kernel="linear")
classifier = tree.DecisionTreeClassifier()
classifier.fit(vec.transform(trainData), trainLabel)

predictResult = classifier.predict(vec.transform(testData))
print("预测结果:",predictResult)
#print("预测概率:",classifier.predict_proba(vec.transform(testData)))
print(classifier.score(vec.transform(testData), testLabel))


count = 0
while count < len(testLabel):
	#if(predictResult[count] != testLabel[count]):
		#print(predictResult[count],testLabel[count],testData[count])
	count = count + 1