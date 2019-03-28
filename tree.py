import nltk
import sys
import csv
import json
import copy
from TreeNode import TreeNode
from map_node import map_node
from pre_deal import pre_deal

class Tree(object):

	def __init__(self, lis, maplist, ON_VN_map):
		self.maplist = maplist
		#注意这里的treesize少了1，不过目前还没什么用
		self.tree, self.treesize = self._build_tree(lis)
		self.edit = 0
		self.ON_VN_map = ON_VN_map

	def get_pos(self, word):
		for val_lis in self.maplist:
			if word == val_lis[3]:
				return val_lis[2]

	def get_position(self, word):
		for val_lis in self.maplist:
			if word == val_lis[3]:
				return val_lis[4]

	def _build_tree(self, lis, temp_id = 1, parent = None):
		if len(lis) == 0:
			return None

		if len(lis) == 0:
			return None
		parentnode = parent
		if temp_id == 1 and parent == None:
			val = lis[0]
			parentnode = TreeNode(val, self.get_pos(val), self.get_position(val), temp_id, parent)
			temp_id += 1

		for i in range(1, len(lis)):
			if type(lis[i]) == str:
				parentnode.add_child(lis[i],self.get_pos(lis[i]), self.get_position(lis[i]), temp_id, parentnode)
				temp_id += 1
			else:
				subtreenode = parentnode.add_child(lis[i][0], self.get_pos(lis[i][0]), self.get_position(lis[i][0]), temp_id, parentnode)
				temp_id += 1
				useless, temp_id = self._build_tree(lis[i], temp_id, subtreenode)

		return parentnode, temp_id

	# 定位节点
	def find_node(self, node, temp_id):
		if node.id == temp_id:
			return node
		else:
			for i in range(0, node.len_child()):
				res = self.find_node(node.child[i], temp_id)
				if  res is not None:
					return res
				else:
					continue

		return None

	def tree_draw(self, rootnode):
		if rootnode is None:
			return

		lis = self.parsetree_to_list(rootnode)

		deal = pre_deal(self.maplist, "zhangyongfu")

		lis = deal.correct_list(lis)

		t = deal.listTotree(lis)
		t.draw()
		return



	# 校正输出列表，便于将树转化为图形输出
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

	# 拷贝树
	def copy_tree(self, treenode, par_node = None):
		if treenode is None:
			return None

		newtree = TreeNode(treenode.val, treenode.pos, treenode.position, treenode.id, par_node)
		for val_node in treenode.child:
			newtree.adjust_add_child(self.copy_tree(val_node, newtree))

		return newtree

	'''
	def copy_tree(self, treenode):
		lis = self.parsetree_to_list(treenode)
		lis = self.correct_list(lis)

		newtree, size = self._build_tree(lis)

		return newtree

'''

	# 这里调整树的结构，避免相同的树不同的结构
	def sort_tree(self, rootnode):

		pos_dic = {'root':0, 'NN': 1, 'CN':2, 'ON': 3, 'VN':4}
		if rootnode == None:
			return

		if rootnode.len_child() == 0:
			return

		rootnode.child.sort(key = lambda a: a.position)

		for node in rootnode.child:
			self.sort_tree(node)

		return


	# hash值保证不把重复的树放入结果中
	def hash_tree(self, treenode):
		map_val = {'root':2, 'ON' :7, 'NN':71, 'VN':773, 'CN':7793}

		if treenode is None:
			return 0
		res_val = 0
		temp_val = 1
		for node in treenode.child:
			temp_val += node.id * map_val[node.pos]
		if treenode.parent is not None:
			res_val += temp_val * treenode.len_child() + map_val[treenode.pos] * treenode.id + map_val[treenode.parent.pos]* treenode.parent.id

		for node in treenode.child:
			res_val += self.hash_tree(node)

		return res_val

	def is_subtree(self, par_node, child_node):

		# print("************")
		# print(child_node.val)

		if child_node.parent is None:
			return False
		if child_node.parent.id == par_node.id:
			return True
		else:
			return self.is_subtree(par_node, child_node.parent)


	# 移动子树
	def move_subtree(self, treenode, parent_id, child_id):

		par_node = self.find_node(treenode, parent_id)
		child_node = self.find_node(treenode, child_id)

		print(parent_id, child_id)
		if par_node is None or child_node is None:
			return False

		print("findpar_node ", par_node.val)
		print("findchild_node ", child_node.val)

		if child_node.parent == par_node:
			return False
		if child_node == par_node:
			return False
		if par_node == None or child_node == None:
			return False

		# print("zhang4")
		# 这里要注意，如果要移动的父节点的位置是子节点的子节点，是不能移动的
		if self.is_subtree(child_node, par_node) == True:
			return False
		# print("zhang5")

		child_node.parent.del_child(child_id)
		child_node.parent = par_node
		child_node.parent.adjust_add_child(child_node)

		# print(" move tree succeed")
		return True


	def find_posnode(self, rootnode, pos, res):
		if rootnode is None:
			return 
		# print(pos)
		# print("xiaoxiaofu ", rootnode.val, rootnode.pos)
		if rootnode.pos == pos:
			# print("JJJJ")
			res.append(rootnode)

		for node in rootnode.child:
			self.find_posnode(node, pos, res)

	def count_invaild_node(self, rootnode):
		# print("zhang", rootnode.val)
		# print("yong", rootnode)
		res = 0
		rootnode.get_maplist(self.maplist)
		rootnode.get_ON_VN_map(self.ON_VN_map)
		rootnode.node_vaild_test()

		if rootnode is None:
			return res

		if rootnode.vaild == False:
			# print("IIIIIIIII", rootnode.val)
			res += 1

		for node in rootnode.child:
			# print(node)
			#print(node.val, node.id)
			res += self.count_invaild_node(node)

		return res

	def print_invaild_node(self, rootnode):
		res = []
		rootnode.get_maplist(self.maplist)
		rootnode.get_ON_VN_map(self.ON_VN_map)
		rootnode.node_vaild_test()

		if rootnode is None:
			return res

		if rootnode.vaild == False:
			# print("IIIIIIIII", rootnode.val)
			res.append(rootnode.val)

		for node in rootnode.child:
			res.append(self.print_invaild_node(node))

		return res

	def pre_adjust(self, rootnode):
		# 调节NN节点，
		# print(rootnode, "zhangxiao")
		self.print_tree(rootnode)
		init_invaild = self.count_invaild_node(rootnode)
		# print("zzzzzzzzzz")
		NNlist = []
		self.find_posnode(rootnode, 'NN', NNlist)

		if len(NNlist) == 0:
			return None

		if len(NNlist) == 1:
			newtree = self.copy_tree(rootnode)
			# self.print_tree(newtree)
			newNN = self.find_node(newtree, NNlist[0].id)

			print( newNN.val, newNN.parent.val)
			if newNN.parent.pos == 'root':
				while(newNN.len_child() != 0):
					node = newNN.child.pop(0)
					node.parent = newNN.parent
					newNN.parent.adjust_add_child(node)

			else:
				# print("Hello world")
				while(newNN.len_child() != 0):
					node = newNN.child.pop(0)
					node.parent = newNN.parent
					newNN.parent.adjust_add_child(node)

				newNN.parent.del_child(newNN.id)
				newNN.parent = newtree
				newtree.adjust_add_child(newNN)
			return newtree
		else:
			newtree = self.copy_tree(rootnode)
			newNN = self.find_node(newtree, NNlist[0].id)
			if newNN.parent.pos == 'root':
				while(newNN.len_child() != 0):
					node = newNN.child.pop(0)
					node.parent = newNN.parent
					newNN.parent.adjust_add_child(node)
			else:
				while(newNN.len_child() != 0):
					node = newNN.child.pop(0)
					node.parent = newNN.parent
					newNN.parent.adjust_add_child(node)

				newNN.parent.del_child(newNN.id)
				newNN.parent = newtree
				newtree.adjust_add_child(newNN)

			for i in range(1, len(NNlist)):
				extra_NN = self.find_node(newtree, NNlist[i].id)
				if extra_NN.len_child() > 0:
					while(extra_NN.len_child() != 0):
						node = extra_NN.child.pop(0)
						node.parent = extra_NN.parent
						extra_NN.parent.adjust_add_child(node)

			# print("zhangyongfu")
			return newtree

	## CN, ON, VN
	# CN 移动到 root, CN
	# ON 移动到 root, CN, VN
	# VN 移动到 root, CN, VN, 这里的VN是没有ON关联的VN
	# 主要的调节函数，调节树直到生成合适的树，这里设一个阈值为5
	def adjust_tree(self, rootnode):
		init_invaild = self.count_invaild_node(rootnode)
		# print(init_invaild)

		res_list = []

		CNlist = []
		self.find_posnode(rootnode, 'CN', CNlist)
		VNlist = []
		self.find_posnode(rootnode, 'VN', VNlist)
		ONlist = []
		self.find_posnode(rootnode, 'ON', ONlist)
		'''
		print("################################################")
		for node in CNlist:
			print("CN   ", node.val)
		for node in ONlist:
			print("ON   ", node.val)
		for node in VNlist:
			print("VN   ", node.val)
		print(self.ON_VN_map)
		'''
		count = 0

		if len(CNlist) > 0:
			# 连词移动到root下
			for i in range(0,len(CNlist)):
				if self.find_node(rootnode, CNlist[i].id).parent is not rootnode:
					newtree = self.copy_tree(rootnode)
					if self.move_subtree(newtree, 1 , self.find_node(newtree, CNlist[i].id).id):
						if self.count_invaild_node(newtree) <= init_invaild:
							print(self.count_invaild_node(newtree))
							print(self.print_invaild_node(newtree))
							res_list.append(newtree)
							
			# 连词移动到连词下
			if len(CNlist) > 1:
				for i in range(0, len(CNlist)):
					for j in range(i + 1, len(CNlist)):
						print(CNlist[i].id, CNlist[i].val, CNlist[j].id, CNlist[j].val)
						if self.find_node(rootnode, CNlist[i].id).parent is not self.find_node(rootnode, CNlist[j].id):
							# print("zhang")
							newtree = self.copy_tree(rootnode)
							# self.tree_draw(newtree)
							# print(self.move_subtree(newtree, self.find_node(newtree, CNlist[j].id).id, self.find_node(newtree, CNlist[i].id).id))
							if self.move_subtree(newtree, self.find_node(newtree, CNlist[j].id).id, self.find_node(newtree, CNlist[i].id).id):
								# print("yong", self.count_invaild_node(newtree))
								if self.count_invaild_node(newtree) <= init_invaild:
									# print("fu")
									print(self.count_invaild_node(newtree))
									print(self.print_invaild_node(newtree))
									res_list.append(newtree)
									

						if self.find_node(rootnode, CNlist[j].id).parent is not self.find_node(rootnode, CNlist[i].id):
							newtree = self.copy_tree(rootnode)
							if self.move_subtree(newtree, self.find_node(newtree, CNlist[i].id).id, self.find_node(newtree, CNlist[j].id).id):
								print(self.count_invaild_node(newtree))
								if self.count_invaild_node(newtree) <= init_invaild:
									print(self.count_invaild_node(newtree))
									print(self.print_invaild_node(newtree))
									res_list.append(newtree)
									

		if len(ONlist) > 0:
			# 移动到root下
			for i in range(0, len(ONlist)):
				if self.find_node(rootnode, ONlist[i].id).parent is not rootnode:
					newtree = self.copy_tree(rootnode)
					if self.move_subtree(newtree, 1, self.find_node(newtree, ONlist[i].id).id):
						if self.count_invaild_node(newtree) <= init_invaild:
							print(self.count_invaild_node(newtree))
							print(self.print_invaild_node(newtree))
							res_list.append(newtree)
							
			# 移动到CN下：
			if len(CNlist) > 0:
				for i in range(0, len(ONlist)):
					for j in range(0, len(CNlist)):
						if self.find_node(rootnode, ONlist[i].id).parent is not self.find_node(rootnode, CNlist[j].id):
							newtree = self.copy_tree(rootnode)
							if self.move_subtree(newtree, self.find_node(newtree, CNlist[j].id).id, self.find_node(newtree, ONlist[i].id).id):
								if self.count_invaild_node(newtree) <= init_invaild:
									print(self.count_invaild_node(newtree))
									print(self.print_invaild_node(newtree))
									res_list.append(newtree)
									
			# 移动到VN下：
			if len(VNlist) > 0:
				for i in range(0, len(ONlist)):
					for j in range(0, len(VNlist)):
						if self.find_node(rootnode, ONlist[i].id).parent is not self.find_node(rootnode, VNlist[j].id):
							newtree = self.copy_tree(rootnode)
							if self.move_subtree(newtree, self.find_node(newtree, VNlist[j].id).id, self.find_node(newtree, ONlist[i].id).id):
								if self.count_invaild_node(newtree) <= init_invaild:
									print(self.count_invaild_node(newtree))
									print(self.print_invaild_node(newtree))
									res_list.append(newtree)
									

		# 处理VN
		if len(VNlist) > 0:
			for i in range(0, len(VNlist)):
				if VNlist[i].val not in self.ON_VN_map:
					if self.find_node(rootnode, VNlist[i].id).parent is not rootnode:
						newtree = self.copy_tree(rootnode)
						if self.move_subtree(newtree, 1, self.find_node(newtree, VNlist[i].id).id):
							
							if self.count_invaild_node(newtree) <= init_invaild:
								print(self.count_invaild_node(newtree))
								print(self.print_invaild_node(newtree))
								res_list.append(newtree)
								

					if len(CNlist) > 0:
						for j in range(0, len(CNlist)):
							if self.find_node(rootnode, VNlist[i].id).parent is not self.find_node(rootnode, CNlist[j].id):
								newtree = self.copy_tree(rootnode)
								if self.move_subtree(newtree, self.find_node(newtree, CNlist[j].id).id, self.find_node(newtree, VNlist[i].id).id):
									if self.count_invaild_node(newtree) <= init_invaild:
										print(self.count_invaild_node(newtree))
										print(self.print_invaild_node(newtree))
										res_list.append(newtree)
										

					if len(VNlist) > 1:
						for j in range(0, len(VNlist)):
							if i != j:
								if self.find_node(rootnode, VNlist[i].id).parent is not self.find_node(rootnode, VNlist[j].id):
									newtree = self.copy_tree(rootnode)
									if self.move_subtree(newtree, self.find_node(newtree, VNlist[j].id).id, self.find_node(newtree, VNlist[i].id).id):
										if self.count_invaild_node(newtree) <= init_invaild:
											print(self.count_invaild_node(newtree))
											print(self.print_invaild_node(newtree))
											res_list.append(newtree)
											
								'''
								if self.find_node(rootnode, VNlist[j].id).parent is not self.find_node(rootnode, VNlist[i].id):
									newtree = self.copy_tree(rootnode)
									if self.move_subtree(newtree, self.find_node(newtree, VNlist[i].id).id, self.find_node(newtree, VNlist[j].id).id):
										if self.count_invaild_node(newtree) <= init_invaild:
											print("zhang yong fu")
											res_list.append(newtree)
											count += 1
											print(count)'''
				else:
					continue



		print(len(res_list))
		return res_list
		

	def find_movenode(self, rootnode, needchild, needmovechild, moveself):
		judge, is_move = rootnode.test_node_vaild()
		if is_move == 'needchild':
			needchild.append(rootnode)
		if is_move == 'needmovechild':
			needmovechild.append(rootnode)
		if is_move == 'needmoveself':
			moveself.append(rootnode)
		for node in rootnode.child:
			self.find_movenode(node, needchild, needmovechild, moveself)

	def return_movenode(self, treenode):
		needchild = []
		needmovechild = []
		moveself = []

		self.find_movenode(treenode, needchild, needmovechild, moveself)

		invaild = len(needchild) + len(needmovechild) + len(moveself)

		return needchild,needmovechild,moveself,invaild


	def print_tree(self, treenode):

		if treenode.parent == None:
			print('None')
		else:
			print(treenode.parent.val)

		print(treenode.val, treenode.id, treenode.pos)
		print('*******************')

		for node in treenode.child:
			self.print_tree(node)

		'''
		for i in range(0,treenode.len_child()):
			self.print_tree(treenode.child[i])
			'''

	# 将树转为列表，便于操作，能否和pre_deal的同样函数合并
	def parsetree_to_list(self, rootnode):
		res = []
		s = rootnode.val
		# print(s, rootnode.len_child())
		res.append(s)
		if rootnode.len_child() == 0:
			return res
		else:
			for node in rootnode.child:
				res.append(self.parsetree_to_list(node))
		return res

	# 输出翻译后的句子，这里的树都是已经按照position排序好的（参见上面的sort_tree()函数）
	def tree_to_sentence(self, rootnode):

		res = ''
		if rootnode is None:
			return res
		if rootnode.pos == 'root':
			res += 'show '
			for node in rootnode.child:
				res += self.tree_to_sentence(node)

		if rootnode.pos == 'CN':
			if rootnode.val == 'and' or rootnode.val == 'or':
				if rootnode.len_child() == 2:
					res += self.tree_to_sentence(rootnode.child[0])
					res += ' ' + rootnode.val + ' '
					res += self.tree_to_sentence(rootnode.child[1])
					res += ' '

			if rootnode.val == 'not':
				if rootnode.len_child() == 1:
					res += rootnode.val + ' '
					for node in rootnode.child:
						res += self.tree_to_sentence(node)


		if rootnode.pos == 'NN':
			res += rootnode.val + " "
			'''
			# 这里调试用的，以后去掉
			if rootnode.len_child() > 0:
				for node in rootnode.child:
					res += self.tree_to_sentence(node)
			'''

		if rootnode.pos == 'ON':
			if rootnode.len_child() == 1:
				res += rootnode.val + " " + rootnode.child[0].val + " "
				for node in rootnode.child[0].child:
					res += self.tree_to_sentence(node)

			if rootnode.len_child() == 2:
				if rootnode.child[0].pos == 'NN' and rootnode.child[1].pos == 'VN':
					res += rootnode.child[0].val + " "
					if rootnode.child[0].len_child() > 0:
						for node in rootnode.child[0].child:
							res += self.tree_to_sentence(node)

					res += rootnode.val + " " + rootnode.child[1].val

					if rootnode.child[1].len_child() > 0:
						for node in rootnode.child[1].child:
							res += self.tree_to_sentence(node)

		if rootnode.pos == 'VN':
			res += rootnode.val + " "
			if rootnode.len_child() > 0:
				for node in rootnode.child[0].child:
					res += self.tree_to_sentence(node) + " "

		return res

	# 返回树的规模，去掉NN节点
	def tree_size(self, rootnode):
		res = 0

		# print("mememem")
		if rootnode is None:
			return res

		if rootnode.pos != 'NN':
			res += 1

		for node in rootnode.child:
			res += self.tree_size(node)
		# print("res ", res)
		return res

	# 计算阶乘，用于计算最大的逆序对
	def cal_factorial(self, num):
		res = 1
		for i in range(1, num + 1):
			res *= i

		return res

	# 怎么判断好坏呢？查看有多少个逆序对（这里要不要去除掉包含NN的逆序对???）
	# 同时句子的长度要够（因为tree_to_sentence会把不合规矩的节点忽略）
	def tree_evaliate(self, rootnode):
		max_reverse = self.cal_factorial(self.tree_size(rootnode))
		trans_sen = self.tree_to_sentence(rootnode)
		print(trans_sen)

		trans_l = trans_sen.split(' ')
		print(trans_l)
		for i in range(len(trans_l) - 1, -1, -1):
			if self.get_pos(trans_l[i]) == 'NN' or trans_l[i] == '':
				trans_l.pop(i)

		print(trans_l)
		print(len(trans_l), self.tree_size(rootnode))
		if abs(len(trans_l) - self.tree_size(rootnode)) > 0.1 * self.tree_size(rootnode):
			print("hello world")
			return max_reverse

		res = 0
		for i in range(1, len(trans_l)):
			for j in range(0, i):
				if self.get_position(trans_l[i]) < self.get_position(trans_l[j]):
					res += 1

		return res


