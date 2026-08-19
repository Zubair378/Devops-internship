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


Issues Faced & Troubleshooting

Several real issues came up during this task. Documenting them here since diagnosing and resolving them was part of the actual work.

1. WSL2 memory too low for minikube's default request

Issue: minikube start --dry-run warned that the default memory request (3072MiB) didn't leave room for system overhead, on a host machine with only 8GB total RAM. Fix: Adjusted WSL2's own memory allocation via .wslconfig (memory=4GB), and explicitly set a smaller, more conservative memory = "2200mb" in the Terraform config instead of relying on the provider's default.

2. .wslconfig changes not applying immediately

Issue: After editing .wslconfig, free -h inside Ubuntu still showed the old memory limit. Fix: A plain wsl command only re-enters an already-running instance — it does not reload config. wsl --shutdown (from PowerShell, not from inside Ubuntu) is required to fully stop WSL2 before the new .wslconfig settings take effect on the next launch.

3. First terraform apply appeared to freeze

Issue: During cluster creation, Terraform's "Still creating..." timer appeared to stall (and briefly showed corrupted/negative timestamps due to a terminal rendering glitch). Fix: Confirmed real progress was happening by checking docker ps and docker stats in a separate terminal — the container was actively being created and using CPU. The apply eventually completed successfully after ~12 minutes, slower than usual due to the host machine's limited resources.

4. kubectl cluster-info failed with "connection refused" after a machine restart

Issue: After restarting the computer, Docker Desktop (and the minikube container) stopped. On restart, the container was reassigned a new local port, but kubectl was still configured to use the old, stale port. Fix: Ran minikube update-context -p devops-week2 to refresh the kubeconfig with the container's current address.

5. Orphaned minikube profile created accidentally

Issue: Running minikube stop without specifying -p devops-week2 caused minikube to default to looking for (and starting to create) a separate cluster literally named minikube — unrelated to the Terraform-managed cluster. This was caught and cancelled before it fully completed, but left behind an incomplete, broken profile. Fix: Removed the stray profile with minikube delete -p minikube, then explicitly restarted the correct cluster with minikube start -p devops-week2. This experience directly motivated hardening recreate-cluster.sh to also clean up orphaned profiles, containers, and dead kubeconfig contexts before running Terraform — since Terraform's own state has no visibility into resources created or broken outside of it.

Key takeaway: local Kubernetes tooling (minikube) can drift out of sync with Terraform's state, especially across restarts or manual command usage. Always target the specific cluster profile explicitly (-p devops-week2), and treat terraform destroy/apply as necessary but not always sufficient for a truly clean reset — hence the additional cleanup steps in the recreate script.

## Week 2 Outcome

* Wrote Terraform configuration to provision a local Kubernetes cluster using the minikube provider.
* Applied the configuration and verified cluster health using `kubectl cluster-info`.
* Documented the Terraform setup process and variables (this section).
* Confirmed `kubectl` context was automatically configured and connected to the new cluster.
* Diagnosed and resolved a real orphaned-profile/state-drift issue encountered during development.
* Wrote and tested an idempotent destroy/recreate script for quickly resetting the cluster during testing.
DevOps Internship - Week 4
Project Overview
This week converts Week 3's raw Kubernetes manifests (Deployments, Services, ConfigMap, Secret) into a single reusable Helm chart. Instead of applying six separate YAML files by hand, the entire application is now installed, configured, and upgraded through one Helm release.

Project Structure
devops-week4/
├── microservices-chart/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── configmap.yaml
│       ├── secret.yaml
│       ├── backend-deployment.yaml
│       ├── backend-service.yaml
│       ├── frontend-deployment.yaml
│       └── frontend-service.yaml
└── upgrade.sh

Technologies Used
Helm v4.2.3
Kubernetes manifests from Week 3, converted into Helm templates
minikube cluster from Week 2

Why Helm
Week 3 required applying 6 separate YAML files in a specific order, and any config change meant editing raw YAML directly. Helm packages all of that into one chart with a single values.yaml controlling every configurable setting, so the whole app is installed and upgraded as one versioned release instead of six independent objects.

Chart Structure
Chart.yaml — chart metadata (name, version, appVersion).
values.yaml — every configurable value: image repo/tag/pullPolicy, replica counts, ports, resource requests/limits, probe settings, ConfigMap values, Secret value, and Service type.
templates/ — the Week 3 manifests, rewritten with Go template placeholders ({{ .Values.xxx }}) instead of hardcoded values.

Setup Instructions

1. Ensure the Week 2 cluster is running and Week 1 images are loaded
minikube start -p devops-week2
minikube image load backend:1.0 -p devops-week2
minikube image load frontend:1.0 -p devops-week2

2. Install the chart
cd devops-week4
helm install microservices ./microservices-chart

3. Verify the release
helm list
kubectl get pods
kubectl get deployments
kubectl get services

Upgrading the Deployment
The included upgrade.sh script demonstrates helm upgrade end-to-end: it bumps backend.replicaCount from 2 to 3 and switches config.logLevel to debug, then waits for both rollouts to finish and prints the release status and pod list to verify the change.

chmod +x upgrade.sh
./upgrade.sh

Verified: helm history microservices shows REVISION 2 (Upgrade complete), and kubectl get pods confirmed 3 backend pods running after the upgrade.

Rolling Back
helm history microservices
helm rollback microservices 1

Uninstalling
helm uninstall microservices

Issues Faced & Troubleshooting
1. Docker Desktop not running
Issue: minikube start failed with PROVIDER_DOCKER_VERSION_EXIT_1 since the cluster's driver is Docker and Docker Desktop wasn't running in the background.
Fix: Started Docker Desktop on Windows and confirmed WSL2 integration was enabled, then retried minikube start successfully.

2. Helm install failed: resources already existed
Issue: helm install failed with "exists and cannot be imported into the current release" because Week 3's raw kubectl apply resources (backend-deployment, frontend-deployment, backend-service, frontend-service, app-config, app-secret) were still present in the cluster from before, and Helm refuses to adopt resources it didn't create.
Fix: Deleted the old Week 3 resources with kubectl delete, confirmed the cluster was clean with kubectl get all, then reran helm install successfully.

Week 4 Outcome
Converted all Week 3 raw manifests into Helm chart templates.
Defined values.yaml with configurable image tags, replica counts, resource limits, probe settings, and app config.
Installed both microservices as a single Helm release (helm install), verified 4/4 pods Running.
Wrote and ran upgrade.sh, confirmed via helm history (REVISION 2) and kubectl get pods (3/3 backend replicas).
Verified rollback capability is available via helm rollback.
Documented full chart usage and troubleshooting in this README section.
