"""Run once to create the site.standard.publication record.
Prints the AT URI to add as BSKY_PUBLICATION_URI in the k8s secret.
"""
import os
from atproto import Client, models

handle = os.environ.get('BSKY_HANDLE')
password = os.environ.get('BSKY_PASS')
site_url = os.environ.get('SITE_URL')
pds = os.environ.get('BSKY_PDS')

client = Client(base_url=pds)
client.login(handle, password)

response = client.com.atproto.repo.create_record(
    models.ComAtprotoRepoCreateRecord.Data(
        repo=client.me.did,
        collection="site.standard.publication",
        record={
            "$type": "site.standard.publication",
            "name": "French Republican Daily Calendar",
            "url": site_url,
            "description": "The French Republican Calendar — one plant, animal, or tool for every day of the year.",
        }
    )
)

print(f"Publication AT URI: {response.uri}")
print(f"\nAdd to k8s secret:")
print(f"  kubectl patch secret bsky-secret -n repcal --type='json' \\")
print(f"    -p='[{{\"op\":\"add\",\"path\":\"/data/bskyPublicationUri\",\"value\":\"'$(echo -n '{response.uri}' | base64)'\"}}]'")
