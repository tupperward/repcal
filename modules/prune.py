"""Delete CronJobs whose webhook URL is recorded in the webhook-failures ConfigMap."""
import os
from kubernetes import client, config


def get_namespace():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get('NAMESPACE', 'repcal')


if __name__ == "__main__":
    config.load_incluster_config()
    v1 = client.CoreV1Api()
    batch = client.BatchV1Api()
    namespace = get_namespace()

    try:
        cm = v1.read_namespaced_config_map('webhook-failures', namespace)
    except client.ApiException as e:
        if e.status == 404:
            print("No webhook-failures ConfigMap found, nothing to prune.")
            raise SystemExit(0)
        raise

    failed_urls = set(filter(None, cm.data.get('failed_urls', '').splitlines()))
    if not failed_urls:
        print("No failed URLs recorded, nothing to prune.")
        raise SystemExit(0)

    pruned = []
    for cj in batch.list_namespaced_cron_job(namespace).items:
        for container in cj.spec.job_template.spec.template.spec.containers:
            for env_var in (container.env or []):
                if env_var.name == 'DISCORD_WEBHOOK_URL' and env_var.value in failed_urls:
                    batch.delete_namespaced_cron_job(cj.metadata.name, namespace)
                    print(f"Deleted CronJob {cj.metadata.name}")
                    pruned.append(cj.metadata.name)

    v1.delete_namespaced_config_map('webhook-failures', namespace)
    print(f"Pruned {len(pruned)} CronJob(s) and cleared webhook-failures ConfigMap.")
