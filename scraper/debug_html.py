from curl_cffi import requests as r

resp = r.get(
    'https://www.bizportal.co.il/capitalmarket/quote/indice/785',
    impersonate='chrome124',
    timeout=20,
    headers={'Referer': 'https://www.bizportal.co.il/'}
)
html = resp.text
print('status:', resp.status_code, 'length:', len(html))

for kw in ['paper_rate', 'paper_change', 'שער בסיס', 'נכון ל']:
    idx = html.find(kw)
    if idx != -1:
        print(f'\n=== {kw} (pos {idx}) ===')
        print(html[max(0, idx-30):idx+250])
