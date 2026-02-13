# 🚀 Store Provisioning Platform

A Kubernetes-native multi-tenant store provisioning system that automatically deploys fully functional e-commerce stores (WooCommerce) on demand using Helm.

Designed to run locally (Minikube/k3d/Kind) and in production (k3s/VPS) with configuration-only changes.

---

# 📌 Features

* Provision WooCommerce stores automatically
* Namespace-per-store isolation
* Kubernetes-native provisioning
* Helm-based deployments
* Resource quotas per store
* Ingress-based URL routing
* Real-time store status tracking
* Event logs & observability
* Clean teardown on deletion
* Production-ready architecture

---

# 🏗️ System Architecture

```
React Dashboard  →  FastAPI Backend  →  Kubernetes Cluster
                         │
                         ├── Helm Charts
                         ├── Namespace creation
                         ├── Resource quotas
                         ├── Ingress creation
                         └── Store lifecycle management
```

---

# 🧩 Components

## 1️. Dashboard (React)

* View all stores
* Provision new stores
* Delete stores
* View status & URLs
* View timestamps & events

Path:

```
dashboard/
```

---

## 2️. Backend (FastAPI)

Handles:

* Store provisioning
* Helm deployments
* Namespace creation
* Resource quotas
* Ingress setup
* Status monitoring
* Event logging

Path:

```
backend/
```

---

## 3️. Kubernetes Layer

Each store gets:

* Dedicated Namespace
* WordPress + MariaDB
* PVC storage
* Service (NodePort / LB)
* Ingress URL
* ResourceQuota

---

# ⚙️ Local Setup Instructions

## 1️. Clone repo

```bash
git clone <your-repo-url>
cd store-provisioning-platform
```

---

## 2️. Start Kubernetes

Using Minikube:

```bash
minikube start
```

Enable ingress:

```bash
minikube addons enable ingress
```

---

## 3️. Install Helm

```bash
choco install kubernetes-helm
```

Add Bitnami repo:

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

---

## 4️. Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs on:

```
http://127.0.0.1:8000
```

---

## 5️. Dashboard setup

```bash
cd dashboard
npm install
npm start
```

Runs on:

```
http://localhost:3000
```

---

# ⚙️ Local Setup Instructions

1. Open CMD in Admin mode and start the cluster "minikube start --driver=docker".
2. Open CMD in Admin mode in another window and use the command "kubectl port-forward svc/platform-db-postgresql 5433:5432" to expose the DB locally on port 5433 because currently we are using PostgreSQL inside Kubernetes.
3. Start the frontend.
4. Start the backend.

---

# ⚙️ Testing - Using Swagger UI

---

# ⚙️ Exposing a Service-Store

```
To expose a store with store id = "store-123456"
    "minikube service store-123456-wordpress -n store-123456"
is used.
You get few urls which open into Wordpress pages/app. 
```

---

# 🌐 Local Domain Mapping

Edit hosts file:

```
C:\Windows\System32\drivers\etc\hosts
```

Add:

```
127.0.0.1 store-xxxx.local
```

(Replace with generated store IDs.)

---

# 🛍️ Creating a Store

1. Open Dashboard

2. Click **Create Store**

3. System provisions:

   * Namespace
   * Helm chart
   * PVC
   * Services
   * Ingress

4. Status → Ready

5. Open Store URL

---

# 🧪 Order Testing (Definition of Done)

WooCommerce store supports:

* Add product to cart
* Checkout (COD/Dummy)
* Order creation in admin panel

---

# 🗑️ Deleting a Store

Deletion removes:

* Helm release
* Pods
* Services
* PVCs
* Ingress
* Namespace

Clean teardown guaranteed.

---

# 📊 Observability

Implemented:

* Store status tracking
* Provision duration
* Kubernetes events
* Failure reasons

---

# 🔐 Security

* Namespace isolation
* Resource quotas
* RBAC-ready architecture
* No hardcoded secrets
* Least-privilege design ready

---

# 📦 Helm Deployment

Helm used for:

* WordPress
* MariaDB
* Services
* PVC
* Ingress

Supports:

```
values-local.yaml
values-prod.yaml
```

---

# ☁️ VPS / Production Deployment

Runs on:

* AWS EC2 / VPS
* k3s cluster
* Same Helm charts
(Properly supports VPS environments)

Steps:

```bash
curl -sfL https://get.k3s.io | sh -
kubectl get nodes
helm install <store>
```

Ingress exposes public URLs.

---

# 📈 Scaling Design

Supports:

* Concurrent store provisioning
* Horizontal API scaling
* Namespace isolation

---

# 🧱 Multi-Tenant Isolation

Each store has:

* Dedicated namespace
* Dedicated DB
* Dedicated PVC
* ResourceQuota
* Network isolation ready

---


# 📁 Repo Structure

```
store-provisioning-platform/
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   └── k8s_helpers.py
│
├── dashboard/
│   ├── src/
│   └── public/
│
├── helm/
│   ├── values-local.yaml
│   └── values-prod.yaml
│
├── deploy.sh
└── README.md
```

---

# 🎥 Demo Coverage

Video demonstrates:

* System architecture
* Store provisioning flow
* Namespace isolation
* Resource quotas
* URL access
* Order placement
* Store deletion
* Observability logs

---

# 🚀 Future Enhancements

* MedusaJS engine
* TLS via cert-manager
* Domain mapping UI
* NetworkPolicies
* Autoscaling provisioning
* Metrics dashboard

---

# Author

Harnoor Kaur Saggu
Store Provisioning Platform — Kubernetes Assignment

---
