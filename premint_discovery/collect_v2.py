#!/usr/bin/env python3
"""
FEE100K Pre-Mint Discovery V2 — zero-cost public-source R&D collector.

Purpose:
- Break the Bluesky-only discovery bias.
- Add direct/public discovery sensors for Reddit RSS, TikTok Creative Center,
  and YouTube search/Shorts-style fresh video discovery.
- Keep raw discovery separate from financializability/canonical-vacancy decisions.
- Never auto-launch. Never store account handles; actor identifiers are hashed.

This file is intentionally isolated from propagation/collect.py until smoke-tested.
"""
import argparse
import asyncio
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import websockets

UA = "fee100k-premint-discovery/2.0 (+github-actions)"
JETSTREAM = "wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

MASTODON_TIMELINES = [
    "https://mastodon.world/api/v1/timelines/public?limit=40",
    "https://mstdn.social/api/v1/timelines/public?limit=40",
    "https://mas.to/api/v1/timelines/public?limit=40",
]

# Broad discovery + meme/viral-heavy surfaces. RSS is public and keyless.
REDDIT_FEEDS = [
    ("all", "rising"),
    ("popular", "rising"),
    ("memes", "rising"),
    ("funny", "rising"),
    ("Unexpected", "rising"),
    ("interestingasfuck", "rising"),
    ("MadeMeSmile", "rising"),
    ("AnimalsBeingDerps", "rising"),
    ("shitposting", "rising"),
]

TIKTOK_HASHTAG_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/hashtag/list"
TIKTOK_VIDEO_API = "https://ads.tiktok.com/creative_radar_api/v1/popular_trend/list"
TIKTOK_REFERER = "https://ads.tiktok.com/business/creativecenter/inspiration/popular/pc/en"
YOUTUBE_SEARCH_API = "https://www.youtube.com/youtubei/v1/search"

ALLOWED_LINK_HOSTS = {
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "instagram.com", "www.instagram.com",
    "x.com", "www.x.com", "twitter.com", "www.twitter.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "reddit.com", "www.reddit.com", "old.reddit.com",
}

# Only these count as creative transformation evidence downstream.
CREATIVE_BUCKETS = {
    "viral", "meme", "remix", "reaction", "template", "parody", "derivative"
}

BUCKET_PATTERNS = {
    "origin_tiktok": ("tiktok.com",),
    "origin_instagram": ("instagram.com",),
    "origin_x": ("x.com/", "twitter.com/"),
    "viral": ("went viral", "goes viral", "gone viral", "viral video", "viral clip", "breaks the internet"),
    "meme": (" meme", "meme ", "memes", "memeable"),
    "remix": ("remix", "remixed", "remixes"),
    "reaction": ("reaction video", "reaction image", "reaction meme"),
    "template": ("template", "green screen"),
    "parody": ("parody", "spoof"),
    "derivative": ("sticker", "fan art", "fanart", "fan account", "edit of", "edits of", "duet", "stitch"),
}

URL_RE = re.compile(r"https?://[^\s<>()\]\[{}\"']+")
HREF_RE = re.compile(r"""href=["'](https?://[^"']+)["']""", re.I)
MENTION_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.-]{1,64}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
RELATIVE_AGE_RE = re.compile(
    r"(\d+)\s*(second|minute|hour|day|week|month|year)s?\s+ago",
    re.I,
)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:24]

def request_bytes(url: str, *, headers=None, data=None, timeout=15):
    hdr = {"User-Agent": UA, **(headers or {})}
    req = urllib.request.Request(url, headers=hdr, data=data)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_json(url: str, *, headers=None, timeout=15):
    raw = request_bytes(url, headers={"Accept": "application/json", **(headers or {})}, timeout=timeout)
    return json.loads(raw.decode("utf-8"))

def post_json(url: str, payload: dict, *, headers=None, timeout=15):
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    raw = request_bytes(
        url,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            **(headers or {}),
        },
        data=body,
        timeout=timeout,
    )
    return json.loads(raw.decode("utf-8"))

def clean_text(text: str) -> str:
    text = URL_RE.sub(" ", text or "")
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = PHONE_RE.sub("[redacted-phone]", text)
    text = MENTION_RE.sub("[mention]", text)
    return WS_RE.sub(" ", text).strip()[:500]

def html_to_text(value: str) -> str:
    return WS_RE.sub(" ", html.unescape(TAG_RE.sub(" ", value or ""))).strip()

