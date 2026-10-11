"""Capture real browser pages on Windows using the installed Microsoft Edge."""
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    if Path(args.name).name != args.name or not args.name.endswith(".png"):
        raise SystemExit("Use a simple PNG filename.")
    evidence = ROOT / "evidence" / "screenshots"
    evidence.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
        page.goto(args.url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(5000)
        page.screenshot(path=str(evidence / args.name), full_page=True)
        print(page.title())
        print(evidence / args.name)
        browser.close()


if __name__ == "__main__":
    main()
