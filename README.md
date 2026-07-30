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

## Week 2 Outcome

* Wrote Terraform configuration to provision a local Kubernetes cluster using the minikube provider.
* Applied the configuration and verified cluster health using `kubectl cluster-info`.
* Documented the Terraform setup process and variables (this section).
* Confirmed `kubectl` context was automatically configured and connected to the new cluster.
* Diagnosed and resolved a real orphaned-profile/state-drift issue encountered during development.
* Wrote and tested an idempotent destroy/recreate script for quickly resetting the cluster during testing.
