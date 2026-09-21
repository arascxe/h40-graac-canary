#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts"
UA = "public-propagation-bridge/1.0 (+github-actions)"

QUERY_BUCKETS = [
    ("origin_tiktok", "tiktok.com"),
    ("origin_instagram", "instagram.com"),
    ("origin_x", "x.com"),
    ("viral_phrase", "\"went viral\""),
    ("viral_phrase", "\"goes viral\""),
    ("meme", "meme"),
    ("remix", "remix"),
    ("reaction", "\"reaction video\""),
]

ALLOWED_LINK_HOSTS = (
    "tiktok.com", "www.tiktok.com",
    "instagram.com", "www.instagram.com",
    "x.com", "twitter.com", "www.x.com", "www.twitter.com",
    "youtube.com", "www.youtube.com", "youtu.be",
    "reddit.com", "www.reddit.com",
)

URL_RE = re.compile(r"https?://[^\s<>()\]\[{}\"']+")
MENTION_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_.-]{1,64}")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)")
WS_RE = re.compile(r"\s+")

def h(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:24]

def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))

def clean_text(text: str) -> str:
    text = URL_RE.sub(" ", text or "")
    text = EMAIL_RE.sub("[redacted-email]", text)
    text = PHONE_RE.sub("[redacted-phone]", text)
    text = MENTION_RE.sub("[mention]", text)
    return WS_RE.sub(" ", text).strip()[:500]

def allowed_links(text: str, post: dict):
    candidates = list(URL_RE.findall(text or ""))
    embed = post.get("embed") or {}
    ext = embed.get("external") if isinstance(embed, dict) else None
    if isinstance(ext, dict) and ext.get("uri"):
        candidates.append(str(ext["uri"]))
    out = []
    for raw in candidates:
        raw = raw.rstrip(".,;:!?)]}")
        try:
            u = urllib.parse.urlparse(raw)
            host = (u.hostname or "").lower()
            if host in ALLOWED_LINK_HOSTS:
                out.append(raw[:500])
        except Exception:
            continue
    return sorted(set(out))[:10]

def collect():
    now = datetime.now(timezone.utc).isoformat()
    rows = {}
    health = []
    for bucket, query in QUERY_BUCKETS:
        params = urllib.parse.urlencode({"q": query, "sort": "latest", "limit": "100"})
        url = f"{API}?{params}"
        try:
            data = fetch_json(url)
            posts = data.get("posts") or []
            health.append({"bucket": bucket, "query": query, "ok": True, "count": len(posts)})
        except Exception as e:
            health.append({"bucket": bucket, "query": query, "ok": False, "error": type(e).__name__})
            continue

        for post in posts:
            record = post.get("record") or {}
            text = str(record.get("text") or "")
            uri = str(post.get("uri") or "")
            did = str((post.get("author") or {}).get("did") or "")
            if not uri:
                continue
            ph = h(uri)
            row = rows.get(ph)
            if row is None:
                row = {
                    "post_hash": ph,
                    "actor_hash": h(did) if did else None,
                    "created_at": record.get("createdAt"),
                    "indexed_at": post.get("indexedAt"),
                    "text": clean_text(text),
                    "links": allowed_links(text, post),
                    "buckets": [],
                    "source": "bluesky_public_search",
                }
                rows[ph] = row
            if bucket not in row["buckets"]:
                row["buckets"].append(bucket)

    items = list(rows.values())
    items.sort(key=lambda x: str(x.get("created_at") or x.get("indexed_at") or ""), reverse=True)
    items = items[:600]
    actors = len({x["actor_hash"] for x in items if x.get("actor_hash")})
    linked = sum(1 for x in items if x.get("links"))

    return {
        "schema": "public_social_propagation_v1",
        "generated_at": now,
        "privacy": {
            "account_handles_stored": False,
            "account_ids_stored": False,
            "actor_identifier": "sha256_truncated",
            "mentions_redacted": True,
            "emails_redacted": True,
            "phones_redacted": True,
            "private_system_data": False,
        },
        "summary": {
            "items": len(items),
            "independent_actor_hashes": actors,
            "items_with_platform_links": linked,
        },
        "source_health": health,
        "items": items,
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    payload = collect()
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps(payload["summary"]))

if __name__ == "__main__":
    main()
