import pymysql
import csv

class database(object):
	"""docstring for database"""
	def __init__(self, host, port, user, password, db):
		self.host = host
		self.port = port
		self.user = user
		self.password = password
		self.db = db

	# 这个验证SQL语句能否执行
	def sql_vaild(self, sql):
		conn = pymysql.connect(host = self.host, port = self.port, user = self.user, passwd = self.password, db = self.db, charset='utf8')
		cursor = conn.cursor()
		try:
			cursor.execute(sql)
			cursor.close()
			conn.close()
		except Exception as e:
			return False

		return True

	def exist_table(self, tb):
		conn = pymysql.connect(host = self.host, port = self.port, user = self.user, passwd = self.password, db = self.db, charset='utf8')
		cursor = conn.cursor()

		sql = "show tables;"
		cursor.execute(sql)
		tables = cursor.fetchall()
		tb_list = []
		for val in tables:
			tb_list.append(val[0])

		print(tb_list)
		cursor.close()
		conn.close()

		if tb.lower() in tb_list:
			return True
		else:
			return False


	#将excel中的数据转入数据库中,若已有数据表，覆盖数据表，若是没有数据表，新建数据表
	def excel_to_db(self, path):
		
		conn = pymysql.connect(host = self.host, port = self.port, user = self.user, passwd = self.password, db = self.db, charset='utf8')
		cursor = conn.cursor()

		name = path.split('/')[-1]
		name = name.split('.')[0]

		print(name)
		if self.exist_table(name):
			print(self.exist_table(name))
			sql = 'drop table ' + name
			cursor.execute(sql)

		print("-------------------------")
		with open(path) as f:
			reader = list(csv.reader(f))
			schema = reader[0]
			create_sql = 'create table ' + name + '( '
			for i in range(0, len(schema) - 1):
				create_sql += str(schema[i]) + ' varchar(100) not null, '
			create_sql += schema[len(schema) - 1] + '  varchar(100) not null);'
			print(create_sql)
			cursor.execute(create_sql)

			schema_type = reader[1]
			type_instead = []
			for val in schema_type:
				s = ''
				for c in val:
					s += chr(ord(c) + 1)
				type_instead.append(s)
			print(schema_type)
			print(type_instead)

			insert_sql = 'insert into ' + name + ' values ( '
			for i in range(0, len(type_instead) - 1):
				insert_sql += '\''+str(type_instead[i]) + '\', '
			insert_sql += '\'' + str(type_instead[len(type_instead)-1]) + '\');'
			print(insert_sql)
			cursor.execute(insert_sql)

			for i in range(2, len(reader)):
				content = reader[i]
				insert_sql = 'insert into ' + name + ' values ( '
				for i in range(0, len(content) - 1):
					insert_sql += '\''+ str(content[i]) + '\', '
				insert_sql += '\''+ str(content[len(content) - 1]) + '\' );'
				print(insert_sql)
				cursor.execute(insert_sql)
			conn.commit()

		cursor.close()
		conn.close()

	# 取得指定数据表的数据
	def get_data(self, tb):
		conn = pymysql.connect(host = self.host, port = self.port, user = self.user, passwd = self.password, db = self.db, charset='utf8')
		cursor = conn.cursor()
		schema = []
		schema_type = []
		dataset = {}

		if self.exist_table(tb):
			field_sql = "show full fields from " + tb + ";"
			cursor.execute(field_sql)
			fields = cursor.fetchall()
			for val in fields:
				schema.append(val[0])
			content_sql = "select * from " + tb + ";"
			cursor.execute(content_sql)
			content = cursor.fetchall()
			#print(content)
			for t in content[0]:
				s = ''
				for c in t:
					s += chr(ord(c) - 1)
				schema_type.append(s)

			for i in range(0, len(schema)):
				lis = []
				for j in range(1, len(content)):
					lis.append(content[j][i])
				dataset[schema[i]] = lis

		cursor.close()
		conn.close()
		return schema, schema_type, dataset


if __name__ == '__main__':
	print("hello database")
	my_db = database(host = 'localhost', port = 3306, user = 'root', password = '903101', db = 'testdb')
	path = "D:/Study/dataset4vis/electricityConsumptionOfEasternChina.csv"
	#my_db.excel_to_db(path)
	print(my_db.sql_vaild("show tables;"))

'''
	schema,schema_type,dataset = my_db.get_data('electricityconsumptionofeasternchina')
	print(schema)
	print(schema_type)
	print(dataset)
	'''
