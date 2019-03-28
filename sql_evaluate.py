import nltk
import sys
import csv
import json
import copy
from TreeNode import TreeNode
from map_node import map_node
from tree import Tree
from translate import translate

class sql_evaluate(object):
	"""docstring for sql_evaluate"""
	def __init__(self, map_list, result):
		self.map_list = map_list
		self.result = self.result

	def sql_score(self, sql):
		lis = sql.split('')
		key_num = []
		for val in lis:
			for val_lis in self.map_list:
				if val_lis[3] == val and val_lis[2] != 'NN':
					key_num.append(val_lis[4])

		res = 0
		for i in range(1, len(key_num)):
			for j in range(0, i):
				if key_num[i] < key_num[j]:
					res += 1

		return res


	def sort_result():
		return 0

if __name__ == '__main__':
	print("hello world")
