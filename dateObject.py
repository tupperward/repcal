import urllib.request, json, os, csv
from os.path import exists, dirname
from sqlalchemy.sql.expression import delete, insert, table, update
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.type_api import UserDefinedType

from sqlalchemy.engine.interfaces import CreateEnginePlugin
from sqlalchemy.sql.annotation import SupportsWrappingAnnotations
from sqlalchemy.sql.base import ColumnCollection
from sqlalchemy import text, create_engine, MetaData, Table, Column, Integer, String, insert, select, and_, update, delete

from unidecode import unidecode 

# # # # # Classes # # # # # 

meta = MetaData()

# This class creates a python object with attributes that match the values of today's 
class DateObject:

  # Some quick variables to clean up what each attribute will be calling
  repcalData = 'https://repcal.info/now.json'
  rd = 'republican_date'
  a = 'attributes'
  
  # Makes the HTTP request to pull raw json data
  def getJsonData(self,api):
    with urllib.request.urlopen(api) as url:
      data = json.loads(url.read())
      return data

  # When a new date object is created it will self-populate accurate information from the json
  def __init__(self):

    # THIS EXISTS SO WE ONLY MAKE THE REQUEST ONCE 
    # Do not just call getJsonData() a half dozen times because it will take forever
    jsonData = self.getJsonData(self.repcalData)

    self.index = None
    self.day = jsonData[self.rd][self.a]['day']
    self.week = jsonData[self.rd][self.a]['week']
    self.weekday = jsonData[self.rd][self.a]['weekday'].strip("('").strip("'),")
    self.month = jsonData[self.rd][self.a]['month'].strip("('").strip("'),")
    self.yearArabic = jsonData[self.rd][self.a]['year_arabic']
    self.yearRoman = jsonData[self.rd][self.a]['year_roman'].strip("('").strip("'),")
    self.sansculottides = jsonData[self.rd][self.a]['sansculottides']
    self.formatted = jsonData[self.rd]['formatted'].strip("('").strip("'),")

# Calendar Table for the sqlite3 db
calendar = Table(
"calendar", meta,
Column('id', Integer, primary_key=True),
Column('day',Integer),
Column('week', Integer),
Column('month', String),
Column('month_of', String),
Column('yearArabic', Integer),
Column('yearRoman', String),
Column('sansculottides', Boolean),
Column('formatted', String),
Column('item', String),
Column('item_url', String),
Column('image', String)
)

# Makes a collection of days that we can build into entries for the feed.
fullCalendar = Table(
"fullCalendar", meta,
Column('id', Integer),
Column('index', Integer),
Column('day', Integer),
Column('week', Integer),
Column('weekday', String),
Column('month', String),
Column('month_of', String),
Column('yearArabic', Integer),
Column('yearRoman', String),
Column('sansculottides', Boolean),
Column('formatted', String),
Column('item', String),
Column('item_url', String),
Column('image', String)
)

# Makes a collection of days that we can build into entries for the feed.
top10 = Table(
"top10", meta,
Column('id', Integer),
Column('index', Integer),
Column('day', Integer),
Column('week', Integer),
Column('weekday', String),
Column('month', String),
Column('month_of', String),
Column('yearArabic', Integer),
Column('yearRoman', String),
Column('sansculottides', Boolean),
Column('formatted', String),
Column('item', String),
Column('item_url', String),
Column('image', String)
)
# # # # # Functions # # # # # 

# Creating a blank file.
def touch(path):
  with open(path, 'a'):
    os.utime(path, None)

#  Select statement helper function for sqlite3 usage
def selectStatement(statement):
  connection = engine.connect()
  results = connection.execute(statement).fetchone()
  return results

# Execute statement helper function for sqlite3 usage
def executeStatement(statement):
  connection = engine.connect()
  connection.execute(statement)

# Retrieves date object from specified table.
def getDateFromTable(tableName, month, day):
  statement = tableName.select().where(tableName.c.month.ilike(unidecode(month)), tableName.c.day == int(day))
  return selectStatement(statement)

# Seize the Day! Creates the today object from a combination of creating a DateObject and querying the sqlite3 database.
def carpeDiem():
  today = DateObject()

  query = getDateFromTable(calendar, today.month, today.day)
  today.id = query.id
  today.item = query.item
  today.item_url = query.item_url 
  today.image = '/i/{}.jpg'.format(today.item.lower())  # I think this needs to be rethought at some point
  today.month_of = query.month_of

  return today

def addTodayToTable(tableName, day):
  
  if tableName == top10:
    day.index = 1

  statement = tableName.insert.values(
    id = day.id,
    index = day.index,
    day = day.day,
    week = day.week,
    weekday = day.weekday,
    month = day.month,
    month_of = day.month_of,
    yearArabic = day.yearArabic,
    yearRoman = day.yearRoman,
    sansculottides = day.sansculottides,
    formatted = day.formatted, 
    item = day.item,
    item_url = day.item_url,
    image = day.image,
    )
  
  executeStatement(statement)

def incrementAllPrimaryKeys(tableName):
  for i in range(0, 9):
      statement = tableName.update().where(tableName.c.index == i).values(id= i + 1)
      executeStatement(statement)

def removeTenthDay(tableName):
  statement = tableName.delete().where(tableName.c.id == 9)
  executeStatement(statement)


#Creating the calendar DB if it hasn't already been created
if not exists ('./calendar.db'):
  touch('./calendar.db')
  engine = create_engine("sqlite+pysqlite:///calendar.db", echo=True)

  meta.create_all(engine)

  with open('./static/full_calendar.csv','r') as file:
    data = csv.DictReader(file)
    for i in data:
      statement = insert(calendar).values(month=i['month'].strip("'").strip("',"), month_of=i['month_of'].strip("'").strip("',"), day=i['day'].strip("'").strip("',"), item=i['item'].strip("'").strip("',"), item_url=i['item_url'].strip("'").strip("',"))
      with engine.connect() as conn:
        result = conn.execute(statement)

else:
  engine = create_engine("sqlite+pysqlite:///calendar.db", echo=True)

