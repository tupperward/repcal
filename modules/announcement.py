"""Send an announcement embed to all registered Discord webhooks."""
import os
from kubernetes import client, config
from discord import SyncWebhook
from datetime import datetime
from webhook import get_data, construct_embed

ANNOUNCEMENT_FILE = os.environ.get('ANNOUNCEMENT_FILE', '/data/announcement.txt')
ANNOUNCEMENT_IMAGE_URL = os.environ.get('ANNOUNCEMENT_IMAGE_URL', '')


def get_namespace():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get('NAMESPACE', 'repcal')


def get_webhook_urls():
    config.load_incluster_config()
    batch = client.BatchV1Api()
    urls = []
    for cj in batch.list_namespaced_cron_job(get_namespace()).items:
        for container in cj.spec.job_template.spec.template.spec.containers:
            for env_var in (container.env or []):
                if env_var.name == 'DISCORD_WEBHOOK_URL' and env_var.value:
                    urls.append(env_var.value)
    return urls


def run():
    with open(ANNOUNCEMENT_FILE) as f:
        text = f.read().strip()

    embed = construct_embed(get_data())
    embed.title = "Une humble annonce"
    embed.description = text
    if ANNOUNCEMENT_IMAGE_URL:
        embed.set_image(url=ANNOUNCEMENT_IMAGE_URL)

    urls = get_webhook_urls()
    print(f"Sending announcement to {len(urls)} webhooks.")

    for url in urls:
        hook = SyncWebhook.from_url(url)
        try:
            hook.send(embed=embed)
            print(f"Sent to ...{url[-30:]}")
        except Exception as e:
            print(f"Failed for ...{url[-30:]}: {e}")
            raise


if __name__ == "__main__":
    run()
