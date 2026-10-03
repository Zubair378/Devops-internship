#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "Installing Argo Rollouts Controller & Kubectl Plugin"
echo "=========================================================="

# 1. Create argo-rollouts namespace
kubectl create namespace argo-rollouts --dry-run=client -o yaml | kubectl apply -f -

# 2. Install Argo Rollouts CRDs & Controller
echo "[1/3] Applying Argo Rollouts manifests..."
kubectl apply --server-side -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

# 3. Wait for controller deployment to be ready
echo "[2/3] Waiting for Argo Rollouts controller to become ready..."
kubectl rollout status deployment/argo-rollouts -n argo-rollouts --timeout=120s

# 4. Install kubectl-argo-rollouts plugin if not present
echo "[3/3] Checking kubectl-argo-rollouts CLI plugin..."
if ! command -v kubectl-argo-rollouts &> /dev/null; then
    ARCH="amd64"
    if [ "$(uname -m)" = "aarch64" ]; then
        ARCH="arm64"
    fi
    curl -sSL -o /tmp/kubectl-argo-rollouts-linux-${ARCH} "https://github.com/argoproj/argo-rollouts/releases/latest/download/kubectl-argo-rollouts-linux-${ARCH}"
    chmod +x /tmp/kubectl-argo-rollouts-linux-${ARCH}
    sudo mv /tmp/kubectl-argo-rollouts-linux-${ARCH} /usr/local/bin/kubectl-argo-rollouts || mv /tmp/kubectl-argo-rollouts-linux-${ARCH} ~/.local/bin/kubectl-argo-rollouts
    echo "kubectl-argo-rollouts plugin installed successfully!"
else
    echo "kubectl-argo-rollouts is already installed."
fi

echo "=========================================================="
echo "Verification:"
kubectl get pods -n argo-rollouts
kubectl argo rollouts version
echo "=========================================================="
