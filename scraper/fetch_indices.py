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

_BIZPORTAL_INDEX_BASE = "https://www.bizportal.co.il/capitalmarket/indices/generalview"

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
    {
        "name":  "אינדקס תעשיות ביטחוניות ישראל",
        "short": "TAASIYOT",
        "url":   f"{_BIZPORTAL_INDEX_BASE}/2160",
        "tapUrl": f"{_BIZPORTAL_INDEX_BASE}/2160",
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

    The page embeds the current price in:
        <div id="paper_rate" ...><span class="num">4,212.5</span>
    and the daily change in:
        <div id="paper_change" ...><span class="drop/rise" ...>
            <span class="num">-4.22%</span>

    Bizportal's /capitalmarket/indices/generalview pages use the same ids.
    """
    # Current price
    price_m = re.search(
        r'id="paper_rate"[^>]*>.*?<span class="num">([\d,]+\.?\d*)</span>',
        html, re.DOTALL
    )
    # Daily % change  (sign is embedded in the value, e.g. "-4.22%" or "2.36%")
    pct_m = re.search(
        r'id="paper_change"[^>]*>.*?<span class="num">([-+]?[\d,]+\.?\d*)%</span>',
        html, re.DOTALL
    )

    if not (price_m and pct_m):
        return None

    price = float(price_m.group(1).replace(",", ""))
    pct_num = round(float(pct_m.group(1).replace(",", "")), 4)

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
