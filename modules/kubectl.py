import kubernetes.client, kubernetes.config
from kubernetes.client.rest import ApiException
import os, secrets

#configuration.api_key['authorization'] = os.environ.get('K8S_API_KEY')
#configuration.host = os.environ.get('K8S_HOST', default="http://localhost")
kubernetes.config.load_incluster_config()

#TODO #16 Remove name, user doesn't need to set this at all. 
def create_cronjob(url: str, time_zone: str, schedule: str):
    """Create CronJob resource in kubernetes."""
    with kubernetes.client.ApiClient() as api_client:
        api_instance = kubernetes.client.BatchV1Api(api_client=api_client)

        if not os.environ.get('K8S_NAMESPACE') == None:
            namespace = os.environ.get('K8S_NAMESPACE')
        else:
            namespace = 'repcal'

        salty = secrets.randbits(5)
        sweet = secrets.randbits(5)

        metadata = kubernetes.client.V1ObjectMeta(
            name=f"webhook-{salty}-{sweet}",
            labels={"app":"discord-webhook"}
        )
        webhook_url = kubernetes.client.V1EnvVar(name='DISCORD_WEBHOOK_URL', value=url)
        container = kubernetes.client.V1Container(image='tupperward/repcal:discord', env=[webhook_url], name=f"webhook-{salty}-{sweet}")
        pod_spec = kubernetes.client.V1PodSpec(containers=[container], restart_policy="OnFailure")
        pod_template = kubernetes.client.V1PodTemplateSpec(spec=pod_spec, metadata=metadata)
        job_spec = kubernetes.client.V1JobSpec(template=pod_template)
        job_template = kubernetes.client.V1JobTemplateSpec(spec=job_spec, metadata=metadata)
        cronjob_spec = kubernetes.client.V1CronJobSpec(schedule=f"CRON_TZ={time_zone} {schedule}", job_template=job_template, successful_jobs_history_limit=1)
        body = kubernetes.client.V1CronJob(spec=cronjob_spec, metadata=metadata)
        pretty = 'true'
    
    try:
        api_response = api_instance.create_namespaced_cron_job(namespace=namespace, body=body, pretty=pretty)
        return api_response
    except ApiException as error:
        return f"Exception when calling BatchV1Api->create_namespaced_cron_job: {error}\n"