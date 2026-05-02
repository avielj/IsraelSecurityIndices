#!/usr/bin/env python3
"""Find working data sources for the two indices."""
import urllib.request, re, json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

def fetch(url, extra_headers=None):
    h = dict(HEADERS)
    if extra_headers:
        h.update(extra_headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=12) as r:
        import gzip
        raw = r.read()
        try:
            data = gzip.decompress(raw)
        except Exception:
            data = raw
        return data.decode("utf-8", errors="replace"), r.geturl()

# --- TASE index list API (no auth needed, just needs right headers) ---
tase_urls = [
    ("tase-index-list", "https://www.tase.co.il/umbraco/api/DataApi/GetIndexMembersList?indexId=2160&lang=he"),
    ("tase-index-data", "https://www.tase.co.il/umbraco/api/DataApi/GetIndexData?indexId=2160&lang=he"),
    ("tase-main",       "https://www.tase.co.il/he/market_data/index/2160/major_data"),
    ("maya",            "https://mayaapi.tase.co.il/api/index/alldata?IndexId=2160"),
    ("bizportal-2160",  "https://www.bizportal.co.il/capitalmarket/quote/generalview/2160"),
    ("bizportal-fund1", "https://www.bizportal.co.il/capitalmarket/quote/generalview/5141882"),
    ("funder-1",        "https://www.funder.co.il/fund/5141882"),
    ("funder-2",        "https://www.funder.co.il/fund/5130604"),
    ("indx-json",       "https://indx.co.il/?rest_route=/indx/v1/index/2160"),
]

for name, url in tase_urls:
    try:
        html, final = fetch(url)
        # Look for price-like patterns
        prices = re.findall(r'[\d,]{3,9}\.\d{2}', html)
        pcts   = re.findall(r'[+-]?\d{1,3}\.\d{1,3}%', html)
        print(f"\n[{name}] {final[:80]}")
        print(f"  len={len(html)}  prices={prices[:5]}  pcts={pcts[:5]}")
        if len(html) < 2000:
            print(f"  body={repr(html[:500])}")
    except Exception as e:
        print(f"\n[{name}] ERROR: {e}")
