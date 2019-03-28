import re
import nltk
import sys
import csv
import json
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer 
from nltk.parse.stanford import StanfordParser
from stanfordcorenlp import StanfordCoreNLP
from nltk.corpus import wordnet
from nltk.tree import Tree


class map_node(object):
	"""docstring for map_node"""
	def __init__(self, inputText,filepath):
		super(map_node, self).__init__()
		self.inputText = inputText
		self.filepath = filepath
		self.schema,self.schematype,self.dataset = self.__dataSet(filepath)
		self.phraseset = self.__spilt_sentence(inputText)

	#获得所有的短语集
	def __spilt_sentence(self,sentence): 
		nlp = StanfordCoreNLP('http://localhost', port=12331)
		 # 句法分析树
		rootTree = Tree.fromstring(nlp.parse(sentence))
		nlp.close()
		# 这里可以获得所有的短语集
		subtrees = rootTree.subtrees()
		phraseSet = set()
		for t in subtrees:
			tleaves = t.leaves()
			if len(tleaves) < 4:
				ele = " ".join(tleaves)
				phraseSet.add(ele)
		return phraseSet

	# 获得所有的单词集，将单词所在句子的位置定位下来：
	def get_allword(self, sentence):
		res = {}
		sen = sentence.split(' ')

		for i in range(len(sen)-1, -1, -1):
			res[sen[i]] = i

		return res


	# 获取数据表的数据
	def __dataSet(self, datasetpath):
		schema = []
		schematype = []
		dataset = {}
		with open(datasetpath) as f:
			reader = list(csv.reader(f))
			schema = reader[0]
			schematype = reader[1]
			for i in range(0, len(schema)):
				tempdata = []
				for j in range(2,len(reader)):
					tempdata.append(reader[j][i])
				dataset[schema[i]] = tempdata
		return schema,schematype,dataset

	# Jaccard相似度，判断单词短语拼写的相似度
	def __diff_spell(self, ori, cur):
		count = 0
		# print(len(cur))
		# print(ori)
		# print(cur)
		for i in range(0, min(len(ori),len(cur))):
			if ori[i] == cur[i]:
				count += 1

		return count / (len(cur) + len(ori) - count)

	# 相似度函数，返回相似度
	def __map_judge_data(self, ori, cur):
		ori = ori.lower()
		cur = cur.lower()
		res = {}
		judge_index1 = self.__diff_spell(ori,cur)
		# print('judge_index1: ', judge_index1)
		ori_list = ori.split()
		cur_list = cur.split()
		if len(ori_list) != len(cur_list):
			return 0.0
		else:
			if len(ori_list) > 1:
				return judge_index1

		if len(wordnet.synsets(ori)) > 0:
			if len(wordnet.synsets(cur)) > 0:
				# print(ori,cur)
				# print(wordnet.synsets(ori), wordnet.synsets(cur))
				judge_index2 = wordnet.synsets(ori)[0].path_similarity(wordnet.synsets(cur)[0])
				if judge_index2 != None:
					#print('judge_index2', judge_index2)
					return max(judge_index1, judge_index2)

		return judge_index1

	### column映射到他的类型
	def schema_type_map(self):
		res = {}
		for i in range(0,len(self.schema)):
			res[self.schema[i]] = self.schematype[i]

		return res

	# 映射出图表类型，函数类型
	def sub_map(self):
		visTypeDic = {'trend': ['line'], 'pie': ['pie'], 'correl': ['line', 'scatter'], 'fluctuat': ['line'], 'proport': ['pie'], 'plot': ['scatter'], 'group': ['bar'], 'min': ['bar', 'line'], 'neg': ['line', 'scatter'], 'categori': ['bar'], 'between': ['scatter'], 'distribut': ['scatter'], 'relationship': ['line', 'scatter'], 'max': ['bar', 'line'], 'relat': ['line', 'scatter'], 'histogram': ['bar'], 'part': ['pie'], 'line': ['line'], 'wave': ['line'], 'stack': ['bar'], 'bar': ['bar'], 'column': ['bar'], 'maximum': ['bar', 'line'], 'minimum': ['bar', 'line'], 'time': ['line'], 'posit': ['line', 'scatter'], 'whole': ['pie'], 'scatter': ['scatter'], 'seri': ['line']}
		visres = []
		for k,v in visTypeDic.items():
			for ph in self.phraseset:
				if self.__map_judge_data(k,ph) > 0.9:
					visres += v
		visres = list(set(visres))
		if len(visres) == 0:
			visres = ['bar', 'line','pie','scatter']

		fun_res = []
		aggrDic = {"sum":["sum"],'summarize':["sum"],'sums':["sum"],'all':["sum","count"],"avg":["avg"],'average':["avg"],'averages':["avg"],"count":["count"],'counts':["count"]}
		for k,v in aggrDic.items():
			for ph in self.phraseset:
				if self.__map_judge_data(k,ph) > 0.9:
					fun_res += v

		fun_res = list(set(fun_res))
		return visres, fun_res

	# 判断是否为数字
	def __is_number(self, str):
		try:
			if str=='NaN':
				return False
			float(str)
			return True
		except ValueError:
			return False

	def return_position(self, word, dic):
		w_l = word.split(" ")

		return dic[w_l[0]]
	
	# 分类【属性名： NN】 【数值：VN包括数据库值和数字】 【运算符：ON】 【连词：CN】
	def match(self, word):

		position_dic = self.get_allword(self.inputText)
		res = []
		# 映射属性名字
		for sc in self.schema:
			score = self.__map_judge_data(word, sc)
			if score > 0.8:
				res.append([word, score, 'NN', sc, self.return_position(word,position_dic)])
		# 映射数据库中数值
		for k,v in self.dataset.items():
			for val in v:
				score = self.__map_judge_data(word,val)
				if score > 0.9:
					res.append([word, score, 'VN', val, self.return_position(word,position_dic), k])

		# 映射数值
		need_map = True
		if self.__is_number(word):
			for val_lis in res:
				if val_lis[0] == word:
					need_map = False
					break

			if need_map == True:
				score = 1.0
				res.append([word, score, 'VN', word, self.return_position(word,position_dic)])

		# 映射运算符
		operatorlist  = ['>','<','=','>=','<=','!=']
		preplist = {'more':'>', 'less':'<','equal': '=','before':'<', 'greater':'>'}
		for k in preplist:
			score = self.__map_judge_data(k,word)
			if score > 0.8:
				res.append([word, score, 'ON', preplist[k], self.return_position(word,position_dic)])

		for val in operatorlist:
			score = self.__map_judge_data(val,word)
			if score > 0.8:
				res.append([word, score, 'ON', val, self.return_position(word,position_dic)])

		# 映射连词
		conjlist = ['and', 'or', 'not']
		for val in conjlist:
			score = self.__map_judge_data(val,word)
			if score > 0.8:
				res.append([word,score,'CN', val, self.return_position(word,position_dic)])

		return res

	def parttion(self, v, left, right):
		key = v[left]
		low = left
		high = right
		while low < high:
			while (low < high) and (v[high][1] <= key[1]):
				high -= 1
			v[low] = v[high]
			while (low < high) and (v[low][1] >= key[1]):
				low += 1
			v[high] = v[low]
			v[low] = key
		return low

	# 快排匹配好的词组，只取出前五就好
	def sort_score(self, v, left, right):
		if left < right:
			p = self.parttion(v, left, right)
			self.sort_score(v, left, p - 1)
			self.sort_score(v, p + 1, right)
		return v

	# 重组匹配
	def _reorg_list(self, res, lis):
		if len(res) == 0:
			for v in lis:
				res.append([v])
			return res
		else:
			for i in range(0,len(res)):
				temp = res.pop(0)
				for v in lis:
					newList = temp + [v]
					res.append(newList)

		return res

	# 去重函数
	def dedup_list(self, lis):
		newlist = []
		for val in lis:
			if val not in newlist:
				newlist.append(val)

		return newlist

	# 匹配对应的词组，这里先不考虑合并词组
	def main_map(self):

		mainmap = []
		for ph in self.phraseset:
			partl = self.match(ph)
			partlis = self.dedup_list(partl)
			# print("**********")
			# print(partlis)
			if len(partlis) == 0:
				continue
			self.sort_score(partlis, 0, len(partlis) - 1)
			temp_list = []
			for i in range(0,5):
				if len(partlis) > 0:
					temp_list.append(partlis.pop(0))
			mainmap.append(temp_list)
		# print(mainmap)

		myres = []
		for li in mainmap:
			self._reorg_list(myres,li)

		return myres

	# 返回隐藏的属性名称，主要是日期属性
	def hide_column(self):
		res = []
		hide_date = ['time', 'year','month', 'day']
		for ph in self.phraseset:
			if ph in hide_date:
				for k,v in self.schema_type_map().items():
					if v == 'DATE':
						res.append(k)
		
		return res



if __name__ == '__main__':
	#inputText = "show me elctConsumption in shanghai over time".lower()
	inputText = "show me elctConsumption > 100 and not less than 1000 in shanghai over time".lower()
	#inputText = inputText = "show me elctConsumption where elctconsumption > shanghai".lower()
	datasetpath = "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"

	ma = map_node(inputText, datasetpath)

	print(ma.schema)
	print(ma.schematype)
	#print(ma.dataset)
	print(ma.phraseset)

	print(ma.sub_map())
	print(ma.hide_column())
	print(ma.main_map())
	