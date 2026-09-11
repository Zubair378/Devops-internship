# DevOps Internship - Week 1

## Project Overview

This project contains two independent Python-based microservices built using the Flask framework, containerized using optimized multi-stage Docker images.

* **Backend Service** (Port 5000)
* **Frontend Service** (Port 5001)

Each service is fully independent — built, run, and verified separately using Docker.

<img width="1920" height="1080" alt="Screenshot (1201)" src="https://github.com/user-attachments/assets/de7edc16-c0c4-4f31-a739-4fd0f33f20a6" />

## Project Structure

```
devops-week1/
├── backend/
│   ├── app.py
│   ├── dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── dockerfile
│   └── requirements.txt
│
└── README.md
```

## Technologies Used

* Python 3.12
* Flask
* Docker (multi-stage builds)
* WSL2 (Ubuntu)
* kubectl, Terraform, Helm (installed and verified as prerequisites)

## Prerequisites Verified

| Tool | Status |
|---|---|
| WSL2 (Ubuntu) | Installed |
| Docker | v29.6.1 |
| kubectl | v1.36.1 |
| Terraform | v1.15.7 |
| Helm | v4.2.3 |

<img width="612" height="248" alt="a" src="https://github.com/user-attachments/assets/fc89a24a-5d1d-41f4-bf0f-bbd6e0e5b827" />

## Microservices

### Backend Service
Runs on port **5000**.

Available endpoints:
* `GET /health`
* `GET /info`

Example:
```
http://localhost:5000/info
```

### Frontend Service
Runs on port **5001**.

Available endpoints:
* `GET /health`
* `GET /info`

Example:
```
http://localhost:5001/info
```

> Note: Frontend and backend currently run as fully independent services. Service-to-service communication (frontend calling backend) is a planned next step, not part of Week 1 scope.

## Docker

Each microservice includes an optimized, multi-stage Dockerfile.

**Features:**
* Multi-stage build (separate builder and runtime stages)
* Lightweight runtime image (`python:3.12-slim`)
* Runs as a non-root user (`appuser`)
* Exposes the required application port

### Build Docker Images

**Backend**
```
cd backend
docker build -t backend:1.0 .
```

**Frontend**
```
cd frontend
docker build -t frontend:1.0 .
```

### Run Docker Containers

**Backend**
```
docker run -d --name backend -p 5000:5000 backend:1.0
```

**Frontend**
```
docker run -d --name frontend -p 5001:5001 frontend:1.0
```

### Verify Running Containers
```
docker ps
```

### Verify Endpoints

**Backend Health**
```
curl http://localhost:5000/health
```

**Backend Info**
```
curl http://localhost:5000/info
```

**Frontend Health**
```
curl http://localhost:5001/health
```

**Frontend Info**
```
curl http://localhost:5001/info
```

### Verify Non-Root User

Check the user inside each running container.

<img width="1438" height="261" alt="image" src="https://github.com/user-attachments/assets/4ff18aaf-4b23-4671-9163-6b3ee294da70" />

**Backend**
```
docker exec -it backend whoami
```

**Frontend**
```
docker exec -it frontend whoami
```

Expected output:
```
appuser
```

## Week 1 Outcome

* Verified all required prerequisites (WSL2, Docker, kubectl, Terraform, Helm).
* Developed two independent Python/Flask microservices.
* Implemented `/health` and `/info` endpoints on both services.
* Wrote optimized, multi-stage Dockerfiles for both services.
* Configured both containers to run as a non-root user (`appuser`).
* Built and tagged Docker images locally.
* Verified successful container execution using `docker run`.
* Verified endpoints using `curl`.
* Verified non-root user execution using `docker exec`.

---

# DevOps Internship - Week 2

## Project Overview

This week builds on Week 1 by provisioning a **local Kubernetes cluster using Terraform**, via the community `minikube` provider. The cluster is fully managed as code — created, verified, and torn down using Terraform rather than manual commands.

## Project Structure

```
devops-week2/
├── main.tf
├── recreate-cluster.sh
├── .terraform.lock.hcl
└── (auto-generated: .terraform/, terraform.tfstate)
```

## Technologies Used

* Terraform v1.15.7
* Terraform minikube provider (`scott-the-programmer/minikube`, v0.6.0)
* minikube v1.38.1
* kubectl
* Docker (used as the minikube driver)

<img width="1550" height="113" alt="image" src="https://github.com/user-attachments/assets/90e29348-3422-4527-a7da-d8da804fedba" />

## Terraform Setup

### Provider and Resource Configuration (`main.tf`)

```hcl
terraform {
  required_providers {
    minikube = {
      source  = "scott-the-programmer/minikube"
      version = "0.6.0"
    }
  }
}

provider "minikube" {}

resource "minikube_cluster" "my-cluster" {
  driver       = "docker"
  cluster_name = "devops-week2"
  memory       = "2200mb"
  cpus         = 2
}
```

### Variables Explained

| Variable | Value | Why |
|---|---|---|
| `driver` | `docker` | Uses Docker (already installed and configured) to run the cluster's node as a container, instead of requiring a separate VM hypervisor. |
| `cluster_name` | `devops-week2` | Identifies this specific cluster/profile. Used by both Terraform and minikube to reference the same cluster consistently. |
| `memory` | `2200mb` | RAM allocated to the cluster's node. Deliberately conservative — tuned to fit an 8GB host machine with limited free memory, after minikube's default (3072mb) triggered a stability warning. |
| `cpus` | `2` | Number of virtual CPUs allocated to the cluster's node. |

