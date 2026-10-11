"""Start localhost-only access to the five demo services."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
SERVICES = [
    ("argocd", "argocd-server", 8080, 80),
    ("kong", "kong-kong-proxy", 8000, 80),
    ("monitoring", "monitoring-kube-prometheus-prometheus", 9090, 9090),
    ("monitoring", "monitoring-grafana", 3000, 80),
    ("monitoring", "monitoring-kube-prometheus-alertmanager", 9093, 9093),
]


def identity(pid):
    try:
        return Path(f"/proc/{pid}/stat").read_text().split()[21]
    except (FileNotFoundError, ProcessLookupError):
        return None


def stop():
    path = RUNTIME / "port-forwards.json"
    if path.exists():
        for entry in json.loads(path.read_text()):
            if identity(entry["pid"]) == entry["identity"]:
                os.kill(entry["pid"], signal.SIGTERM)
        path.unlink()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", default="devops-week2")
    parser.add_argument("--stop", action="store_true")
    args = parser.parse_args()
    RUNTIME.mkdir(exist_ok=True)
    if args.stop:
        stop()
        raise SystemExit()
    stop()
    entries = []
    for namespace, service, local, remote in SERVICES:
        with socket.socket() as probe:
            if probe.connect_ex(("127.0.0.1", local)) == 0:
                raise SystemExit(f"Port {local} is already in use; identify its owner before retrying.")
    for namespace, service, local, remote in SERVICES:
        log = (RUNTIME / f"{service}.log").open("a")
        command = ["kubectl", "--context", args.context, "-n", namespace,
                   "port-forward", "--address=127.0.0.1", "svc/" + service, f"{local}:{remote}"]
        process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        log.close()
        entries.append({"pid": process.pid, "identity": identity(process.pid), "service": service, "port": local})
        (RUNTIME / "port-forwards.json").write_text(json.dumps(entries))
    for entry in entries:
        for attempt in range(60):
            if identity(entry["pid"]) != entry["identity"]:
                raise SystemExit(f"Port-forward failed for {entry['service']}; inspect .runtime logs.")
            with socket.socket() as probe:
                if probe.connect_ex(("127.0.0.1", entry["port"])) == 0:
                    break
            time.sleep(1)
        else:
            raise SystemExit(f"Timed out waiting for {entry['service']}")
        print(f"{entry['service']}: http://localhost:{entry['port']}")
