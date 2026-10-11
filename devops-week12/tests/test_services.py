"""Application and metric contracts used by the final demo."""
import importlib.util
import io
import json
import os
from pathlib import Path
import urllib.error

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(params=[os.getenv("TEST_SERVICE")] if os.getenv("TEST_SERVICE") else ["backend", "frontend"])
def service(request, monkeypatch):
    name = request.param
    monkeypatch.setenv("APP_VERSION", "test-commit")
    monkeypatch.setenv("POD_REVISION", "test-revision")
    monkeypatch.delenv("DEMO_FAIL_INFO", raising=False)
    spec = importlib.util.spec_from_file_location(name + "_week12", ROOT / name / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return name, module, module.app.test_client()


def test_version_and_health(service):
    name, _, client = service
    assert client.get("/health").status_code == 200
    payload = client.get("/info").get_json()
    assert payload["service"] == name
    assert payload["version"] == "test-commit"


def test_metrics_measure_requests_not_health_checks(service):
    _, _, client = service
    client.get("/health")
    client.get("/info")
    client.get("/unknown-user-path")
    metrics = client.get("/metrics").text
    assert 'path="/info"' in metrics
    assert 'status="200"' in metrics
    assert 'path="unmatched"' in metrics
    assert 'status="404"' in metrics
    assert 'revision="test-revision"' in metrics
    assert 'path="/health"' not in metrics
    assert 'path="/metrics"' not in metrics


def test_backend_failure_is_real_and_measured(service, monkeypatch):
    name, _, client = service
    if name != "backend":
        pytest.skip("backend-specific fault injection")
    monkeypatch.setenv("DEMO_FAIL_INFO", "true")
    assert client.get("/info").status_code == 503
    assert client.get("/health").status_code == 200
    assert 'status="503"' in client.get("/metrics").text


def test_frontend_calls_backend_and_handles_failures(service, monkeypatch):
    name, module, client = service
    if name != "frontend":
        pytest.skip("frontend-specific service communication")
    def upstream(*args, **kwargs):
        return io.BytesIO(json.dumps({"service": "backend", "version": "test-commit"}).encode())
    monkeypatch.setattr(module.urllib.request, "urlopen", upstream)
    response = client.get("/backend")
    assert response.status_code == 200
    assert response.get_json()["backend"]["version"] == "test-commit"
    def unavailable(*args, **kwargs):
        raise urllib.error.URLError("offline")
    monkeypatch.setattr(module.urllib.request, "urlopen", unavailable)
    assert client.get("/backend").status_code == 502
    def faulty(*args, **kwargs):
        raise urllib.error.HTTPError("http://backend/info", 503, "fault", {}, None)
    monkeypatch.setattr(module.urllib.request, "urlopen", faulty)
    assert client.get("/backend").status_code == 503
