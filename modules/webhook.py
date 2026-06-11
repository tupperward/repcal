"""Webhook for posting to discord."""
import os
from discord import Embed, SyncWebhook, Colour
from datetime import datetime
from flask import current_app

base_url = 'frenchrepublican.info'

def get_data():
  """Get today's date data and AT-URI from the local DB via app."""
  from app import carpe_diem, get_post
  now = datetime.now()
  today = carpe_diem(now)
  post = get_post(now.strftime('%Y-%m-%d'))
  return {
    'day': today.day,
    'weekday': today.weekday.lower(),
    'month': today.month,
    'year_arabic': today.year_arabic,
    'year_roman': today.year_roman,
    'month_of': today.month_of,
    'item': today.item,
    'item_url': today.item_url,
    'image': today.image,
    'at_uri': post[0] if post else None,
    'bsky_post_uri': post[1] if post else None,
  }

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
  embed.url = f"https://{base_url}/gregorian_date/{datetime.now().strftime('%Y-%m-%d')}"
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
      raise


def _report_failure(webhook_url):
  from kubernetes import client, config
  config.load_incluster_config()
  try:
    with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
      namespace = f.read().strip()
  except FileNotFoundError:
    namespace = os.environ.get('NAMESPACE', 'repcal')
  v1 = client.CoreV1Api()
  try:
    cm = v1.read_namespaced_config_map('webhook-failures', namespace)
    existing = set(filter(None, cm.data.get('failed_urls', '').splitlines()))
    existing.add(webhook_url)
    v1.patch_namespaced_config_map('webhook-failures', namespace,
      client.V1ConfigMap(data={'failed_urls': '\n'.join(existing)}))
  except client.ApiException as e:
    if e.status == 404:
      v1.create_namespaced_config_map(namespace, client.V1ConfigMap(
        metadata=client.V1ObjectMeta(name='webhook-failures', namespace=namespace),
        data={'failed_urls': webhook_url}
      ))
    else:
      raise


if __name__ == "__main__":
  webhook_url = os.environ.get('DISCORD_WEBHOOK_URL')
  data = get_data()
  message = construct_embed(data)
  try:
    use_webhook(webhook_url, message=message)
  except Exception:
    _report_failure(webhook_url)
    raise