def allowed_links_from_values(values):
    out = set()
    for raw in values:
        if not isinstance(raw, str):
            continue
        candidates = [raw] if raw.startswith("http") else []
        candidates += URL_RE.findall(raw)
        for candidate in candidates:
            candidate = html.unescape(candidate).rstrip(".,;:!?)]}")
            try:
                u = urllib.parse.urlparse(candidate)
                host = (u.hostname or "").lower()
                if host in ALLOWED_LINK_HOSTS:
                    out.add(candidate[:500])
            except Exception:
                pass
    return sorted(out)[:12]

def recursive_urls(obj):
    vals = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and (k.lower() in {"uri", "url", "href"} or v.startswith("http")):
                vals.append(v)
            elif isinstance(v, (dict, list)):
                vals.extend(recursive_urls(v))
    elif isinstance(obj, list):
        for v in obj:
            vals.extend(recursive_urls(v))
    return vals

def buckets_for(text: str, links):
    hay = (text + " " + " ".join(links)).lower()
    return sorted([name for name, pats in BUCKET_PATTERNS.items() if any(p in hay for p in pats)])

def upsert(rows, *, source, actor_id, post_id, created_at, text, links, buckets):
    if not buckets and not links:
        return False
    ph = h(f"{source}:{post_id}")
    ts = now_iso()
    prev = rows.get(ph)
    if prev:
        prev["last_observed_at"] = ts
        prev["buckets"] = sorted(set((prev.get("buckets") or []) + buckets))
        prev["links"] = sorted(set((prev.get("links") or []) + links))[:12]
        return False
    rows[ph] = {
        "post_hash": ph,
        "actor_hash": h(actor_id) if actor_id else None,
        "created_at": created_at,
        "first_observed_at": ts,
        "last_observed_at": ts,
        "text": clean_text(text),
        "links": links[:12],
        "buckets": sorted(set(buckets)),
        "source": source,
    }
    return True

def parse_jetstream_event(evt):
    if evt.get("kind") == "commit":
        commit = evt.get("commit") or {}
        if commit.get("collection") != "app.bsky.feed.post":
            return None
        if commit.get("operation") not in (None, "create", "update"):
            return None
        record = commit.get("record") or {}
        did = str(evt.get("did") or "")
        rkey = str(commit.get("rkey") or "")
        post_id = f"at://{did}/app.bsky.feed.post/{rkey}" if did and rkey else json.dumps(evt, sort_keys=True)[:1000]
        return did, post_id, record
    payload = evt.get("payload") if evt.get("$type") == "message" else evt
    if isinstance(payload, dict) and str(payload.get("$type", "")).endswith("#commit"):
        if payload.get("collection") != "app.bsky.feed.post":
            return None
        if payload.get("operation") not in (None, "create", "update"):
            return None
        record = payload.get("record") or {}
        did = str(payload.get("did") or "")
        rkey = str(payload.get("rkey") or "")
        post_id = f"at://{did}/app.bsky.feed.post/{rkey}" if did and rkey else json.dumps(payload, sort_keys=True)[:1000]
        return did, post_id, record
    return None

async def collect_jetstream(rows, seconds, health):
    start = time.monotonic()
    messages = matched = created = 0
    error = None
    try:
        async with websockets.connect(
            JETSTREAM,
            max_size=2_000_000,
            ping_interval=20,
            ping_timeout=20,
            open_timeout=15,
            close_timeout=5,
        ) as ws:
            while time.monotonic() - start < seconds:
                remain = max(1, seconds - (time.monotonic() - start))
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=min(15, remain))
                except asyncio.TimeoutError:
                    continue
                if isinstance(raw, bytes):
                    continue
                messages += 1
                try:
                    evt = json.loads(raw)
                except Exception:
                    continue
                parsed = parse_jetstream_event(evt)
                if not parsed:
                    continue
                did, post_id, record = parsed
                text = str(record.get("text") or "")
                links = allowed_links_from_values([text] + recursive_urls(record))
                buckets = buckets_for(text, links)
                if not buckets and not links:
                    continue
                matched += 1
                if upsert(
                    rows,
                    source="bluesky_jetstream",
                    actor_id=did,
                    post_id=post_id,
                    created_at=record.get("createdAt"),
                    text=text,
                    links=links,
                    buckets=buckets,
                ):
                    created += 1
    except Exception as e:
        error = f"{type(e).__name__}:{str(e)[:160]}"
    health.append({
        "source": "bluesky_jetstream",
        "ok": error is None,
        "seconds": round(time.monotonic() - start, 1),
        "messages": messages,
        "matched": matched,
        "new_items": created,
        **({"error": error} if error else {}),
    })

