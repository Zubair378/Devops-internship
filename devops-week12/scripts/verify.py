"""Assert the live release, Kong behavior, and fresh application telemetry."""
import argparse
import base64
import datetime
import json
from pathlib import Path
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def http(url, headers=None):
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers)


def query(expression):
    status, body, _ = http("http://127.0.0.1:9090/api/v1/query?" + urllib.parse.urlencode({"query": expression}))
    assert status == 200, f"Prometheus returned HTTP {status}"
    result = json.loads(body)
    assert result["status"] == "success", result
    return result["data"]["result"]


def run(context, expected, rate_limit=False):
    def k(*args):
        return subprocess.check_output(["kubectl", "--context", context, *args], text=True)

    record = {"time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "context": context, "expected_source_sha": expected, "checks": {}}
    def passed(name, value):
        record["checks"][name] = value
        print(f"PASS {name}: {value}", flush=True)

    nodes = json.loads(k("get", "nodes", "-o", "json"))["items"]
    assert nodes and all(any(c["type"] == "Ready" and c["status"] == "True"
                             for c in n["status"]["conditions"]) for n in nodes)
    passed("nodes_ready", [n["metadata"]["name"] for n in nodes])
    app = json.loads(k("-n", "argocd", "get", "application", "microservices-app", "-o", "json"))
    assert app["status"]["sync"]["status"] == "Synced", app["status"]["sync"]
    assert app["status"]["health"]["status"] == "Healthy", app["status"]["health"]
    passed("argocd_synced_healthy", app["status"]["sync"]["revision"])
    rollout = json.loads(k("-n", "default", "get", "rollout", "backend-rollout", "-o", "json"))
    assert rollout["status"]["phase"] == "Healthy", rollout["status"]["phase"]
    passed("rollout_healthy", rollout["status"].get("stableRS"))
    pods = json.loads(k("-n", "default", "get", "pods", "-o", "json"))["items"]
    images = {}
    for service in ("backend", "frontend"):
        matching = [p for p in pods if p["metadata"].get("labels", {}).get("app") == service
                    and not p["metadata"].get("deletionTimestamp")]
        assert matching, f"No {service} pods"
        for pod in matching:
            containers = pod["status"]["containerStatuses"]
            assert all(c["ready"] for c in containers), pod["metadata"]["name"]
            container = next(c for c in containers if c["name"] == service)
            assert container["image"].endswith(":" + expected), container["image"]
            assert container.get("imageID"), container
            images[pod["metadata"]["name"]] = container["imageID"]
    passed("expected_images_ready", images)

    status, _, _ = http("http://127.0.0.1:8000/info")
    assert status == 401, f"Expected key-auth rejection, received {status}"
    passed("kong_rejects_missing_key", status)
    secret = json.loads(k("-n", "default", "get", "secret", "week12-api-key", "-o", "json"))
    key = base64.b64decode(secret["data"]["key"]).decode()
    headers = {"apikey": key}
    for route in ("info", "backend"):
        status, body, response_headers = http("http://127.0.0.1:8000/" + route, headers)
        assert status == 200, f"{route}: HTTP {status}"
        payload = json.loads(body)
        version = payload["version"] if route == "info" else payload["backend"]["version"]
        assert version == expected, payload
        passed("kong_" + route, {"status": status, "response": payload})
    targets = query('up{job=~"backend-service|frontend-service"}')
    assert targets and all(float(row["value"][1]) == 1 for row in targets), targets
    assert all(time.time() - float(row["value"][0]) < 45 for row in targets)
    assert {"backend-service", "frontend-service"} <= {r["metric"]["job"] for r in targets}
    passed("application_scrape_targets_up", len(targets))
    traffic = query('sum by (service) (increase(devops_http_requests_total[2m]))')
    totals = {row["metric"]["service"]: float(row["value"][1]) for row in traffic}
    assert totals.get("backend", 0) > 0 and totals.get("frontend", 0) > 0, totals
    passed("real_application_requests", totals)
    gateway = query("sum(kong_http_requests_total)")
    assert gateway and float(gateway[0]["value"][1]) > 0, gateway
    passed("kong_metrics_present", gateway[0]["value"][1])
    status, body, _ = http("http://127.0.0.1:3000/api/health")
    assert status == 200 and json.loads(body)["database"] == "ok"
    passed("grafana_database_healthy", json.loads(body)["version"])
    dashboards = json.loads(k("-n", "default", "get", "configmap", "week12-grafana-dashboard", "-o", "json"))
    dashboard = json.loads(dashboards["data"]["final-demo.json"])
    assert dashboard["uid"] == "devops-week12"
    passed("grafana_dashboard_provisioned", dashboard["title"])
    grafana_secret = json.loads(k("-n", "monitoring", "get", "secret", "monitoring-grafana", "-o", "json"))
    username = base64.b64decode(grafana_secret["data"]["admin-user"]).decode()
    password = base64.b64decode(grafana_secret["data"]["admin-password"]).decode()
    basic = base64.b64encode((username + ":" + password).encode()).decode()
    grafana_headers = {"Authorization": "Basic " + basic}
    status, body, _ = http("http://127.0.0.1:3000/api/dashboards/uid/devops-week12", grafana_headers)
    assert status == 200, f"Grafana dashboard API returned {status}"
    loaded = json.loads(body)["dashboard"]
    passed("grafana_dashboard_loaded", loaded["title"])
    panels = {}
    for panel in loaded["panels"]:
        expression = panel["targets"][0]["expr"]
        url = "http://127.0.0.1:3000/api/datasources/proxy/uid/prometheus/api/v1/query?"
        status, body, _ = http(url + urllib.parse.urlencode({"query": expression}), grafana_headers)
        assert status == 200, f"Grafana query failed for {panel['title']}"
        data = json.loads(body)
        assert data["status"] == "success" and data["data"]["result"], panel["title"]
        panels[panel["title"]] = len(data["data"]["result"])
    passed("all_grafana_panels_have_live_data", panels)

    if rate_limit:
        statuses = [http("http://127.0.0.1:8000/info", headers)[0] for _ in range(125)]
        assert 200 in statuses and 429 in statuses, statuses
        assert set(statuses) <= {200, 429}, statuses
        passed("kong_rate_limit", {str(code): statuses.count(code) for code in sorted(set(statuses))})
    record["result"] = "PASS"
    output = ROOT / "evidence" / "verification.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(record, indent=2) + "\n")
    print(f"Verified results saved to {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", default="devops-week2")
    parser.add_argument("--sha", required=True)
    parser.add_argument("--rate-limit", action="store_true")
    args = parser.parse_args()
    run(args.context, args.sha, args.rate_limit)