if __name__ == '__main__':

	map_list = [['show',1.0, 'root', 'show', 0],['less', 1.0, 'ON', '<', 7], ['elctconsumption', 1.0, 'NN', 'elctConsumption', 2], ['1000', 1.0, 'VN', '1000', 9], ['shanghai', 1.0, 'VN', 'Shanghai', 11, 'cityName'], ['100', 1.0, 'VN', '100', 4], ['not', 1.0, 'CN', 'not', 6], ['and', 1.0, 'CN', 'and', 5], ['>', 1.0, 'ON', '>', 3]]
	ON_VN_map = {'100': '>', '1000': '<'}
	inputText = "show me elctConsumption > 100 and not less than 1000 in shanghai over time".lower()
	mylist = ['show', ['elctConsumption', ['>', '100'], 'and', 'not', ['<', '1000', 'Shanghai']]]
	# mylist = ['show', 'elctConsumption', ['and', ['>', '100'], ['not', ['<', '1000']]], 'Shanghai']
	# mylist = ['show', 'elctConsumption', ['not', ['and', ['<', '1000'], 'Shanghai']], ['>', '100']]
	ctree = Tree(mylist, map_list, ON_VN_map)

	# print(ctree.count_invaild_node(ctree.tree))
	# print(ctree.print_invaild_node(ctree.tree))
	
	lis = ctree.parsetree_to_list(ctree.tree)
	# print(lis)

	deal =  pre_deal(map_list,inputText)
	lis = deal.correct_list(lis)
	# print(lis)
	deal.listTotree(lis).draw()
	print(ctree.count_invaild_node(ctree.tree))
	print(ctree.tree_size(ctree.tree))
	print(ctree.tree_evaliate(ctree.tree))


	newtree = ctree.pre_adjust(ctree.tree)
	newtree.node_vaild_test()
	# ctree.print_tree(ctree.tree)
	print("(((((((((((((((((((((((((((((((((((((((((9")
	# ctree.print_tree(newtree)
	lis = ctree.parsetree_to_list(newtree)
	print(ctree.count_invaild_node(newtree))
	print(ctree.print_invaild_node(newtree))
	ctree.sort_tree(newtree)
	print(ctree.tree_size(newtree))
	print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
	print(ctree.tree_evaliate(newtree))
	print(")))))))))))))))))))))))))))")
	ctree.print_tree(newtree)
	# print(lis)

	deal =  pre_deal(map_list,inputText)
	lis = deal.correct_list(lis)
	print(lis)
	deal.listTotree(lis).draw()


	print("------------------------------------")
	list_res = ctree.adjust_tree(newtree)
	i = 0
	for t in list_res:
		print(i)
		i+=1
		print(ctree.tree_evaliate(t))
		# print(ctree.count_invaild_node(t))
		# ctree.print_tree(t)
		lis1 = ctree.parsetree_to_list(t)
		deal1 =  pre_deal(map_list,inputText)
		lis1 = deal1.correct_list(lis1)
		# print(lis1)
		deal.listTotree(lis1).draw()
		print("------------------------------------")


'''
	ctree.print_tree(ctree.tree)

	print("((((((((((((((((((((((((")
	newtree = ctree.copy_tree(ctree.tree)
	ctree.print_tree(newtree)

	print("????????????????????")

	if ctree.move_subtree(ctree.tree, 2 , 4):
		print("XIXI")
		ctree.print_tree(ctree.tree)

	ctree.print_tree(newtree)



	print(ctree.hash_tree(newtree))
	print(ctree.hash_tree(ctree.tree))

	print("PPPPPPPPPPPPPPPPPPPPPP")
	print(ctree.count_invaild_node(newtree))

	res = []
	ctree.find_posnode(newtree,'VN', res)
	print([r.val for r in res])
	'''
