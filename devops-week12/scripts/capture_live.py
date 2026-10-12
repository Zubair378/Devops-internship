"""Capture authenticated final-demo pages in Microsoft Edge without logging credentials."""
import base64
import json
from pathlib import Path
import subprocess
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
KUBECONFIG = ROOT / '.runtime' / 'kubeconfig.windows'
OUT = ROOT / 'evidence' / 'screenshots'


def secret(namespace, name, field):
    raw = subprocess.check_output([
        'kubectl', '--kubeconfig', str(KUBECONFIG), '-n', namespace,
        'get', 'secret', name, '-o', 'json', '--request-timeout=15s',
    ])
    return base64.b64decode(json.loads(raw)['data'][field]).decode()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel='msedge', headless=True)
        page = browser.new_page(viewport={'width': 1600, 'height': 1000})
        page.set_default_timeout(20000)
        for name, url in [
            ('04-prometheus-targets.png', 'http://localhost:9090/targets'),
            ('05-kong-authenticated-backend.png', 'http://localhost:8000/backend'),
            ('06-argocd-healthy.png', 'http://localhost:8080/applications/argocd/microservices-app'),
            ('07-grafana-final-dashboard.png', 'http://localhost:3000/d/devops-week12'),
        ]:
            if len(sys.argv) > 1 and name not in sys.argv[1:]:
                continue
            page.set_extra_http_headers({})
            if name.startswith('05'):
                page.set_extra_http_headers({'apikey': secret('default', 'week12-api-key', 'key')})
            if name.startswith('06'):
                page.goto('http://localhost:8080/login', wait_until='domcontentloaded')
                page.wait_for_timeout(3000)
                page.locator('input[name="username"]').first.fill('admin')
                page.locator('input[type="password"]').first.fill(secret('argocd', 'argocd-initial-admin-secret', 'password'))
                page.locator('button[type="submit"]').first.click()
                page.wait_for_timeout(2500)
            if name.startswith('07'):
                page.goto('http://localhost:3000/login', wait_until='domcontentloaded')
                page.locator('input[name="user"]').fill('admin')
                page.locator('input[name="password"]').fill(secret('monitoring', 'monitoring-grafana', 'admin-password'))
                page.locator('button[type="submit"]').first.click()
                page.wait_for_timeout(2500)
            page.goto(url, wait_until='domcontentloaded', timeout=45000)
            page.wait_for_timeout(30000 if name.startswith('07') else 8000)
            path = OUT / name
            page.screenshot(path=str(path), full_page=True)
            print(name, page.url, page.title(), flush=True)
        browser.close()


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Browser capture failed: {type(exc).__name__}: {exc}', file=sys.stderr)
        raise
