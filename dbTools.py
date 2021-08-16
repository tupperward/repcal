from sqlalchemy.engine.interfaces import CreateEnginePlugin
from sqlalchemy.sql.annotation import SupportsWrappingAnnotations
from sqlalchemy.sql.base import ColumnCollection
from sqlalchemy import text, create_engine, MetaData, Table, Column, Integer, String, insert, select, and_, update
#from dateObject import generateThumbprint
engine = create_engine("sqlite+pysqlite:///calendar.db", echo=True)
meta = MetaData()

calendar = Table(
  "calendar", meta,
  Column('id', Integer, primary_key=True),
  Column('month', String),
  Column('month_of', String),
  Column('day',Integer),
  Column('item',String),
  Column('item_url',String)
)

lastPost = Table(
  'lastPost',meta,
  Column('id', Integer, primary_key=True),
  Column('lastPost', String)
)

def selectStatement(statement):
  connection = engine.connect()
  results = connection.execute(statement).fetchone()
  return results

def executeStatement(statement):
  connection = engine.connect()
  connection.execute(statement)

#test = selectStatement(statement)

#print (test.item)
#meta.create_all(engine)

#with open('C:/Users/Ward/Desktop/repcalRSS/TwitterFetch/csv/aaaaaaa.csv','r') as file:
#  data = csv.DictReader(file)
#  for i in data:
#    statement = insert(calendar).values(month=i['month'].strip("'").strip("',"), month_of=i['month_of'].strip("'").strip("',"), day=i['day'].strip("'").strip("',"), item=i['item'].strip("'").strip("',"), item_url=i['item_url'].strip("'").strip("',"))
#    with engine.connect() as conn:
#      result = conn.execute(statement)
#      #conn.commit()
