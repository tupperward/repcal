"""Create a and publish a json object at /json."""
import urllib.request, json, os, csv
from os.path import exists
from flask import Flask, request, send_from_directory
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from sqlalchemy.orm import Session
from unidecode import unidecode 

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///calendar.db")
meta = MetaData()

# # # # # Classes # # # # # 
# This class creates a python object with attributes that match the values of today's 
class DateObject:
  """Create the date and ingest its attributes."""

  # Some quick variables to clean up what each attribute will be calling
  repcalData = 'https://repcal.info/now.json'
  rd = 'republican_date'
  a = 'attributes'
  
  # Makes the HTTP request to pull raw json data
  #TODO #4 Make a Gregorian Calendar and convert it all for yourself.
  def getJsonData(self,api):
    """Retrieve data from the original deal."""
    with urllib.request.urlopen(api) as url:
      data = json.loads(url.read())
      return data
  
  def jsonFormat(self):
    """Genereate JSON format of the data."""
    jsonDict = {
      "day":self.day,
      "weekday":self.weekday,
      "week":self.week,
      "month":self.month,
      "month_of":self.month_of,
      "yearArabic":self.yearArabic,
      "yearRoman":self.yearRoman,
      "formattedDate":self.formatted,
      "item":self.item,
      "item_url":self.item_url
    }
    return json.dumps(jsonDict)


  # When a new date object is created it will self-populate accurate information from the json
  def __init__(self):
    """Initialize the object by getting data from the external endpoint."""
    # THIS EXISTS SO WE ONLY MAKE THE REQUEST ONCE 
    # Do not just call getJsonData() a half dozen times because it will take forever
    jsonData = self.getJsonData(self.repcalData)

    self.day = jsonData[self.rd][self.a]['day']
    self.weekday = jsonData[self.rd][self.a]['weekday'].strip("('").strip("'),")
    self.month = jsonData[self.rd][self.a]['month'].strip("('").strip("'),")
    self.yearArabic = jsonData[self.rd][self.a]['year_arabic']
    self.yearRoman = jsonData[self.rd][self.a]['year_roman'].strip("('").strip("'),")
    self.formatted = jsonData[self.rd]['formatted'].strip("('").strip("'),")
    self.week = None
    self.month_of = None
    self.item = None
    self.item_url = None

# Makes a collection of days that we can build into entries for the feed.
calendar = Table(
  'calendar', meta,
  Column('id', Integer, unique=True, nullable=False),
  Column('day', Integer),
  Column('week',Integer),
  Column('month', String),
  Column('month_of', String),
  Column('item', String),
  Column('item_url', String)
)

meta.create_all(engine)

def carpeDiem():
  """Seize the day."""
  today = DateObject()
  month = unidecode(today.month); day = today.day
  statement = 'SELECT id, day, week, month, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(day,month)
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()

  today.id = query.id
  today.week = query.week
  today.month_of = query.month_of
  today.item = query.item
  today.item_url = query.item_url
  today.image = today.item.lower().replace('the ','').replace(' ','_')

  return today

@app.route('/')
def data():
  """Path for json object publication."""
  today = carpeDiem()
  return today.jsonFormat()

@app.route('/images/<image>')
def image(image):
  """Path for any given image for a day."""
  return send_from_directory(app.static_folder, request.path[1:])

if __name__ == "__main__":
  app.run()