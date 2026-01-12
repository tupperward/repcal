import os, pytz, requests
from datetime import datetime
from atproto import Client, client_utils
from repcal_shared import RepublicanDate, carpe_diem, get_database_engine

website_url = 'sansculottid.es'
base_url = os.environ.get('BSKY_HANDLE')
engine = get_database_engine("sqlite+pysqlite:///repcal_shared/calendar.db")

def post_to_bsky(now):
  today = carpe_diem(now, engine)
  handle = os.environ.get('BSKY_HANDLE')
  password = os.environ.get('BSKY_PASS')

  # Fetch image from website instead of local file
  image_url = f"https://{website_url}/static/images/{today.image}.jpg"
  image_response = requests.get(image_url)
  img_data = image_response.content

  alt_text = f"An old time-y illustration of a {today.item}."
  caption = f"Today is {today.weekday.capitalize()} the {today.ordinal} of {today.month} in the year {today.year_arabic}.\n{today.month} is the month of {today.month_of.lower()}.\nToday we celebrate {today.item.lower()}."
  link = f"\n\nMore information on {today.item.lower()}"
  client = Client()
  client.login(handle,password)
  text_builder = client_utils.TextBuilder()

  text_builder.text(caption)
  text_builder.tag(text=" #JacobinDay ", tag="JacobinDay")
  text_builder.link(link, today.item_url)

  client.send_image(text=text_builder, image=img_data, image_alt=alt_text)

  return True

if __name__ == "__main__":
  paris_timezone = pytz.timezone('Europe/Paris')
  timestamp = datetime.now(paris_timezone)
  response = post_to_bsky(timestamp)
  print(response)