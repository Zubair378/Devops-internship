"""Adopt earlier manually installed Kong CRDs without replacing their contents."""
import argparse
import json
import subprocess


def run(context, apply=False):
    command = ["kubectl", "--context", context, "--request-timeout=30s"]
    resources = json.loads(subprocess.check_output(command + ["get", "crds", "-o", "json"]))["items"]
    candidates = [r for r in resources if r["spec"]["group"] == "configuration.konghq.com"]
    expected = {"meta.helm.sh/release-name": "kong", "meta.helm.sh/release-namespace": "kong"}
    # Check every owner before changing any metadata. Never steal another release.
    for resource in candidates:
        metadata = resource["metadata"]
        annotations = metadata.get("annotations", {})
        manager = metadata.get("labels", {}).get("app.kubernetes.io/managed-by")
        if manager not in (None, "Helm") or any(annotations.get(k) not in (None, v) for k, v in expected.items()):
            raise SystemExit("Different owner on " + metadata["name"] + "; adoption stopped.")
    patch = {"metadata": {"labels": {"app.kubernetes.io/managed-by": "Helm"}, "annotations": expected}}
    for resource in candidates:
        name = resource["metadata"]["name"]
        if apply:
            subprocess.run(command + ["patch", "crd", name, "--type=merge", "-p", json.dumps(patch)], check=True)
        else:
            print("Can adopt:", name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", default="devops-week2")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    run(args.context, args.apply)
