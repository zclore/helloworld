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

from match import Data_preprocessing

class Tree_Operator(object):

	__tree = Tree('root',[])
	def __init__(self, inputText, filename): 
		self.data = Data_preprocessing(inputText,filename)
		self.tree = self.__dep2Tree(inputText)

	@property
	def tree(self):
		return self.__tree

	@tree.setter
	def tree(self, tree):
		self.__tree = tree

	def draw(self):
		self.tree.draw()

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
		# root = ['show']
		newList = []
		for e in lis:
			if type(e) == str:
				if e in self.data.media_val_list() or e in self.data.NN_list() or e in self.data.conj_map(): # or e in root
					newList.append(e)
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

	# 介词上移
	def prep_up(self, lis):
		#root = ['show']
		temp = lis[0]
		flag = True
		if temp in self.data.NN_list():#or temp in root:
			for i in range(1,len(lis)):
				if type(lis[i]) == str and flag == True:
					if lis[i] in self.data.media_val_list():
						lis[0] = lis[i]
						lis[i] = temp
						break
		newList = []

		for e in lis:
			if type(e) == str:
				newList.append(e)
			else:
				newList.append(self.prep_up(e))
		return newList

	# column_val_map中是否有column：val的关系
	def __in_column_val(self, colu, val):
		column_val_map = self.data.column_val_map()
		if colu in column_val_map.items():
			for dic in column_val_map[colu]:
				if val in dic:
					return True

		return False

	# 找到column_val_map中column：val的关系
	def __is_in_column_val(self, val):
		print(val)
		column_val_map = self.data.column_val_map()

		for k,v in column_val_map.items():
			for dic in v:
				if val in dic:
					return k
		return None
	
	# 翻译主函数，现在有三条规则
	def __shell_transform(self,par_node, lis_tree):
		if lis_tree[0] in self.data.operator_map():
			operator = lis_tree[0]
		if lis_tree[0] in self.data.prep_map():
			prep_to_op = self.data.prep_to_operator()
			operator = prep_to_op[lis_tree[0]]

		newList = []
		# 1.父节点是column, 子节点为column内容
		column_map = self.data.column_map()
		if par_node in column_map:
			for clou in column_map[par_node]:
				for i in range(1,len(lis_tree)):
					if type(lis_tree[i]) == str and self.__in_column_val(clou,lis_tree[i]):
						newList.append(clou + " " + operator + " " + lis_tree[i])

		schema_type_map = self.data.schema_type_map()
		# 2.父节点是column，子节点为数据或者日期，其类型和父节点相同
		if par_node in column_map:
			for colu in column_map[par_node]:
				for i in range(1,len(lis_tree)):
					if lis_tree[i] in self.data.digit_map():
						if schema_type_map[colu] == 'FLOAT':
							newList.append(clou + " " + operator + " " + lis_tree[i])
					if lis_tree[i] in self.data.date_map():
						if schema_type_map[colu] == 'DATE':
							newList.append(clou + " " + operator + " " + lis_tree[i])

		# 3.父节点无用，子节点直接和自己的关联的类型相连接,子节点和父节点无关系
		for i in range(1,len(lis_tree)):
			if type(lis_tree[i]) == str:
				if self.__is_in_column_val(lis_tree[i]) != None:
					newList.append(self.__is_in_column_val(lis_tree[i]) + " " + operator + " " + lis_tree[i])
				else:
					for sch in self.data.schema:
						if lis_tree[i] in self.data.digit_map():
							if schema_type_map[sch] == 'FLOAT':
								newList.append(sch + " " + operator + " " + lis_tree[i])
						if lis_tree[i] in self.data.date_map():
							if schema_type_map[sch] == 'DATE':
								newList.append(sch + " " + operator + " " + lis_tree[i])

		return list(set(newList))

	#这边的树是否只能最多为二叉树，翻译函数
	def transform_tree(self, lis):
		res_list = []
		for i in range(1, len(lis)):
			if type(lis[i]) == str :
				res_list.append(lis[i])
			else:
				if lis[i][0] in self.data.media_val_list():
					res_list.append(self.transform_tree(lis[i]))
					print('******************')
					print(lis[0])
					print(lis[i])
					print(self.__shell_transform(lis[0], lis[i]))
					res_list.append(self.__shell_transform(lis[0], lis[i]))
					print(res_list)

		return res_list


	def __pailie(self, res, lis):
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

	# 这里生成select语句
	def generate_select(self):
		select_culumn = []
		column_map = self.data.column_map()
		hide_column = self.data.hide_column()

		if column_map:
			for k in column_map:
				select_column = self.__pailie(select_culumn, column_map[k])
			for i in range(0, len(select_column)):
				temp = select_column.pop(0)
				select_column.append(temp + hide_column)
		else:
			select_culumn = hide_column

		for val in select_culumn:
			val.sort()
		res = []
		for val in select_culumn:
			if val not in res:
				res.append(val)
			if len(res) >= 5:
				break
		return res

	# 简化列表，把list中的string全提出来，去除嵌套作用
	def simplify_list(self, lis, res):
		for li in lis:
			if type(li) == str:
				res.append(li)
			else:
				self.simplify_list(li, res)

		return
			

	# 这里生成where语句
	def generate_where(self, lis):
		res = []
		for s in lis:
			tempstr = s
			if len(s.split(' ')) == 3:
				res.append(tempstr)

		return res

	# 由select和where生成SQL语句
	def generate_sql(self, lis_select, lis_where, conj_ident):
		if 'not' in conj_ident:
			index = conj_ident.index('not')
			if index + 1 < len(conj_ident):
				if conj_ident[index + 1] in self.data.NN_list():
					for i in range(0, len(lis_where)):
						temp_str = lis_where[i]
						if lis_where[i].split(' ')[2] == conj_ident[index + 1]:
							lis_where.pop(i)
							lis_where.append("( not " + temp_where + " )" )

		if 'and' in conj_ident:
			index = conj_ident.index('and')
			if index + 1 < len(conj_ident) and index - 1 >= 0:
				if conj_ident[index + 1] in self.data.NN_list() and conj_ident[index - 1] in self.data.NN_list():
					res_str = ''
					for i in range(0, len(lis_where)):
						temp_str = lis_where[i]
						if lis_where[i].split(' ')[2] == conj_ident[index - 1]:
							lis_where.pop(i)
							res_str += "( " + temp_str + " and" 
							break
					for i in range(0, len(lis_where)):
						temp_str = lis_where[i]
						if lis_where[i].split(' ')[2] == conj_ident[index + 1]:
							lis_where.pop(i)
							res_str += " " + temp_str + " )" 
							break
					lis_where.append(res_str)

		if 'or' in conj_ident:
			index = conj_ident.index('or')
			if index + 1 < len(conj_ident) and index - 1 >= 0:
				if conj_ident[index + 1] in self.data.NN_list() and conj_ident[index - 1] in self.data.NN_list():
					res_str = ''
					for i in range(0, len(lis_where)):
						temp_str = lis_where[i]
						if lis_where[i].split(' ')[2] == conj_ident[index - 1]:
							lis_where.pop(i)
							res_str += "( " + temp_str + " or" 
							break
					for i in range(0, len(lis_where)):
						temp_str = lis_where[i]
						if lis_where[i].split(' ')[2] == conj_ident[index + 1]:
							lis_where.pop(i)
							res_str += " " + temp_str + " )" 
							break
					lis_where.append(res_str)

		print("newlis_where:            ", lis_where)
		res = []
		for sele in lis_select:
			s = 'select '
			temp_select = ', '.join(sele)
			temp_where = ' and '.join(lis_where)
			s = s + temp_select + ' where '+ temp_where
			res.append(s)

		return res


