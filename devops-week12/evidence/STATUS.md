# Verification status — 11 October 2026

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
- The original Quay CDN DNS route timed out. An alternate DNS-over-HTTPS answer
  passed TLS hostname verification. An actual image-layer range request returned
  HTTP 206 and 1024 bytes, but full Docker pulls did not complete.
- Docker/WSL repeatedly stopped, including a Docker WSL startup error with status
  `0xc00000fd` and a subsequent `Wsl/Service/E_UNEXPECTED` failure.
- Windows also reported an allocation failure while C: had about 225 MB free.
  Disk space later increased, but the WSL failure recurred. The root cause of the
  recurring WSL crashes is not established by these observations.
- WSL memory was reduced from 5 GB to 3500 MB, processors from four to three, and
  automatic cache reclaim enabled. The original file is backed up at
  `C:\Users\TARIQ COMPUTER\.wslconfig.week12-backup`.
- Docker processes were stopped after graceful shutdown timed out, to end the
  restart loop. No cluster/profile, application data, or unrelated user files
  were deleted. Ubuntu remains available for the saved source and local tests.

Still required before calling this demo complete:
1. Recover a stable Docker/WSL runtime (restart Windows after saving open work).
2. Run `bash devops-week12/scripts/bootstrap.sh` and finish infrastructure setup.
3. Verify ArgoCD automatic reconciliation and full-SHA images running in all pods.
4. Verify Kong authentication/routing/rate limit and frontend-to-backend calls.
5. Verify fresh Prometheus targets and real data in all Grafana dashboard panels.
6. Exercise successful canary promotion and metric-driven failure/rollback.
7. Recreate the platform in a separate profile and verify it from scratch.
8. Capture the live ArgoCD, gateway, Prometheus and Grafana screens.

No `verification.json` success report has been generated. The CI screenshot and
local-test screenshot are evidence only of their respective checks.

The exit survey needs the student's own feedback. The supplied assignment screen
shows the submission window locked; this must be handled with the course provider.
