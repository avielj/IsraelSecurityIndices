// ============================================================
//  IsraelSecurityIndices — Scriptable iOS Widget
//  מדד ת"א בטחוניות     (Bizportal code 785)
//  תשתיות לאומיות ישראל (Bizportal code 2126)
//  אינדקס תעשיות ביטחוניות ישראל (Bizportal index code 2160)
//  מדד ת"א טכנולוגיה 35 (Bizportal index code 790)
//  אינדקס חברות ניהול השקעות ומסחר בישראל (Bizportal index code 2155)
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
    // Append timestamp to bust GitHub's CDN cache (Cache-Control header alone is not enough)
    const req = new Request(DATA_URL + "?t=" + Date.now());
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

function displayName(d) {
  const names = {
    BITCHONI: "ת\"א בטחוניות",
    TASHTIOT: "תשתיות לאומיות",
    TAASIYOT: "תעשיות ביטחוניות",
    TECH35: "ת\"א טכנולוגיה 35",
    INVEST: "ניהול השקעות ומסחר",
  };
  return names[d.short] || d.name;
}

function addChangeBadge(parent, d, fontSize, horizontalPadding) {
  const badge = parent.addStack();
  badge.backgroundColor = clrFor(d);
  badge.cornerRadius = 6;
  badge.setPadding(3, horizontalPadding, 3, horizontalPadding);
  const label = badge.addText(d.pct);
  label.font = Font.boldSystemFont(fontSize);
  label.textColor = C.white;
  label.lineLimit = 1;
  label.minimumScaleFactor = 0.8;
  return badge;
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
  widget.setPadding(12, 14, 12, 14);
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

  widget.addSpacer(8);

  const rows = data.length > 3 ? [data.slice(0, 3), data.slice(3)] : [data];
  for (let ri = 0; ri < rows.length; ri++) {
    const row = widget.addStack();
    row.layoutHorizontally();
    row.spacing = 8;

    for (const d of rows[ri]) {
      const card = row.addStack();
      card.layoutVertically();
      card.backgroundColor = C.card;
      card.cornerRadius = 10;
      card.setPadding(8, 10, 8, 10);
      card.spacing = 3;
      card.url = d.tapUrl;

      const ticker = card.addText(d.short);
      ticker.font = Font.boldSystemFont(10);
      ticker.textColor = C.gray;
      ticker.lineLimit = 1;
      ticker.minimumScaleFactor = 0.75;

      const price = card.addText(d.price);
      price.font = Font.boldSystemFont(d.price.length > 8 ? 14 : 16);
      price.textColor = C.white;
      price.minimumScaleFactor = 0.55;
      price.lineLimit = 1;

      const bw = card.addStack();
      addChangeBadge(bw, d, 10, 6);

      card.addSpacer(1);
      const fn = card.addText(displayName(d));
      fn.font = Font.systemFont(8);
      fn.textColor = C.gray;
      fn.lineLimit = 1;
      fn.minimumScaleFactor = 0.65;
    }

    if (ri < rows.length - 1) {
      widget.addSpacer(7);
    }
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

  const fn = col.addText(displayName(d));
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
  addChangeBadge(bw, d, 13, 8);
}

function buildLarge(widget, data, updatedAt) {
  widget.backgroundColor = C.bg;
  widget.setPadding(16, 20, 16, 20);
  widget.url = data[0].tapUrl;

  const hdr = widget.addStack();
  hdr.layoutHorizontally();
  hdr.centerAlignContent();
  const t = hdr.addText("מדדים");
  t.font = Font.heavySystemFont(22);
  t.textColor = C.white;
  hdr.addSpacer();
  const ts = formatUpdatedAt(updatedAt);
  const tl = hdr.addText(ts ? ts : "");
  tl.font = Font.mediumSystemFont(12);
  tl.textColor = C.gray;

  widget.addSpacer(8);

  for (let i = 0; i < data.length; i++) {
    const d = data[i];
    const row = widget.addStack();
    row.layoutHorizontally();
    row.centerAlignContent();
    row.url = d.tapUrl;

    const nc = row.addStack();
    nc.layoutVertically();
    nc.spacing = 1;
    const tk = nc.addText(d.short);
    tk.font = Font.heavySystemFont(16);
    tk.textColor = C.white;
    tk.lineLimit = 1;
    const fn = nc.addText(displayName(d));
    fn.font = Font.systemFont(11);
    fn.textColor = C.gray;
    fn.lineLimit = 1;
    fn.minimumScaleFactor = 0.85;

    row.addSpacer();

    const rc = row.addStack();
    rc.layoutHorizontally();
    rc.centerAlignContent();
    rc.spacing = 10;

    const price = rc.addText(d.price);
    price.font = Font.heavySystemFont(19);
    price.textColor = C.white;
    price.rightAlignText();
    price.minimumScaleFactor = 0.75;
    price.lineLimit = 1;

    addChangeBadge(rc, d, 12, 9);

    if (i < data.length - 1) {
      widget.addSpacer(8);
      const sep = widget.addStack();
      sep.backgroundColor = C.sep;
      sep.size = new Size(0, 0.5);
      widget.addSpacer(8);
    }
  }
}

// ── Main ──────────────────────────────────────────────────────

async function main() {
  const json = await fetchData();
  const data = json ? json.indices : [
    { name: "מדד ת\"א בטחוניות", short: "BITCHONI", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/quote/indice/785" },
    { name: "תשתיות לאומיות",    short: "TASHTIOT", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/quote/indice/2126" },
    { name: "אינדקס תעשיות ביטחוניות ישראל", short: "TAASIYOT", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/indices/generalview/2160" },
    { name: "מדד ת\"א טכנולוגיה 35", short: "TECH35", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/indices/performance/790" },
    { name: "אינדקס חברות ניהול השקעות ומסחר בישראל", short: "INVEST", price: "—", pct: "—", pctNum: 0, ok: false, tapUrl: "https://www.bizportal.co.il/capitalmarket/indices/generalview/2155" },
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