def collect_mastodon(rows, health):
    for url in MASTODON_TIMELINES:
        host = urllib.parse.urlparse(url).hostname or "mastodon"
        matched = created = 0
        try:
            statuses = fetch_json(url, timeout=10)
            for st in statuses if isinstance(statuses, list) else []:
                content_html = str(st.get("content") or "")
                text = html_to_text(content_html)
                links = allowed_links_from_values([content_html] + HREF_RE.findall(content_html))
                buckets = buckets_for(text, links)
                if not buckets and not links:
                    continue
                matched += 1
                account = st.get("account") or {}
                actor_id = str(account.get("uri") or account.get("url") or account.get("id") or "")
                post_id = str(st.get("uri") or st.get("url") or st.get("id") or "")
                if not post_id:
                    continue
                if upsert(
                    rows,
                    source=f"mastodon_public:{host}",
                    actor_id=actor_id,
                    post_id=post_id,
                    created_at=st.get("created_at"),
                    text=text,
                    links=links,
                    buckets=buckets,
                ):
                    created += 1
            health.append({"source": f"mastodon_public:{host}", "ok": True, "matched": matched, "new_items": created})
        except Exception as e:
            health.append({"source": f"mastodon_public:{host}", "ok": False, "error": f"{type(e).__name__}:{str(e)[:140]}"})

def collect_reddit_rss(rows, health):
    total = created = 0
    errors = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for subreddit, feed in REDDIT_FEEDS:
        url = f"https://old.reddit.com/r/{subreddit}/{feed}.rss?limit=20"
        try:
            raw = request_bytes(
                url,
                headers={"Accept": "application/atom+xml,application/xml,text/xml;q=0.9"},
                timeout=12,
            )
            root = ET.fromstring(raw)
            for entry in root.findall(".//atom:entry", ns)[:20]:
                title = entry.findtext("atom:title", "", ns) or ""
                entry_id = entry.findtext("atom:id", "", ns) or ""
                updated = entry.findtext("atom:updated", "", ns) or None
                author = entry.findtext("atom:author/atom:name", "", ns) or ""
                content = entry.findtext("atom:content", "", ns) or ""
                link_el = entry.find("atom:link", ns)
                permalink = link_el.get("href", "") if link_el is not None else ""
                links = allowed_links_from_values([permalink, content] + HREF_RE.findall(content))
                text = f"{title} {html_to_text(content)}"
                buckets = buckets_for(text, links)
                total += 1
                if upsert(
                    rows,
                    source=f"reddit_rss:r/{subreddit}:{feed}",
                    actor_id=author,
                    post_id=entry_id or permalink or title,
                    created_at=updated,
                    text=text,
                    links=links,
                    buckets=buckets,
                ):
                    created += 1
        except Exception as e:
            errors.append(f"r/{subreddit}:{type(e).__name__}:{str(e)[:80]}")
    health.append({
        "source": "reddit_rss",
        "ok": len(errors) < len(REDDIT_FEEDS),
        "feeds": len(REDDIT_FEEDS),
        "matched": total,
        "new_items": created,
        **({"errors": errors[:4]} if errors else {}),
    })

