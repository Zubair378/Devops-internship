"""Read this repository's CI results without printing authentication material."""
import argparse
import json
import subprocess
import time
import urllib.request

REPO = "Zubair378/Devops-internship"


def headers():
    result = subprocess.run(
        ["git", "credential", "fill"],
        input="protocol=https\nhost=github.com\n\n",
        text=True, capture_output=True, check=True,
    )
    fields = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
    return {"Authorization": "Bearer " + fields["password"],
            "Accept": "application/vnd.github+json", "User-Agent": "week12-verification"}


def get(path, auth):
    request = urllib.request.Request("https://api.github.com/" + path, headers=auth)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True)
    parser.add_argument("--wait", type=int, default=0)
    args = parser.parse_args()
    auth = headers()
    deadline = time.monotonic() + args.wait
    while True:
        runs = get(f"repos/{REPO}/actions/runs?head_sha={args.sha}&per_page=10", auth)["workflow_runs"]
        if runs:
            run = runs[0]
            print(json.dumps({key: run.get(key) for key in
                              ["id", "html_url", "head_sha", "status", "conclusion"]}), flush=True)
            if run["status"] == "completed":
                jobs = get(f"repos/{REPO}/actions/runs/{run['id']}/jobs", auth)["jobs"]
                print(json.dumps([{"name": j["name"], "conclusion": j["conclusion"]} for j in jobs], indent=2))
                raise SystemExit(0 if run["conclusion"] == "success" else 1)
        else:
            print("Waiting for the CI run to appear.", flush=True)
        if time.monotonic() >= deadline:
            raise SystemExit(2)
        time.sleep(15)
