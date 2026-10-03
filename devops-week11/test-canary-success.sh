#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "Test 1: Successful Canary Deployment (10% -> 30% -> 60% -> 100%)"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[Step 1] Applying Services and AnalysisTemplate..."
kubectl apply -f "${SCRIPT_DIR}/services.yaml"
kubectl apply -f "${SCRIPT_DIR}/analysis-template.yaml"

echo "[Step 2] Applying Base Rollout (backend:1.0)..."
kubectl apply -f "${SCRIPT_DIR}/rollout.yaml"

echo "Waiting for baseline rollout to be fully healthy..."
kubectl argo rollouts status rollout backend-rollout --timeout 90s

echo ""
echo "[Step 3] Triggering Canary update to backend:2.0..."
kubectl argo rollouts set image backend-rollout backend=backend:2.0

echo ""
echo "[Step 4] Monitoring Canary progression in real-time..."
kubectl argo rollouts get rollout backend-rollout --watch &
WATCH_PID=$!

sleep 30
kill ${WATCH_PID} 2>/dev/null || true

echo ""
echo "Current Rollout Status:"
kubectl argo rollouts get rollout backend-rollout
echo ""
echo "AnalysisRuns recorded:"
kubectl get analysisruns -l app.kubernetes.io/part-of=devops-week11 || kubectl get analysisruns
echo "=========================================================="
