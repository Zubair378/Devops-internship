# Week 12 verification status — 12 October 2026

**Live end-to-end verification passed again on the existing `devops-week2` cluster at 18:48 UTC on 12 October 2026.** The final rerun passed every assertion in `verification.json`. The machine has 8 GB of RAM, so the stack can respond slowly under load. Earlier in this rerun, the Kubernetes API and Grafana briefly timed out and the Rollouts controller restarted; they recovered without resetting the cluster, and all application pods and the controller were ready when the full rerun passed. A separate empty-cluster rebuild and a deliberate failure/rollback test were not run on this machine.

## Passed checks

- Source commit `6ab6abb6f0a2b19fc15a40b9f7d23197f7d5738e` was pushed. [GitHub Actions run 38192657087](https://github.com/Zubair378/Devops-internship/actions/runs/38192657087) finished all five test, build, and image-update jobs successfully. Bot deployment commit: `c69155dd6218854e9ef1f2eed96af2f14814081a`.
- Local service tests: six passed, two intentional service-specific skips. The Helm chart linted successfully.
- ArgoCD was Synced and Healthy at repository commit `94f7f10d588a8bc7fc48d94dae080a19bb517db6` during the rerun. Both frontend and backend images were running from the expected full source SHA with Istio sidecars ready.
- The backend rollout was Healthy with two ready replicas. Three candidate AnalysisRuns were Successful, validating the 10%, 30%, and 60% gates before full promotion.
- Kong returned 401 without a key; with the rotated demo key, `/info` and `/backend` returned 200 and the expected source version. The rate-limit check observed 118 successful requests and seven 429 responses in its window.
- Prometheus had three live application scrape targets. Real backend and frontend request metrics and Kong response metrics were present.
- Grafana was healthy via its API, the Week 12 dashboard was provisioned, and all six panels returned live data through the Grafana query API.

The exact machine-readable result is [`verification.json`](verification.json), with the command output in [`final-live-verification.log`](final-live-verification.log). Real CI, terminal, ArgoCD, Prometheus, authenticated gateway, and live Grafana dashboard screenshots are in [`screenshots/`](screenshots/).

## Scope and environment

The existing cluster was recovered without deleting profiles or user data. The Quay CDN route was repaired, the Kubernetes clock was synced to Windows, and Docker Desktop's local socket was used when its Ubuntu socket was unavailable. Docker Desktop's original setting was restored. Ubuntu's `systemd-timesyncd` was disabled after it repeatedly shifted WSL several minutes ahead of Windows; it can be re-enabled when that time source is fixed.

The separate fresh-profile reproduction and controlled fault-injection rollback remain untested to avoid destabilizing the demonstrated working cluster on this 8 GB laptop. The documented bootstrap and rollback design are in the Week 12 guide. The course exit survey requires the student's own feedback, and the assignment screenshot shows the submission window locked; deployment work cannot reopen it.
