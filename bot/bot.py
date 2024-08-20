import requests, os, pytz, shutil
from repcal import RepublicanDate as rd
from datetime import datetime
from unidecode import unidecode
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import Session
from bsky_bridge import BskySession, post_image

base_url = os.environ.get('BSKY_HANDLE')
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

def carpe_diem(time):
  """Seize the day. Create a RepublicanDate and then queries the calendar.db to add the natural details."""
  today = RepublicanDate(time)
  ordinal = lambda n: f"{n}{['th', 'st', 'nd', 'rd'][((n//10%10!=1)*(n%10<4)*n%10)::4][0]}"
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

def post_to_bsky(now):
  today = carpe_diem(now)
  handle = os.environ.get('BSKY_HANDLE')
  password = os.environ.get('BSKY_PASS')
  image_path = f"/images/{today.item}"
  alt_text = f"An old time-y illustration of a {today.item}."
  caption = f"Today is {today.weekday.capitalize()} the {today.ordinal} of {today.month} in the year {today.year_arabic}.\n**{today.month} is the month of {today.month_of.lower()}.**\nToday we celebrate {today.item}.\n\n {today.item_url}"
  bsky_session = BskySession(handle, password)

  response = post_image(session=bsky_session, post_text=caption, image_path=image_path, alt_text=alt_text)

  return response

if __name__ == "__main__":
  paris_timezone = pytz.timezone('Europe/Paris')
  timestamp = datetime.datetime.now(paris_timezone)
  response = post_to_bsky(timestamp)
  print(response.status_code)
  print(response.text)