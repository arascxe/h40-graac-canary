import { chromium } from "playwright";

const PAGE = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en";
const out = {
  page_ok: false,
  title: null,
  intercepted_api_calls: 0,
  captured_signed_headers: false,
  hashtag_items: [],
  video_items: [],
  errors: [],
};

const browser = await chromium.launch({
  headless: true,
  args: ["--disable-dev-shm-usage", "--no-sandbox"],
});

try {
  const context = await browser.newContext({
    userAgent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36",
    locale: "en-US",
    viewport: { width: 1365, height: 900 },
  });
  const page = await context.newPage();

  page.on("request", (req) => {
    if (!req.url().includes("creative_radar_api")) return;
    out.intercepted_api_calls += 1;
    const h = req.headers();
    if ((h["user-sign"] || h["User-Sign"]) && (h["timestamp"] || h["Timestamp"]) &&
        (h["anonymous-user-id"] || h["web-id"] || h["Web-Id"])) {
      out.captured_signed_headers = true;
    }
  });

  page.on("response", async (resp) => {
    const url = resp.url();
    if (!url.includes("creative_radar_api")) return;
    try {
      const data = await resp.json();
      const d = data?.data || {};
      const list = d?.list || d?.hashtags || d?.videos || [];
      if (!Array.isArray(list)) return;
      for (const item of list.slice(0, 50)) {
        const tag = item?.hashtag_name || item?.hashtag || item?.name;
        if (tag) {
          out.hashtag_items.push({
            hashtag: String(tag).replace(/^#/, ""),
            video_count: item?.video_count ?? null,
            view_count: item?.video_views ?? item?.view_count ?? null,
            trend: item?.trend ?? null,
          });
        }
        const u = item?.item_url || item?.url || item?.share_url;
        if (u) {
          out.video_items.push({
            url: String(u),
            title: String(item?.title || item?.desc || "").slice(0, 300),
            author: String(item?.author_name || item?.creator_name || "").slice(0, 120),
            thumbnail_url: item?.thumbnail_url || item?.cover || item?.cover_url || null,
          });
        }
      }
    } catch (e) {
      out.errors.push("response_parse:" + String(e?.message || e).slice(0, 120));
    }
  });

  const resp = await page.goto(PAGE, { waitUntil: "domcontentloaded", timeout: 60000 });
  out.page_ok = Boolean(resp?.ok());
  out.title = (await page.title()).slice(0, 200);

  // Allow the first-party JS to create signed Creative Center requests.
  await page.waitForTimeout(20000);

  // Small scroll to trigger lazy network activity without interacting with accounts.
  await page.evaluate(() => window.scrollTo(0, Math.max(document.body.scrollHeight / 2, 600)));
  await page.waitForTimeout(8000);

  // Deduplicate output.
  const seenTags = new Set();
  out.hashtag_items = out.hashtag_items.filter(x => {
    const k = x.hashtag.toLowerCase();
    if (seenTags.has(k)) return false;
    seenTags.add(k); return true;
  }).slice(0, 50);
  const seenUrls = new Set();
  out.video_items = out.video_items.filter(x => {
    if (seenUrls.has(x.url)) return false;
    seenUrls.add(x.url); return true;
  }).slice(0, 50);

  await context.close();
} catch (e) {
  out.errors.push((e?.name || "Error") + ":" + String(e?.message || e).slice(0, 240));
} finally {
  await browser.close();
}

console.log(JSON.stringify(out));
