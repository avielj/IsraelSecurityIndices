# 📈 Israel Security Indices Widget

Live home-screen widget (iOS + Android) for two Israeli defence/infrastructure indices:

| Index | Short | indx.co.il |
|-------|-------|-----------|
| מדד בטחוניות | BITCHONI | [2160-index](https://indx.co.il/index/2160-index/) |
| מדד תשתיות  | TASHTIOT | [2156-index](https://indx.co.il/index/2156-index/) |

Data is scraped from [indx.co.il](https://indx.co.il) every **15 minutes** by GitHub Actions and written to [`data.json`](data.json) in this repo.  
The widgets just fetch that file — no backend server required.

---

## How it works

```
GitHub Actions (scrape.yml)
  └─ runs scraper/fetch_indices.py every 15 min (Sun-Thu, market hours)
       └─ commits data.json to main branch
            └─ iOS widget (Scriptable)  ──┐
            └─ Android widget (PWA)     ──┘  both fetch data.json via raw.githubusercontent.com
```

---

## iOS — Scriptable Widget

### Requirements
- [Scriptable](https://apps.apple.com/app/scriptable/id1405459188) (free, App Store)

### Setup
1. Make sure this repo is **public** on GitHub (raw URLs must be accessible without auth).
2. Open Scriptable → **+** → paste the contents of [`IsraelSecurityIndices.js`](IsraelSecurityIndices.js).
3. Verify `DATA_URL` at the top of the script points to your fork:
   ```js
   const DATA_URL = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data.json";
   ```
4. Long-press your iOS home screen → **+** → **Scriptable** → choose **Small**, **Medium** or **Large**.
5. Edit the widget → select the script → tap **Done**.

### Widget sizes
| Size | Shows |
|------|-------|
| Small | Single index (first one) |
| Medium | Both indices side-by-side *(recommended)* |
| Large | Both indices stacked with separator |

---

## Android — PWA Shortcut Widget

Android doesn't have a Scriptable equivalent, but the included [`android/widget.html`](android/widget.html) is a **self-contained Progressive Web App** page that mimics the iOS widget look and can be pinned to your home screen.

### Setup
1. Enable GitHub Pages on the repo: **Settings → Pages → Branch: main / (root) → Save**.
2. Open this URL in **Chrome** on your Android phone:
   ```
   https://avielj.github.io/IsraelSecurityIndices/android/widget.html
   ```
3. Tap **⋮ → "Add to Home screen"** and confirm.

### KWGT / Tasker (advanced)
If you prefer a native homescreen widget (no browser):

**KWGT** formula to fetch the price:
```
$df(http_get("https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data.json"), "json", "indices[0].price")$
```

**Tasker** — use *HTTP Request* action with the raw URL, then parse with `JsonExtract` variable and push to a **Tasker Widget**.

---

## Data format (`data.json`)

```json
{
  "updatedAt": "2026-05-01T15:41:59Z",
  "indices": [
    {
      "name":     "מדד בטחוניות",
      "short":    "BITCHONI",
      "url":      "https://indx.co.il/index/2160-index/",
      "tapUrl":   "https://indx.co.il/index/2160-index/",
      "price":    "1,234.56",
      "pct":      "+1.23%",
      "pctNum":   1.23,
      "positive": true,
      "ok":       true
    },
    { "...": "same shape for TASHTIOT" }
  ]
}
```

`ok: false` means the scraper couldn't parse the page — the widgets fall back to `"—"`.

---

## Repository structure

```
.
├── IsraelSecurityIndices.js   ← Scriptable iOS widget script
├── data.json                  ← Auto-updated by CI; consumed by both widgets
├── android/
│   └── widget.html            ← Android PWA widget
├── scraper/
│   ├── fetch_indices.py       ← Scraper (run by GitHub Actions)
│   └── test_sources.py        ← Manual test harness for data sources
└── .github/
    └── workflows/
        └── scrape.yml         ← GitHub Actions workflow (every 15 min)
```

---

## GitHub Actions workflow

The workflow ([`.github/workflows/scrape.yml`](.github/workflows/scrape.yml)) runs on a cron:
- **Every 15 minutes**, Sunday–Thursday, **08:00–18:00 Israel time** (05:00–15:00 UTC)
- Can be triggered manually from the **Actions** tab

It checks out the repo, runs `scraper/fetch_indices.py`, and commits `data.json` back only when its content changed.

---

## Running the scraper locally

```bash
# from repo root
python scraper/fetch_indices.py
```

To test which data sources are reachable:
```bash
python scraper/test_sources.py
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Widget shows `—` for all values | `ok: false` in data.json → check Actions logs |
| Data is stale (>30 min old) | Actions workflow may be paused — re-enable it in the GitHub UI |
| iOS widget doesn't refresh | Scriptable respects iOS background refresh limits; open the app once |
| Android page not found | Ensure GitHub Pages is enabled and the URL matches |

---

## License

MIT — feel free to fork and adapt.
