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

class Data_preprocessing(object):
	"""docstring for Data preprocessing"""
	def __init__(self, inputText,filepath):
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
			if len(tleaves) < 5:
				ele = " ".join(tleaves)
				phraseSet.add(ele)
		return phraseSet


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

	# Jaccard相似度，判断单词短语的相似度
	def __diff_spell(self, ori, cur):
		count = 0
		# print(len(cur))
		# print(ori)
		# print(cur)
		for i in range(0, min(len(ori),len(cur))):
			if ori[i] == cur[i]:
				count += 1

		return count / (len(cur) + len(ori) - count)


	# 对映射字典排序，返回大于阈值的前五的值,dic = {val:key}
	def __dict_order(self, dic):
		res = []
		sort_list = sorted(dic)
		for val in sort_list:
			res.append(dic[val])
			if len(res) >= 5:
				return res

		return res

	# 相似度函数，返回两个单词是否一样，这个函数主要匹配常识集和单词
	def __map_judge(self, ori, cur):
		ori = ori.lower()
		cur = cur.lower()
		judge_index1 = self.__diff_spell(ori,cur)
		# print('judge_index1: ', judge_index1)
		ori_list = ori.split()
		cur_list = cur.split()
		if len(ori_list) != len(cur_list):
			return False
		else:
			if len(ori_list) > 1:
				if judge_index1 > 0.91:
					return True 
				else:
					return False
		if len(wordnet.synsets(ori)) > 0:
			if len(wordnet.synsets(cur)) > 0:
				# print(ori,cur)
				# print(wordnet.synsets(ori), wordnet.synsets(cur))
				judge_index2 = wordnet.synsets(ori)[0].path_similarity(wordnet.synsets(cur)[0])
				if judge_index2 != None:
					#print('judge_index2', judge_index2)
					if max(judge_index1, judge_index2) > 0.91:
						return True
					else:
						return False
		if judge_index1 > 0.91:
			return True
		return False

	# 相似度函数，寻找前五函数
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

	# 判断是否为数字
	def __is_number(self, str):
		try:
			if str=='NaN':
				return False
			float(str)
			return True
		except ValueError:
			return False

	### column映射到他的类型
	def schema_type_map(self):
		res = {}
		for i in range(0,len(self.schema)):
			res[self.schema[i]] = self.schematype[i]

		return res

	 #  获得出现的图像类型的筛选
	def vis_map(self):
		visTypeDic = {'trend': ['line'], 'pie': ['pie'], 'correl': ['line', 'scatter'], 'fluctuat': ['line'], 'proport': ['pie'], 'plot': ['scatter'], 'group': ['bar'], 'min': ['bar', 'line'], 'neg': ['line', 'scatter'], 'categori': ['bar'], 'between': ['scatter'], 'distribut': ['scatter'], 'relationship': ['line', 'scatter'], 'max': ['bar', 'line'], 'relat': ['line', 'scatter'], 'histogram': ['bar'], 'part': ['pie'], 'line': ['line'], 'wave': ['line'], 'stack': ['bar'], 'bar': ['bar'], 'column': ['bar'], 'maximum': ['bar', 'line'], 'minimum': ['bar', 'line'], 'time': ['line'], 'posit': ['line', 'scatter'], 'whole': ['pie'], 'scatter': ['scatter'], 'seri': ['line']}
		res = []
		for k,v in visTypeDic.items():
			for ph in self.phraseset:
				if self.__map_judge(k,ph):
					res += v
		res = list(set(res))
		if len(res) == 0:
			res = ['bar', 'line','pie','scatter']

		return res

	# 获取出现的属性名
	def column_map(self):
		res = {}
		for ph in self.phraseset:
			map_dic = {}
			for colu in self.schema:
				sim = self.__map_judge_data(colu,ph)
				if sim > 0.8:
					map_dic[sim] = colu
			if len(self.__dict_order(map_dic)) > 0:
				res[ph] = self.__dict_order(map_dic)

		return res

	# 出现的函数筛选，(聚合函数，sum)等
	def fun_map(self):
		res = []
		aggrDic = {"sum":["sum"],'summarize':["sum"],'sums':["sum"],'all':["sum","count"],"avg":["avg"],'average':["avg"],'averages':["avg"],"count":["count"],'counts':["count"]}
		for k,v in aggrDic.items():
			for ph in self.phraseSet:
				if self.__map_judge(k,ph):
					fun_map += v
		return res

	 # 内容映射，文本中的短语是否为数据集的内容，映射到column中,TODO
	def column_val_map(self):
		column_val_map = {}
		for ph in self.phraseset:
			for k,v in self.dataset.items():
				for con in v:
					#if self.__map_judge(ph,con):
					if ph.lower() == con.lower():
						column_val_map.setdefault(k,[]).append({ph:con})

		for k,v in column_val_map.items():
			newList = []
			for x in v:
				if x not in newList:
					newList.append(x)
			column_val_map[k] = newList

		return column_val_map

	# 数字映射
	def digit_map(self):
		res= []
		for ph in self.phraseset:
			if self.__is_number(ph):
				res.append(ph)
		return res

	# 连词映射
	def conj_map(self):
		res = []
		conjlist = ['and','or', 'not']
		for ph in self.phraseset:
			if ph in conjlist:
				res.append(ph)
		return res

	# 介词映射
	def prep_map(self):
		res = []
		preplist = ['more','less','after','before', 'between', 'greater']
		for ph in self.phraseset:
			if ph in preplist:
				res.append(ph)
		return res

	# 运算符映射
	def operator_map(self):
		res = []
		operatorlist  = ['>','<','=','>=','<=','!=']
		for ph in self.phraseset:
			if ph in operatorlist:
				res.append(ph)
		return res

	# 日期映射
	def date_map(self):
		date = re.compile(r'\d{4}/\d{1,2}/\d{1,2}')
		date_map = date.findall(self.inputText)
		return date_map

	# 出现的中间词，可用于条件 = 介词 + 运算词
	def media_val_list(self):
		res= []
		res = self.prep_map() + self.operator_map()
		return res

	def prep_to_operator(self):
		res = {'more':'>', 'less':'<','equal': '=','before':'<', 'between':'<', 'greater':'>'}
		return res

	# 出现的名词 = 数字 + 日期 + 属性 + 数据集内容
	def NN_list(self):
		res = []
		res = self.date_map() + self.digit_map()

		for k,v in self.column_map().items():
			res.append(k)

		for k,v in self.column_val_map().items():
			for val in v:
				for m,n in val.items():
					res.append(m)
		return list(set(res))

	#出现在句子中的数据集的内容
	def dataval_list(self):
		res = []
		for k,v in self.column_val_map().items():
			for val in v:
				for m,n in val.items():
					res.append(m)
		return list(set(res))

	# 返回隐藏的属性名称，主要是日期属性
	def hide_column(self):
		res = []
		hide_date = ['time', 'year','month', 'day']
		for ph in self.phraseset:
			if ph in hide_date:
				for k,v in self.schema_type_map().items():
					if v == 'DATE':
						res.append(k)
				break

		return res

	# 这里要给出所有的词可能的映射，[[val:NN], [val: ON], .......]
	def show_all_map()：
		res = []
		column_map = self.column_map()
		temp_dic = {}
		for k in column_map:
			temp_dic[k] == 'NN'

		column_val_map = self.column_val_map()





if __name__ == '__main__':

	inputText = "show me elctConsumption in shanghai over time".lower()#"show me elctConsumption not more than 10000 or less than 1000".lower()
	datasetpath = "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"
	data = Data_preprocessing(inputText,datasetpath)
	print('vis_map: ', data.vis_map())	
	print('column_map: ', data.column_map())
	print('column_val_map: ', data.column_val_map())	
	print('digitalgroup: ', data.digit_map())
	print('prep_map: ', data.prep_map())	
	print('conj_map: ', data.conj_map())
	print('operator_map: ', data.operator_map())
	print('media_val_list: ', data.media_val_list())
	print('date_map: ', data.date_map())	
	print('NN_list: ', data.NN_list())
	print('dataval_list: ', data.dataval_list())
	print('hide_column: ', data.hide_column())

