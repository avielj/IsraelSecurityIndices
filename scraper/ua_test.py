import urllib.request, re, json

HEADERS_GOOD = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8",
}
HEADERS_BOT = {
    "User-Agent": "Mozilla/5.0 (compatible; GitHubActions; +https://github.com)",
    "Accept-Language": "he-IL,he;q=0.9",
}

for name, ua in [("BOT UA (current scraper)", HEADERS_BOT), ("BROWSER UA", HEADERS_GOOD)]:
    try:
        req = urllib.request.Request("https://indx.co.il/index/2160-index/", headers=ua)
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8")
        pm = re.search(r'שער אחרון</p>[\s\S]{1,200}?data-val="([\d.]+)"', html)
        cm = re.search(r'שינוי יומי</p>[\s\S]{1,300}?data-val="([+-]?[\d.]+)"[^>]*data-suf="%"', html)
        print(f"[{name}] len={len(html)} price={pm.group(1) if pm else 'NONE'} pct={cm.group(1) if cm else 'NONE'}")
        if not pm:
            # Check if Cloudflare challenge
            if "cf-browser-verification" in html or "challenge" in html[:1000].lower() or "__cf_chl" in html:
                print("  --> CLOUDFLARE CHALLENGE DETECTED")
            else:
                print("  --> first 500:", repr(html[:500]))
    except Exception as e:
        print(f"[{name}] ERROR: {e}")

# Also try Globes proper URL patterns
print()
for url in [
    "https://www.globes.co.il/portal/instrument.aspx?instrumentid=2160",
    "https://www.globes.co.il/portal/instrument.aspx?instrumentid=2156",
]:
    try:
        req = urllib.request.Request(url, headers=HEADERS_GOOD)
        with urllib.request.urlopen(req, timeout=10) as r:
            html = r.read().decode("utf-8", errors="replace")
        prices = re.findall(r'[\d,]{3,9}\.\d{2}', html)
        print(f"Globes {url.split('=')[-1]}: len={len(html)} prices={prices[:5]}")
        if prices:
            # find context
            m = re.search(r"[\d,]{3,9}\.\d{2}", html)
            if m:
                print("  context:", repr(html[max(0,m.start()-80):m.start()+80]))
    except Exception as e:
        print(f"Globes ERR: {e}")