def collect_tiktok_creative_center(rows, health):
    tags = []
    tag_created = 0
    video_created = 0
    errors = []
    common_headers = {
        "Referer": TIKTOK_REFERER,
        "Accept": "application/json",
    }

    try:
        qs = urllib.parse.urlencode({
            "page": 1, "limit": 30, "period": 7,
            "country_code": "US", "sort_by": "popular",
        })
        data = fetch_json(f"{TIKTOK_HASHTAG_API}?{qs}", headers=common_headers, timeout=15)
        items = ((data.get("data") or {}).get("list") or [])
        for item in items:
            tag = str(item.get("hashtag_name") or "").strip().lstrip("#")
            if not tag:
                continue
            tags.append(tag)
            url = f"https://www.tiktok.com/tag/{urllib.parse.quote(tag)}"
            text = (
                f"#{tag} TikTok Creative Center trend "
                f"videos={item.get('video_count', 0)} "
                f"views={item.get('video_views', item.get('view_count', 0))} "
                f"trend={item.get('trend', 0)}"
            )
            if upsert(
                rows,
                source="tiktok_creative_center:hashtag",
                actor_id=None,
                post_id=f"hashtag:{tag.lower()}",
                created_at=now_iso(),
                text=text,
                links=[url],
                buckets=["trend_seed"],
            ):
                tag_created += 1
    except Exception as e:
        errors.append(f"hashtags:{type(e).__name__}:{str(e)[:120]}")

    # Best-effort direct trending-video endpoint. Some TikTok deployments require
    # dynamic headers; failure is recorded and never treated as success.
    try:
        qs = urllib.parse.urlencode({
            "page": 1, "limit": 30, "period": 7,
            "country_code": "US", "order_by": "vv",
        })
        data = fetch_json(f"{TIKTOK_VIDEO_API}?{qs}", headers=common_headers, timeout=15)
        d = data.get("data") or {}
        videos = d.get("videos") or d.get("list") or []
        for item in videos:
            url = str(item.get("item_url") or item.get("url") or "").strip()
            title = str(item.get("title") or item.get("desc") or "").strip()
            if not url:
                continue
            links = allowed_links_from_values([url])
            if not links:
                continue
            actor = str(item.get("author_name") or item.get("author") or item.get("creator_name") or "")
            post_id = str(item.get("item_id") or item.get("id") or url)
            buckets = buckets_for(title, links)
            if upsert(
                rows,
                source="tiktok_creative_center:video",
                actor_id=actor,
                post_id=post_id,
                created_at=now_iso(),
                text=title,
                links=links,
                buckets=buckets + ["direct_video_seed"],
            ):
                video_created += 1
    except Exception as e:
        errors.append(f"videos:{type(e).__name__}:{str(e)[:120]}")

    health.append({
        "source": "tiktok_creative_center",
        "ok": bool(tags) or video_created > 0,
        "hashtags": len(tags),
        "hashtag_items": tag_created,
        "video_items": video_created,
        **({"errors": errors} if errors else {}),
    })
    return tags[:8]

def parse_relative_age_seconds(value: str):
    if not value:
        return None
    m = RELATIVE_AGE_RE.search(value)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2).lower()
    mult = {
        "second": 1, "minute": 60, "hour": 3600,
        "day": 86400, "week": 604800,
        "month": 2592000, "year": 31536000,
    }[unit]
    return n * mult

def parse_youtube_video_renderers(data):
    contents = (
        data.get("contents", {})
        .get("twoColumnSearchResultsRenderer", {})
        .get("primaryContents", {})
        .get("sectionListRenderer", {})
        .get("contents", [])
    )
    for section in contents:
        for item in section.get("itemSectionRenderer", {}).get("contents", []):
            video = item.get("videoRenderer") or {}
            if video.get("videoId"):
                yield video

def collect_youtube_discovery(rows, health, seed_tags):
    queries = ["viral meme", "internet meme", "remix", "parody", "funny shorts"]
    queries += [f"#{x}" for x in seed_tags[:3]]
    created = matched = 0
    errors = []
    for query in queries:
        payload = {
            "context": {
                "client": {
                    "clientName": "WEB",
                    "clientVersion": "2.20260920.00.00",
                    "hl": "en",
                    "gl": "US",
                }
            },
            "query": query,
        }
        try:
            data = post_json(YOUTUBE_SEARCH_API, payload, timeout=15)
            for video in parse_youtube_video_renderers(data):
                video_id = str(video.get("videoId") or "")
                if not video_id:
                    continue
                title = " ".join(
                    str(x.get("text") or "")
                    for x in (video.get("title", {}).get("runs") or [])
                ).strip()
                channel = " ".join(
                    str(x.get("text") or "")
                    for x in (video.get("ownerText", {}).get("runs") or [])
                ).strip()
                published = str(video.get("publishedTimeText", {}).get("simpleText") or "")
                age_s = parse_relative_age_seconds(published)
                # Discovery is about birth, not evergreen relevance.
                if age_s is not None and age_s > 48 * 3600:
                    continue
                created_at = None
                if age_s is not None:
                    created_at = (datetime.now(timezone.utc) - timedelta(seconds=age_s)).isoformat()
                url = f"https://www.youtube.com/watch?v={video_id}"
                text = f"{title} {published} query={query}"
                buckets = buckets_for(text, [url])
                matched += 1
                if upsert(
                    rows,
                    source="youtube_fresh_search",
                    actor_id=channel,
                    post_id=video_id,
                    created_at=created_at,
                    text=text,
                    links=[url],
                    buckets=buckets + ["discovery_seed"],
                ):
                    created += 1
        except Exception as e:
            errors.append(f"{query}:{type(e).__name__}:{str(e)[:90]}")
        time.sleep(0.15)
    health.append({
        "source": "youtube_fresh_search",
        "ok": matched > 0,
        "queries": len(queries),
        "matched": matched,
        "new_items": created,
        **({"errors": errors[:4]} if errors else {}),
    })

