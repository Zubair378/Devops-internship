"""Set the GitOps image tag after both CI builds succeed."""
import pathlib
import re
import sys

path = pathlib.Path(__file__).resolve().parents[1] / "chart" / "values.yaml"
sha = sys.argv[1]
if not re.fullmatch(r"[a-f0-9]{40}", sha):
    raise SystemExit("Expected a full Git commit SHA")
text = path.read_text()
updated, count = re.subn(r"(?m)^  tag: .*$", f'  tag: "{sha}"', text)
if count != 1:
    raise SystemExit("Expected exactly one image tag")
path.write_text(updated)
print(f"GitOps image tag updated to {sha}")
