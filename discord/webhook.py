import os
import requests
import json
from discord import Embed, SyncWebhook, Colour
from datetime import datetime

# Construct Webhook
webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
hook = SyncWebhook.from_url(webhook_url)

# Get data from /data route
data_url = os.environ.get('REPCAL_DATA_URL')
res = requests.get(data_url).text 
data = json.loads(res)

# Construct Embed 
embed = Embed()
embed.title = f"Today is: {data['weekday'].lower()} {data['day']} {data['month']} an {data['yearArabic']}"
embed.color = Colour.green()
embed.description = f"\n**{data['month']} is the month of {data['month_of']}.**\n\nToday we celebrate {data['item']}.\n\n {data['item_url']}"
embed.set_image(url=f"https://repcal.tupperward.net/static/images/{data['image']}.jpg")
embed.set_footer(text=f"{data['weekday'].lower()} {data['day']} {data['month']} an {data['yearRoman'].upper()}", icon_url="https://repcal.tupperward.net")
embed.url = "https://repcal.tupperward.net"
embed.type = "rich"
embed.timestamp = datetime.now()

# Send embed via hook
hook.send(embed=embed) 