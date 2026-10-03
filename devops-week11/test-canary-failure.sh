#!/usr/bin/env bash
set -euo pipefail

echo "=========================================================="
echo "Test 2: Failed Canary Deployment & Automated Rollback Trigger"
echo "=========================================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[Step 1] Ensuring stable baseline is running..."
kubectl apply -f "${SCRIPT_DIR}/services.yaml"
kubectl apply -f "${SCRIPT_DIR}/analysis-template.yaml"
kubectl apply -f "${SCRIPT_DIR}/rollout.yaml"
kubectl argo rollouts status rollout backend-rollout --timeout 60s || true

echo ""
echo "[Step 2] Applying Faulty Canary Deployment (canary-fail-simulation)..."
kubectl apply -f "${SCRIPT_DIR}/rollout-failure-test.yaml"

echo ""
echo "[Step 3] Triggering update to faulty-v3..."
kubectl argo rollouts set image backend-rollout backend=backend:faulty-v3

echo ""
echo "[Step 4] Monitoring Analysis failure and Automated Rollback..."
sleep 15

echo ""
echo "AnalysisRun Results:"
kubectl get analysisruns -o wide

echo ""
echo "Rollout Status (verifying RolloutAborted / Degraded state):"
kubectl argo rollouts get rollout backend-rollout

echo ""
echo "Verifying traffic returned 100% to stable revision:"
kubectl get pods -l app=backend -o wide
echo "=========================================================="
