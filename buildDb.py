import sqlite3, csv, glob
from sqlite3.dbapi2 import Error
from dateObject import DateObject
from pathlib import Path
import sqlalchemy

today = DateObject()
paths = Path('C:/Users/Ward/Desktop/repcalRSS/csv').glob('**/*.csv')
db = 'calendar.db'

engine = sqlalchemy.create_engine('sqlite+pysqlite:///:memory:', echo=True, future=True)

with engine.connect() as conn:
  result = conn.execute((sqlalchemy.text("select 'hello world'")))

def dbConnection(database):
  connection = sqlite3.connect(database)
  return connection

def cursor():
  cursor = dbConnection(db).cursor()
  return cursor

def createTable(con,statement):
  try:
    cur = con.cursor()
    cur.execute(statement)
  except Error as e:
    print(e)

def populateTables():
  cur = cursor()

  for path in paths:
    pathInStr = str(path)
    with open(pathInStr, 'r') as fin:
      dr = csv.DictReader(fin)
      to_db = [(i['month_of'],i['day'],i['item'],i['item_url']) for i in dr]
    
    tableName = pathInStr.strip('.csv')
    cur.executemany("INSERT INTO {table} (month_of, day, item, item_url) VALUES (?, ?, ?, ?);".format(table = tableName), to_db)
  
  dbConnection(db).commit()

def createAllTables():

  vendemiare = "CREATE TABLE IF NOT EXISTS vendemiaire (month_of,day,item,item_url);"
  brumaire = "CREATE TABLE IF NOT EXISTS brumaire (month_of,day,item,item_url);"
  frimaire = "CREATE TABLE IF NOT EXISTS frimaire (month_of,day,item,item_url);"
  nivose = "CREATE TABLE IF NOT EXISTS nivose (month_of,day,item,item_url);"
  pluviose = "CREATE TABLE IF NOT EXISTS pluviose (month_of,day,item,item_url);"
  ventose = "CREATE TABLE IF NOT EXISTS ventose (month_of,day,item,item_url);"
  germinal = "CREATE TABLE IF NOT EXISTS germinal (month_of,day,item,item_url);"
  floreal =  "CREATE TABLE IF NOT EXISTS floreal (month_of,day,item,item_url);"
  prairial = "CREATE TABLE IF NOT EXISTS prairial (month_of,day,item,item_url);"
  messidor = "CREATE TABLE IF NOT EXISTS messidor (month_of,day,item,item_url);"
  thermidor = "CREATE TABLE IF NOT EXISTS thermidor (month_of,day,item,item_url);"
  fructidor = "CREATE TABLE IF NOT EXISTS fructidor (month_of,day,item,item_url);"
  sans = "CREATE TABLE IF NOT EXISTS sansculottides (month_of,day,item,item_url);"
  latestPost = "CREATE TABLE IF NOT EXISTS latestPost (latest);"

  list = [vendemiare,brumaire,frimaire,nivose,pluviose,ventose,germinal,floreal,prairial,messidor,thermidor,fructidor,sans, latestPost]

  for i in list:
    createTable(dbConnection(db),i)

  populateTables()

  dbConnection(db).close()

createAllTables()