def collect_direct_sources(rows, health):
    collect_mastodon(rows, health)
    collect_reddit_rss(rows, health)
    seed_tags = collect_tiktok_creative_center(rows, health)
    collect_youtube_discovery(rows, health, seed_tags)

def select_stratified(rows, limit=800):
    """Prevent Bluesky volume from crowding direct birth-surface sensors."""
    items = list(rows.values())
    items.sort(key=lambda x: str(x.get("last_observed_at") or ""), reverse=True)

    groups = {
        "bluesky": [],
        "reddit": [],
        "youtube": [],
        "tiktok": [],
        "mastodon": [],
        "other": [],
    }
    for item in items:
        src = str(item.get("source") or "")
        if src == "bluesky_jetstream":
            groups["bluesky"].append(item)
        elif src.startswith("reddit_"):
            groups["reddit"].append(item)
        elif src.startswith("youtube_"):
            groups["youtube"].append(item)
        elif src.startswith("tiktok_"):
            groups["tiktok"].append(item)
        elif src.startswith("mastodon_"):
            groups["mastodon"].append(item)
        else:
            groups["other"].append(item)

    caps = {
        "bluesky": 420,
        "reddit": 140,
        "youtube": 100,
        "tiktok": 60,
        "mastodon": 60,
        "other": 20,
    }
    out = []
    selected_hashes = set()
    for name, cap in caps.items():
        for item in groups[name][:cap]:
            out.append(item)
            selected_hashes.add(item["post_hash"])

    if len(out) < limit:
        for item in items:
            if item["post_hash"] in selected_hashes:
                continue
            out.append(item)
            if len(out) >= limit:
                break

    out.sort(key=lambda x: str(x.get("last_observed_at") or ""), reverse=True)
    return out[:limit]

async def collect(duration, cycle):
    rows = {}
    health = []

    # Direct public discovery sources refresh every 4th 90s cycle (~6 min).
    run_direct = cycle <= 1 or cycle % 4 == 1
    if run_direct:
        direct_task = asyncio.to_thread(collect_direct_sources, rows, health)
        await asyncio.gather(collect_jetstream(rows, duration, health), direct_task)
    else:
        await collect_jetstream(rows, duration, health)

    items = select_stratified(rows, limit=800)
    actors = len({x["actor_hash"] for x in items if x.get("actor_hash")})
    linked = sum(1 for x in items if x.get("links"))
    creative = sum(1 for x in items if set(x.get("buckets") or []) & CREATIVE_BUCKETS)

    source_mix = {}
    for item in items:
        source_mix[item["source"]] = source_mix.get(item["source"], 0) + 1

    return {
        "schema": "premint_object_discovery_v2",
        "generated_at": now_iso(),
        "window_minutes": round(duration / 60.0, 2),
        "capture_seconds": duration,
        "cycle": cycle,
        "direct_sources_refreshed": run_direct,
        "delivery_mode": "DELTA_STRATIFIED_V2",
        "privacy": {
            "account_handles_stored": False,
            "account_ids_stored": False,
            "actor_identifier": "sha256_truncated",
            "mentions_redacted": True,
            "emails_redacted": True,
            "phones_redacted": True,
            "private_system_data": False,
            "private_strategy_thresholds": False,
        },
        "policy": {
            "auto_launch": False,
            "financializability_decision_in_collector": False,
            "semantic_vacancy_decision_in_collector": False,
            "trend_seed_is_not_demand_proof": True,
        },
        "summary": {
            "items": len(items),
            "independent_actor_hashes": actors,
            "items_with_platform_links": linked,
            "creative_evidence_items": creative,
            "source_mix": source_mix,
        },
        "source_health": health,
        "items": items,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--cycle", type=int, default=1)
    args = ap.parse_args()
    payload = asyncio.run(collect(max(20, min(args.duration, 120)), max(1, args.cycle)))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps(payload["summary"], ensure_ascii=False))

if __name__ == "__main__":
    main()

# smoke-trigger: 2026-09-23T00:00Z
