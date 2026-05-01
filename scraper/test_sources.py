#!/usr/bin/env python3
"""Test which data sources work for scraping fund/index prices."""
import urllib.request
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

ID1 = "5141882"
ID2 = "5130604"

SOURCES = [
    ("funder",    f"https://www.funder.co.il/fund/{ID1}"),
    ("bizportal", f"https://www.bizportal.co.il/capitalmarket/quote/generalview/{ID1}"),
    ("sponser",   f"https://www.sponser.co.il/Stock.aspx?id={ID1}"),
    ("globes",    f"https://www.globes.co.il/portal/instrument.aspx?instrumentid={ID1}"),
    ("funder2",   f"https://www.funder.co.il/fund/{ID2}"),
    ("sponser2",  f"https://www.sponser.co.il/Stock.aspx?id={ID2}"),
]

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode("utf-8", errors="ignore"), r.geturl()

for name, url in SOURCES:
    try:
        html, final_url = fetch(url)
        prices = re.findall(r'[\d,]{2,7}\.\d{2}', html)
        pcts   = re.findall(r'[+-]?\d{1,3}\.\d{2}%', html)
        print(f"\n{'='*60}")
        print(f"[{name}] {final_url[:80]}")
        print(f"  HTML len: {len(html)}")
        print(f"  Prices:   {prices[:8]}")
        print(f"  Pcts:     {pcts[:8]}")
        # show 200 chars around first price hit
        m = re.search(r'[\d,]{3,7}\.\d{2}', html)
        if m:
            s = max(0, m.start()-80)
            print(f"  Context:  {repr(html[s:s+180])}")
    except Exception as e:
        print(f"\n[{name}] ERROR: {e}")
