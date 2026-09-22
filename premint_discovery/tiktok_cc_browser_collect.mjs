import { chromium } from "playwright";
import fs from "node:fs";

const OUT = process.argv[2] || "/tmp/tiktok-browser-v2.json";
const REGION = process.env.TIKTOK_CC_REGION || "US";
const PERIOD = process.env.TIKTOK_CC_PERIOD || "7";
const BASE = "https://ads.tiktok.com/creative/creativeCenter/trends";
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36";

function metric(v) {
  const s = String(v || "").trim().toUpperCase().replace(/,/g, "");
  const m = s.match(/^([0-9]+(?:\.[0-9]+)?)([KMB])?$/);
  if (!m) return null;
  const n = Number(m[1]);
  const mult = m[2] === "K" ? 1e3 : m[2] === "M" ? 1e6 : m[2] === "B" ? 1e9 : 1;
  return Math.round(n * mult);
}

function parseHashtags(body) {
  const out = [];
  const re = /#([A-Za-z0-9_]{2,64})\s+(.{0,120}?)\s+([0-9]+(?:\.[0-9]+)?[KMB]?)\s+Posts\s+([0-9]+(?:\.[0-9]+)?[KMB]?)\s+Views/gi;
  let m;
  while ((m = re.exec(body)) && out.length < 60) {
    out.push({
      name: m[1],
      category: m[2].trim().slice(0,120),
      posts: metric(m[3]),
      views: metric(m[4]),
      rank: out.length + 1,
      url: "https://www.tiktok.com/tag/" + encodeURIComponent(m[1]),
    });
  }
  return out;
}

const payload = {
  schema: "tiktok_cc_browser_seed_v2",
  generated_at: new Date().toISOString(),
  region: REGION,
  period_days: Number(PERIOD),
  hashtags: [],
  videos: [],
  health: { page_ok: false, video_page_ok: false, errors: [] },
};

const browser = await chromium.launch({ headless: true, args: ["--disable-dev-shm-usage","--no-sandbox"] });
try {
  const ctx = await browser.newContext({ userAgent: UA, locale: "en-US", viewport: {width:1365,height:900} });
  const page = await ctx.newPage();

  try {
    const resp = await page.goto(`${BASE}/hashtag?region=${REGION}&period=${PERIOD}`, {waitUntil:"domcontentloaded", timeout:60000});
    payload.health.page_ok = Boolean(resp?.ok());
    await page.waitForTimeout(16000);
    const body = await page.locator("body").innerText().catch(()=>"");
    payload.hashtags = parseHashtags(body.replace(/\s+/g," "));
  } catch (e) {
    payload.health.errors.push("hashtag:" + String(e?.message || e).slice(0,180));
  }

  try {
    const resp = await page.goto(`${BASE}/video?region=${REGION}&period=${PERIOD}`, {waitUntil:"domcontentloaded", timeout:60000});
    payload.health.video_page_ok = Boolean(resp?.ok());
    await page.waitForTimeout(16000);
    payload.videos = await page.evaluate(() => {
      const seen = new Set();
      const out = [];
      for (const a of Array.from(document.querySelectorAll("a[href]"))) {
        const href = a.href || "";
        if (!/tiktok\.com\/@[^/]+\/video\/\d+/i.test(href)) continue;
        const m = href.match(/\/video\/(\d+)/);
        if (!m || seen.has(m[1])) continue;
        seen.add(m[1]);
        const text = (a.textContent || a.closest("div")?.textContent || "").replace(/\s+/g," ").trim().slice(0,300);
        const img = a.querySelector("img")?.src || a.closest("div")?.querySelector("img")?.src || null;
        out.push({url:href,video_id:m[1],text,thumbnail_url:img});
        if (out.length >= 50) break;
      }
      return out;
    });
  } catch (e) {
    payload.health.errors.push("video:" + String(e?.message || e).slice(0,180));
  }

  await ctx.close();
} finally {
  await browser.close();
}

payload.health.ok = payload.health.page_ok && (payload.hashtags.length > 0 || payload.videos.length > 0);
fs.writeFileSync(OUT, JSON.stringify(payload));
console.log(JSON.stringify({
  ok: payload.health.ok,
  hashtags: payload.hashtags.length,
  videos: payload.videos.length,
  sample_hashtags: payload.hashtags.slice(0,5).map(x=>x.name),
}));
