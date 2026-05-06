#!/usr/bin/env python3
"""
Scrapes מדד ת"א בטחוניות and אינדקס תשתיות לאומיות from bizportal.co.il
and writes /data.json to the repo root.
Run by GitHub Actions every 15 minutes during market hours.

Requires:  pip install curl-cffi
  curl_cffi impersonates Chrome's TLS fingerprint, bypassing Cloudflare's
  bot detection that blocks Python urllib/requests from datacenter IPs.
"""
import json
import re
import sys
from datetime import datetime, timezone

try:
    from curl_cffi import requests as cffi_requests
    _USE_CFFI = True
except ImportError:
    import urllib.request
    _USE_CFFI = False

_BIZPORTAL_BASE = "https://www.bizportal.co.il/capitalmarket/quote/indice"

INDICES = [
    {
        "name":  "מדד ת\"א בטחוניות",
        "short": "BITCHONI",
        "url":   f"{_BIZPORTAL_BASE}/785",
        "tapUrl": f"{_BIZPORTAL_BASE}/785",
    },
    {
        "name":  "תשתיות לאומיות",
        "short": "TASHTIOT",
        "url":   f"{_BIZPORTAL_BASE}/2126",
        "tapUrl": f"{_BIZPORTAL_BASE}/2126",
    },
]

# Fallback headers for urllib (used when curl_cffi is unavailable)
_URLLIB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Referer": "https://www.bizportal.co.il/",
}


def fetch(url: str) -> str:
    """Fetch URL, impersonating Chrome via curl_cffi if available."""
    if _USE_CFFI:
        r = cffi_requests.get(url, impersonate="chrome124", timeout=20,
                              headers={"Referer": "https://www.bizportal.co.il/"})
        r.raise_for_status()
        return r.text
    # Fallback: stdlib urllib with browser-like headers
    import gzip
    req = urllib.request.Request(url, headers=_URLLIB_HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        raw = r.read()
        if r.info().get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8")


def parse(html: str) -> dict:
    """
    Parse price and daily % change from a Bizportal index page.

    The page contains a summary line like:
        8,196.48 -3.86% נכון ל: 06/05/2026
    and a detail row:
        שער בסיס  8,525.26

    We extract the price from the summary line and calculate the exact
    percentage from (current - base) / base * 100 so we keep full precision.
    """
    # Current price + displayed % (used as fallback)
    summary_m = re.search(
        r'([\d,]+\.\d+)\s+([-+]?\d+(?:\.\d+)?)%\s*נכון ל:',
        html,
    )
    # Base price (שער בסיס / שער אחרון בסיס)
    base_m = re.search(r'שער בסיס[^\d]*([\d,]+\.\d+)', html)

    if not summary_m:
        return None

    price_str = summary_m.group(1).replace(",", "")
    price = float(price_str)

    if base_m:
        base = float(base_m.group(1).replace(",", ""))
        pct_num = round((price - base) / base * 100, 4) if base else 0.0
    else:
        # fall back to the displayed percentage
        pct_num = round(float(summary_m.group(2)), 4)

    return {
        "price":    f"{price:,.2f}",
        "pct":      f"{'+' if pct_num >= 0 else ''}{pct_num:.2f}%",
        "pctNum":   pct_num,
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
        # Print errors but don't fail the workflow — partial data is still useful.
        # The widget gracefully handles ok=false entries by showing "—".
        print("WARNINGS (partial failures):", errors, file=sys.stderr)


if __name__ == "__main__":
    main()
