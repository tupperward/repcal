"""Create a and publish a json object at /json."""
from flask import Flask, request, render_template, send_from_directory, redirect
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from unidecode import unidecode 
from repcal import RepublicanDate as rd
from datetime import datetime

app = Flask(__name__)
engine = create_engine("sqlite+pysqlite:///calendar.db")
meta = MetaData()
# # # # # Classes # # # # # 
# This class creates a python object with attributes that match the values of today's 
class DateObject():
  """Create the date and ingest its attributes."""

  def __init__(self, time):
    """Initialize the object by getting data from the external endpoint."""
    rd_date = rd.from_gregorian(time.date())

    self.day = rd.get_day(rd_date)
    self.weekday = rd.get_weekday(rd_date)
    self.month = rd.get_month(rd_date)
    self.yearArabic = rd.get_year_arabic(rd_date)
    self.yearRoman = rd.get_year_roman(rd_date)
    self.week = rd.get_week_number(rd_date)
    self.month_of = None
    self.item = None
    self.item_url = None
    self.is_sansculottides = rd.is_sansculottides(rd_date) 

def carpeDiem(now):
  """Seize the day."""
  today = DateObject(now)

  month = unidecode(today.month); day = today.day
  statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(day,month)
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()
  today.id = query.id
  today.month_of = query.month_of
  today.item = query.item
  today.item_url = query.item_url
  today.image = today.item.lower().replace('the ','').replace(' ','_')

  return today

@app.route('/', methods=["POST","GET"])
def index():
  """Index page."""
  return render_template('loading.html', today=today )

@app.route('/today', methods=["POST","GET"])
def today():
  """Finished rendered page."""
  print(request.data)
  print(request.form.get('local_time', str))
  local_time = request.form.get('local_time', str)
  print(type(local_time))
  int_time = int(local_time)
  date = datetime.utcfromtimestamp(int_time)
  print(f"Time: {local_time}   int(local_time): {type(int_time)}   dateType: {type(date)}")
  today = carpeDiem(date)
  return render_template('index.html', today=today, local_time=local_time )

@app.route('/about')
def about():
  """About page for the project."""
  return render_template('about.html')

@app.route('/favicon.ico')
def favicon():
  """Shutup linter."""
  return send_from_directory('static/','favicon.ico')

if __name__ == "__main__":
  app.run()