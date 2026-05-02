import urllib.request, re

HEADERS = {
    "Accept-Language": "he-IL,he;q=0.9",
    "User-Agent": "Mozilla/5.0 (compatible; GitHubActions; +https://github.com)",
}

for url in ["https://indx.co.il/index/2160-index/", "https://indx.co.il/index/2156-index/"]:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode("utf-8")

    pm = re.search(r'שער אחרון</p>[\s\S]{1,200}?data-val="([\d.]+)"', html)
    cm = re.search(r'שינוי יומי</p>[\s\S]{1,300}?data-val="([+-]?[\d.]+)"[^>]*data-suf="%"', html)
    print(url)
    print("  price match:", pm.group(1) if pm else "NONE")
    print("  pct   match:", cm.group(1) if cm else "NONE")
    if not pm or not cm:
        # show raw context to debug
        for label, pat in [("שער אחרון", r"שער אחרון</p>.{0,400}"), ("שינוי יומי", r"שינוי יומי</p>.{0,400}")]:
            m = re.search(pat, html, re.DOTALL)
            if m:
                print(f"  [{label} raw]:", repr(m.group(0)[:300]))
