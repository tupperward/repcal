import urllib.request, json, os, csv
from os.path import exists, dirname
from sqlalchemy.sql.expression import insert, update
from sqlalchemy.sql.functions import user
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy.sql.type_api import UserDefinedType

from sqlalchemy.engine.interfaces import CreateEnginePlugin
from sqlalchemy.sql.annotation import SupportsWrappingAnnotations
from sqlalchemy.sql.base import ColumnCollection
from sqlalchemy import text, create_engine, MetaData, Table, Column, Integer, String, insert, select, and_, update

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
Column('month', String),
Column('month_of', String),
Column('day',Integer),
Column('item',String),
Column('item_url',String)
)

# Makes a collection of days that we can build into entries for the feed.
top10 = Table(
"top10", meta,
Column('id', Integer,primary_key=True),
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

# Add today to the top10 table, which
def func():
  statement = insert(calendar).values(month=i['month'].strip("'").strip("',"), month_of=i['month_of'].strip("'").strip("',"), day=i['day'].strip("'").strip("',"), item=i['item'].strip("'").strip("',"), item_url=i['item_url'].strip("'").strip("',"))
    with engine.connect() as conn:
      result = conn.execute(statement)

# Seize the Day! Creates the today object from a combination of creating a DateObject and querying the sqlite3 database.
def carpeDiem():
  today = DateObject()
  userDomain = os.environ.get('DOMAIN_NAME')
  if userDomain == None:
    userDomain = 'localhost'
  statement = calendar.select().where(calendar.c.month.ilike(unidecode(today.month)), calendar.c.day == int(today.day))
  query = selectStatement(statement)
  print(query)
  today.id = query.id
  today.item = query.item
  today.item_url = query.item_url 
  today.image = 'http://{domain}/i/{item}.jpg'.format(domain = userDomain, item = today.item.lower())
  today.month_of = query.month_of
  return today

def addToTop10():
  today = carpeDiem()
  
  addItemStmnt = insert(top10).values(
    day = today.day,
    week = today.week,
    weekday = today.weekday,
    month = today.month,
    month_of = today.month_of,
    yearArabic = today.yearArabic,
    yearRoman = today.yearRoman,
    sansculottides = today.sansculottides,
    formatted = today.formatted, 
    item = today.item,
    item_url = today.item_url,
    image = today.image,
    )


#Creating the calendar DB if it hasn't already been created
if not exists ('./calendar.db'):
  touch('./calendar.db')
  engine = create_engine("sqlite+pysqlite:///calendar.db")

  meta.create_all(engine)

  with open('./static/full_calendar.csv','r') as file:
    data = csv.DictReader(file)
    for i in data:
      statement = insert(calendar).values(month=i['month'].strip("'").strip("',"), month_of=i['month_of'].strip("'").strip("',"), day=i['day'].strip("'").strip("',"), item=i['item'].strip("'").strip("',"), item_url=i['item_url'].strip("'").strip("',"))
      with engine.connect() as conn:
        result = conn.execute(statement)
else:
  engine = create_engine("sqlite+pysqlite:///calendar.db", echo=True)

