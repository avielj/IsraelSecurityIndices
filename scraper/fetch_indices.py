#!/usr/bin/env python3
"""
Scrapes selected Israeli indices from bizportal.co.il and writes data.json.

RUNS ON THE ISRAELI VPS, NOT GITHUB ACTIONS.
bizportal serves the pages to Israeli IPs but not to GitHub's US runners; the
Action scraped happily for months and wrote "—" for all five indices while
reporting success. Verified 2026-09-04: identical code returns real prices from
the VPS and from a home connection, nothing from CI.

Behaviour differences from the old CI version:
  * A failing index KEEPS its previous value (marked stale) instead of being
    overwritten with "—". A stale number beats no number on the widget.
  * If EVERY index fails, data.json is left untouched and the script exits 1,
    so the failure is loud instead of being committed as dashes.
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

try:
    from curl_cffi import requests as cffi_requests
    _USE_CFFI = True
except ImportError:
    import urllib.request
    import gzip
    _USE_CFFI = False

# NOTE: /capitalmarket/quote/indice/<id> now 301-redirects to
# /capitalmarket/indices/generalview/<id>. Point straight at the target.
_GENERAL = "https://www.bizportal.co.il/capitalmarket/indices/generalview"
_PERF = "https://www.bizportal.co.il/capitalmarket/indices/performance"

INDICES = [
    {"name": 'מדד ת"א בטחוניות',                    "short": "BITCHONI", "url": f"{_GENERAL}/785"},
    {"name": "תשתיות לאומיות",                       "short": "TASHTIOT", "url": f"{_GENERAL}/2126"},
    {"name": "אינדקס תעשיות ביטחוניות ישראל",        "short": "TAASIYOT", "url": f"{_GENERAL}/2160"},
    {"name": 'מדד ת"א טכנולוגיה 35',                 "short": "TECH35",   "url": f"{_PERF}/790"},
    {"name": "אינדקס חברות ניהול השקעות ומסחר בישראל", "short": "INVEST",  "url": f"{_GENERAL}/2155"},
]
for _i in INDICES:
    _i["tapUrl"] = _i["url"]

_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.bizportal.co.il/",
}

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data.json")


def fetch(url: str) -> str:
    if _USE_CFFI:
        r = cffi_requests.get(url, impersonate="chrome124", timeout=25,
                              headers={"Referer": "https://www.bizportal.co.il/"})
        r.raise_for_status()
        return r.text
    req = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read()
        if r.info().get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return raw.decode("utf-8", "replace")


def parse(html: str):
    price_m = re.search(r'id="paper_rate"[^>]*>.*?<span class="num">([\d,]+\.?\d*)</span>',
                        html, re.DOTALL)
    pct_m = re.search(r'id="paper_change"[^>]*>.*?<span class="num">([-+]?[\d,]+\.?\d*)%</span>',
                      html, re.DOTALL)
    if not (price_m and pct_m):
        return None
    price = float(price_m.group(1).replace(",", ""))
    pct_num = round(float(pct_m.group(1).replace(",", "")), 4)
    return {
        "price": f"{price:,.2f}",
        "pct": f"{'+' if pct_num >= 0 else ''}{pct_num:.2f}%",
        "pctNum": pct_num,
        "positive": pct_num >= 0,
    }


def load_previous():
    """Previous values, keyed by `short`, so a blip doesn't wipe the widget."""
    try:
        with open(OUT_PATH, encoding="utf-8") as f:
            return {i["short"]: i for i in json.load(f).get("indices", [])}
    except Exception:
        return {}


def main():
    prev = load_previous()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results, errors, ok_count = [], [], 0

    for idx in INDICES:
        try:
            data = parse(fetch(idx["url"]))
            if not data:
                raise ValueError("regex matched nothing (page markup changed?)")
            results.append({**idx, **data, "ok": True, "stale": False, "lastOkAt": now})
            ok_count += 1
        except Exception as e:
            errors.append(f"{idx['short']}: {e}")
            p = prev.get(idx["short"])
            if p and p.get("price") not in (None, "", "—"):
                # Keep the last good number, flagged stale.
                results.append({**idx,
                                "price": p["price"], "pct": p["pct"],
                                "pctNum": p.get("pctNum", 0),
                                "positive": p.get("positive", True),
                                "ok": False, "stale": True,
                                "lastOkAt": p.get("lastOkAt")})
            else:
                results.append({**idx, "price": "—", "pct": "—", "pctNum": 0,
                                "positive": True, "ok": False, "stale": False,
                                "lastOkAt": None})

    if ok_count == 0:
        # Total failure: leave data.json alone and make noise. Committing dashes
        # over good data is what hid this bug for four months.
        print(f"FATAL: all {len(INDICES)} indices failed, data.json left untouched", file=sys.stderr)
        for e in errors:
            print("  " + e, file=sys.stderr)
        return 1

    payload = {"updatedAt": now, "okCount": ok_count, "total": len(INDICES), "indices": results}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"{now}  ok={ok_count}/{len(INDICES)}  " +
          "  ".join(f"{r['short']}={r['price']}({r['pct']}){'*' if r.get('stale') else ''}"
                    for r in results))
    if errors:
        print("PARTIAL FAILURES:", "; ".join(errors), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
