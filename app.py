"""Run the application."""
from flask import Flask, request, render_template, send_from_directory, session, redirect, url_for
from urllib.parse import urlparse
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from unidecode import unidecode 
from repcal import RepublicanDate as rd
from datetime import datetime, timedelta
import json, secrets, pytz

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
  server_second = now.time().second
  server_microsecond = now.time().microsecond
  return all([time.date() == server_date, time.time().hour == server_hour, time.time().minute == server_minute, time.time().second == server_second, time.time().microsecond == server_microsecond])

def carpe_diem(time):
  """Seize the day. Create a RepublicanDate and then queries the calendar.db to add the natural details."""
  today = RepublicanDate(time)
  ordinal = lambda n: f"{n}{['th', 'st', 'nd', 'rd'][((n//10%10!=1)*(n%10<4)*n%10)::4][0]}"
  app.logger.info(f"Today's Date: {today.year_arabic} {today.month} {today.day}")
  if today.month == None:
    today.month = "Sansculottides"
  statement = 'SELECT id, month_of, item, item_url FROM calendar WHERE day == {} AND month LIKE "{}"'.format(today.day,unidecode(today.month))
  with Session(engine) as session:
    query = session.execute(text(statement)).fetchone()
  today.id = query.id
  today.month_of = query.month_of
  today.item = query.item
  today.item_url = query.item_url
  today.image = today.item.lower().replace('the ','').replace(' ','_').replace('-','_')
  today.ordinal = ordinal(today.day)

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
  try:
    local_time = request.form.get('local_time', str)
    timezone_offset = request.form.get('timezone_offset')
  except Exception as e:
    app.logger.error(f"Could not retrieve time data from browser. {e}")
  # Store the timestamp variable to the session
  session['timestamp'] = local_time

  timezone_offset_hours = int(timezone_offset) // 60
  session['timezone_offset'] = timezone_offset_hours
  return 'OK'

@app.route('/today', methods=["GET"])
def today():
  """Finished rendered page."""
  server_time = False
  try:
    timestamp = int(session.get('timestamp'))
    timezone_offset = int(session.get('timezone_offset'))

    if timezone_offset >= 0:
      timezone = pytz.timezone(f"Etc/GMT+{timezone_offset}")
    else:
      timezone = pytz.timezone(f"Etc/GMT{timezone_offset}")

    date = datetime.fromtimestamp(timestamp, tz=timezone)
    server_time = check_if_js_time(date)
    app.logger.info(f"Timezone Offset: {timezone_offset}  Timezone: {timezone}  Local Time: {datetime.fromtimestamp(timestamp, tz=timezone).time()}")
  except Exception as e:
    app.logger.info(f'Using UTC time. {e}')
    date = datetime.now()
    server_time = True
  
  session['date'] = date
  today = carpe_diem(date)

  if today.month == "Sansculottides":
    return render_template('sansculottides.html', today=today, server_time=server_time, permalink=url_for('linkable_converted_date', date=date.strftime("%Y-%m-%d")))
  return render_template('today.html', today=today, server_time=server_time, permalink=url_for('linkable_converted_date', date=date.strftime("%Y-%m-%d")))

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

@app.route('/date_converter')
def converter():
  """Date converter so you can see what any given day was."""
  return render_template('converter.html')


@app.route('/vulgar_date/<date>', methods=['GET'])
def linkable_converted_date(date):
  """Return a linkable page."""
  specific_date = datetime.strptime(date, "%Y-%m-%d")
  today = carpe_diem(specific_date)
  date_string = specific_date.strftime("%B %dth %Y")
  converted=True

  if today.month == "Sansculottides":
    return render_template('sansculottides.html', today=today, converted=converted, date_string=date_string)
  return render_template('today.html', today=today, converted=converted, date_string=date_string)

@app.route('/process_date', methods=['POST','GET'])
def specific_date_conversion():
  """Return a page describing the date you wanted."""
  date_string = str(request.form.get('date'))

  return redirect(url_for('linkable_converted_date', date=date_string))

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
  try:
    date = session.get('date')
  except:
    date = datetime.now()
  today = carpe_diem(date)
  return render_template('about.html', today=today)

@app.route('/favicon.ico')
def favicon():
  """Shutup linter."""
  return send_from_directory('static/','favicon.ico')

if __name__ == "__main__":
  app.run()