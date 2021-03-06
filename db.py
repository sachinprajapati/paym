from settings import *

class DB():
	db_name = dir_path+'/demo.db'
	conn = None
	curr = None
	table = None
	schema = """CREATE TABLE Cards (
				id integer PRIMARY KEY AUTOINCREMENT,
			    card_num int NOT NULL UNIQUE,
			    date text NOT NULL,
				cvv int NOT NULL,
			    pin int NOT NULL
			);
			CREATE TABLE Transactions (
				id integer PRIMARY KEY AUTOINCREMENT,
				tid varchar(255) NOT NULL UNIQUE,
				amount int NOT NULL,
				status varchar(255) NOT NULL,
				message varchar(255) NOT NULL,
				card_id integer,
				dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (card_id) REFERENCES Cards (card_id)
			)"""

	def __init__(self, table):
		if not os.path.exists(self.db_name):
			self.conn = connect(self.db_name)
			self.curr = self.conn.cursor()
			self.curr.executescript(self.schema)
			self.conn.commit()
		else:
			self.conn = connect(self.db_name)
			self.curr = self.conn.cursor()
		self.table = table

	def InsertOne(self, myDict):
		placeholders = ', '.join(['?'] * len(myDict))
		columns = ', '.join(myDict.keys())
		sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(self.table, columns, placeholders)
		if myDict.get('date'):
			if isinstance(myDict['date'], datetime):
				myDict['date'] = myDict['date'].strftime("%Y-%m")
		try:
			print("sql is", sql, list(myDict.values()))
			self.curr.execute(sql, list(myDict.values()))
			self.conn.commit()
		except IntegrityError as e:
			print(e)

	def getDetail(self, **kwargs):
		sql = "select id from {0} where {1}".format(self.table, ' AND '.join('{} = {}'.format(key, value) for key, value in kwargs.items()))
		self.curr.execute(sql)
		return self.curr.fetchone()

	def DateFilter(self, date):
		print("date is", date.day, date.month, date.year)
		sql = """select card_num, cvv, date, pin, count(case message when 'SUCCESS' then 1 else null end) as 
		success FROM Transactions left join Cards on Cards.id=Transactions.card_id where dt BETWEEN 
		'{0}-{1:02d}-{2:02d}' AND '{0}-{1:02d}-{3:02d}' group by Cards.id order by success;""".format(date.year, date.month, date.day, date.day+1)
		print("sql is", sql)
		self.curr.execute(sql)
		return self.curr.fetchall()