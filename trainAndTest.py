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

def getWordsAndMakeLabel(content_lines, sentences, label):
	for line in content_lines:
		try:
			lineLower = line.lower()#全部转化为小写，排除大小写的干扰
			words=jieba.lcut(lineLower)
			words = [v for v in words if not str(v).isdigit()]#去数字
			words = list(filter(lambda x:x.strip(), words))   #去左右空格
			words = list(filter(lambda x:len(x)>1, words)) #长度为1的字符
			words = list(filter(lambda x:x not in stopwords, words)) #去掉停用词
			sentences.append((" ".join(words), label))# 打标签
		except Exception:
			print(line)
			continue

def dataSpliter(sentences):
	x, y = zip(*sentences)
	trainData,testData,trainLabel,testLabel = train_test_split(x, y, test_size=0.3, random_state=0)
	return trainData,testData,trainLabel,testLabel

#加载停用词
stopwords=pd.read_csv('stopWords.txt',index_col=False,quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
stopwords=stopwords['stopword'].values

commonSiteTitle = []
adultSiteTitle = []
#加载语料
csvReader("oldData/commonSiteDescription.csv",commonSiteTitle)
csvReader("oldData/adultSiteDescription.csv",adultSiteTitle)

adultSiteWords = []
getWordsAndMakeLabel(adultSiteTitle, adultSiteWords, 0)
random.shuffle(adultSiteWords)
adultSiteTrainData,adultSiteTestData,adultSiteTrainLabel,adultSiteTestLabel = dataSpliter(adultSiteWords)

commonSiteWords = []
getWordsAndMakeLabel(commonSiteTitle, commonSiteWords,1)
random.shuffle(commonSiteWords)
commonSiteTrainData,commonSiteTestData,commonSiteTrainLabel,commonSiteTestLabel = dataSpliter(commonSiteWords)

trainData = []
trainLabel = []
testData = []
testLabel = []

trainData = adultSiteTrainData + commonSiteTrainData
trainLabel = adultSiteTrainLabel + commonSiteTrainLabel
testData = adultSiteTestData + commonSiteTestData
testLabel = adultSiteTestLabel + commonSiteTestLabel

vec = CountVectorizer(analyzer='word',max_features=4000,)
#vec = TfidfVectorizer(analyzer='word',max_features=4000,)
#vec = HashingVectorizer(n_features=2)
vec.fit(trainData)
#print(vec.transform(testData).toarray())
#print(vec.get_feature_names())
classifier = MultinomialNB()
#classifier = SVC(kernel="linear")
#classifier = tree.DecisionTreeClassifier()
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