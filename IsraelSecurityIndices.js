// ============================================================
//  IsraelSecurityIndices — Scriptable iOS Widget
//  מדד ת"א בטחוניות     (Bizportal code 785)
//  תשתיות לאומיות ישראל (Bizportal code 2126)
//  Styled like the iOS Stocks app (dark, colour-coded badges)
//
//  Data is updated every 15 min by GitHub Actions and stored
//  in data.json in the repo. This widget just fetches that file.
//
//  SETUP (one-time):
//    1. Push this repo to GitHub (must be PUBLIC).
//    2. Replace GITHUB_RAW_URL below with your actual URL.
//    3. Install "Scriptable" from the App Store.
//    4. Paste this script into Scriptable.
//    5. Add a Scriptable widget (Medium size recommended).
// ============================================================

// ── !! SET THIS to your repo's raw data.json URL !! ─────────
//  Format: https://raw.githubusercontent.com/USERNAME/REPO/main/data.json
const DATA_URL = "https://raw.githubusercontent.com/avielj/IsraelSecurityIndices/main/data.json";

// ── Colours (iOS Stocks dark palette) ────────────────────────
const C = {
  bg:      new Color("#000000"),
  card:    new Color("#1c1c1e"),
  green:   new Color("#30d158"),
  red:     new Color("#ff453a"),
  neutral: new Color("#636366"),
  white:   new Color("#ffffff"),
  gray:    new Color("#8e8e93"),
  sep:     new Color("#2c2c2e"),
};

// ── Data fetching ─────────────────────────────────────────────

async function fetchData() {
  try {
    const req = new Request(DATA_URL);
    // bust CDN cache so we always get the latest commit
    req.headers = { "Cache-Control": "no-cache" };
    const json = await req.loadJSON();
    return json; // { updatedAt, indices: [{name,short,price,pct,pctNum,positive,ok,tapUrl}] }
  } catch (_) {
    return null;
  }
}

function clrFor(d) {
  if (!d.ok || d.pct === "—") return C.neutral;
  return d.pctNum >= 0 ? C.green : C.red;
}

// ── Widget builders ───────────────────────────────────────────

function formatUpdatedAt(updatedAt) {
  if (!updatedAt) return "";
  try {
    const d = new Date(updatedAt);
    return d.toLocaleTimeString("he-IL", { hour: "2-digit", minute: "2-digit", timeZone: "Asia/Jerusalem" });
  } catch (_) { return ""; }
}

function buildMedium(widget, data, updatedAt) {
  widget.backgroundColor = C.bg;
  widget.setPadding(16, 16, 16, 16);
  widget.url = data[0].tapUrl;

  // Header
  const hdr = widget.addStack();
  hdr.layoutHorizontally();
  hdr.centerAlignContent();
  const t = hdr.addText("📈  מדדים");
  t.font = Font.boldSystemFont(14);
  t.textColor = C.white;
  hdr.addSpacer();
  const ts = formatUpdatedAt(updatedAt);
  const tl = hdr.addText(ts ? "עודכן " + ts : "");
  tl.font = Font.systemFont(11);
  tl.textColor = C.gray;

  widget.addSpacer(12);

  // Side-by-side cards
  const row = widget.addStack();
  row.layoutHorizontally();
  row.spacing = 10;

  for (const d of data) {
    const card = row.addStack();
    card.layoutVertically();
    card.backgroundColor = C.card;
    card.cornerRadius = 14;
    card.setPadding(12, 14, 12, 14);
    card.spacing = 5;
    card.url = d.tapUrl;

    const ticker = card.addText(d.short);
    ticker.font = Font.boldSystemFont(11);
    ticker.textColor = C.gray;

    const price = card.addText(d.price);
    price.font = Font.boldSystemFont(d.price.length > 8 ? 18 : 22);
    price.textColor = C.white;
    price.minimumScaleFactor = 0.65;
    price.lineLimit = 1;

    const bw = card.addStack();
    bw.backgroundColor = clrFor(d);
    bw.cornerRadius = 6;
    bw.setPadding(3, 8, 3, 8);
    const pl = bw.addText(d.pct);
    pl.font = Font.boldSystemFont(13);
    pl.textColor = C.white;

    card.addSpacer(2);
    const fn = card.addText(d.name);
    fn.font = Font.systemFont(9);
    fn.textColor = C.gray;
    fn.lineLimit = 1;
    fn.minimumScaleFactor = 0.7;
  }
}

