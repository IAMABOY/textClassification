#-*- coding:utf8 -*-


import csv
import sys
import os
import re
from bs4 import BeautifulSoup
import codecs
import pandas as pd

#reload(sys)
#sys.setdefaultencoding('latin1')#将python默认编码从ascii改为utf8，因为ascii只能表示128以内的二进制，128-256之间表示不了
csv.field_size_limit(sys.maxsize)
outputFile = codecs.open("commonSiteKeywords.csv",'wb')
dataPath = 'top4500_commonSite.csv'#训练数据
#print(path)
dataReader = csv.reader(codecs.open(dataPath,'rb'))


outputFileWriter = csv.writer(outputFile)
	

for i,row in enumerate(dataReader):
	
	if row and row[1]:
		soup = BeautifulSoup(row[1],"html.parser")
		if soup:
			#description = soup.find(attrs={"name":"description"})['content']
			description = soup.find(attrs={"name":"keywords"})
			if description:

				descriptionContent = description.get('content')#不用description['content']原因是，当没有content而是value的时候会发生崩溃

				if descriptionContent:
					if all(ord(c) < 128 for c in descriptionContent):
						outputFileWriter.writerow([descriptionContent])

			'''title = soup.title.string
			if title:
				if all(ord(c) < 128 for c in title):
					print(title)
					outputFileWriter.writerow([title])'''

		'''m = re.search("<title>.*</title>", row[1])
		if m:
			title = m.group().strip("</title>")
			if all(ord(c) < 128 for c in title):
				print m.group() # 这里输出结果 <title>Apple</title>
				#outputFileWriter.writerow(m.group().strip("</title>"))
				outputFileWriter.writerow([title])'''
		#print m.group().strip("</title>") #问题应该出现在这个正则
