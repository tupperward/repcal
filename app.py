"""Create a and publish a json object at /json."""
import urllib.request, json, os, csv
from os.path import exists
from flask import Flask, request, send_from_directory
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, text
from sqlalchemy.orm import Session
from unidecode import unidecode 
from repcal import RepublicanDate as rd
from datetime import datetime

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///calendar.db")
meta = MetaData()
# # # # # Classes # # # # # 
# This class creates a python object with attributes that match the values of today's 
class DateObject:
  """Create the date and ingest its attributes."""

  # Some quick variables to clean up what each attribute will be calling
  
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
    n = datetime.now()
    rd_date = rd.from_gregorian(n.date())
    
    self.day = rd.get_day(rd_date)
    self.weekday = rd.get_weekday(rd_date)
    self.month = rd.get_month(rd_date)
    self.yearArabic = rd.get_year_arabic(rd_date)
    self.yearRoman = rd.get_year_roman(rd_date)
    self.formatted = rd_date
    self.week = rd.get_week_number(rd_date)
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
  statement = 'SELECT id, day, month, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(day,month)
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()

  today.id = query.id
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