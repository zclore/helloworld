import nltk
import sys
import csv
import json
import copy
from TreeNode import TreeNode
from map_node import map_node
from tree import Tree

class translate(object):
	"""docstring for translate"""
	def __init__(self, t, map_list, ON_VN_map):
		super(translate, self).__init__()
		self.tree = t
		self.map_list = map_list
		self.ON_VN_map = ON_VN_map

	def str_jion(self, midword, lis):
		res = ""
		for i in range(0, len(lis) - 1):
			res += lis[i] + midword
		res += lis[len(lis)-1]

		return res

	# 依据树生成SQL语句
	def generate_sql(self, rootnode):
		res = ''
		if rootnode.pos != 'root':
			return res

		count = 0
		for node in rootnode.child:
			if node.pos == 'NN':
				count += 1
				N_node = node
				if node.len_child() != 0:
					return res
		print("**** ", count)
		if count != 1:
			return res

		self.NN = N_node

		res += "select " + N_node.val + " where "
		where_filter = []
		for node in rootnode.child:
			if node.pos != 'NN' and node.pos != 'root':
				where_filter.append(self.genrate_condition(node))

		print(where_filter)
		where_state = self.str_jion(" ) and ( ", where_filter)
		
		res += "( " + where_state + " )"

		return res

	# 生成where条件
	def genrate_condition(self, midnode):
		res = ''

		if midnode.pos == "CN":
			res += self.deal_CN(midnode)

		if midnode.pos == "ON":
			res += self.deal_ON(midnode)

		if midnode.pos == "VN":
			res += self.deal_VN(midnode)

		return res

	# 处理连词
	def deal_CN(self, midnode):
		res = ''
		if midnode.val == 'not':
			if midnode.len_child() == 1:
				res += " not ( " + self.genrate_condition(midnode.child[0]) + " )" 

		if midnode.val == 'and':
			if midnode.len_child() == 2:
				res += "( " + self.genrate_condition(midnode.child[0]) + " ) and ( "+ self.genrate_condition(midnode.child[1]) + " )"

		if midnode.val == 'or':
			if midnode.len_child() == 2:
				res += "( " + self.genrate_condition(midnode.child[0]) + " ) or ( "+ self.genrate_condition(midnode.child[1]) + " )"

		return res

	# 处理运算词
	def deal_ON(self, midnode):
		res = ""
		# 这里的VN有多种可能，需要进一步处理,判断二者的类型是否一致，要不然就是一种随意的映射
		# 随意的映射中优先从存在的column中选，再从类型一致的column中选
		# 若是column中有日期，VN为数字也可以映射
		if midnode.len_child() == 1:
			if midnode.child[0].pos == "VN":
				res += self.NN.val + " " + midnode.val + " " + midnode.child[0].val

				if midnode.child[0].len_child() > 0:
					mid_list = []
					for node in midnode.child[0].child:
						mid_list.append(self.genrate_condition(node))
					if len(mid_list) != 0:
						res += " and " + self.str_jion(" and ", mid_list)


		# 这里也要进一步的处理
		if midnode.len_child() == 2:
			if midnode.child[0].pos == "NN" and midnode.child[1].pos == "VN":
				if midnode.child[0].len_child() == 0:
					res += midnode.child[0].val +" " +  midnode.VN  + " " + midnode.child[1].val
					if midnode.child[1].len_child() != 0:
						mid_list = []
						for node in midnode.child[1].child:
							mid_list.append(self.genrate_condition(node))
						if len(mid_list) != 0:
							res += " and " + self.str_join(" and ", mid_list)

			if midnode.child[1].pos == "NN" and midnode.child[0].pos == "VN":
				if midnode.child[1].len_child() == 0:
					res += midnode.child[1].val +" " +  midnode.VN  + " " + midnode.child[0].val

					if midnode.child[0].len_child() != 0:
						mid_list = []
						for node in midnode.child[0].child:
							mid_list.append(self.genrate_condition(node))
						if len(mid_list) != 0:
							res += " and " + self.str_join(" and ", midnode)

		return res



	# 处理数字或者内容词
	def deal_VN(self, midnode):
		res = ''
		if midnode.val in self.ON_VN_map:
			return res

		for lis in self.map_list:
			if lis[3] == midnode.val:
				if len(lis) == 6:
					res += lis[5] + " = " + lis[3]

		if midnode.len_child() > 0:
			mid_list = []
			for node in midnode.child:
				mid_list.append(self.genrate_condition(node))
			if len(mid_list) != 0:
				res += " and " + self.str_join(" and ",mid_list)

		return res


if __name__ == '__main__':

	map_list = [['show',1.0, 'root', 'show'],['100', 1.0, 'VN', '100'], ['1000', 1.0, 'VN', '1000'], ['not', 1.0, 'CN', 'not'], ['less', 1.0, 'ON', '<'], ['and', 1.0, 'CN', 'and'], ['elctconsumption', 1.0, 'NN', 'elctConsumption'], ['shanghai', 1.0, 'VN', 'Shanghai', 'cityName'], ['>', 1.0, 'ON', '>']]
	ON_VN_map = {'100': '>', '1000': '<'}

	mylis = ['show', 'elctConsumption', 'Shanghai',['and',  ['>', '100'],['not', ['<', '1000']]]]

	metree = Tree(mylis, map_list, ON_VN_map)
	metrans = translate(metree.tree, map_list, ON_VN_map)
	metree.print_tree(metree.tree)

	print(metrans.generate_sql(metree.tree))
	