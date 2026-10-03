# Week 11 — Automated Canary Rollback Procedure

## 1. Executive Summary & Architecture Overview
This runbook formalizes the automated rollback procedure for Canary Deployments orchestrated with **Argo Rollouts** and **Prometheus** metrics.

In modern continuous delivery, deploying new microservice revisions directly to 100% of production traffic introduces unacceptable risk. A canary deployment mitigates this by routing a small fraction (e.g. 10%) of incoming user traffic to the newly deployed candidate. As the canary handles live production load, Prometheus continuously monitors golden signals (Error Rate, Latency, Saturation, HTTP 5xx codes).

If the canary meets all health criteria, traffic weight is incrementally increased through staged canary gates (10% -> 30% -> 60% -> 100%). If at any point the candidate breaches predefined metric thresholds, Argo Rollouts automatically triggers an **Automated Rollback (Abort)**, immediately terminating the unhealthy canary pods and directing 100% of traffic back to the known-healthy stable revision.

```
       Incoming Traffic
              │
              ▼
   ┌───────────────────────┐
   │    backend-service    │
   └──────────┬────────────┘
              │
      ┌───────┴───────┐
      │ (Traffic Split)
      ▼               ▼
┌───────────┐   ┌───────────┐
│  Stable   │   │  Canary   │
│ (90% / v1)│   │ (10% / v2)│
└─────┬─────┘   └─────┬─────┘
      │               │
      │         ┌─────▼─────┐
      │         │Prometheus │
      │         │Scrapes    │
      │         └─────┬─────┘
      │               │
      │         ┌─────▼─────┐
      │         │ Analysis- │  (Pass -> Advance to 30%, 60%, 100%)
      │         │   Run     │──┐
      │         └─────┬─────┘  │
      │               │ (Fail: Error Rate > 5%)
      │               ▼
      │    ┌──────────────────────┐
      │    │  AUTOMATED ROLLBACK  │
      │    │ 1. Abort Rollout     │
      └───<│ 2. Canary Weight = 0 │
           │ 3. 100% to Stable v1 │
           └──────────────────────┘
```

---

## 2. Metric Evaluation & Automated Decision Logic

Argo Rollouts couples with Prometheus via the `AnalysisTemplate` resource.

### A. Health & Error Metric Query
The canary health is evaluated using rate of HTTP 5xx responses:
```promql
sum(rate(flask_http_request_total{status=~"5.."}[1m]))
/
(sum(rate(flask_http_request_total[1m])) > 0)
```
- **Target Threshold:** Error rate must remain $\le 5\%$ (`0.05`).
- **Success Criteria:** `result[0] <= 0.05`
- **Evaluation Interval:** Every `10s` across `3` consecutive iterations.
- **Failure Limit:** `1` (a single confirmed breach triggers immediate mitigation).

### B. Decision Lifecycle
1. When `rollout.yaml` steps transition to an `analysis` phase, the controller spawns an `AnalysisRun` pod or job.
2. The `AnalysisRun` runs the Prometheus query against `http://monitoring-kube-prometheus-prometheus.monitoring.svc.cluster.local:9090`.
3. If metric conditions pass (`Successful`):
   - The step completes.
   - The rollout advances to the next configured weight (e.g. 10% -> 30%).
4. If metric conditions fail (`Failed`):
   - The `AnalysisRun` state changes immediately from `Running` to `Failed`.
   - The parent `Rollout` controller intercepts the failure event.

---

## 3. Sequence of Events During an Automated Rollback

When a failure is detected, the automated rollback executes the following deterministic lifecycle:

1. **Analysis Failure Event:**
   - Prometheus query returns values exceeding the allowed threshold.
   - Event logged: `AnalysisRun degraded / condition failed`.
2. **Immediate Traffic Shedding:**
   - The Rollout controller sets canary traffic weight immediately to `0%`.
   - The active routing points exclusively to the `backend-stable` service.
3. **Rollout Status Transition:**
   - The Rollout status transitions to `RolloutAborted` and `Degraded`.
   - Ingress and Service selectors drop the canary pods.
4. **Pod Teardown / Quarantine:**
   - Unhealthy canary pods are terminated (or scaled down to 0) to prevent further erroneous responses from reaching clients.
5. **Stable Continuity:**
   - The stable replica set maintains 100% of desired replicas (`replicas: 10`), guaranteeing uninterrupted user traffic.

---

## 4. Verification & Diagnostic Commands

During or after an incident, run the following commands to inspect the state and timeline:

### 1. View Rollout State in Terminal
```bash
kubectl argo rollouts get rollout backend-rollout
```
*Expected output for aborted rollout:*
```
Status:       Degraded
Message:      RolloutAborted: Rollout aborted update to revision 2: metric 'error-rate' failed
```

### 2. Inspect AnalysisRuns
```bash
kubectl get analysisruns -A
kubectl describe analysisrun <analysisrun-name>
```
*Key inspection points:* Check `Message`, `Values`, and `Status: Failed`.

### 3. Check Pod Replicas and Service Routing
```bash
# Verify all active traffic is pointing to stable pods
kubectl get pods -l app=backend -o wide
kubectl describe service backend-stable
```

### 4. Query Controller Logs
```bash
kubectl logs -n argo-rollouts deployment/argo-rollouts --tail=50
```

---

## 5. Manual Fallback & Emergency Procedures

If automated rollback requires manual override or post-mortem handling:

### 1. Manual Abort
If an operator identifies an unmonitored issue (e.g. unexpected visual bug):
```bash
kubectl argo rollouts abort backend-rollout
```

### 2. Rollback to Stable Revision (Undo)
To explicitly revert the rollout definition to the previous stable revision:
```bash
kubectl argo rollouts undo backend-rollout --to-revision=1
```

### 3. Retry a Corrected Release
Once the underlying bug is fixed and a new image is pushed:
```bash
kubectl argo rollouts retry rollout backend-rollout
```

---

## 6. Post-Rollback Checklist
- [ ] Verify 0% user traffic is reaching the faulty canary revision.
- [ ] Confirm `backend-stable` is receiving 100% traffic with 0 elevated error rates.
- [ ] Archive Prometheus query graphs and `AnalysisRun` logs for RCA.
- [ ] Create hotfix branch and update test vectors before initiating a new canary cycle.
