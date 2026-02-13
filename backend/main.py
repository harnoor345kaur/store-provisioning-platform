from fastapi import FastAPI, HTTPException
import subprocess
import time

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from database import engine, Base, SessionLocal
from models.store import Store

from fastapi.middleware.cors import CORSMiddleware

from k8s_helpers import get_k8s_events


# -------------------------------
# K8s Config
# -------------------------------
config.load_kube_config()   # Uses your kubeconfig (Minikube)

core_v1 = client.CoreV1Api()
networking_v1 = client.NetworkingV1Api()


# -------------------------------
# FastAPI Init
# -------------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Store Provisioning Platform",
    description="Kubernetes Store Orchestration API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Helper — Resource Quota
# =========================================================
def create_resource_quota(store_id):

    v1 = client.CoreV1Api()

    quota = client.V1ResourceQuota(
        metadata=client.V1ObjectMeta(
            name="store-quota",
            namespace=store_id
        ),
        spec=client.V1ResourceQuotaSpec(
            hard={
                "pods": "10",
                "requests.cpu": "2",
                "requests.memory": "4Gi",
                "limits.cpu": "4",
                "limits.memory": "8Gi"
            }
        )
    )

    v1.create_namespaced_resource_quota(
        namespace=store_id,
        body=quota
    )


# =========================================================
# Helper — Create Namespace (SDK)
# =========================================================
def create_namespace(store_id: str):

    ns_body = client.V1Namespace(
        metadata=client.V1ObjectMeta(name=store_id)
    )

    try:
        core_v1.create_namespace(ns_body)
        print(f"Namespace {store_id} created")

    except ApiException as e:
        if e.status != 409:
            raise Exception(f"Namespace creation failed: {e}")
        else:
            print(f"Namespace {store_id} already exists")


# =========================================================
# Helper — Create Ingress (SDK)
# =========================================================
def create_ingress(store_id: str):

    ingress_body = client.V1Ingress(
        metadata=client.V1ObjectMeta(
            name=f"{store_id}-ingress",
            namespace=store_id
        ),
        spec=client.V1IngressSpec(
            rules=[
                client.V1IngressRule(
                    host=f"{store_id}.local",
                    http=client.V1HTTPIngressRuleValue(
                        paths=[
                            client.V1HTTPIngressPath(
                                path="/",
                                path_type="Prefix",
                                backend=client.V1IngressBackend(
                                    service=client.V1IngressServiceBackend(
                                        name=f"{store_id}-wordpress",
                                        port=client.V1ServiceBackendPort(
                                            number=80
                                        )
                                    )
                                )
                            )
                        ]
                    )
                )
            ]
        )
    )

    try:
        networking_v1.create_namespaced_ingress(
            namespace=store_id,
            body=ingress_body
        )
    except ApiException as e:
        if e.status != 409:
            raise Exception(f"Ingress creation failed: {e}")

    return f"http://{store_id}.local"


# =========================================================
# Helper — Store Status
# =========================================================
def get_store_status(store_id: str):

    try:
        pods = core_v1.list_namespaced_pod(namespace=store_id)

        if not pods.items:
            return "Provisioning"

        statuses = [pod.status.phase for pod in pods.items]

        if all(s == "Running" for s in statuses):
            return "Ready"

        if any(s in ["Failed"] for s in statuses):
            return "Failed"

        return "Provisioning"

    except ApiException:
        return "Deleted"


# =========================================================
# Helper — NodePort URL
# =========================================================
def get_nodeport_url(store_id: str):

    try:
        svc = core_v1.read_namespaced_service(
            name=f"{store_id}-wordpress",
            namespace=store_id
        )

        node_port = svc.spec.ports[0].node_port

        ip = subprocess.run(
            ["minikube", "ip"],
            capture_output=True,
            text=True
        ).stdout.strip()

        return f"http://{ip}:{node_port}"

    except:
        return "URL not available"


# =========================================================
# Health
# =========================================================
@app.get("/")
def health():
    return {"status": "Provisioning API running"}


def wait_for_store_ready(store_id, timeout=600):

    start = time.time()

    while time.time() - start < timeout:

        status = get_store_status(store_id)

        if status == "Ready":
            return "Ready"

        if status == "Failed":
            return "Failed"

        time.sleep(10)

    return "Timeout"


# =========================================================
# Create Store
# =========================================================
@app.post("/stores")
def create_store():

    try:
        store_id = f"store-{int(time.time())}"

        # 1️⃣ Namespace
        create_namespace(store_id)

        # -------------------------------
        # Step added — Create Resource Quota
        # -------------------------------
        try:
            create_resource_quota(store_id)
        except ApiException as e:
            if e.status != 409:
                raise


        # 2️⃣ Helm install (still via CLI)
        helm = subprocess.run(
            [
                "helm",
                "install",
                store_id,
                "bitnami/wordpress",
                "-n",
                store_id,
                "-f",
                "values-local.yaml"
            ],
            capture_output=True,
            text=True
        )


        if helm.returncode != 0:
            print(helm.stderr)
            raise Exception(helm.stderr)

        # 3️⃣ Ingress
        domain_url = create_ingress(store_id)

        # 4️⃣ DB entry
        db = SessionLocal()

        new_store = Store(
            store_id=store_id,
            namespace=store_id,
            status="Provisioning",
            ingress_url=domain_url
        )

        db.add(new_store)
        db.commit()
        db.close()

        return {
            "store_id": store_id,
            "status": "Provisioning started"
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# =========================================================
# List Stores
# =========================================================
@app.get("/stores")
def list_stores():

    try:
        # 1️⃣ Get namespaces from K8s
        namespaces = core_v1.list_namespace()

        store_names = [
            ns.metadata.name
            for ns in namespaces.items
            if ns.metadata.name.startswith("store-")
        ]

        # 2️⃣ Fetch DB records
        db = SessionLocal()

        data = []

        for store_name in store_names:

            db_store = (
                db.query(Store)
                .filter(Store.store_id == store_name)
                .first()
            )

            # Status logic priority
            if db_store and db_store.status == "Deleting":
                status = "Deleting"
                node = ingress = "Deleting…"

            else:
                status = get_store_status(store_name)

                if not db_store and status == "Deleted":
                    continue  # Skip this store entirely

                if status == "Ready":
                    node = get_nodeport_url(store_name)
                    ingress = f"http://{store_name}.local"
                else:
                    node = ingress = "Provisioning…"

            created_time = (
                db_store.created_at if db_store else None
            )

            events = get_k8s_events(store_name)

            data.append({
                "store_id": store_name,
                "namespace": store_name,
                "status": status,
                "nodeport_url": node,
                "ingress_url": ingress,
                "created_at": created_time,
                "events": events      # 👈 ADDED
            })



        db.close()

        return {
            "total_stores": len(data),
            "stores": data
        }

    except Exception as e:
        raise HTTPException(500, str(e))


# =========================================================
# Delete Store
# =========================================================
@app.delete("/stores/{store_id}")
def delete_store(store_id: str):

    try:
        # Mark deleting in DB
        db = SessionLocal()
        store = db.query(Store).filter(
            Store.store_id == store_id
        ).first()

        if store:
            store.status = "Deleting"
            db.commit()

        db.close()

        # Helm uninstall
        subprocess.run(
            ["helm", "uninstall", store_id, "-n", store_id],
            capture_output=True,
            text=True
        )

        # Namespace delete
        core_v1.delete_namespace(name=store_id)

        return {
            "store_id": store_id,
            "status": "Deletion started"
        }

    except ApiException as e:
        raise HTTPException(500, str(e))
