import nltk
import sys
import csv
import json
import copy
from TreeNode import TreeNode
from map_node import map_node
from tree import Tree
from translate import translate
from pre_deal import pre_deal
from adjust import adjust

class Main(object):
	"""docstring for Main"""
	def __init__(self, inputText, datapath):
		super(Main, self).__init__()
		self.inputText = inputText
		self.datapath = datapath

		self.sql = self.final_sql()

	def final_sql(self):
		final_res = []
		# 得到映射函数
		n_map = map_node(self.inputText, self.datapath)
		vis_map, fun_map = n_map.sub_map()
		hide_column = n_map.hide_column()
		maplist = n_map.main_map()
		print(maplist)

		# 可能有多种映射，对每一种映射进行处理
		for p_list in maplist:
			# 早期预处理，主要是介词上移和连词上移
			pre = pre_deal(p_list, self.inputText)
			tree_list = pre.treeTolist(pre.tree)
			tree_list = pre.remove_uselessword(tree_list)
			tree_list = pre.correct_list(tree_list)
			pre.init_ON_VN_map(tree_list)
			tree_list = pre.prep_up(tree_list)
			tree_list = pre.conj_up(tree_list)

			print(tree_list)
			print(pre.ON_VN_map)
			print(pre.map_list)
			# 中期预处理，主要是NN节点的处理
			ctree = Tree(tree_list, pre.map_list, pre.ON_VN_map)
			ctree.tree_draw(ctree.tree)
			newtree = ctree.pre_adjust(ctree.tree)
			print("-------------------------------")
			ctree.tree_draw(newtree)
			newtree.node_vaild_test()
			
			# 开始调节语法树
			adjustor = adjust(tree_list, pre.map_list, pre.ON_VN_map)
			adjustor.main_adjust()
			adjustor.get_result()
			print("hahahahhahahahhah")
			for v_tree in adjustor.get_result():
				print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ " ,v_tree.count_invaild_node(v_tree.tree), v_tree.tree_evaliate(v_tree.tree))
			res = adjustor.tree_to_sql()
			
			final_res += res

		return final_res


if __name__ == '__main__':
	print("hello world")

	inputText = "show me elctConsumption > 100 and not more than 1000 in shanghai over time".lower()
	datapath =  "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"
	ma = Main(inputText, datapath)

	for sql in ma.sql:
		print(sql)
		