if __name__ == '__main__':
	inputText = "show me elctConsumption > 100 and less than 1000 in shanghai over time".lower()
	datasetpath = "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"
	tree = Tree_Operator(inputText, datasetpath)
	print('vis_map: ', tree.data.vis_map())	
	print('column_map: ', tree.data.column_map())
	print('column_val_map: ', tree.data.column_val_map())	
	print('digitalgroup: ', tree.data.digit_map())
	print('prep_map: ', tree.data.prep_map())	
	print('conj_map: ', tree.data.conj_map())
	print('operator_map: ', tree.data.operator_map())
	print('media_val_list: ', tree.data.media_val_list())
	print('date_map: ', tree.data.date_map())	
	print('NN_list: ', tree.data.NN_list())
	print('dataval_list: ', tree.data.dataval_list())
	print('hide_column: ', tree.data.hide_column())

	# tree.draw()

	lis = tree.treeTolist(tree.tree)   #树转列表
	print(lis)
	lis = tree.remove_uselessword(lis) # 
	print(lis)
	lis = tree.correct_list(lis)
	print(lis)
	lis = tree.prep_up(lis)
	print(lis)

	print('&&&&&&&&&&&&&&')
	spare_lis =  copy.deepcopy(lis)
	mytree = tree.listTotree(spare_lis)
	mytree.draw()
	conj_ident = mytree.leaves()

	print(conj_ident)
	print(lis)

	lis = tree.transform_tree(lis)
	print(lis)
	print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
	slect_lis = tree.generate_select()
	print(slect_lis)
	whe_lis = []
	tree.simplify_list(lis, whe_lis)
	print(whe_lis)
	whe_lis = tree.generate_where(whe_lis)
	print(whe_lis)
	sql_lis = tree.generate_sql(slect_lis, whe_lis, conj_ident)
	print(sql_lis)
