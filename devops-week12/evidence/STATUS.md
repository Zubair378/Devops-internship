# Verification status — 12 October 2026

**Incomplete: the live end-to-end demo has not passed.**

Verified:
- Source commit `1d845a31b12f9ca4dc31a5d90e5650da08f2d649` was pushed.
- GitHub Actions run [38113483248](https://github.com/Zubair378/Devops-internship/actions/runs/38113483248)
  completed all five test/build/GitOps jobs successfully.
- The bot updated the deployment image tag in commit `e291f89`.
- Local Week 12 tests: six passed, two intentional service-specific skips.
- Helm chart lint, bootstrap shell syntax, and Git whitespace checks passed.
- Documentation and recovery tools commit `95b1820` was pushed using the existing
  Windows Git Credential Manager sign-in after the WSL stored credential failed.

Live findings:
- The existing cluster initially lacked ArgoCD, Kong and monitoring components.
- Kubernetes and Istio were recovered; monitoring installation remained incomplete.
- The original Quay CDN DNS route timed out. The repair script now resolves and
  verifies the CDN certificate from inside the actual minikube node. A full
  Prometheus Operator image pull succeeded, and Prometheus and Alertmanager pods
  subsequently reached Running.
- The repeatable bootstrap still times out while upgrading the Istio base CRDs:
  the Kubernetes API did not respond before the Helm timeout. A subsequent run
  also ended with Docker API/WSL connection timeouts. ArgoCD and Kong were not
  installed, the dashboard was not ready, and the final application was not
  deployed or verified.
- WSL was limited to 3500 MB, automatic cache reclaim enabled, and its CPU count
  restored to the original four. The prior settings are backed up at
  `C:\Users\TARIQ COMPUTER\.wslconfig.week12-backup`.
- The root cause of the slow Kubernetes API and repeated Docker/WSL timeouts is
  still unresolved. No cluster/profile, application data, or unrelated user
  files were deleted. The local source and test environment are saved.

Still required before calling this demo complete:
1. Recover a stable Docker/WSL runtime (restart Windows after saving open work).
2. Run `bash devops-week12/scripts/bootstrap.sh` and finish infrastructure setup.
3. Verify ArgoCD automatic reconciliation and full-SHA images running in all pods.
4. Verify Kong authentication/routing/rate limit and frontend-to-backend calls.
5. Verify fresh Prometheus targets and real data in all Grafana dashboard panels.
6. Exercise successful canary promotion and metric-driven failure/rollback.
7. Recreate the platform in a separate profile and verify it from scratch.
8. Capture the live ArgoCD, gateway, Prometheus and Grafana screens.

No `verification.json` success report has been generated. The screenshots show
CI and local checks only; they do not show a successful live deployment.

The exit survey needs the student's own feedback. The supplied assignment screen
shows the submission window locked; this must be handled with the course provider.
