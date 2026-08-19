#!/bin/bash
set -e

RELEASE_NAME="microservices"
CHART_PATH="./microservices-chart"

echo "Step 1: Upgrading release '$RELEASE_NAME'..."
helm upgrade "$RELEASE_NAME" "$CHART_PATH" \
  --set backend.replicaCount=3 \
  --set config.logLevel=debug

echo "Step 2: Waiting for backend rollout to complete..."
kubectl rollout status deployment/backend-deployment

echo "Step 3: Waiting for frontend rollout to complete..."
kubectl rollout status deployment/frontend-deployment

echo "Step 4: Current release status..."
helm status "$RELEASE_NAME"

echo "Step 5: Pods after upgrade..."
kubectl get pods

echo "Done. Upgrade applied and verified."
