import nltk
import sys
import csv
import json
import copy
from nltk import CFG
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer 
from nltk.parse.stanford import StanfordDependencyParser
from stanfordcorenlp import StanfordCoreNLP
from nltk.corpus import wordnet
from nltk.tree import Tree

from map_node import map_node

class pre_deal(object):
	"""docstring for pre_deal"""
	def __init__(self, map_list, inputText):
		self.map_list = map_list + [['show',1.0, 'root', 'show', 0]]
		self.tree = self.__dep2Tree(inputText)
		self.ON_VN_map = {}

	def draw(self):
		self.tree.draw()

	def get_map_list(self):
		return self.map_list

	# 得到依存关系树
	def __dep2Tree(self, sentence):
		path_to_jar = 'D:/myPlugin/stanford-parser-full-2018-10-17/stanford-parser.jar'
		path_to_models_jar = 'D:/myPlugin/stanford-parser-full-2018-10-17/stanford-parser-3.9.2-models.jar'
		dependency_parser = StanfordDependencyParser(path_to_jar=path_to_jar, path_to_models_jar=path_to_models_jar)
		result = dependency_parser.raw_parse(sentence)
		t = result.__next__().tree()
		return t

	# 树转为列表便于操作
	def treeTolist(self, t):
		res = []
		s = t.label()
		res.append(s)
		if len(t) == 0:
			return res
		for sub in t:
			if type(sub) == str:
				res.append(sub)
			else:
				res.append(self.treeTolist(sub))
		return res

	# 列表转回树
	def listTotree(self, lis):
		root = lis.pop(0)

		sub = []
		for t in lis:
			if type(t) == str:
				sub.append(t)
			else:
				sub.append(self.listTotree(t))

		return Tree(root,sub)

	# 去除列表中的无用的单词
	def remove_uselessword(self, lis):
		newList = []
		#print("********")
		#print(self.get_map_list())
		for e in lis:
			if type(e) == str:
					for subl in self.map_list:
						if subl[0] == e:
							newList.append(subl[3])
			else:
				newList.append(self.remove_uselessword(e))

		return newList

	# 这个校正列表，使其符合树结构
	def correct_list(self, lis):
		newList = []
		for e in lis:
			if type(e) != str:
				if len(e) == 1:
					newList.append(e[0])
				else:
					if(len(e) > 0):
						newList.append(self.correct_list(e))
			else:
				newList.append(e)
		if len(newList) == 1:
			newList = newList[0]
		return newList

	def is_pos(self, word, pos):
		for subl in self.map_list:
			if subl[3] == word and subl[2] == pos:
				return True

		return False

	def get_pos(self, word):

		for val_list in self.map_list:
			if val_list[3] == word:
				return val_list[2]

	# 预处理，以免去掉了原有的映射关系
	def init_ON_VN_map(self, lis):
		temp = lis[0]

		# print("&&&&&&")
		# print(temp)

		if self.get_pos(lis[0]) == 'ON':
			for i in range(1, len(lis)):
				# print(lis[i])
				# print(self.get_pos(lis[i]))
				if type(lis[i]) == str:
					# print("hhhhhh")
					# print(lis[i])
					# print(self.get_pos(lis[i]))
					if self.get_pos(lis[i]) == 'VN':
						print("hello word")
						self.ON_VN_map[lis[i]] = lis[0]
		else:
			for i in range(1, len(lis)):
				if type(lis[i]) != str:
					self.init_ON_VN_map(lis[i])

		# print("zhang")
		# print(self.ON_VN_map)

	# 介词上移
	def prep_up(self, lis):
		temp = lis[0]

		if self.is_pos(temp, 'VN'):
			for i in range(1,len(lis)):
				if type(lis[i]) == str:
					if self.is_pos(lis[i], 'ON'):
						lis[0] = lis[i]
						lis[i] = temp
						self.ON_VN_map[lis[i]] = lis[0]
						break
		newList = []

		for e in lis:
			if type(e) == str:
				newList.append(e)
			else:
				newList.append(self.prep_up(e))
		return newList

	# 连词上移
	def conj_up(self, lis):
		temp = lis[0]

		if self.is_pos(temp, 'ON'):
			for i in range(1, len(lis)):
				if type(lis[i]) == str:
					if self.is_pos(lis[i], 'CN'):
						lis[0] = lis[i]
						lis[i] = temp
						break
		print("************")
		print(lis)
		
		for k,v in self.ON_VN_map.items():
			if k in lis and v in lis:
				if lis[0] != v and lis[0] != k:
					lis.insert(lis.index(k), [v, k])
					lis.remove(k)
					lis.remove(v)

		newList = []

		for e in lis:
			if type(e) == str:
				newList.append(e)
			else:
				newList.append(self.conj_up(e))
		return newList


if __name__ == '__main__':

	#inputText = "show me elctConsumption where city = shanghai"
	inputText = "show me elctConsumption > 100 and not less than 1000 in shanghai over time".lower()
	# inputText = "show me  elctConsumption where the elctConsumption > shanghai after 2000 ".lower()
	#inputText = "show me elctConsumption where elctconsumption > shanghai".lower()
	map_list = [['100', 1.0, 'VN', '100'], ['1000', 1.0, 'VN', '1000'], ['not', 1.0, 'CN', 'not'], ['less', 1.0, 'ON', '<'], ['and', 1.0, 'CN', 'and'], ['elctconsumption', 1.0, 'NN', 'elctConsumption'], ['shanghai', 1.0, 'VN', 'Shanghai', 'cityName'], ['>', 1.0, 'ON', '>']]
	#map_list = [['>', 1.0, 'ON', '>'],  ['shanghai', 1.0, 'VN', 'Shanghai', 'cityName'], ['elctconsumption', 1.0, 'NN', 'elctConsumption']]
	
	pre = pre_deal(map_list, inputText)
	'''
	mylis = ['show', 'elctConsumption', 'Shanghai',['and',  ['>', '100'],['not', ['<', '1000']]]]
	mytree = pre.listTotree(mylis)
	mytree.draw()
'''
	print(pre.map_list)

	mylis = pre.treeTolist(pre.tree)
	print(mylis)

	mylis = pre.remove_uselessword(mylis)
	mylis = pre.correct_list(mylis)
	print(mylis)
	pre.init_ON_VN_map(mylis)
	print(pre.ON_VN_map)


	mylis = pre.prep_up(mylis)
	print(mylis)
	print(pre.ON_VN_map)
	mylis = pre.conj_up(mylis)
	print(mylis)
	print(pre.ON_VN_map)
	
	mytree = pre.listTotree(mylis)
	mytree.draw()

