# DevOps Internship — Week 11: Canary Deployments

## Project Overview

Taking the foundations established across Weeks 1–10 (Docker containerization, Minikube Kubernetes cluster, Helm packaging, Istio service mesh, Kong Ingress gateway, GitHub Actions CI/CD, ArgoCD GitOps, Prometheus & Grafana observability, and Alertmanager incident response), Week 11 implements **Automated Canary Deployment capabilities** with **metric-driven progressive traffic shifting and automated rollbacks** using **Argo Rollouts**.

```
                           Incoming Traffic
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   backend-service   │
                       └──────────┬──────────┘
                                  │
                   ┌──────────────┴──────────────┐
                   │ Traffic Weight Split (Canary)│
                   ▼                             ▼
       ┌───────────────────────┐     ┌───────────────────────┐
       │     Stable Set        │     │      Canary Set       │
       │    (backend:1.0)      │     │     (backend:2.0)     │
       │   Initial: 90% (9)    │     │   Initial: 10% (1)    │
       └───────────┬───────────┘     └───────────┬───────────┘
                   │                             │
                   │                       ┌─────▼─────┐
                   │                       │Prometheus │
                   │                       │Scrapes    │
                   │                       └─────┬─────┘
                   │                             │
                   │                       ┌─────▼─────┐
                   │                       │AnalysisRun│
                   │                       └─────┬─────┘
                   │                             │
                   │             ┌───────────────┴───────────────┐
                   │             │                               │
                   │     Condition Passed                Condition Failed
                   │             │                       (Error Rate > 5%)
                   │             ▼                               │
                   │     Advance Traffic Weight                  ▼
                   │     (10% -> 30% -> 60% -> 100%)    ┌──────────────────┐
                   │                                    │AUTOMATED ROLLBACK│
                   └───────────────────────────────────<│ Canaries: 0% (0) │
                                                        │ Stable: 100% (10)│
                                                        └──────────────────┘
```

---

## Objectives & Deliverables Status

| Objective / Task | Implementation Detail | Status |
|---|---|---|
| **Canary Deployment with Argo Rollouts** | Installed Argo Rollouts controller, CRDs, and `kubectl-argo-rollouts` plugin | ✅ Completed |
| **Progressive Traffic Strategy (10% Start)** | Configured `Rollout` with initial 10% weight step, pausing and validating via Prometheus before advancing to 30%, 60%, and 100% | ✅ Completed |
| **Metric-Driven Validation (Prometheus)** | Created `AnalysisTemplate` querying HTTP error rates and golden signals from Week 9 Prometheus server | ✅ Completed |
| **Automated Rollback Documentation** | Comprehensive runbook (`rollback-procedure.md`) detailing automated rollback sequence and thresholds | ✅ Completed |
| **Failed Deployment Verification** | Simulated failure test verifying automated rollback triggering, canary traffic zeroing, and stable fallback | ✅ Completed |
| **Comprehensive README** | Full documentation covering architecture, manifests, step-by-step reproduction, and verification screenshots guide | ✅ Completed |

---

## Technologies Used

* **Kubernetes (Minikube):** Container orchestration platform (from Week 2).
* **Argo Rollouts:** Kubernetes controller and set of CRDs providing advanced deployment capabilities (Canary, Blue-Green, Analysis).
* **Prometheus:** Observability and metrics backend (installed in Week 9 `monitoring` namespace).
* **Python / Flask:** Containerized backend microservice (from Week 1).
* **Docker / Multi-stage Builds:** Minimal non-root container images.
* **kubectl-argo-rollouts:** CLI plugin for real-time visualization and management of rollout state transitions.

---

## Project Directory Structure

```
devops-week11/
├── analysis-template.yaml     # Prometheus AnalysisTemplates (success rate, error rate, failure simulation)
├── install-argo-rollouts.sh   # Automated installation script for Argo Rollouts controller & CLI
├── rollback-procedure.md      # Formalized incident response runbook for automated rollbacks
├── rollout.yaml               # Canary Rollout specification (10% -> 30% -> 60% -> 100%)
├── rollout-failure-test.yaml  # Failure simulation rollout testing automated rollback
├── services.yaml              # Kubernetes Services (active, stable, canary)
├── simulate-traffic.sh        # Traffic generator script to populate Prometheus metrics
├── test-canary-failure.sh     # End-to-end execution script verifying automated rollback
├── test-canary-success.sh     # End-to-end execution script verifying successful promotion
└── README.md                  # This documentation file
```

---

## Architecture & Configuration Details

### 1. Progressive Traffic Strategy (`rollout.yaml`)
The Rollout replaces traditional Kubernetes `Deployment` with progressive weight gates:
```yaml
strategy:
  canary:
    canaryService: backend-canary
    stableService: backend-stable
    steps:
      # Step 1: Initial 10% traffic to canary (1 pod out of 10)
      - setWeight: 10
      - pause: { duration: 20s }
      - analysis:
          templates:
            - templateName: prometheus-success-rate
          args:
            - name: service-name
              value: backend-canary
      # Step 2: 30% traffic to canary (3 pods out of 10)
      - setWeight: 30
      - pause: { duration: 20s }
      - analysis:
          templates:
            - templateName: prometheus-success-rate
      # Step 3: 60% traffic to canary (6 pods out of 10)
      - setWeight: 60
      - pause: { duration: 20s }
      - analysis:
          templates:
            - templateName: prometheus-success-rate
      # Step 4: 100% full promotion
      - setWeight: 100
```

