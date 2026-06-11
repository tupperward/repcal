"""Delete CronJobs whose most recent Job failed."""
import os
from kubernetes import client, config

def get_namespace():
    try:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get('NAMESPACE', 'repcal')


def is_failed(job):
    for condition in (job.status.conditions or []):
        if condition.type == 'Failed' and condition.status == 'True':
            return True
    return False


def get_owner_cronjob(job):
    for ref in (job.metadata.owner_references or []):
        if ref.kind == 'CronJob':
            return ref.name
    return None


if __name__ == "__main__":
    config.load_incluster_config()
    batch = client.BatchV1Api()
    namespace = get_namespace()

    jobs = batch.list_namespaced_job(namespace).items
    failed_cronjobs = set()

    for job in jobs:
        if is_failed(job):
            cj_name = get_owner_cronjob(job)
            if cj_name:
                failed_cronjobs.add(cj_name)

    if not failed_cronjobs:
        print("No failed CronJobs to prune.")
    else:
        for name in failed_cronjobs:
            batch.delete_namespaced_cron_job(name, namespace)
            print(f"Deleted CronJob {name}")
        print(f"Pruned {len(failed_cronjobs)} CronJob(s).")
