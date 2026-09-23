#!/usr/bin/env python3
"""FEE100K crypto-native crossover sensor: public RSS only, zero-cost, observation only.
An item observed here is NOT verified independent demand or evidence of a $100k outcome.
No account handles, raw account IDs, private keys, thresholds or auto-launch logic are published.
"""
import argparse
import hashlib
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

UA = "FEE100K-Research-Crossover/1.0 (public RSS, 15m)"
ATOM = {"a": "http://www.w3.org/2005/Atom"}
# Separate audiences: crypto trading, Solana, memecoins. Each gets its own reliability label.
FEEDS = [
    ("solana", "new", "SOLANA_GENERAL"),
    ("CryptoCurrency", "new", "CRYPTO_GENERAL"),
    ("CryptoMoonShots", "new", "MEME_SPECULATIVE_SPAM_PRONE"),
    ("SolanaMemeCoins", "new", "MEME_SPECULATIVE_SPAM_PRONE"),
]
URLS = re.compile(r"https?://[^\s<>\"']+", re.I)
TAGS = re.compile(r"<[^>]*>")
MENTION = re.compile(r"(?<!\w)@[A-Za-z0-9_.-]{2,64}")
EMAIL = re.compile(r"\b[\w.+%-]+@[\w.-]+\.[a-z]{2,}\b", re.I)
WORD = re.compile(r"[a-z0-9][a-z0-9_-]{2,}", re.I)
STOP = set("the and for from that with this your about video crypto cryptocurrency solana pump token coin coins memes viral posted reddit comments comment submitted linking official trending news made please what when how where new today yesterday".split())

def now():
    return datetime.now(timezone.utc).isoformat()

def hid(s):
    return hashlib.sha256(s.encode("utf-8", "ignore")).hexdigest()[:24]

def object_url(raw):
    """Return only an exact external post/video object. Profiles, hashtags, roots excluded."""
    from urllib.parse import urlparse, parse_qs
    u = urlparse(html.unescape(raw).rstrip(".,;:!?)]}"))
    host = (u.hostname or "").lower().removeprefix("www.")
    path = u.path
    if host in ("twitter.com", "x.com"):
        m = re.search(r"/status/(\d+)", path)
        return "x.com/status/" + m.group(1) if m else None
    if host in ("tiktok.com", "vm.tiktok.com"):
        m = re.search(r"/video/(\d+)", path)
        return "tiktok.com/video/" + m.group(1) if m else None
    if host == "youtu.be":
        v = path.strip("/").split("/")[0]
        return "youtube.com/video/" + v if v else None
    if host == "youtube.com":
        m = re.match(r"/shorts/([-\w]+)", path)
        v = m.group(1) if m else parse_qs(u.query).get("v", [None])[0] if path == "/watch" else None
        return "youtube.com/video/" + v if v else None
    if host in ("reddit.com", "old.reddit.com"):
        m = re.search(r"/comments/([a-z0-9]+)", path, re.I)
        return "reddit.com/comments/" + m.group(1).lower() if m else None
    if host == "instagram.com":
        m = re.search(r"/(p|reel|reels)/([^/?#]+)", path)
        return "instagram.com/" + m.group(1) + "/" + m.group(2) if m else None
    return None