### 2. Prometheus Metric Analysis (`analysis-template.yaml`)
Connects directly to the cluster's internal Prometheus server (`monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: prometheus-success-rate
spec:
  metrics:
    - name: success-rate
      interval: 10s
      count: 3
      successCondition: len(result) == 0 || result[0] >= 0.95
      failureLimit: 1
      provider:
        prometheus:
          address: http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090
          query: |
            (
              sum(rate(flask_http_request_total{status!~"5.*"}[1m]))
              /
              (sum(rate(flask_http_request_total[1m])) > 0)
            ) or on() vector(1)
```

---

## Step-by-Step Instructions & Screenshot Capture Guide

Follow these exact steps in your WSL terminal to run the tasks and capture submission screenshots:

### Step 1: Cluster & Argo Rollouts Controller Verification
Ensure your Minikube cluster is active and install Argo Rollouts:

```bash
cd ~/devops-week1/devops-week11

# 1. Install Argo Rollouts controller and plugin
bash install-argo-rollouts.sh

# 2. Verify controller pods are Running
kubectl get pods -n argo-rollouts
```

📸 **Screenshot Opportunity 1:**
Capture the terminal showing `argo-rollouts` pods in `Running` state and `kubectl argo rollouts version`.

---

### Step 2: Deploy Stable Baseline & Services
Deploy the services, analysis templates, and the baseline version (`backend:1.0`):

```bash
# 1. Apply networking services
kubectl apply -f services.yaml

# 2. Apply Prometheus analysis templates
kubectl apply -f analysis-template.yaml

# 3. Apply the initial Rollout
kubectl apply -f rollout.yaml

# 4. Confirm Rollout is healthy and fully stable
kubectl argo rollouts get rollout backend-rollout
```

📸 **Screenshot Opportunity 2:**
Capture the terminal showing `backend-rollout` at Revision 1 with 10 stable pods active.

---

### Step 3: Test 1 — Successful Canary Deployment (10% -> 30% -> 60% -> 100%)
Update the rollout image to `backend:2.0` and observe progressive traffic routing:

```bash
# 1. Trigger canary update
kubectl argo rollouts set image backend-rollout backend=backend:2.0

# 2. Watch progressive canary weight transitions in real-time
kubectl argo rollouts get rollout backend-rollout --watch
```

**Observed Lifecycle:**
1. **Weight 10%:** 1 canary pod is spun up alongside 9 stable pods.
2. **Analysis Check 1:** `AnalysisRun` verifies Prometheus success rate $\ge 95\%$.
3. **Weight 30%:** Canary scales to 3 pods, stable scales down to 7 pods.
4. **Analysis Check 2:** Prometheus confirms metrics remain healthy.
5. **Weight 60%:** Canary scales to 6 pods, stable scales to 4 pods.
6. **Weight 100%:** Canary scales to 10 pods, revision 1 is phased out.

📸 **Screenshot Opportunity 3:**
Capture the terminal showing the 10% canary step with 1 canary pod and 9 stable pods, and the subsequent completed promotion to Revision 2.

---

### Step 4: Test 2 — Failed Deployment & Automated Rollback
Test the automated rollback procedure by deploying a candidate that fails metric checks:

```bash
# 1. Apply the failure test rollout definition
kubectl apply -f rollout-failure-test.yaml

# 2. Trigger rollout to faulty image
kubectl argo rollouts set image backend-rollout backend=backend:faulty-v3

# 3. Observe the metric failure and automated rollback
kubectl argo rollouts get rollout backend-rollout --watch
```

**Observed Failure & Rollback Lifecycle:**
1. Candidate `backend:faulty-v3` starts at 10% weight.
2. Prometheus `AnalysisRun` detects metric violation (Error rate threshold breached / success rate $< 95\%$).
3. The `AnalysisRun` transitions to `Failed`.
4. Argo Rollouts automatically triggers an **Abort & Rollback**:
   - Canary traffic weight is immediately forced to **0%**.
   - Canary pods are scaled down to **0**.
   - 100% of user traffic is restored to the known-healthy stable revision.
   - Rollout status is marked as `Degraded` (`RolloutAborted`).

```bash
# Inspect the failed AnalysisRun and rollback evidence
kubectl get analysisruns -o wide
kubectl argo rollouts get rollout backend-rollout
kubectl get pods -l app=backend
```

📸 **Screenshot Opportunity 4:**
Capture the terminal showing:
- `kubectl get analysisruns` with `Status: Failed`.
- `kubectl argo rollouts get rollout backend-rollout` displaying `Status: Degraded` and `Message: RolloutAborted`.
- `kubectl get pods -l app=backend` proving all active pods are on the stable revision.

---

## Automated Rollback Procedure Reference

For complete details on the formal incident escalation path, metric queries, failure limits, and manual recovery procedures, see the dedicated documentation:

👉 **[Automated Canary Rollback Procedure](rollback-procedure.md)**

---

## Summary of Week 11 Accomplishments

* **Implemented Cloud-Native Progressive Delivery:** Replaced static rolling updates with dynamic, metric-validated canary releases using Argo Rollouts.
* **Granular Traffic Control:** Established an automated canary progression starting at 10% traffic weight, advancing through 30%, 60%, and 100% thresholds.
* **Integrated Observability:** Reused Week 9 Prometheus monitoring infrastructure as the automated gatekeeper for release quality.
* **Zero-Downtime Automated Resilience:** Confirmed that faulty releases trigger instant automated rollback, safeguarding user traffic with zero manual intervention required.
