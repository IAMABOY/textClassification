#-*- coding:utf8 -*-
import csv
import jieba
import pandas as pd
import random
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

def getWordsAndMakeLabel(allLines, sentences, label):
	for line in allLines:
		lineLower = line.lower()#全部转化为小写，排除大小写的干扰
		wordsOfALine=jieba.lcut(lineLower)
		wordsOfALine = [word for word in wordsOfALine if not str(word).isdigit()]#去数字
		wordsOfALine = list(filter(lambda word:word.strip(), wordsOfALine))   #去左右空格
		wordsOfALine = list(filter(lambda word:word not in stopWords, wordsOfALine)) #去掉停用词
		sentences.append((" ".join(wordsOfALine), label))# 打标签
		

def dataSpliter(sentences):
	x, y = zip(*sentences)
	trainData,testData,trainLabel,testLabel = train_test_split(x, y, test_size=0.3, random_state=0)
	return trainData,testData,trainLabel,testLabel

#加载语料和停用词
commonSiteTitle = []
adultSiteTitle = []
stopWords = []

csvReader("oldData/commonSiteDescription.csv",commonSiteTitle)
csvReader("oldData/adultSiteDescription.csv",adultSiteTitle)
csvReader("oldData/stopWords.csv",stopWords)

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
	if(predictResult[count] != testLabel[count]):
		print(predictResult[count],testLabel[count],testData[count])
	count = count + 1