def parse_atom(raw, subreddit, reliability, observation_time):
    root = ET.fromstring(raw)
    out = []
    for e in root.findall("a:entry", ATOM)[:25]:
        postid = e.findtext("a:id", default="", namespaces=ATOM)
        permalink_node = e.find("a:link", ATOM)
        permalink = permalink_node.get("href", "") if permalink_node is not None else ""
        content = html.unescape(e.findtext("a:content", default="", namespaces=ATOM))
        title = html.unescape(e.findtext("a:title", default="", namespaces=ATOM))
        published = e.findtext("a:published", default=None, namespaces=ATOM) or e.findtext("a:updated", default=None, namespaces=ATOM)
        author = e.findtext("a:author/a:name", default="", namespaces=ATOM)
        if not (postid or permalink):
            continue
        self_object = object_url(permalink)
        # Incoming links to OTHER precise objects; the crypto post's own permalink is NOT a crossover.
        urls = {object_url(x) for x in URLS.findall(content + " " + title)}
        urls.discard(None)
        urls.discard(self_object)
        body = TAGS.sub(" ", content)
        body = re.sub(r"\s*submitted by /u/\S+ to r/\S+.*$", " ", body, flags=re.I)
        body = URLS.sub(" ", body)
        clean = " ".join((title + " " + body).split())
        clean = EMAIL.sub("[redacted-email]", MENTION.sub("[mention]", clean))
        tokens = []
        for t in WORD.findall(clean.lower()):
            if t not in STOP and not t.isdigit() and t not in tokens and len(t) < 36:
                tokens.append(t)
            if len(tokens) >= 24:
                break
        out.append({
            "post_hash": hid("reddit:" + (self_object or permalink or postid)),
            "actor_hash": hid("reddit_crypto:" + author.lower()) if author else None,
            "source_surface": "reddit:r/" + subreddit,
            "source_reliability": reliability,
            "published_at": published,
            "first_observed_at": observation_time,
            "linked_object_urls": sorted(urls)[:8],
            # Text is for later adjudication, NOT a confirmed object match.
            "semantic_tokens": tokens,
            "text_excerpt": clean[:180],
            "has_exact_outbound_object": bool(urls)
        })
    return out

def collect(timeout=12):
    items, health = {}, []
    observed = now()
    for subreddit, feed, reliability in FEEDS:
        url = "https://www.reddit.com/r/" + subreddit + "/" + feed + "/.rss?limit=25"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 FEE100K research RSS monitor",
                "Accept": "application/atom+xml,application/xml;q=0.9",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                blob = r.read(1_000_001)
            if len(blob) > 1_000_000:
                raise ValueError("feed exceeds 1MB cap")
            posts = parse_atom(blob, subreddit, reliability, observed)
            for p in posts:
                items[p["post_hash"]] = p
            health.append({"surface":"reddit:r/"+subreddit,"ok":True,"observed":len(posts)})
        except Exception as ex:
            health.append({"surface":"reddit:r/"+subreddit,"ok":False,"error_type":type(ex).__name__})
    return {
        "schema":"fee100k_crypto_native_crossover_v1",
        "generated_at":now(),
        "observation_started_at":observed,
        "privacy":{"actor_identifiers_hashed":True,"handles_stored":False,"raw_ids_stored":False,
                   "no_private_system_data":True,"no_auto_launch":True},
        "policy":{"no_self_post_as_crossover":True,"links_are_evidence_only":True,
                  "no_inferred_buys":True,"no_text_match_as_verified":True},
        "source_health":health,
        "items":list(items.values())[:100]
    }

def self_test():
    rss = ('''<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>t3_abcd</id>
        <title>A remix referencing this original</title><published>2026-09-23T16:00:00Z</published>
        <author><name>example-user</name></author>
        <link href="https://www.reddit.com/r/solana/comments/abc/our_post/" />
        <content type="html">Check https://www.youtube.com/watch?v=VidA123&amp;amp;t=40
        and https://x.com/test/status/123456789; @example-user</content></entry></feed>''')
    items = parse_atom(rss,"solana","SOLANA_GENERAL","2026-09-23T16:01:00Z")
    assert len(items)==1
    assert items[0]["post_hash"] and items[0]["actor_hash"]
    assert "reddit.com/comments/abc" not in items[0]["linked_object_urls"]
    assert "x.com/status/123456789" in items[0]["linked_object_urls"]
    assert "youtube.com/video/VidA123" in items[0]["linked_object_urls"]
    assert "example-user" not in items[0]["text_excerpt"]
    assert object_url("https://x.com/bill") is None
    assert object_url("https://www.reddit.com/r/solana/") is None
    print("PASS: self-post exclusion, normalized exact outbound links, privacy redaction")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out")
    p.add_argument("--self-test",action="store_true")
    a = p.parse_args()
    if a.self_test:
        return self_test()
    if not a.out:
        p.error("--out required outside self-test")
    payload = collect()
    with open(a.out,"w",encoding="utf-8") as f:
        json.dump(payload,f,separators=(",",":"),ensure_ascii=False)
    print(json.dumps({"items":len(payload["items"]),"health":payload["source_health"]}))

if __name__ == "__main__":
    main()
