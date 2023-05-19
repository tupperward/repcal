import kubernetes.client, kubernetes.config
from kubernetes.client.rest import ApiException
from pprint import pprint
import os, secrets

configuration = kubernetes.client.Configuration()
#configuration.api_key['authorization'] = os.environ.get('K8S_API_KEY')
#configuration.host = os.environ.get('K8S_HOST', default="http://localhost")
conf = kubernetes.config.load_incluster_config(client_configuration=configuration)

def create_cronjob(name: str, url: str, time_zone: str, schedule: str):
    """Create CronJob resource in kubernetes."""
    with kubernetes.client.ApiClient(configuration=conf) as api_client:
        api_instance = kubernetes.client.BatchV1Api(api_client=api_client)

        namespace = os.environ.get('K8S_NAMESPACE')
        salt = secrets.randbits(8)
        metadata = kubernetes.client.V1ObjectMeta(
            name=f"{name}-discord-{salt}",
            labels="discord webhook"
        )
        webhook_url = kubernetes.client.V1EnvVar(name='DISCORD_WEBHOOK_URL', value=url)
        container = kubernetes.client.V1Container(image='tupperward/repcal:discord', env=[webhook_url])
        pod_spec = kubernetes.client.V1PodSpec(containers=[container])
        pod_template = kubernetes.client.V1PodTemplateSpec(spec=pod_spec, metadata=metadata)
        job_spec = kubernetes.client.V1JobSpec(template=pod_template)
        job_template = kubernetes.client.V1JobTemplateSpec(spec=job_spec, metadata=metadata)
        cronjob_spec = kubernetes.client.V1CronJobSpec(schedule=f"CRON_TZ={time_zone} {schedule}", job_template=job_template)
        body = kubernetes.client.V1CronJob(spec=cronjob_spec, metadata=metadata)
        pretty = 'true'
    
    try:
        api_response = api_instance.create_namespaced_cron_job(namespace=namespace, body=body, pretty=pretty)
        pprint(api_response)
    except ApiException as error:
        print(f"Exception when calling BatchV1Api->create_namespaced_cron_job: {error}\n")