import os
import socket
import time
import json
import urllib.error
import urllib.request

from flask import Flask, Response, g, jsonify, request
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, start_http_server
from prometheus_client.exposition import CONTENT_TYPE_LATEST

app = Flask(__name__)
registry = CollectorRegistry()
identity = {
    "service": "frontend",
    "version": os.getenv("APP_VERSION", "local"),
    "revision": os.getenv("POD_REVISION", "local"),
}
requests_total = Counter(
    "devops_http_requests_total", "Application requests excluding probes and scrapes",
    ["service", "version", "revision", "method", "path", "status"], registry=registry,
)
duration = Histogram(
    "devops_http_request_duration_seconds", "Application request duration",
    ["service", "version", "revision", "method", "path"], registry=registry,
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
)


@app.before_request
def start_timer():
    g.started = time.monotonic()


@app.after_request
def observe(response):
    if request.path not in ("/health", "/metrics"):
        path = request.url_rule.rule if request.url_rule else "unmatched"
        labels = dict(identity, method=request.method, path=path)
        requests_total.labels(**labels, status=str(response.status_code)).inc()
        duration.labels(**labels).observe(time.monotonic() - g.started)
    return response


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/")
@app.get("/info")
def info():
    return jsonify(**identity, developer="Zubair", hostname=socket.gethostname())


@app.get("/metrics")
def metrics():
    return Response(generate_latest(registry), content_type=CONTENT_TYPE_LATEST)


@app.get("/backend")
def backend():
    url = os.getenv("BACKEND_URL", "http://backend-service:5000").rstrip("/") + "/info"
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            payload = json.load(response)
        return jsonify(frontend=identity["version"], backend=payload)
    except urllib.error.HTTPError as error:
        return jsonify(error="Backend returned an error", backend_status=error.code), error.code
    except (urllib.error.URLError, TimeoutError, ValueError):
        return jsonify(error="Backend unavailable"), 502


if __name__ == "__main__":
    # Dedicated in-cluster scrape port; the application port remains in the mesh.
    start_http_server(8001, registry=registry)
    app.run(host="0.0.0.0", port=5001)
