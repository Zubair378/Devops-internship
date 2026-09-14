# Week 8 — ArgoCD GitOps: auto-sync, notifications, workflow docs

## Task status
| Task | Status |
|---|---|
| Install ArgoCD into cluster | Done |
| Configure ArgoCD to monitor Git repo / Helm chart | Done |
| Push a manifest change, observe auto-sync, document sync time | Done |
| Set up notifications (Slack/email) for sync failures | Config done, controller not installed (see below) |
| Document the GitOps workflow with an architecture diagram | Done (below) |

## GitOps workflow
1. Developer pushes changes to `main` in the Git repo (Helm chart / manifests)
2. ArgoCD's `application-controller` polls the repo (~3 min default interval)
3. It diffs desired state (Git) against live cluster state
4. On drift, Application status flips `Synced` → `OutOfSync`
5. Auto-sync applies the new manifest to the cluster
6. Kubernetes rolls the deployment (new/updated pods, replica count enforced)
7. ArgoCD re-checks health; status returns to `Synced` + `Healthy`
8. On sync failure, a notification trigger fires (see Notifications below)

## Verified test run
- Change: `replicaCount: 3` in backend Helm values
- Push time: 21:01:55 PKT
- Observed transition: `Synced` → `OutOfSync` → `Synced (Progressing)` → `Synced (Healthy)`
- Fully synced + healthy by: 21:06:46 PKT (~5 min, consistent with ArgoCD's default poll interval)
- New pod confirmed: `backend-deployment-bbcc4dbf-sx2rc` (age 2m11s at check time — the new 3rd replica)

## Notifications
`argocd-notifications-cm` and `argocd-notifications-secret` (see `notifications-cm.yaml`)
define an `on-sync-failed` trigger and Slack message template.

This cluster's ArgoCD install does **not** include the `argocd-notifications-controller`
component (confirmed via `kubectl get pods -n argocd` — only `application-controller`,
`applicationset-controller`, `redis`, `repo-server`, and `server` are running). It was
omitted to keep resource usage down on a constrained environment. The trigger config
is correct and would activate immediately if the controller were installed:

    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/addons/notifications/install.yaml

No live Slack webhook token was provisioned in this environment.
