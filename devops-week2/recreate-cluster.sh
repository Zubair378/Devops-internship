#!/bin/bash

# recreate-cluster.sh
# Destroys and recreates the local minikube Kubernetes cluster using Terraform.
# Useful for quickly resetting the environment during testing.

set -e

echo "Destroying existing cluster (if any)..."
terraform destroy -auto-approve

echo "Creating a fresh cluster..."
terraform apply -auto-approve

echo "Verifying cluster health..."
kubectl cluster-info

echo "Done. Cluster has been recreated successfully."

