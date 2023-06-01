from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
from urllib.parse import urlparse
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
class RepublicanDate():
  """Create the date and ingest its attributes."""

  def __init__(self, time):
    """Initialize the object by getting data from the external endpoint."""
    rd_date = rd.from_gregorian(time.date())

    self.day = rd.get_day(rd_date)
    self.weekday = rd.get_weekday(rd_date)
    self.month = rd.get_month(rd_date)
    self.year_arabic = rd.get_year_arabic(rd_date)
    self.year_roman = rd.get_year_roman(rd_date)
    self.week = rd.get_week_number(rd_date)
    self.month_of = None
    self.item = None
    self.item_url = None
    self.is_sansculottides = rd.is_sansculottides(rd_date) 

def check_if_js_time(time):
  """Validate time to make sure the JS time is not just UTC."""
  now = datetime.now()
  server_date = now.date()
  server_hour = now.time().hour
  server_minute = now.time().minute
  return all([time.date() == server_date, time.time().hour == server_hour, time.time().minute == server_minute])

def carpe_diem(time):
  """Seize the day. Create a RepublicanDate and then queries the calendar.db to add the natural details."""
  today = RepublicanDate(time)
  statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(today.day,unidecode(today.month))
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()
  today.id = query.id
  today.month_of = query.month_of
  today.item = query.item
  today.item_url = query.item_url
  today.image = today.item.lower().replace('the ','').replace(' ','_')

  return today

def is_valid_url(url: str):
  """Validate URL. Uses urlparse to validate that all the components are present in the provided string."""
  parsed_url = urlparse(url)
  return all([parsed_url.scheme, parsed_url.netloc, parsed_url.path])

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
  server_time = False
  try:
    time = session.get('timestamp')
    date = datetime.fromtimestamp(int(time))
    server_time = check_if_js_time(date)
  except:
    date = datetime.now()
    server_time = True
  
  today = carpe_diem(date)
  return render_template('today.html', today=today, server_time=server_time)

@app.route('/data')
def data():
  """Return date data for constructing Discord embeds."""
  time = datetime.now()
  today = carpe_diem(time)
  data = {
    "day": today.day,
    "weekday": today.weekday.lower(),
    "month": today.month,
    "year_arabic": today.year_arabic,
    "year_roman": today.year_roman,
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
  import modules.kubectl
    
  url = request.form.get('url', type=str)
  timezone = request.form.get('timezone', type=str)
  time  = request.form.get('time', type=str)

  # Validate the URL
  if not is_valid_url(url):
      error = "Invalid URL"
      app.logger.error(f"Invalid URL: {url}")
      return render_template('failure.html', error=error)

  session['url'] = url

  # Process time into component parts, create a cron compatible schedule string.
  hours, minutes = time.split(':')
  schedule = f"{minutes} {hours} * * *"

  app.logger.info(f"\nWebhook Url: {url}\nTimezone: {timezone}\nSchedule: {schedule}")

  try:
    api_response = modules.kubectl.create_cronjob(url=url, time_zone=timezone, schedule=schedule)
    app.logger.info(api_response)
    return redirect(url_for('success'))
  except Exception as err:
    app.logger.error(f"Failed to create cronjob : {err}")
    return render_template('failure.html', error=err)
  
@app.route('/success')
def success():
  """Render successful webhook creation page."""
  from modules.webhook import construct_embed, use_webhook
  time = datetime.now()
  today = carpe_diem(time)
  data = {
    "day": today.day,
    "weekday": today.weekday.lower(),
    "month": today.month,
    "year_arabic": today.year_arabic,
    "year_roman": today.year_roman,
    "week": today.week,
    "month_of": today.month_of,
    "item": today.item, 
    "item_url": today.item_url,
    "image": today.image,
    "is_sansculottides": today.is_sansculottides
  }
  message = construct_embed(data, component=True)
  url = session.get('url')
  use_webhook(webhook_url=url, message=message, component=True)
  return render_template('success.html')

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