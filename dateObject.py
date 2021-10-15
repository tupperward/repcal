import urllib.request, json, os, csv
from os.path import exists, dirname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from unidecode import unidecode 

# Creating a blank file.
def touch(path):
  with open(path, 'a'):
    os.utime(path, None)

### Initialize Flask ###

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite+pysqlite:///calendar.db"
db = SQLAlchemy(app)

# # # # # Classes # # # # # 
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
class Calendar(db.Model):
  id = db.Column(db.Integer, primary_key=True),
  day = db.Column(db.Integer),
  week = db.Column(db.Integer),
  month = db.Column( db.String),
  month_of = db.Column( db.String),
  yearArabic = db.Column( db.Integer),
  yearRoman = db.Column(db.String),
  sansculottides = db.Column(db.Boolean),
  formatted = db.Column( db.String),
  item = db.Column( db.String),
  item_url = db.Column( db.String),
  image = db.Column( db.String)

  def __init__(self, month, month_of, day, item, item_url):
    self.month = month
    self.month_of = month_of
    self.day = day
    self.item = item
    self.item_url = item_url


# Makes a collection of days that we can build into entries for the feed.
class FullCalendar(db.Model):
  id = db.Column(db.Integer, primary_key=True),
  index = db.Colunm(db.Integer)
  day = db.Column(db.Integer),
  week = db.Column(db.Integer),
  month = db.Column( db.String),
  month_of = db.Column( db.String),
  yearArabic = db.Column( db.Integer),
  yearRoman = db.Column(db.String),
  sansculottides = db.Column(db.Boolean),
  formatted = db.Column( db.String),
  item = db.Column( db.String),
  item_url = db.Column( db.String),
  image = db.Column( db.String)

  def __init__(self, id, index, day, week, month, month_of, yearArabic, yearRoman, sansculottides, formatted, item, item_url, image):
    self. id = id
    self.index = index
    self.day = day
    self.week = week
    self.month = month
    self.month_of = month_of
    self.yearArabic = yearArabic
    self.yearRoman = yearRoman
    self.sansculottides = sansculottides
    self.formatted = formatted
    self.item = item
    self.item_url = item_url
    self.image = image


# Makes a collection of days that we can build into entries for the feed.
class  Top10(db.Model):
  id = db.Column(db.Integer, primary_key=True),
  index = db.Colunm(db.Integer)
  day = db.Column(db.Integer),
  week = db.Column(db.Integer),
  month = db.Column( db.String),
  month_of = db.Column( db.String),
  yearArabic = db.Column( db.Integer),
  yearRoman = db.Column(db.String),
  sansculottides = db.Column(db.Boolean),
  formatted = db.Column( db.String),
  item = db.Column( db.String),
  item_url = db.Column( db.String),
  image = db.Column( db.String)

  def __init__(self, id, index, day, week, month, month_of, yearArabic, yearRoman, sansculottides, formatted, item, item_url, image):
    self. id = id
    self.index = index
    self.day = day
    self.week = week
    self.month = month
    self.month_of = month_of
    self.yearArabic = yearArabic
    self.yearRoman = yearRoman
    self.sansculottides = sansculottides
    self.formatted = formatted
    self.item = item
    self.item_url = item_url
    self.image = image
# # # # # Functions # # # # # 



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

  with open('./static/full_calendar.csv','r') as file:
    data = csv.DictReader(file)
    for i in data:
      statement = insert(calendar).values(month=i['month'].strip("'").strip("',"), month_of=i['month_of'].strip("'").strip("',"), day=i['day'].strip("'").strip("',"), item=i['item'].strip("'").strip("',"), item_url=i['item_url'].strip("'").strip("',"))
      with engine.connect() as conn:
        result = conn.execute(statement)