All other cluster settings (API server port, disk size, DNS domain, etc.) use the provider's built-in defaults, since they weren't explicitly required for this setup.

## Setup Instructions

### 1. Initialize Terraform
```
cd devops-week2
terraform init
```
Downloads the minikube provider plugin and prepares the working directory.

### 2. Preview the plan
```
terraform plan
```
Shows what Terraform will create, without making any changes yet.

### 3. Apply (create the cluster)
```
terraform apply
```
Type `yes` when prompted. This provisions the actual local Kubernetes cluster via minikube.

## Verifying the Cluster

### Check cluster health
```
kubectl cluster-info
```
Expected output confirms the control plane and CoreDNS are running.

### Check node status
```
kubectl get nodes
```
Expected output shows one node named `devops-week2` with status `Ready`.

### Check system pods
```
kubectl get pods -A
```
Confirms core Kubernetes components (`coredns`, `etcd`, `kube-apiserver`, `kube-scheduler`, `kube-controller-manager`, `storage-provisioner`) are all `Running`.

<img width="1910" height="566" alt="image" src="https://github.com/user-attachments/assets/b10eccaf-2b16-4e5f-9e9e-9d8caa51c7c4" />

## kubectl Context

Applying the Terraform configuration automatically configures `kubectl` to point at the new cluster. This can be confirmed with:
```
kubectl config current-context
```
Expected output: `devops-week2`

