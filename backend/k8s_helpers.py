from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()

core_v1 = client.CoreV1Api()
networking_v1 = client.NetworkingV1Api()


# Namespace
def create_namespace(store_id):

    ns = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=store_id)
    )

    try:
        core_v1.create_namespace(ns)
    except ApiException as e:
        if e.status != 409:
            raise


# Resource quota
def create_resource_quota(store_id):

    quota = client.V1ResourceQuota(
        metadata=client.V1ObjectMeta(
            name="store-quota",
            namespace=store_id
        ),
        spec=client.V1ResourceQuotaSpec(
            hard={
                "pods": "10",
                "requests.cpu": "2",
                "requests.memory": "4Gi"
            }
        )
    )

    core_v1.create_namespaced_resource_quota(
        namespace=store_id,
        body=quota
    )


# Ingress
def create_ingress(store_id):

    ingress = client.V1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{store_id}-ingress",
            namespace=store_id
        )
    )

    networking_v1.create_namespaced_ingress(
        namespace=store_id,
        body=ingress
    )

    return f"http://{store_id}.local"


# =========================================================
# Kubernetes Events Helper
# =========================================================
def get_k8s_events(store_id):

    try:
        events = core_v1.list_namespaced_event(
            namespace=store_id
        )

        logs = []

        for e in events.items:
            logs.append(
                f"{e.last_timestamp} — {e.message}"
            )

        return "\n".join(logs)

    except Exception:
        return "No events available"
