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
