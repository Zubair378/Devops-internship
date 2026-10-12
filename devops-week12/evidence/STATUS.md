# Week 12 verification status — 12 October 2026

**The final live end-to-end demo is not verified.** The application and infrastructure were deployed far enough to show GitOps reconciliation and running pods, but the local Docker/WSL runtime failed before canary promotion, gateway, Prometheus, and Grafana checks could complete. Do not present these checks as passed.

## Verified results

- Source commit `6ab6abb6f0a2b19fc15a40b9f7d23197f7d5738e` was pushed. [GitHub Actions run 38192657087](https://github.com/Zubair378/Devops-internship/actions/runs/38192657087) completed all five test, build, and image-update jobs successfully in 56 seconds. The bot committed the image-tag update as `c69155dd6218854e9ef1f2eed96af2f14814081a`.
- Local Week 12 tests passed (six passed, two intentional service-specific skips), and the final Helm chart lint passed. Actual terminal and CI browser screenshots are in `screenshots/`.
- ArgoCD synced the `microservices-app` Application to the image-update commit and reported its sync operation succeeded. The new frontend, backend candidate, and demo-traffic pods were each observed with both containers running. Kong was observed with both containers ready and zero restarts. These were point-in-time observations, not a completed end-to-end validation.
- The Quay CDN route was repaired and its certificate was verified from the node. The ArgoCD image pulled successfully. Prometheus and Alertmanager were observed with both containers running before the later cluster failure.

## Blocker and remaining checks

The existing minikube node exited with Docker exit code 255. Restarting the node brought up kubelet and etcd, but minikube timed out after three minutes because the Kubernetes API server could not answer health checks. Its log showed repeated etcd request deadlines. During the attempt, Docker's Ubuntu socket disappeared; Windows Docker remained responsive. Ubuntu was restarted, then Docker Desktop restart was requested. The final live state must be rechecked before a demo.

Still unverified: completed metric-gated canary promotion and rollback, authenticated Kong response and rate limiting, live Prometheus series, Grafana dashboard panel data, the `verify.py` all-pass report, and a second empty-cluster reproduction. No live-success screenshot or `verification.json` is claimed.

The assignment screenshot says the submission window is locked. The exit survey needs the student's own feedback; a technical deployment cannot submit it or reopen the window.
