from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from unidecode import unidecode 
from repcal import RepublicanDate as rd
from datetime import datetime
import json, secrets

# Set up Flask as app, generate a secret key using secrets.
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
app.logger.setLevel('INFO')
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
  # This instantiates a DateObject  
  today = DateObject(now)
  statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(today.day,unidecode(today.month))
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()
  today.id = query.id
  today.month_of = query.month_of
  today.item = query.item
  today.item_url = query.item_url
  today.image = today.item.lower().replace('the ','').replace(' ','_')

  return today

@app.route('/', methods=["GET"])
def index():
  """Root path page that contains JS script."""
  return render_template('loading.html' )

@app.route('/local_time', methods=['POST'])
def local_time():
  """Get time from JS."""
  local_time = request.form.get('local_time', str)
  # Store the timestamp variable to the session
  session['timestamp'] = local_time
  return 'OK'

@app.route('/today', methods=["GET"])
def today():
  """Finished rendered page."""
  # Retrieving the timestamp variable from the session
  try:
    time = session.get('timestamp')
    date = datetime.utcfromtimestamp(int(time))
  except:
    date = datetime.now()
  
  today = carpeDiem(date)
  return render_template('today.html', today=today )

@app.route('/data')
def data():
  """Return date data for constructing Discord embeds."""
  time = datetime.now()
  today = carpeDiem(time)
  data = {
    "day": today.day,
    "weekday": today.weekday.lower(),
    "month": today.month,
    "yearArabic": today.yearArabic,
    "yearRoman": today.yearRoman,
    "week": today.week,
    "month_of": today.month_of,
    "item": today.item, 
    "item_url": today.item_url,
    "image": today.image,
    "is_sansculottides": today.is_sansculottides
  }
  json_data = json.dumps(data)
  return json_data

@app.route('/signup')
def signup():
  """Signup page to add the webhook to your discord."""
  return render_template('signup.html')

@app.route('/create_webhook', methods=['POST'])
def create_webhook():
  """Create Cronjob for Webhook."""
  import modules.kubectl as k

  name = request.form.get('name', type=str).strip().replace(' ', '-')
  url = request.form.get('url', type=str)
  timezone = request.form.get('timezone', type=str)
  schedule = request.form.get('schedule', type=str)

  session['name'] = name
  session['url'] = url
  session['timezone'] = timezone
  session['schedule' ] = schedule

  app.logger.info(f"Name: {session.get('name')}   URL: {session.get('url')}    TimeZone: {session.get('timezone')}    Schedule: {session.get('schedule')}")
  
  try:
    k.create_cronjob(name=session.get('name'), url=session.get('url'), time_zone=session.get('timezone'), schedule=session.get('schedule'))
    app.logger.info('Successfully created cronjob.')
  except Exception as err:
    app.logger.error(f"Failed to create cronjob : {err}")
  return redirect(url_for('today'))

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