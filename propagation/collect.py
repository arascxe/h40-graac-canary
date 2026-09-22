#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import websockets

UA = "public-propagation-bridge/2.1 (+github-actions)"
JETSTREAM = "wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post"

MASTODON_TIMELINES = [
    "https://mastodon.world/api/v1/timelines/public?limit=40",
    "https://mstdn.social/api/v1/timelines/public?limit=40",
    "https://mas.to/api/v1/timelines/public?limit=40",
]

ALLOWED_LINK_HOSTS = {
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "instagram.com", "www.instagram.com",
    "x.com", "www.x.com", "twitter.com", "www.twitter.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "reddit.com", "www.reddit.com",
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
    "derivative": ("sticker", "fan art", "fanart", "fan account", "edit of", "edits of"),
}

URL_RE = re.compile(r"https?://[^\s<>()\]\[{}\"']+")
HREF_RE = re.compile(r"""href=["'](https?://[^"']+)["']""", re.I)
MENTION_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.-]{1,64}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:24]

def fetch_json(url: str, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

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
        for candidate in URL_RE.findall(raw):
            candidate = html.unescape(candidate).rstrip(".,;:!?)]}")
            try:
                u = urllib.parse.urlparse(candidate)
                host = (u.hostname or "").lower()
                if host in ALLOWED_LINK_HOSTS:
                    out.add(candidate[:500])
            except Exception:
                pass
    return sorted(out)[:10]

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
    ph = h(post_id)
    ts = now_iso()
    prev = rows.get(ph)
    if prev:
        prev["last_observed_at"] = ts
        prev["buckets"] = sorted(set((prev.get("buckets") or []) + buckets))
        prev["links"] = sorted(set((prev.get("links") or []) + links))[:10]
        return False
    rows[ph] = {
        "post_hash": ph,
        "actor_hash": h(actor_id) if actor_id else None,
        "created_at": created_at,
        "first_observed_at": ts,
        "last_observed_at": ts,
        "text": clean_text(text),
        "links": links[:10],
        "buckets": buckets,
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
            health.append({"source": f"mastodon_public:{host}", "ok": False, "error": f"{type(e).__name__}:{str(e)[:120]}"})

async def collect(duration):
    # DELTA MODE: DB is the durable history. Never carry the previous 30-minute snapshot.
    rows = {}
    health = []
    collect_mastodon(rows, health)
    await collect_jetstream(rows, duration, health)

    items = list(rows.values())
    items.sort(key=lambda x: str(x.get("last_observed_at") or ""), reverse=True)
    items = items[:800]
    actors = len({x["actor_hash"] for x in items if x.get("actor_hash")})
    linked = sum(1 for x in items if x.get("links"))

    return {
        "schema": "public_social_propagation_v2",
        "generated_at": now_iso(),
        "window_minutes": round(duration / 60.0, 2),
        "capture_seconds": duration,
        "delivery_mode": "DELTA_ONLY_V2_1",
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
        "summary": {
            "items": len(items),
            "independent_actor_hashes": actors,
            "items_with_platform_links": linked,
            "previous_items_carried": 0,
        },
        "source_health": health,
        "items": items,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--duration", type=int, default=90)
    args = ap.parse_args()
    payload = asyncio.run(collect(max(30, min(args.duration, 120))))
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps(payload["summary"]))

if __name__ == "__main__":
    main()
