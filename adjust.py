import nltk
import sys
import csv
import json
import copy
from TreeNode import TreeNode
from map_node import map_node
from pre_deal import pre_deal
from tree import Tree
from translate import translate


class adjust(object):
	"""docstring for adjust"""
	def __init__(self, lis, maplist, ON_VN_map):
		super(adjust, self).__init__()
		self.tree = Tree(lis, maplist, ON_VN_map)
		self.result = []
		# self.hash_list = []
		self.maplist = maplist
		self.ON_VN_map = ON_VN_map
		self.have_tree = []

	# 取得合适的SQL语法树
	def get_result(self):
		init_invaild = self.tree.count_invaild_node(self.tree.tree)
		# self.tree.tree_draw(self.tree.tree)
		print(self.tree.print_invaild_node(self.tree.tree))

		print("___________________________ ", init_invaild)
		count = 0
		res_list = []
		for v_tree in self.result:
			#print(count, v_tree.edit)
			if v_tree.tree_evaliate(v_tree.tree) == v_tree.cal_factorial(v_tree.tree_size(v_tree.tree)):
				continue

			if init_invaild == v_tree.edit or v_tree.count_invaild_node(v_tree.tree) == 0:
				count += 1
				print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& ",count, v_tree.tree_evaliate(v_tree.tree))
				res_list.append(v_tree)
				'''
				print(v_tree.tree_evaliate(v_tree.tree))
				print(v_tree.correct_list(v_tree.parsetree_to_list(v_tree.tree)))
				v_tree.tree_draw(v_tree.tree)
				res_list.append(v_tree)
				'''

		res_list.sort(key = lambda a: a.tree_evaliate(a.tree))
		return res_list

	# 获取将合适的语法树转为SQL语句
	def tree_to_sql(self):
		sql_list = []
		res_list = self.get_result()

		for v_tree in res_list:
			# v_tree.tree_draw(v_tree.tree)
			tran = translate(v_tree.tree, self.maplist, self.ON_VN_map)
			sql_list.append(tran.generate_sql(v_tree.tree))

		return sql_list



	# 主要的调节函数
	def main_adjust(self):

		temp_list = [self.tree]
		self.tree.sort_tree(self.tree.tree)
		self.have_tree.append(self.tree.correct_list(self.tree.parsetree_to_list(self.tree.tree)))

		while len(temp_list) > 0:
			# print(len(temp_list))

			temptree = temp_list.pop(0)

			if temptree.count_invaild_node(temptree.tree) == 0:
				self.result.append(temptree)
				continue

			if temptree.edit == 5:
				self.result.append(temptree)
				continue

			newtree_list = temptree.adjust_tree(temptree.tree)

			for v_tree in newtree_list:
				# hash_val = temptree.hash_tree(v_tree)
				temptree.sort_tree(v_tree)
				templ = temptree.parsetree_to_list(v_tree)
				templ = temptree.correct_list(templ)
				if templ not in self.have_tree:
					# self.hash_list.append(hash_val)
					self.have_tree.append(templ)
					newtree = Tree(templ, self.maplist, self.ON_VN_map)
					newtree.edit = temptree.edit + 1
					temp_list.append(newtree)

		print("-------------------------------------------------------- ",len(self.result))


if __name__ == '__main__':

	print("hello world")
	# map_list = [['100', 1.0, 'VN', '100'],['show',1.0, 'root', 'show'], ['1000', 1.0, 'VN', '1000'], ['not', 1.0, 'CN', 'not'], ['less', 1.0, 'ON', '<'], ['and', 1.0, 'CN', 'and'], ['elctconsumption', 1.0, 'NN', 'elctConsumption'], ['shanghai', 1.0, 'VN', 'Shanghai', 'cityName'], ['>', 1.0, 'ON', '>']]
	map_list = [['show',1.0, 'root', 'show', 0],['less', 1.0, 'ON', '<', 7], ['elctconsumption', 1.0, 'NN', 'elctConsumption', 2], ['1000', 1.0, 'VN', '1000', 9], ['shanghai', 1.0, 'VN', 'Shanghai', 11, 'cityName'], ['100', 1.0, 'VN', '100', 4], ['not', 1.0, 'CN', 'not', 6], ['and', 1.0, 'CN', 'and', 5], ['>', 1.0, 'ON', '>', 3]]
	
	ON_VN_map = {'100': '>', '1000': '<'}
	inputText = "show me elctConsumption > 100 and not less than 1000 in shanghai over time".lower()
	mylist = ['show', ['elctConsumption', ['>', '100'], 'and', 'not', ['<', '1000', 'Shanghai']]]
	# mylist = ['show', 'elctConsumption', ['>', '100'], 'and', 'not', ['<', '1000', 'Shanghai']]

	ctree = Tree(mylist, map_list, ON_VN_map)
	lis = ctree.parsetree_to_list(ctree.tree)
	# print(lis)

	deal =  pre_deal(map_list,inputText)
	lis = deal.correct_list(lis)
	# print(lis)
	deal.listTotree(lis).draw()

	newtree = ctree.pre_adjust(ctree.tree)
	newtree.node_vaild_test()
	lis = ctree.parsetree_to_list(newtree)
	lis = ctree.correct_list(lis)
	print('++++++++++++++++++++++++++++++++++++++++++++')
	print(lis)
	ctree.tree_draw(newtree)
	adjustor = adjust(lis, map_list, ON_VN_map)
	print(adjustor.tree.count_invaild_node(adjustor.tree.tree))
	print(adjustor.tree.print_invaild_node(adjustor.tree.tree))
	print("xiaoxiao fu")
	adjustor.main_adjust()
	print("zhan")
	adjustor.get_result()
	print("hahahahhahahahhah")
	res = adjustor.tree_to_sql()
	for val in res:
		print(val)