If the context ever becomes stale (for example, after a machine restart changes the cluster's local port mapping), it can be refreshed with:
```
minikube update-context -p devops-week2
```

## Destroy and Recreate Script

A wrapper script, `recreate-cluster.sh`, is included to reset the cluster to a clean, known baseline for testing. Rather than only running `terraform destroy` and `terraform apply` back to back, it also removes orphaned local resources that Terraform's own state may not be aware of (a real issue encountered during development, where a manually-run minikube command left behind an untracked cluster profile).

```bash
#!/bin/bash

set -e

CLUSTER_NAME="devops-week2"

echo "Step 1: Attempting Terraform destroy (best effort)..."
terraform destroy -auto-approve || echo "Terraform destroy failed or nothing to destroy — continuing cleanup."

echo "Step 2: Force-removing any orphaned minikube profile..."
minikube delete -p "$CLUSTER_NAME" || echo "No orphaned minikube profile found — continuing."

echo "Step 3: Removing any leftover Docker container for this cluster..."
docker rm -f "$CLUSTER_NAME" 2>/dev/null || echo "No leftover container found — continuing."

echo "Step 4: Dropping dead kubeconfig context (if present)..."
kubectl config delete-context "$CLUSTER_NAME" 2>/dev/null || echo "No stale kubeconfig context found — continuing."

echo "Step 5: Clearing local Terraform cache..."
rm -rf .terraform .terraform.lock.hcl

echo "Step 6: Reinitializing Terraform..."
terraform init

echo "Step 7: Creating a fresh cluster..."
terraform apply -auto-approve

echo "Step 8: Verifying cluster health..."
kubectl cluster-info

echo "Done. Cluster has been reset to a known, clean baseline."
```

### Usage
```
chmod +x recreate-cluster.sh
./recreate-cluster.sh
```

> Note: This script uses `-auto-approve` for both Terraform commands, which skips the interactive confirmation prompt. This is appropriate for a local testing/reset script, but would be reconsidered for any shared or production environment.

<img width="1920" height="643" alt="image" src="https://github.com/user-attachments/assets/64411084-695e-4dda-bde3-368ee0d523c7" />

## Issues Faced & Troubleshooting

Several real issues came up during this task. Documenting them here since diagnosing and resolving them was part of the actual work.

### 1. WSL2 memory too low for minikube's default request
**Issue:** `minikube start --dry-run` warned that the default memory request (3072MiB) didn't leave room for system overhead, on a host machine with only 8GB total RAM.
**Fix:** Adjusted WSL2's own memory allocation via `.wslconfig` (`memory=4GB`), and explicitly set a smaller, more conservative `memory = "2200mb"` in the Terraform config instead of relying on the provider's default.

### 2. `.wslconfig` changes not applying immediately
**Issue:** After editing `.wslconfig`, `free -h` inside Ubuntu still showed the old memory limit.
**Fix:** A plain `wsl` command only re-enters an already-running instance — it does not reload config. `wsl --shutdown` (from PowerShell, not from inside Ubuntu) is required to fully stop WSL2 before the new `.wslconfig` settings take effect on the next launch.

### 3. First `terraform apply` appeared to freeze
**Issue:** During cluster creation, Terraform's "Still creating..." timer appeared to stall (and briefly showed corrupted/negative timestamps due to a terminal rendering glitch).
**Fix:** Confirmed real progress was happening by checking `docker ps` and `docker stats` in a separate terminal — the container was actively being created and using CPU. The apply eventually completed successfully after ~12 minutes, slower than usual due to the host machine's limited resources.

### 4. `kubectl cluster-info` failed with "connection refused" after a machine restart
**Issue:** After restarting the computer, Docker Desktop (and the minikube container) stopped. On restart, the container was reassigned a new local port, but `kubectl` was still configured to use the old, stale port.
**Fix:** Ran `minikube update-context -p devops-week2` to refresh the kubeconfig with the container's current address.

### 5. Orphaned minikube profile created accidentally
**Issue:** Running `minikube stop` without specifying `-p devops-week2` caused minikube to default to looking for (and starting to create) a separate cluster literally named `minikube` — unrelated to the Terraform-managed cluster. This was caught and cancelled before it fully completed, but left behind an incomplete, broken profile.
**Fix:** Removed the stray profile with `minikube delete -p minikube`, then explicitly restarted the correct cluster with `minikube start -p devops-week2`. This experience directly motivated hardening `recreate-cluster.sh` to also clean up orphaned profiles, containers, and dead kubeconfig contexts before running Terraform — since Terraform's own state has no visibility into resources created or broken outside of it.

**Key takeaway:** local Kubernetes tooling (minikube) can drift out of sync with Terraform's state, especially across restarts or manual command usage. Always target the specific cluster profile explicitly (`-p devops-week2`), and treat `terraform destroy`/`apply` as necessary but not always sufficient for a truly clean reset — hence the additional cleanup steps in the recreate script.

## Week 2 Outcome

* Wrote Terraform configuration to provision a local Kubernetes cluster using the minikube provider.
* Applied the configuration and verified cluster health using `kubectl cluster-info`.
* Documented the Terraform setup process and variables (this section).
* Confirmed `kubectl` context was automatically configured and connected to the new cluster.
* Diagnosed and resolved a real orphaned-profile/state-drift issue encountered during development.
* Wrote and tested an idempotent destroy/recreate script for quickly resetting the cluster during testing.

---

# DevOps Internship - Week 3

## Project Overview

This week takes the Docker images built in Week 1 and actually runs them inside the Kubernetes cluster provisioned in Week 2, using raw Kubernetes YAML manifests — Deployments, Services, a ConfigMap, and a Secret. This is the point where all three weeks connect: Week 1's images finally run inside Week 2's cluster, wired together the way a real Kubernetes-hosted application would be.

## Project Structure

```
devops-week3/
├── configmap.yaml
├── secret.yaml
├── backend-deployment.yaml
├── backend-service.yaml
├── frontend-deployment.yaml
└── frontend-service.yaml
```

## Manifests

### ConfigMap (`configmap.yaml`)
Stores non-sensitive configuration values, injected into both containers as environment variables.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
```

### Secret (`secret.yaml`)
Stores a placeholder sensitive value, demonstrating how credentials would be injected without hardcoding them into the image. Data is base64-encoded (a storage format requirement, not encryption).

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  API_KEY: ZGVtby1zZWNyZXQta2V5LTEyMw==
```

<img width="1920" height="1080" alt="Screenshot (1213)" src="https://github.com/user-attachments/assets/021483d7-39ec-49ec-8d1b-dd3c8bb98bdd" />


### Backend Deployment (`backend-deployment.yaml`)
Runs 2 replicas of the `backend:1.0` image built in Week 1, with the ConfigMap/Secret injected as environment variables, resource limits, and liveness/readiness probes against the `/health` endpoint built in Week 1.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: backend:1.0
          imagePullPolicy: Never
          ports:
            - containerPort: 5000
          envFrom:
            - configMapRef:
                name: app-config
            - secretRef:
                name: app-secret
          resources:
            requests:
              cpu: "100m"
              memory: "64Mi"
            limits:
              cpu: "250m"
              memory: "128Mi"
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 5
```

### Backend Service (`backend-service.yaml`)
Gives the backend pods a stable, permanent internal address (`backend-service`), so other pods never need to depend on a pod's individual, changeable IP.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
    - port: 5000
      targetPort: 5000
  type: ClusterIP
```

### Frontend Deployment and Service (`frontend-deployment.yaml`, `frontend-service.yaml`)
Structurally identical to backend's, targeting the `frontend:1.0` image and port `5001`.

## Setup Instructions

### 1. Ensure the Week 2 cluster is running
```
minikube start -p devops-week2
```

### 2. Load local Docker images into minikube

Since the Deployments use `imagePullPolicy: Never`, the images must exist inside minikube's own Docker environment, not just the host machine's:

```
minikube image load backend:1.0 -p devops-week2
minikube image load frontend:1.0 -p devops-week2
```

### 3. Apply the manifests, in order

ConfigMap and Secret are applied first, since the Deployments reference them:

```
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml
```

## Verification

### Check pod status
```
kubectl get pods
```
Expected: 4 pods (2 backend, 2 frontend), all `Running`, `1/1` ready, `0` restarts.

### Check deployment health
```
kubectl get deployments
```
Expected: `2/2` ready for both.

### Check services
```
kubectl get services
```
Expected: `backend-service` and `frontend-service` listed with `ClusterIP` addresses.

### Verify internal service-to-service communication

Since the base image (`python:3.12-slim`) does not include `curl`, verification was done using Python's built-in `urllib` from inside a pod instead:

```
kubectl exec -it <frontend-pod-name> -- python3 -c "import urllib.request; print(urllib.request.urlopen('http://backend-service:5000/health').read())"
```

```
kubectl exec -it <backend-pod-name> -- python3 -c "import urllib.request; print(urllib.request.urlopen('http://frontend-service:5001/health').read())"
```

This proves communication happens via the **Service name**, not a pod's individual IP — the correct, stable pattern for Kubernetes networking, since pod IPs change whenever a pod restarts or gets replaced.

## Resource Limits and Probes

| Setting | Value | Purpose |
|---|---|---|
| `requests.cpu` / `requests.memory` | `100m` / `64Mi` | Minimum resources guaranteed to each container |
| `limits.cpu` / `limits.memory` | `250m` / `128Mi` | Hard ceiling, keeping any single container from consuming all node resources — kept deliberately small given host machine memory constraints identified in Week 2 |
| `livenessProbe` | `GET /health` every 10s | If this fails repeatedly, Kubernetes restarts the container automatically |
| `readinessProbe` | `GET /health` every 5s | If this fails, the pod is temporarily removed from the Service's routing until it passes again, without being restarted |

Both probes reuse the `/health` endpoint built in Week 1 — the same endpoint that was manually verified with `curl` in Week 1 is now used by Kubernetes to continuously and automatically verify container health.


<img width="1920" height="1080" alt="Screenshot (1214)" src="https://github.com/user-attachments/assets/b5f0a8c7-0d7d-477f-9da8-c5a4a1d7fe11" />


## Issues Faced & Troubleshooting

### 1. `frontend:1.0` image missing when loading into minikube
**Issue:** `minikube image load frontend:1.0 -p devops-week2` failed with "image not found," even though `backend:1.0` loaded successfully.
**Fix:** `docker images` confirmed the `frontend:1.0` tag no longer existed locally. Rebuilt it from the original Week 1 Dockerfile (`docker build -t frontend:1.0 .`), then loaded it into minikube successfully.

### 2. `curl` not available inside containers
**Issue:** `kubectl exec ... -- curl ...` failed with `executable file not found in $PATH`.
**Fix:** The `python:3.12-slim` base image deliberately excludes extra tools like `curl` to stay minimal. Used Python's built-in `urllib.request` module instead to make the same HTTP request from inside the pod, avoiding the need to rebuild the image just for a debugging tool.

## Week 3 Outcome

* Wrote raw Kubernetes manifests (Deployment, Service, ConfigMap, Secret) for both microservices.
* Loaded Week 1's locally-built Docker images into the minikube cluster.
* Applied all manifests successfully using `kubectl apply`.
* Verified both Deployments reached the desired replica count (`2/2`) with all pods `Running`.
* Verified internal service-to-service communication using `kubectl exec` and an HTTP request from inside one pod to another, addressed by Service name.
* Configured CPU/memory resource requests and limits on both Deployments.
* Added liveness and readiness probes using the `/health` endpoint built in Week 1.



## DevOps Internship - Week 4

### Project Overview
This week converts Week 3's raw Kubernetes manifests (Deployments, Services, ConfigMap, Secret) into a single reusable Helm chart. Instead of applying six separate YAML files by hand, the entire application is now installed, configured, and upgraded through one Helm release.

### Project Structure
devops-week4/
├── microservices-chart/
│ ├── Chart.yaml
│ ├── values.yaml
│ └── templates/
│ ├── configmap.yaml
│ ├── secret.yaml
│ ├── backend-deployment.yaml
│ ├── backend-service.yaml
│ ├── frontend-deployment.yaml
│ └── frontend-service.yaml
└── upgrade.sh



### Technologies Used
- Helm v4.2.3
- Kubernetes manifests from Week 3, converted into Helm templates
- minikube cluster from Week 2

### Why Helm
Week 3 required applying 6 separate YAML files in a specific order, and any config change meant editing raw YAML directly. Helm packages all of that into one chart with a single `values.yaml` controlling every configurable setting, so the whole app is installed and upgraded as one versioned release instead of six independent objects.

### Chart Structure
- `Chart.yaml` — chart metadata (name, version, appVersion)
- `values.yaml` — every configurable value: image repo/tag/pullPolicy, replica counts, ports, resource requests/limits, probe settings, ConfigMap values, Secret value, and Service type
- `templates/` — the Week 3 manifests, rewritten with Go template placeholders (`{{ .Values.xxx }}`) instead of hardcoded values

  <img width="1920" height="844" alt="image" src="https://github.com/user-attachments/assets/8294fe90-d91d-4aef-87a0-1151b4cb1d98" />


### Setup Instructions

**1. Ensure the Week 2 cluster is running and Week 1 images are loaded**
```bash
minikube start -p devops-week2
minikube image load backend:1.0 -p devops-week2
minikube image load frontend:1.0 -p devops-week2
```

**2. Install the chart**
```bash
cd devops-week4
helm install microservices ./microservices-chart
```

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9cf61897-65fa-44a8-83af-ab4f134793e9" />


**3. Verify the release**
```bash
helm list
kubectl get pods
kubectl get deployments
kubectl get services
```

### Upgrading the Deployment
The included `upgrade.sh` script demonstrates `helm upgrade` end-to-end: it bumps `backend.replicaCount` from 2 to 3 and switches `config.logLevel` to `debug`, then waits for both rollouts to finish and prints the release status and pod list to verify the change.

```bash
chmod +x upgrade.sh
./upgrade.sh
```

Verified: `helm history microservices` shows REVISION 2 (Upgrade complete), and `kubectl get pods` confirmed 3 backend pods running after the upgrade.

### Rolling Back
```bash
helm history microservices
helm rollback microservices 1
```

### Uninstalling
```bash
helm uninstall microservices
```

### Issues Faced & Troubleshooting

**1. Docker Desktop not running**
Issue: `minikube start` failed with `PROVIDER_DOCKER_VERSION_EXIT_1` since the cluster's driver is Docker and Docker Desktop wasn't running in the background.
Fix: Started Docker Desktop on Windows and confirmed WSL2 integration was enabled, then retried `minikube start` successfully.

**2. Helm install failed: resources already existed**
Issue: `helm install` failed with "exists and cannot be imported into the current release" because Week 3's raw `kubectl apply` resources (backend-deployment, frontend-deployment, backend-service, frontend-service, app-config, app-secret) were still present in the cluster from before, and Helm refuses to adopt resources it didn't create.
Fix: Deleted the old Week 3 resources with `kubectl delete`, confirmed the cluster was clean with `kubectl get all`, then reran `helm install` successfully.

### Week 4 Outcome
- Converted all Week 3 raw manifests into Helm chart templates.
- Defined `values.yaml` with configurable image tags, replica counts, resource limits, probe settings, and app config.
- Installed both microservices as a single Helm release (`helm install`), verified 4/4 pods Running.
- Wrote and ran `upgrade.sh`, confirmed via `helm history` (REVISION 2) and `kubectl get pods` (3/3 backend replicas).
- Verified rollback capability is available via `helm rollback`.
- Documented full chart usage and troubleshooting in this README section.

  <img width="1920" height="816" alt="image" src="https://github.com/user-attachments/assets/eb5b6478-16f7-409a-b406-b7431e7a6cc8" />




---

## DevOps Internship - Week 5

### Project Overview
This week installs the Istio service mesh into the Week 2 cluster via Helm, enables automatic sidecar injection for the microservices namespace, and enforces strict mTLS (mutual TLS) so that only traffic passing through the mesh is accepted between the frontend and backend services. Verified by confirming that a pod deliberately excluded from the mesh cannot reach the backend.

### Project Structure
```
devops-week5/
└── peer-authentication.yaml
```

### Technologies Used
- Istio (installed via Helm: `istio-base`, `istiod`)
- Kiali + Prometheus (Istio observability addons)
- minikube cluster from Week 2
- Helm v4.2.3

### Why a Service Mesh
Up to Week 4, any pod inside the cluster could call `backend-service` or `frontend-service` over plain, unauthenticated HTTP — nothing prevented a compromised or unintended pod from reading or calling either service. A service mesh adds a transparent proxy ("sidecar") to every pod that intercepts all network traffic, and can enforce that only encrypted, mutually-authenticated connections between mesh members are allowed — without changing any application code.


<img width="1920" height="1080" alt="Screenshot (1237)" src="https://github.com/user-attachments/assets/c014ad16-a699-4423-99ea-8180f6b90a13" />


### Setup Instructions

**1. Ensure the cluster has enough resources for Istio**

Istio's control plane and per-pod sidecars add real CPU/memory overhead on top of the base cluster, so the cluster was restarted with a higher memory ceiling for this week:
```bash
minikube stop -p devops-week2
minikube start -p devops-week2 --memory=3072mb --cpus=2
```

**2. Install Istio via Helm**
```bash
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
kubectl create namespace istio-system
helm install istio-base istio/base -n istio-system
helm install istiod istio/istiod -n istio-system --wait
```

**3. Enable automatic sidecar injection for the application namespace**
```bash
kubectl label namespace default istio-injection=enabled
kubectl rollout restart deployment backend-deployment
kubectl rollout restart deployment frontend-deployment
```
Labels only apply to newly created pods, so existing Week 3/4 pods were restarted to pick up the sidecar. Verified with:
```bash
kubectl get pods
```
Every pod moved from `1/1` (app container only) to `2/2` (app container + injected Istio sidecar).

**4. Enforce strict mTLS**

`peer-authentication.yaml`:
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: default
  namespace: default
spec:
  mtls:
    mode: STRICT
```
```bash
kubectl apply -f peer-authentication.yaml
```

**5. Install Kiali and Prometheus (mesh visualization)**
```bash
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.22/samples/addons/prometheus.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.22/samples/addons/kiali.yaml
kubectl port-forward svc/kiali -n istio-system 20001:20001
```
Kiali was viewed at `http://localhost:20001`, confirming the mesh's registered apps and services in the `default` namespace.

<img width="1920" height="1080" alt="Screenshot (1243)" src="https://github.com/user-attachments/assets/2faadd95-435b-4432-9bbb-557c497c475d" />


### Verifying mTLS Enforcement

The core requirement of this task: confirm that a pod **without** the Istio sidecar cannot successfully call a backend that requires strict mTLS.

```bash
kubectl run testpod --image=curlimages/curl -n default \
  --labels="sidecar.istio.io/inject=false" \
  -it -- curl -v http://backend-service:5000/health
```

**Result:** the request failed with `curl` exit code **56** (`CURLE_RECV_ERROR` — connection reset by peer), confirmed via `kubectl describe pod testpod`:
```
State: Terminated
Reason: Error
Exit Code: 56
```
The pod itself started and pulled its image successfully three times (confirmed in the pod's Events log), and each attempt failed identically at the network call — isolating the failure specifically to the mTLS-enforced connection, not a pod startup issue.

This confirms: backend's sidecar rejected the plaintext connection from a pod with no Istio-issued certificate, exactly as strict mTLS is designed to do.

<!-- Add testpod failure screenshot here -->

### Before / After Networking Behavior

| | Before (Week 3/4) | After (Week 5) |
|---|---|---|
| Pod-to-pod traffic | Plain HTTP, unauthenticated | Encrypted, mutually authenticated via Istio sidecars |
| Un-injected pod calling backend | Would succeed | Fails (`curl` exit 56 — connection reset) |
| Enforcement point | None — any pod could call any service | `PeerAuthentication` (`mode: STRICT`) at the namespace level |
| Verification method | `kubectl exec` + successful `urllib` request | `kubectl exec` + **expected failure** from a non-mesh pod |

### Issues Faced & Troubleshooting

**1. Registry connectivity warning during minikube start**
Issue: `minikube start` reported `Failing to connect to https://registry.k8s.io/ from inside the minikube container`.
Fix: The cluster started successfully anyway since required images were already cached locally from prior weeks. Flagged as a risk for later steps that needed to pull new images (Istio, Kiali, Prometheus).

**2. Memory allocation errors when starting minikube with more resources**
Issue: `minikube start --memory=4000mb` failed with `RSRC_OVER_ALLOC_MEM`, since the host's WSL2 memory ceiling (set in Week 2's `.wslconfig`) was only ~3916MB.
Fix: Reduced to `--memory=3072mb`, minikube's own suggested fallback, which fit within the existing WSL2 memory limit.

**3. Kiali graph failed to load**
Issue: Kiali loaded, but the traffic graph showed `Cannot load the graph: ... dial tcp: lookup prometheus.istio-system ... no such host`.
Fix: Kiali depends on Prometheus for traffic metrics, which had not been installed. Applying the Prometheus addon resolved this, and the graph subsequently loaded correctly.

**4. `testpod` initially deleted before its failure could be inspected**
Issue: The first verification attempt used `--rm`, which deleted the pod immediately after the command finished, making the actual failure reason unclear (plain "timed out waiting for the condition").
Fix: Re-ran without `--rm` so the pod's terminal state could be inspected with `kubectl describe pod`, revealing the precise `curl` exit code (56) and confirming the failure was a connection reset, not a stuck/pending pod.

<img width="1920" height="1080" alt="Screenshot (1239)" src="https://github.com/user-attachments/assets/53464f30-b86f-4615-a397-50ee8dc3bb5c" />


### Week 5 Outcome
- Installed Istio (`istio-base`, `istiod`) into the Week 2 cluster via Helm.
- Enabled automatic sidecar injection for the `default` namespace and confirmed all application pods moved from `1/1` to `2/2`.
- Applied a `PeerAuthentication` policy enforcing strict mTLS for all traffic in the namespace.
- Verified enforcement by confirming a pod without the sidecar fails to reach `backend-service`, with a specific, reproducible `curl` error (exit code 56, connection reset).
- Installed Prometheus and Kiali to visualize the mesh topology.
- Documented before/after networking behavior and troubleshooting encountered during setup.



  ---

## DevOps Internship - Week 6

### Project Overview
This week installs the Kong API Gateway as the single external entry point into the cluster, routes it to the frontend microservice, and enforces two API-level controls: rate limiting (5 requests/minute) and API key authentication.

### Project Structure
```
devops-week6/
├── frontend-ingress.yaml
├── rate-limit-plugin.yaml
├── key-auth-plugin.yaml
├── api-consumer.yaml
├── frontend-permissive.yaml
└── rate-limit-test.sh
```

### Technologies Used
- Kong API Gateway (installed via Helm)
- Kong Ingress Controller CRDs (KongPlugin, KongConsumer)
- Istio (from Week 5) — required a `PeerAuthentication` adjustment for Kong to reach the mesh
- minikube cluster from Weeks 2-5

### Installing Kong
```bash
helm repo add kong https://charts.konghq.com
helm repo update
kubectl create namespace kong
helm install kong kong/kong -n kong --set ingressController.installCRDs=false
```

Verified with:
```bash
kubectl get pods -n kong
kubectl get svc -n kong
```

Since minikube has no real cloud load balancer, `kong-kong-proxy`'s `EXTERNAL-IP` stays `<pending>`. Local access is via port-forward:
```bash
kubectl port-forward -n kong svc/kong-kong-proxy 8000:80
```

### Routing to the Frontend Service

`frontend-ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend-ingress
  namespace: default
  annotations:
    konghq.com/strip-path: "true"
    konghq.com/plugins: rate-limit-5-per-minute,api-key-auth
spec:
  ingressClassName: kong
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 5001
```

### Resolving a conflict with Week 5's strict mTLS

Applying the Ingress initially produced `502 Bad Gateway`. Since Kong runs outside the Istio mesh (no sidecar), its plain HTTP requests were being rejected by frontend's sidecar, which was enforcing the namespace-wide `STRICT` mTLS policy from Week 5.

Fix — relax mTLS specifically for the frontend workload, since it is the legitimate external entry point, while backend remains fully `STRICT`:

`frontend-permissive.yaml`:
```yaml
apiVersion: security.istio.io/v1
kind: PeerAuthentication
metadata:
  name: frontend-permissive
  namespace: default
spec:
  selector:
    matchLabels:
      app: frontend
  mtls:
    mode: PERMISSIVE
```
```bash
kubectl apply -f frontend-permissive.yaml
```

After this, `curl http://localhost:8000/health` returned `200 OK`, routed correctly through Kong → Istio sidecar → frontend.

### Rate Limiting (5 requests/minute)

`rate-limit-plugin.yaml`:
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: rate-limit-5-per-minute
  namespace: default
config:
  minute: 5
  policy: local
plugin: rate-limiting
```

`rate-limit-test.sh`:
```bash
#!/bin/bash

echo "Sending 7 rapid requests to test rate limiting (limit: 5/minute)..."
echo ""

for i in {1..7}; do
  status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
  echo "Request $i: $status"
  if [ "$status" == "429" ]; then
    echo "  --> Rate limit triggered as expected"
  fi
done
```

**Result:**
```
Request 1: 200
Request 2: 200
Request 3: 200
Request 4: 200
Request 5: 200
Request 6: 429
Request 7: 429
```
Requests 6 and 7 were correctly rejected once the 5/minute limit was exceeded.

<img width="1920" height="1080" alt="Screenshot (1251)" src="https://github.com/user-attachments/assets/37f8a257-52a5-4d4d-89c8-a430f1a0d858" />


### API Key Authentication

`key-auth-plugin.yaml`:
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongPlugin
metadata:
  name: api-key-auth
  namespace: default
plugin: key-auth
```

`api-consumer.yaml`:
```yaml
apiVersion: configuration.konghq.com/v1
kind: KongConsumer
metadata:
  name: test-consumer
  namespace: default
username: test-consumer
credentials:
  - test-api-key-secret
---
apiVersion: v1
kind: Secret
metadata:
  name: test-api-key-secret
  namespace: default
  labels:
    konghq.com/credential: key-auth
stringData:
  key: my-secret-api-key-123
type: Opaque
```

**Test without a key:**
```bash
curl -i http://localhost:8000/health
```
```
HTTP/1.1 401 Unauthorized
{"message":"No API key found in request"}
```

**Test with the valid key:**
```bash
curl -i http://localhost:8000/health -H "apikey: my-secret-api-key-123"
```
```
HTTP/1.1 200 OK
X-RateLimit-Limit-Minute: 5
RateLimit-Remaining: 4
{"status":"good idea"}
```

Both rate limiting and API key auth headers are present simultaneously, confirming both plugins are active together on the same route.

<img width="1920" height="1080" alt="Screenshot (1253)" src="https://github.com/user-attachments/assets/a45289c4-d47d-4587-b1d6-2c91d8c5f951" />


### Issues Faced & Troubleshooting

**1. `502 Bad Gateway` after applying the Ingress**
Issue: Kong could reach the cluster but frontend's Istio sidecar rejected the plain-text request, due to Week 5's namespace-wide strict mTLS policy.
Fix: Added a `PeerAuthentication` override in `PERMISSIVE` mode scoped only to `app: frontend`, allowing the gateway's plain HTTP traffic in while keeping backend-to-backend traffic under strict mTLS.

**2. `minikube start` failed with `DRV_UNSUPPORTED_OS: driver ''`**
Issue: After multiple stop/start cycles during the week, minikube's stored driver setting for the profile became blank.
Fix: Explicitly specified the driver: `minikube start -p devops-week2 --driver=docker`.

**3. Stale kubeconfig after cluster restart**
Issue: `kubectl apply` failed with a connection refused error on a stale local port, the same category of issue encountered in Week 2.
Fix: `minikube update-context -p devops-week2` to refresh the config with the container's current port mapping.

**4. API key initially rejected as invalid, not missing**
Issue: A request with the API key header returned `401 Unauthorized` (as opposed to "No API key found"), indicating Kong received the key but didn't recognize it as valid.
Fix: The credential Secret required a `konghq.com/credential: key-auth` label for Kong's ingress controller to recognize it as a valid key-auth credential — a `kongCredType` field alone inside `stringData` was not sufficient. Recreating the Secret with the correct label resolved it.

**5. Memory pressure before installing Kong**
Issue: The cluster was already running Istio's control plane and sidecar-injected pods from Week 5, leaving very little free memory (as low as ~58Mi) to safely add Kong's own components.
Fix: Removed the Kiali/Prometheus addons (no longer needed after Week 5's documentation was complete) and scaled backend/frontend down from 3/2 replicas to 1/1 each, freeing enough memory to install and run Kong reliably.

<img width="1920" height="1080" alt="Screenshot (1252)" src="https://github.com/user-attachments/assets/8b2e8076-a166-45d6-ae57-aef25ae7bfda" />


### Week 6 Outcome
- Installed Kong API Gateway via Helm as the cluster's single external ingress point.
- Configured an Ingress resource routing external traffic to the frontend microservice.
- Diagnosed and resolved a real conflict between Kong and Week 5's strict mTLS policy, without weakening backend's security posture.
- Implemented and verified a rate-limiting plugin (5 requests/minute), confirmed via a written test script producing `429` responses on request 6 and 7.
- Implemented API key authentication on the route, verified both the unauthenticated-rejection and valid-key-success paths.
- Documented all real issues encountered and their root causes and fixes.



  ---

# DevOps Internship - Week 7

## Overview
This week focused on setting up Continuous Integration (CI) for the microservices repository using GitHub Actions. The goal was to automate linting and testing on every push, and automatically build and push Docker images to a container registry whenever changes are merged to `main`, tagged with the Git commit SHA for traceability.

## Project Structure
```
.github/
  workflows/
    ci-cd.yml
backend/
  test_app.py
  requirements.txt (updated)
frontend/
  test_app.py
  requirements.txt (updated)
```

## Technologies Used
- **GitHub Actions** — CI/CD pipeline orchestration
- **GitHub Container Registry (ghcr.io)** — chosen as the image registry for simplicity, since it uses the built-in `GITHUB_TOKEN` with no separate account or credentials needed
- **flake8** — linting
- **pytest** — unit testing (Flask test client)
- **docker/build-push-action** and **docker/login-action** — official GitHub Actions for building and pushing Docker images

## Workflow File Explained (`.github/workflows/ci-cd.yml`)
The pipeline runs on every `push` and `pull_request` to `main`, and consists of two jobs:

**`lint-and-test`**
- Runs as a matrix across `backend` and `frontend`, so both services are tested independently and in parallel
- Installs dependencies from each service's `requirements.txt`
- Runs `flake8` restricted to `--select=E9,F63,F7,F82` (syntax errors and undefined names only) — deliberately lenient since the codebase had never been linted before this week
- Runs `pytest -v` against `test_app.py` in each service

**`build-and-push`**
- Depends on `lint-and-test` passing (`needs: lint-and-test`)
- Only runs on an actual push to `main` (`if: github.ref == 'refs/heads/main' && github.event_name == 'push'`) — so pull requests only run linting/tests, not image builds
- Logs into `ghcr.io` using `docker/login-action`, authenticated with `github.actor` and the built-in `secrets.GITHUB_TOKEN`
- Gets the short Git commit SHA via `git rev-parse --short HEAD`
- Builds and pushes each service's image tagged both `:latest` and `:<short-sha>` — e.g. `ghcr.io/zubair378/backend:2244bd9`
- Repository owner is explicitly lowercased in a separate step before use in the image tag, since `ghcr.io` requires lowercase image names and the GitHub username (`Zubair378`) has a capital letter

- <img width="1786" height="620" alt="image" src="https://github.com/user-attachments/assets/76c82a91-b14f-4578-85b1-008a477b853c" />


## Verification
- Created `backend/test_app.py` and `frontend/test_app.py`, each testing `/health` (status 200) and `/info` (status 200 + JSON contains a `service` key) — deliberately checking structure rather than exact response text, since frontend's `/health` intentionally returns `{"status": "good idea"}` instead of `"ok"`
- Pushed to `main` and confirmed all four jobs completed successfully: `lint-and-test (backend)`, `lint-and-test (frontend)`, `build-and-push (backend)`, `build-and-push (frontend)` — total run time 51s
- Confirmed both `backend` and `frontend` packages appear under GitHub → Packages, published under `Zubair378/Devops-internship`, confirming the images were successfully built and pushed to `ghcr.io`

## Issues Faced & Troubleshooting
- **Stale cached PAT:** the old Personal Access Token stored via `credential.helper store` had expired, causing `git push` to fail with "Invalid username or token." Fixed by clearing `~/.git-credentials` and generating a fresh token.
- **Missing `workflow` scope:** the first new token was generated with only the `repo` scope, which GitHub rejects for any push that creates or modifies files inside `.github/workflows/` (error: `refusing to allow a Personal Access Token to create or update workflow ... without workflow scope`). Fixed by regenerating the token with both `repo` and `workflow` scopes checked.
- **GITHUB_TOKEN permissions:** by default the built-in `GITHUB_TOKEN` used inside the workflow has read-only permissions, which would have caused the `build-and-push` job to fail when pushing to `ghcr.io`. Fixed proactively by enabling "Read and write permissions" under repo Settings → Actions → General → Workflow permissions, before the first push.
- **Case sensitivity in image names:** `ghcr.io` requires lowercase repository/image names, but the GitHub username `Zubair378` contains a capital letter. Solved by adding a dedicated step in the workflow to lowercase `github.repository_owner` before using it in the image tag, avoiding a build failure that would otherwise have occurred on the first run.


<img width="1689" height="810" alt="image" src="https://github.com/user-attachments/assets/a6b3ef02-5028-4076-a831-7379494150eb" />

## Outcome Checklist
- [x] GitHub Actions workflow set up for the microservices repository
- [x] CI pipeline runs linting and basic unit tests on every push
- [x] CI pipeline builds Docker images and pushes them to a container registry (ghcr.io) on merges to `main`
- [x] Image tagging implemented using Git commit SHAs
- [x] Pipeline verified running successfully, with both `backend` and `frontend` images confirmed present in the registry
