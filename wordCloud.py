#-*- coding:utf8 -*-
import jieba.analyse
from scipy.misc import imread 
from wordcloud import WordCloud,ImageColorGenerator
import matplotlib.pyplot as plt
import csv

def csvReader(dataPath,dataArray):
    dataReader = csv.reader(open(dataPath,'r'))
    for row in dataReader:
        dataArray.append(row[0])

#语料数据
content = []
csvReader("oldData/commonSiteTitle.csv",content)

#分词
jieba.analyse.set_stop_words("stopWords.txt")#停用词
tags = jieba.analyse.extract_tags(str(content).lower(), topK=100000, withWeight=True)

#词云输入
wordsNumber = len(tags)
wordsAndNumber = {}#单词和词频
for v, n in tags:
    if not str(v).isdigit() and len(v) > 1:#去数字and长度为1的字符
        wordsAndNumber[v] = int(n*wordsNumber)
        #print(v,n)

wordCloud=WordCloud(background_color='white',  # 设置背景颜色 
                     max_font_size= 80,  # 字体最大值
                     )

wordCloud=wordCloud.fit_words(wordsAndNumber)
wordCloud.recolor()

plt.imshow(wordCloud)
plt.axis("off")
plt.show()
wordCloud.to_file(r'wordCloud.jpg')  #保存结果
