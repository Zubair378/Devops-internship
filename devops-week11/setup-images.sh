#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "Preparing Backend Images for Week 11 Canary Deployments"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../backend" && pwd)"

# 1. Build baseline image backend:1.0
echo "[1/3] Building baseline image: backend:1.0 ..."
if docker image inspect backend:1.0 >/dev/null 2>&1; then
    echo "Image backend:1.0 already exists."
else
    docker build -t backend:1.0 "${BACKEND_DIR}"
fi

# 2. Tag backend:2.0 (healthy canary release)
echo "[2/3] Tagging healthy canary release: backend:2.0 ..."
docker tag backend:1.0 backend:2.0

# 3. Tag backend:faulty-v3 (for failure/rollback testing)
echo "[3/3] Tagging failure test release: backend:faulty-v3 ..."
docker tag backend:1.0 backend:faulty-v3

# 4. If minikube is running, load images into minikube cache
if minikube status -p devops-week2 >/dev/null 2>&1; then
    echo "Loading images into Minikube cluster 'devops-week2'..."
    minikube image load backend:1.0 -p devops-week2 || true
    minikube image load backend:2.0 -p devops-week2 || true
    minikube image load backend:faulty-v3 -p devops-week2 || true
fi

echo "=========================================================="
echo "All images prepared successfully!"
docker images | grep backend || true
echo "=========================================================="