function buildSmall(widget, d, updatedAt) {
  widget.backgroundColor = C.card;
  widget.setPadding(14, 16, 14, 16);
  widget.url = d.tapUrl;

  const col = widget.addStack();
  col.layoutVertically();
  col.spacing = 4;

  const tk = col.addText(d.short);
  tk.font = Font.boldSystemFont(13);
  tk.textColor = C.gray;

  const fn = col.addText(d.name);
  fn.font = Font.systemFont(10);
  fn.textColor = C.gray;
  fn.lineLimit = 1;
  fn.minimumScaleFactor = 0.7;

  col.addSpacer();

  const price = col.addText(d.price);
  price.font = Font.boldSystemFont(24);
  price.textColor = C.white;
  price.minimumScaleFactor = 0.6;
  price.lineLimit = 1;

  const bw = col.addStack();
  bw.backgroundColor = clrFor(d);
  bw.cornerRadius = 6;
  bw.setPadding(3, 8, 3, 8);
  const pl = bw.addText(d.pct);
  pl.font = Font.boldSystemFont(13);
  pl.textColor = C.white;
}

function buildLarge(widget, data, updatedAt) {
  widget.backgroundColor = C.bg;
  widget.setPadding(18, 18, 18, 18);
  widget.url = data[0].tapUrl;

  const hdr = widget.addStack();
  hdr.layoutHorizontally();
  hdr.centerAlignContent();
  const t = hdr.addText("מדדים");
  t.font = Font.boldSystemFont(20);
  t.textColor = C.white;
  hdr.addSpacer();
  const ts = formatUpdatedAt(updatedAt);
  const tl = hdr.addText(ts ? "עודכן " + ts : "");
  tl.font = Font.systemFont(12);
  tl.textColor = C.gray;

  widget.addSpacer(16);

  for (let i = 0; i < data.length; i++) {
    const d = data[i];
    const row = widget.addStack();
    row.layoutHorizontally();
    row.centerAlignContent();
    row.url = d.tapUrl;

    const nc = row.addStack();
    nc.layoutVertically();
    nc.spacing = 3;
    const tk = nc.addText(d.short);
    tk.font = Font.boldSystemFont(16);
    tk.textColor = C.white;
    const fn = nc.addText(d.name);
    fn.font = Font.systemFont(11);
    fn.textColor = C.gray;

    row.addSpacer();

    const rc = row.addStack();
    rc.layoutVertically();
    rc.spacing = 4;

    const price = rc.addText(d.price);
    price.font = Font.boldSystemFont(22);
    price.textColor = C.white;
    price.rightAlignText();
    price.minimumScaleFactor = 0.7;

    const br = rc.addStack();
    br.layoutHorizontally();
    br.addSpacer();
    const bw = br.addStack();
    bw.backgroundColor = clrFor(d);
    bw.cornerRadius = 6;
    bw.setPadding(3, 10, 3, 10);
    const pl = bw.addText(d.pct);
    pl.font = Font.boldSystemFont(13);
    pl.textColor = C.white;

    if (i < data.length - 1) {
      widget.addSpacer(14);
      const sep = widget.addStack();
      sep.backgroundColor = C.sep;
      sep.size = new Size(0, 0.5);
      widget.addSpacer(14);
    }
  }
}

// ── Main ──────────────────────────────────────────────────────

async function main() {
  const json = await fetchData();
  const data = json ? json.indices : [
    { name: "מדד ת\"א בטחוניות", short: "BITCHONI", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/quote/indice/785" },
    { name: "תשתיות לאומיות",    short: "TASHTIOT", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/quote/indice/2126" },
  ];
  // updatedAt from the JSON (e.g. "2026-05-01T10:30:00Z") → show as Israel time
  const updatedAt = json ? json.updatedAt : null;

  const widget = new ListWidget();
  // refresh every 15 min to match the GitHub Actions cadence
  widget.refreshAfterDate = new Date(Date.now() + 15 * 60 * 1000);

  const size = config.widgetFamily;
  if      (size === "small")                         buildSmall(widget, data[0], updatedAt);
  else if (size === "large" || size === "extraLarge") buildLarge(widget, data, updatedAt);
  else                                               buildMedium(widget, data, updatedAt);

  if (config.runsInWidget) {
    Script.setWidget(widget);
  } else {
    await widget.presentMedium();
  }
  Script.complete();
}

await main();
