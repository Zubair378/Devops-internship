# Week 10 — Incident Response Runbook

## Alert: HighAPILatency
**Severity:** Warning
**Meaning:** The 95th percentile of API server request latency has exceeded 1 second for more than 2 minutes.
**Response:**
1. Check current cluster resource usage: `kubectl top nodes` and `kubectl top pods -A`.
2. Identify if a specific workload is consuming excess CPU/memory, causing scheduling delays.
3. Consider scaling down non-critical pods temporarily to relieve pressure.
4. If latency persists beyond 10 minutes, escalate to infrastructure review.

## Alert: HighErrorRate
**Severity:** Critical
**Meaning:** More than 5% of API server requests are returning 5xx errors over the last 5 minutes.
**Response:**
1. Check API server pod health: `kubectl get pods -n kube-system`.
2. Review API server logs: `kubectl logs -n kube-system kube-apiserver-devops-week2`.
3. Check etcd health, since API server errors often stem from etcd issues: `kubectl get pods -n kube-system | grep etcd`.
4. If errors continue, restart the affected component and monitor recovery.

## Alert: TargetDown
**Severity:** Critical
**Meaning:** A Prometheus scrape target (a pod/service Prometheus monitors) has been unreachable for over 1 minute — commonly indicates a pod crash, restart, or CrashLoopBackOff.
**Response:**
1. Identify the affected target: check the `job` and `instance` labels on the firing alert.
2. Check pod status: `kubectl get pods -A | grep -v Running`.
3. Investigate the specific pod: `kubectl describe pod <pod-name> -n <namespace>` and `kubectl logs <pod-name> -n <namespace>`.
4. If OOMKilled, consider increasing memory limits or reducing replica count.
5. If a genuine crash loop, roll back the most recent change or image.

## General Escalation Policy
- Warning-severity alerts: monitor, investigate within the hour.
- Critical-severity alerts: investigate immediately, notify team via the configured notification channel.
