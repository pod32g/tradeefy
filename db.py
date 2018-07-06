import sqlite3

class Database():
	"""docstring for Database"""
	def __init__(self):
		self.db = sqlite3.connect(':memory:')

	def first_run(self):
		cursor = self.db.cursor()
		cursor.excecute('''
				CREATE TABLE companies (id INTEGER PRIMARY KEY AUTOINCREMENT, _date_ VARCHAR, open NUMBER, close NUMBER);
				CREATE TABLE cripto (id INTEGER PRIMARY KEY AUTOINCREMENT, _date_ VARCHAR, close NUMBER);
			''')
		self.db.commit()

	def company_to_database(self, data):
		cursor = self.db.cursor()
		for d in data: 
			cursor.excecute("INSERT INTO companies (_date_, open, close) VALUES ('{}', {}, {})".format(d[0], d[1], d[2]))
		self.db.commit()

	def cripto_to_database(self, data):
		cursor = self.db.cursor()
		for d in data: 
			cursor.excecute("INSERT INTO cripto (_date_, close) VALUES ('{}', {})".format(d[0], d[1]))


	def close(self):
		self.db.close()
