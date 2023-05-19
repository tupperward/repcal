import os
import requests
import json
from discord import Embed, SyncWebhook, Colour
from datetime import datetime

# Get data from /data route
def get_data():
  """Get data from data API."""
  if not os.environ.get('REPCAL_DATA_URL'):
    data_url = os.environ.get('REPCAL_DATA_URL')
  else: 
    data_url = 'https://repcal.tupperward.net/data'
  res = requests.get(data_url).text 
  data = json.loads(res)
  return data

def construct_embed(data):
  """Construct embed to send to Discord."""
  embed = Embed()
  embed.title = f"Today is: {data['weekday'].lower()} {data['day']} {data['month']} an {data['yearArabic']}"
  embed.color = Colour.green()
  embed.description = f"\n**{data['month']} is the month of {data['month_of'].lower()}.**\nToday we celebrate {data['item'].lower()}.\n\n {data['item_url'].lower()}"
  embed.set_image(url=f"https://repcal.tupperward.net/static/images/{data['image']}.jpg")
  embed.set_footer(text=f"{data['weekday'].lower()} {data['day']} {data['month']} an {data['yearRoman'].upper()}", icon_url="https://repcal.tupperward.net/static/images/apricots.jpg")
  embed.url = "https://repcal.tupperward.net"
  embed.type = "rich"
  embed.timestamp = datetime.now()
  return embed

def use_webhook(url, message: Embed):
  """Instantiate webhook and send message."""
  hook = SyncWebhook.from_url(url)
  hook.send(embed=message)
  return 'OK'


# Send embed via hook
if __name__ == "__main__":
  # Construct Webhook
  webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
  
  data = get_data()
  message = construct_embed(data)
  use_webhook(webhook_url, message=message)