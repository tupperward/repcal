import os
import requests
import json
from discord import Embed, SyncWebhook

# Construct Webhook
webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
hook = SyncWebhook.from_url(webhook_url)

# Get data from /data route
data_url = os.environ.get('REPCAL_DATA_URL')
res = requests.get(data_url).text 
data = json.loads(res)

# Construct Embed 
embed = Embed()
embed.title = f"Today is {data['weekday']} {data['day']} {data['month']} an {data['yearArabic']}"
embed.description = f"Today we celebrate {data['item']}."
embed.footer = "https://repcal.tupperward.net"
embed.image = f"https://repcal.tupperward.net{}"
embed.url


if __name__ == "__main__":
    hook.send(embed)