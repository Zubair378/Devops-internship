"""Repair an unreachable Quay CDN route only inside the selected minikube node."""
import argparse
import ipaddress
import json
import subprocess
import urllib.request

HOST = "cdn01.quay.io"


def reachable(address, profile):
    try:
        result = subprocess.run(
            ["docker", "exec", profile, "openssl", "s_client", "-connect", address + ":443",
             "-servername", HOST, "-verify_return_error", "-verify_hostname", HOST, "-brief"],
            input="", text=True, capture_output=True, timeout=7)
        return result.returncode == 0 and "Verification: OK" in result.stderr
    except (OSError, subprocess.TimeoutExpired):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="devops-week2")
    parser.add_argument("--refresh", action="store_true",
                        help="Refresh the CDN route after a failed blob download")
    args = parser.parse_args()
    profile = args.profile
    info = json.loads(subprocess.check_output(["docker", "inspect", profile], text=True))[0]
    if info["Config"].get("Labels", {}).get("created_by.minikube.sigs.k8s.io") != "true":
        raise SystemExit("Refusing to modify a container that is not a minikube node")
    result = subprocess.run(["docker", "exec", profile, "getent", "ahostsv4", HOST],
                            text=True, capture_output=True)
    addresses = list(dict.fromkeys(line.split()[0] for line in result.stdout.splitlines()))
    if not args.refresh and addresses and all(reachable(address, profile) for address in addresses):
        print("Quay CDN route is reachable")
        return
    answers = []
    for resolver in ("https://cloudflare-dns.com/dns-query", "https://dns.google/resolve"):
        request = urllib.request.Request(resolver + "?name=" + HOST + "&type=A",
                                         headers={"Accept": "application/dns-json"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                answers.extend(json.load(response).get("Answer", []))
        except (OSError, ValueError) as error:
            print("Resolver unavailable:", resolver, type(error).__name__)
    for answer in answers:
        if answer["type"] != 1:
            continue
        address = answer["data"]
        if not ipaddress.ip_address(address).is_global or not reachable(address, profile):
            continue
        original = subprocess.check_output(["docker", "exec", profile, "cat", "/etc/hosts"], text=True)
        lines = [line for line in original.splitlines() if HOST not in line.split("#", 1)[0].split()[1:]]
        updated = "\n".join(lines) + "\n" + address + " " + HOST + " # week12 TLS-verified CDN route\n"
        subprocess.run(["docker", "exec", "-i", profile, "sh", "-c", "cat > /etc/hosts"],
                       input=updated, text=True, check=True)
        print("Repaired", HOST, "inside", profile, "using", address)
        return
    raise SystemExit("No reachable, TLS-verified Quay CDN address found")


if __name__ == "__main__":
    main()
