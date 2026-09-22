import { JSDOM, VirtualConsole } from "jsdom";

const PAGE = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en";
const API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list?page=1&limit=20&period=7&country_code=US&sort_by=popular";
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36";

const out = {
  page_ok: false,
  captured: { anonymous_user_id: false, timestamp: false, user_sign: false },
  api_ok: false,
  api_code: null,
  item_count: 0,
  error: null,
};

try {
  const pageRes = await fetch(PAGE, {
    headers: { "user-agent": UA, "accept": "text/html,application/xhtml+xml" },
    redirect: "follow",
  });
  const body = await pageRes.text();
  out.page_ok = pageRes.ok && body.length > 1000;

  const captured = {};
  const vconsole = new VirtualConsole();
  vconsole.on("jsdomError", () => {});
  vconsole.on("error", () => {});

  const dom = new JSDOM(body, {
    url: PAGE,
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    virtualConsole: vconsole,
    beforeParse(window) {
      const proto = window.XMLHttpRequest?.prototype;
      if (proto) {
        const originalSet = proto.setRequestHeader;
        proto.setRequestHeader = function(name, value) {
          const k = String(name || "").toLowerCase();
          if (["anonymous-user-id", "timestamp", "user-sign", "web-id"].includes(k)) {
            captured[k] = String(value || "");
          }
          try { return originalSet.call(this, name, value); } catch { return undefined; }
        };
      }
    },
  });

  const deadline = Date.now() + 25000;
  while (Date.now() < deadline) {
    if ((captured["anonymous-user-id"] || captured["web-id"]) && captured["timestamp"] && captured["user-sign"]) break;
    await new Promise(r => setTimeout(r, 500));
  }
  dom.window.close();

  out.captured.anonymous_user_id = Boolean(captured["anonymous-user-id"] || captured["web-id"]);
  out.captured.timestamp = Boolean(captured["timestamp"]);
  out.captured.user_sign = Boolean(captured["user-sign"]);

  if (out.captured.anonymous_user_id && out.captured.timestamp && out.captured.user_sign) {
    const headers = {
      "user-agent": UA,
      "accept": "application/json, text/plain, */*",
      "referer": PAGE,
      "timestamp": captured["timestamp"],
      "user-sign": captured["user-sign"],
      "anonymous-user-id": captured["anonymous-user-id"] || captured["web-id"],
      "web-id": captured["web-id"] || captured["anonymous-user-id"],
    };
    const apiRes = await fetch(API, { headers });
    const data = await apiRes.json().catch(() => ({}));
    out.api_code = data?.code ?? apiRes.status;
    const items = data?.data?.list ?? data?.data?.hashtags ?? [];
    out.item_count = Array.isArray(items) ? items.length : 0;
    out.api_ok = apiRes.ok && out.api_code === 0 && out.item_count > 0;
  }
} catch (e) {
  out.error = `${e?.name || "Error"}:${String(e?.message || e).slice(0,180)}`;
}

console.log(JSON.stringify(out));
if (!out.page_ok) process.exitCode = 2;

// smoke-trigger v2
