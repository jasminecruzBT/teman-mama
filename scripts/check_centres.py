"""Re-check every confinement centre's published price on its own website.

Run by .github/workflows/check-centres.yml every 3 months (or by hand):
    pip install playwright && python -m playwright install chromium
    python scripts/check_centres.py

For each centre in site-data/confinement.json and each hospital in site-data/delivery.json it opens source_url in a real (headless) browser
and looks for price_from_rm (and price_to_rm if set) on the page.
  - found     -> "checked" date is moved to today (the site then shows the new date)
  - not found -> date left alone and the centre is listed in centres-report.md so a person can update it
Promotions past their valid_until date are also listed.
Writes GITHUB_OUTPUT problems=<count> when running in GitHub Actions.
"""
import datetime
import json
import os
import re

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
# (file in site-data/, list keys inside it) - every entry needs name, source_url and price_from_rm.
# delivery.json entries with "auto_check": false (price only in a scanned PDF) are skipped.
SOURCES = [("confinement.json", ["centres"]), ("delivery.json", ["private", "university"])]
REPORT = os.path.join(HERE, "..", "centres-report.md")
TODAY = datetime.date.today().isoformat()


def digits(text):
    return re.sub(r"[,\s]", "", text)


def main():
    files = {}
    for fname, keys in SOURCES:
        with open(os.path.join(HERE, "..", "site-data", fname), encoding="utf-8") as f:
            files[fname] = (json.load(f), keys)
    entries = [c for data, keys in files.values() for k in keys for c in data.get(k, [])
               if c.get("price_from_rm") and c.get("auto_check", True)]
    problems, ok = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                            "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"))
        for c in entries:
            # Only the "from" price must be on the source page (top room prices are often on other pages).
            want = [c["price_from_rm"]]
            try:
                page.goto(c["source_url"], wait_until="domcontentloaded", timeout=60000)
                try:
                    page.wait_for_load_state("networkidle", timeout=20000)
                except Exception:
                    pass
                # Visible text plus the page source: some prices sit in tabs/accordions that are hidden until clicked.
                text = digits(page.inner_text("body")) + digits(page.content())
                missing = [str(p) for p in want if str(p) not in text]
                if missing:
                    problems.append(f"- **{c['name']}**: price RM{', RM'.join(missing)} is no longer on {c['source_url']} "
                                    "- the price may have changed or the page moved.")
                else:
                    c["checked"] = TODAY
                    ok.append(c["name"])
            except Exception as e:  # page down, timeout, blocked
                problems.append(f"- **{c['name']}**: could not open {c['source_url']} ({type(e).__name__}).")
            if c.get("valid_until") and TODAY > c["valid_until"]:
                problems.append(f"- **{c['name']}**: its promotion ended on {c['valid_until']} - check the normal price.")
        browser.close()

    for fname, (data, _keys) in files.items():
        with open(os.path.join(HERE, "..", "site-data", fname), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

    lines = [f"Automatic price check on {TODAY}.", "",
             f"Still correct ({len(ok)}): " + (", ".join(ok) if ok else "none") + ".", ""]
    if problems:
        lines += ["Need a person to look (update `site-data/confinement.json` or `site-data/delivery.json`, or remove the entry):", ""] + problems
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"problems={len(problems)}\n")


if __name__ == "__main__":
    main()
