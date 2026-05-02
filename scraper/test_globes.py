import urllib.request, ssl

ctx = ssl.create_default_context()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.globes.co.il/",
}
for url in [
    "https://b.globes.co.il/bdigital/GTOFeeder.ashx?type=indx&id=2160",
    "https://b.globes.co.il/bdigital/GTOFeeder.ashx?type=indx&id=2156",
    "http://b.globes.co.il/bdigital/GTOFeeder.ashx?type=indx&id=2160",
]:
    try:
        req = urllib.request.Request(url, headers=headers)
        kw = {"context": ctx} if url.startswith("https") else {}
        with urllib.request.urlopen(req, timeout=10, **kw) as r:
            body = r.read().decode("utf-8", errors="replace")
            print(f"OK {url}")
            print(f"  {body[:400]}")
    except Exception as e:
        print(f"ERR {url}: {e}")
