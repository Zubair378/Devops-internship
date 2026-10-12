# Week 12 final demo: output and evidence

This project is a small API behind Kong, with deployment and monitoring dashboards. The application output is JSON in the browser or terminal; there is no separate graphical storefront. The complete path is GitHub Actions -> GHCR images -> ArgoCD -> Kong -> frontend -> Istio -> backend -> Prometheus -> Grafana.

## Start and view it

In WSL, with Docker Desktop and the `devops-week2` minikube profile running:

```bash
cd ~/devops-week1
python3 devops-week12/scripts/start_demo.py
```

Open `http://localhost:8080/applications/argocd/microservices-app` for the ArgoCD deployment status, `http://localhost:9090/targets` for Prometheus scrape targets, and `http://localhost:3000/d/devops-week12` for the six-panel Grafana dashboard. ArgoCD and Grafana use the `admin` account; the main [Week 12 guide](README.md#open-the-demo) explains how to retrieve their local passwords privately. Alertmanager is at `http://localhost:9093`.

Kong is the application entry point at `http://localhost:8000`. It requires an `apikey` header. Opening `/info` or `/backend` in an ordinary browser tab without that header returns **401 Unauthorized**, which is expected. The verification script reads the local Kubernetes Secret itself; do not put the key in a screenshot or README.

With the key, `/info` returns HTTP 200 and JSON identifying the frontend, including its `version` (the full source commit SHA). `/backend` returns HTTP 200 and JSON with both `frontend` and `backend.version` set to that same SHA. The backend object also identifies the serving pod and rollout revision. Pod names and rollout hashes change between deployments. This `/backend` response is the visible proof that Kong routed to the frontend and the frontend reached the backend through Istio.

## Run the complete check

Read `image.tag` from `devops-week12/chart/values.yaml`, then run:

```bash
python3 devops-week12/scripts/verify.py --sha FULL_SOURCE_COMMIT_SHA --rate-limit
```

The terminal prints `PASS` lines for node readiness, ArgoCD sync and health, backend rollout, ready images and sidecars, Kong authentication and both application routes, fresh Prometheus targets and request metrics, the Grafana dashboard and every panel query, and Kong's 120-requests-per-minute limit. It writes the detailed result to `devops-week12/evidence/verification.json`. The rate-limit test intentionally produces HTTP 429; wait for the next minute before manually browsing the gateway again.

The last successful check and screenshots are in [evidence/](evidence/). Look at the actual timestamps in `verification.json` and screenshot files when presenting; they are evidence of that run, not a promise that the cluster stays healthy indefinitely. A separate empty-cluster rebuild and deliberate rollback test have not been completed on this 8 GB laptop.

## Presentation order

1. Show the successful [GitHub Actions run](https://github.com/Zubair378/Devops-internship/actions/runs/38192657087) and source SHA.
2. Show ArgoCD **Synced / Healthy** and the healthy backend rollout.
3. Show Kong's expected 401 without a key, then authenticated `/info` and `/backend` HTTP 200 JSON with matching versions.
4. Show Prometheus application scrape targets **UP** and Grafana's six panels with live data.
5. Run `verify.py` and show its final `PASS` result and `verification.json`.

Screenshots are in [evidence/screenshots/](evidence/screenshots/). Never include Kubernetes Secret values or dashboard passwords in submitted images.
