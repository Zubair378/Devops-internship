#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROFILE="${PROFILE:-devops-week2}"
export HELM_KUBECONTEXT="$PROFILE"
for tool in docker minikube kubectl helm python3 openssl; do
  command -v "$tool" >/dev/null || { echo "Missing prerequisite: $tool"; exit 1; }
done
docker info >/dev/null
if minikube status -p "$PROFILE" >/dev/null 2>&1; then
  minikube update-context -p "$PROFILE"
elif minikube profile list -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if any(p["Name"] == sys.argv[1] for p in d.get("valid", [])) else 1)' "$PROFILE"; then
  minikube start -p "$PROFILE" --driver=docker
else
  minikube start -p "$PROFILE" --driver=docker --memory=4096 --cpus=3 --kubernetes-version=v1.35.1
fi
docker update --cpus=3 --memory=4g --memory-swap=6g "$PROFILE"
python3 "$ROOT/scripts/repair_registry_dns.py" --profile "$PROFILE"
k() { kubectl --context "$PROFILE" "$@"; }
k wait --for=condition=Ready node --all --timeout=180s
helm repo add argo https://argoproj.github.io/argo-helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add kong https://charts.konghq.com
helm repo add istio https://istio-release.storage.googleapis.com/charts
helm repo update
if helm history istio-base --namespace istio-system -o json | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if any(r["status"] == "deployed" and r["chart"] == "base-1.30.5" for r in d) else 1)'; then
  echo "Pinned Istio base chart already has a deployed release; skipping its unchanged CRDs."
else
  helm upgrade --install istio-base istio/base --version 1.30.5 -n istio-system --create-namespace --wait --timeout 10m
fi
helm upgrade --install istiod istio/istiod --version 1.30.5 -n istio-system -f "$ROOT/istio-values.yaml" --wait --timeout 10m
k label namespace default istio-injection=enabled --overwrite
k create namespace argo-rollouts --dry-run=client -o yaml | k apply -f -
k apply --server-side -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/download/v1.10.0/install.yaml
k -n argo-rollouts patch deployment argo-rollouts --patch-file "$ROOT/rollouts-patch.yaml"
k -n argo-rollouts rollout status deployment/argo-rollouts --timeout=180s
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 92.3.0 -n monitoring --create-namespace -f "$ROOT/monitoring-values.yaml" --wait --timeout 15m
helm upgrade --install kong kong/kong --version 3.4.1 -n kong --create-namespace -f "$ROOT/kong-values.yaml" --wait --timeout 10m
helm upgrade --install argocd argo/argo-cd --version 10.10.2 -n argocd --create-namespace -f "$ROOT/argocd-values.yaml" --wait --timeout 10m
if ! k -n default get secret week12-api-key >/dev/null 2>&1; then
  python3 -c 'import json,secrets; print(json.dumps({"apiVersion":"v1","kind":"Secret","metadata":{"name":"week12-api-key","namespace":"default","labels":{"konghq.com/credential":"key-auth"}},"type":"Opaque","stringData":{"key":secrets.token_hex(24)}}))' | k apply -f -
fi
if [[ "${1:-}" != "--infra-only" ]]; then
  if grep -q 'tag: bootstrap' "$ROOT/chart/values.yaml"; then
    echo "Push the application code and let CI publish images before applying the Application."
    exit 1
  fi
  k apply -f "$ROOT/application.yaml"
fi
echo "Infrastructure ready for context $PROFILE."
