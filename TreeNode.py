import nltk
import sys
import csv
import json
import copy
#from match import Data_preprocessing

class TreeNode(object):
	"""docstring for TreeNode"""
	def __init__(self, val, pos, position, temp_id, parent = None):
		super(TreeNode, self).__init__()
		self.val = val
		self.pos = pos
		self.parent = parent
		self.child = []
		self.id = temp_id
		self.vaild = True
		self.position = position

	def print_info(self):
		return "TreeNode(%s %d %s) " % (self.val, self.id, self.pos)

	def get_ON_VN_map(self, ON_VN_map):
		self.ON_VN_map = ON_VN_map

	def get_maplist(self, maplist):
		self.maplist = maplist

	def __contains__(self):
		return self.child

	def len_child(self):
		return len(self.child)

	@property
	def path(self):
		"""return path string (from root to current node)"""
		if self.parent:
			return '%s %s' % (self.parent.path.strip(), self.name)
		else:
			return self.name

	def get_child(self, temp_id):
		"""get a child node of current node"""
		for ch in self.child:
			if ch.id == temp_id:
				return ch
		return None

	# 建树的时候用
	def add_child(self, val, pos, position, temp_id, parent = None):
		obj = TreeNode(val, pos, position, temp_id, parent)

		obj.parent = self
		self.child.append(obj)
		return obj

	# 调节树的时候用
	def adjust_add_child(self, node):
		self.child.append(node)

	# 删除子节点
	def del_child(self, temp_id):
		"""remove a child node from current node"""
		for i in range(0, self.len_child()):
			if self.child[i].id == temp_id:
				return self.child.pop(i)
		return None


	def node_vaild_test(self):
		self.vaild = True

		if self.pos == 'root':
			if self.parent is not None:
				self.vaild = False
			have_NN = False
			for node in self.child:
				if node.pos == 'NN':
					have_NN = True
					break
			if have_NN == False:
				self.vaild = False
				for node in self.child:
					node.vaild = False

		if self.pos == 'NN':
			if self.parent.pos != 'root' and self.parent.pos != 'ON':
				self.vaild = False
			if self.len_child() != 0:
				self.vaild = False
				for node in self.child:
					node.vaild = False

		if self.pos == 'CN':
			if self.val == 'or' or self.val == 'and':
				if self.len_child() != 2:
					self.vaild = False
					# print("zhang")
					for node in self.child:
						if node.pos == 'root' or node.pos == 'NN':
							node.vaild = False
							# print("yong")
				else:
					for node in self.child:
						if node.pos == 'root' or node.pos == 'NN':
							self.vaild = False
							node.vaild = False
							# print("fu")
			if self.val == 'not':
				if self.len_child() != 1:
					self.vaild = False
					for node in self.child:
						if node.pos == 'root' or node.pos == 'NN':
							node.vaild = False
				else:
					if self.child[0].pos == 'root' or self.child[0].pos == 'NN':
							self.vaild = False
							self.child[0].vaild = False
							# print("xixixixi")

		# ON节点的判断，这个应该是主要的函数
		if self.pos == 'ON':
			if self.len_child() == 1:
				if self.child[0].pos != 'VN':
					self.vaild = False
					self.child[0].vaild = False
				else:
					#print("xixixixixixi")
					if self.child[0].val in self.ON_VN_map:
						# print("VVVVVVVVVVVVV")
						if self.ON_VN_map[self.child[0].val] != self.val:
							self.vaild = False
							self.child[0].vaild = False
					else:
						self.vaild = False
						self.child[0].vaild = False
			elif self.len_child() == 2:
				if self.child[0].pos == 'NN' and self.child[1].pos == 'VN':
					if self.child[1].val in self.ON_VN_map:
						if self.ON_VN_map[self.child[1].val] != self.val:
							self.vaild = False
							self.child[1].vaild = False
					else:
						self.vaild = False
						self.child[1].vaild = False
				elif self.child[1].pos == 'NN' and self.child[0].pos == 'VN':
					if self.child[0].val in self.ON_VN_map:
						if self.ON_VN_map[self.child[0].val] != self.val:
							self.vaild = False
							self.child[0].vaild = False
					else:
						self.vaild = False
						self.child[0].vaild = False
				else: 
					self.vaild = False
					if self.child[1].val in self.ON_VN_map:
						if self.ON_VN_map[self.child[1].val] != self.val:
							self.child[1].vaild = False
					else:
						self.child[1].vaild = False

					if self.child[0].val in self.ON_VN_map:
						if self.ON_VN_map[self.child[0].val] != self.val:
							self.child[0].vaild = False
					else:
						self.child[0].vaild = False
			else:
				self.vaild = False
				for node in self.child:
					if node.pos == 'ON' or node.pos == 'CN':
						node.vaild == False
					if node.pos == 'VN':
						if node.val not in self.ON_VN_map:
							self.vaild = False
							node.vaild = False
						else:
							if self.ON_VN_map[node.val] != self.val:
								self.vaild = False
								node.vaild = False

		# 这里的VN节点还需要判断否?
		if self.pos == 'VN':
			if self.parent.pos == 'ON':
				if self.val not in self.ON_VN_map:
					self.vaild = False
				else:
					if self.ON_VN_map[self.val] != self.parent.val:
						self.vaild = False
			for node in self.child:
				if node.pos == 'NN' or node.pos == 'root':
					self.vaild = False
					node.vaild = False

	# 测试树节点是否符合要求，这里更该valid属性，遇到不合适的节点返回其适合的父节点的词性
	def test_node_valid(self):
		if self.pos == 'root':
			if self.parent != None:
				self.vaild =  False
				return False, 'noneed'
			have_NN = False
			for node in self.child:
				if node.pos == 'NN':
					have_NN = True
					break
			if have_NN == True:
				return True, 'noneed'
			else:
				return False, 'needchild'
			return True, 'noneed'

		if self.pos == 'ON':
			if self.len_child() < 1:
				return False, 'needchild'
			elif self.len_child() == 2:
				if self.child[0].pos == 'NN' and self.child[1].pos == 'VN':
					return True, 'noneed'
				if self.child[1].pos == 'NN' and self.child[0].pos == 'VN':
					return True, 'noneed'
				return False, 'needmovechild'
			elif self.len_child() == 1:
				if self.child[0].pos == 'VN':
					return True, 'noneed'
				return False, 'needmovechild'
			else:
				return False, 'needmovechild'

		if self.pos == 'NN':
			if self.parent.pos == 'root':
				if self.len_child() == 0:
					return True, 'noneed'
				else:
					return False, 'needmovechild'
			if self.parent.pos == 'ON':
				if self.vaild == 0:
					return True, 'noneed'
				else:
					return False, 'needmovechild'
			return False, 'needmoveself'

		if self.pos == 'CN':
			if self.val == 'and':
				if self.len_child() == 2:
					return True, 'noneed'

				if self.len_child() < 2:
					return False, 'needchild'

				if self.len_child() > 2:
					return False, 'needmovechild'

			if self.val == 'or':
				if self.len_child() == 2:
					return True, 'noneed'
				if self.len_child() < 2:
					return False, 'needchild'
				if self.len_child() > 2:
					return False, 'needmovechild'
			if self.val == 'not':
				if self.len_child() == 1:
					return True, 'noneed'
				if self.len_child() < 1:
					return False, 'needchild'
				if self.len_child() > 1:
					return False, 'needmovechild'

		if self.pos == 'VN':
			if self.len_child() == 1:
				if self.child[0].pos == 'VN':
					return True, 'noneed'
				else:
					return False, 'needmovechild'
			elif self.len_child() > 1:
				return False, 'needmovechild'

			return True, 'noneed'

	

if __name__ == '__main__':

	print("hello world!")
