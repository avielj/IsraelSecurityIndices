#!/usr/bin/env python3
"""
Scrapes מדד בטחוניות and מדד תשתיות from indx.co.il
and writes /data.json to the repo root.
Run by GitHub Actions every 15 minutes during market hours.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

INDICES = [
    {
        "name":  "מדד בטחוניות",
        "short": "BITCHONI",
        "url":   "https://indx.co.il/index/2160-index/",
        "tapUrl":"https://indx.co.il/index/2160-index/",
    },
    {
        "name":  "מדד תשתיות",
        "short": "TASHTIOT",
        "url":   "https://indx.co.il/index/2156-index/",
        "tapUrl":"https://indx.co.il/index/2156-index/",
    },
]

HEADERS = {
    "Accept-Language": "he-IL,he;q=0.9",
    "User-Agent": (
        "Mozilla/5.0 (compatible; GitHubActions; +https://github.com)"
    ),
}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8")


def parse(html: str) -> dict:
    # Price: first data-val after שער אחרון
    pm = re.search(r'שער אחרון</p>[\s\S]{1,200}?data-val="([\d.]+)"', html)
    # Change: data-val + posneg class after שינוי יומי
    cm = re.search(
        r'שינוי יומי</p>[\s\S]{1,300}?class="([^"]*posneg[^"]*)"[^>]*data-val="([\d.]+)"',
        html,
    )
    if not (pm and cm):
        return None

    price = float(pm.group(1))
    cls   = cm.group(1).replace("posneg", "")
    is_neg = bool(re.search(r"\bneg\b", cls))
    pct_num = float(cm.group(2)) * (-1 if is_neg else 1)

    return {
        "price":    f"{price:,.2f}",
        "pct":      f"{'+' if pct_num >= 0 else ''}{pct_num:.2f}%",
        "pctNum":   round(pct_num, 4),
        "positive": pct_num >= 0,
    }


def main():
    results = []
    errors  = []

    for idx in INDICES:
        try:
            html = fetch(idx["url"])
            data = parse(html)
            if data:
                results.append({**idx, **data, "ok": True})
            else:
                raise ValueError("regex matched nothing")
        except Exception as e:
            errors.append(str(e))
            results.append({**idx, "price": "—", "pct": "—", "pctNum": 0, "positive": True, "ok": False})

    payload = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "indices":   results,
    }

    out_path = "data.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    if errors:
        print("ERRORS:", errors, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
