"""Webhook for posting to discord."""
import os
import requests
import json
from discord import Embed, SyncWebhook, Colour
from datetime import datetime
from flask import current_app

base_url = 'sansculottid.es'

# Get data from /data route
def get_data():
  """Get data from data API."""
  data_url = f'https://{base_url}/data'
  res = requests.get(data_url).text 
  data = json.loads(res)
  return data

def construct_embed(data, component = False):
  """Construct embed to send to Discord."""
  ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])
  embed = Embed()
  embed.title = f"Today is {data['weekday'].capitalize()} the {ordinal(int(data['day']))} of {data['month']} in the year {data['year_arabic']}."
  embed.color = Colour.green()
  embed.description = f"\n**{data['month']} is the month of {data['month_of'].lower()}.**\nToday we celebrate {data['item'].lower()}.\n\n {data['item_url'].lower()}"
  if data['month'] == "Sansculottides":
    embed.title = f"Today is {data['weekday'].lower()}, {ordinal(int(data['day']))} of the {data['month'].lower()} in the year {data['year_arabic']}."
    embed.color = Colour.dark_blue()
    embed.description = f"\n**The {data['month'].lower()} are {data['month_of'].lower()} that serve as a year-end festival.**\nToday we celebrate the concept of {data['item'].lower()}.\n\n {data['item_url'].lower()}"
  embed.set_image(url=f"https://{base_url}/static/images/{data['image']}.jpg")
  embed.set_footer(text=f"{data['weekday'].lower()}, {data['day']} des {data['month']} an {data['year_roman'].upper()}", icon_url=f"https://{base_url}/static/images/apricots.jpg")
  embed.url = f"https://{base_url}"
  embed.type = "rich"
  embed.timestamp = datetime.now()
  if component:
    current_app.logger.info("Embed created.")
  return embed

def use_webhook(webhook_url, message: Embed, component = False):
  """Instantiate webhook and send message."""
  hook = SyncWebhook.from_url(webhook_url)
  try:
    if component:
      current_app.logger.info('Sending discord message via webhook.')
    hook.send(embed=message)
    if component:
      current_app.logger.info('Successfully sent discord message with embed.')
  except Exception as err:
    if component:
      current_app.logger.error(f"Could not send discord message: {err}")
      exit(1)
    else: 
      print(err)


# Send embed via hook
if __name__ == "__main__":
  # Construct Webhook
  webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')

  data = get_data()
  message = construct_embed(data)
  use_webhook(webhook_url, message=message)