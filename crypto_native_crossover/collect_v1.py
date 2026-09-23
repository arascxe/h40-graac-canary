#!/usr/bin/env python3
"""FEE100K crypto-native crossover sensor: public RSS only, zero-cost, observation only.
An item observed here is NOT verified independent demand or evidence of a $100k outcome.
No account handles, raw account IDs, private keys, thresholds or auto-launch logic are published.
"""
import argparse
import asyncio
import time
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

def timely_public_post(published, observed, max_lag_minutes=120):
    """Fail closed on unknown or old publish times: late RSS is not early attention."""
    try:
        post = datetime.fromisoformat(str(published).replace("Z", "+00:00")).astimezone(timezone.utc)
        obs = datetime.fromisoformat(str(observed).replace("Z", "+00:00")).astimezone(timezone.utc)
        age = (obs-post).total_seconds()/60
        return -5 <= age <= max_lag_minutes
    except (ValueError, TypeError):
        return False

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
        if not (postid or permalink) or not timely_public_post(published, observation_time):
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

# Public tagged discussions are an additional WEAK sensor. A tag does not
# establish a buyer, unique meme identity or genuine independent demand.
MASTODON_TAGS = [
    ("mastodon.social", "memecoin"),
    ("mastodon.social", "solana"),
]

def parse_mastodon_tag(raw, instance, tag, observation_time):
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, list):
        raise ValueError("unexpected mastodon tagged timeline shape")
    out = []
    for status in data[:20]:
        if not isinstance(status, dict) or status.get("reblog") is not None:
            continue
        permalink = str(status.get("url") or "")
        if not permalink or not timely_public_post(status.get("created_at"), observation_time):
            continue
        user = str((status.get("account") or {}).get("id") or "")
        content = html.unescape(str(status.get("content") or ""))
        clean = TAGS.sub(" ", content)
        urls = {object_url(u) for u in URLS.findall(content)}
        urls.discard(None)
        urls.discard(object_url(permalink))
        clean = URLS.sub(" ", clean)
        clean = " ".join(clean.split())
        clean = EMAIL.sub("[redacted-email]", MENTION.sub("[mention]", clean))
        tokens = []
        for t in WORD.findall(clean.lower()):
            if t not in STOP and not t.isdigit() and t not in tokens and len(t)<36:
                tokens.append(t)
            if len(tokens)>=24:
                break
        out.append({
            "post_hash":hid("mastodon:"+instance+":"+permalink),
            "actor_hash":hid("mastodon:"+instance+":"+user) if user else None,
            "source_surface":"mastodon:tag/"+tag+"@"+instance,
            "source_reliability":"TAG_MEME_PROMOTION_SPAM_PRONE",
            "published_at":status.get("created_at"),
            "first_observed_at":observation_time,
            "linked_object_urls":sorted(urls)[:8],
            "semantic_tokens":tokens,"text_excerpt":clean[:180],
            "has_exact_outbound_object":bool(urls)
        })
    return out

def parse_bluesky_search(raw, query, observation_time):
    """Public appview search; independent crypto discussion remains UNVERIFIED."""
    data = json.loads(raw.decode("utf-8"))
    posts = data.get("posts") if isinstance(data,dict) else None
    if not isinstance(posts,list):
        raise ValueError("unexpected Bluesky search API response")
    out=[]
    for item in posts[:35]:
        rec = item.get("record") or {}
        published = rec.get("createdAt") or item.get("indexedAt")
        if not timely_public_post(published,observation_time):
            continue
        uri=str(item.get("uri") or "")
        did=str((item.get("author") or {}).get("did") or "")
        if not uri or not did:
            continue
        message = str(rec.get("text") or "")
        raw_links = URLS.findall(message)
        for source in (rec.get("facets") or []):
            for ft in (source.get("features") or []):
                if isinstance(ft,dict) and ft.get("uri"):
                    raw_links.append(ft["uri"])
        for emb in (rec.get("embed"),item.get("embed")):
            if not isinstance(emb,dict):
                continue
            ext = emb.get("external") or {}
            if isinstance(ext,dict) and ext.get("uri"):
                raw_links.append(ext["uri"])
        urls = {object_url(x) for x in raw_links if isinstance(x,str)}
        urls.discard(None)
        clean = " ".join(URLS.sub(" ",message).split())
        clean = EMAIL.sub("[redacted-email]",MENTION.sub("[mention]",clean))
        toks=[]
        for t in WORD.findall(clean.lower()):
            if t not in STOP and not t.isdigit() and t not in toks and len(t)<36:
                toks.append(t)
            if len(toks)>=24:
                break
        out.append({
          "post_hash":hid("bluesky_jetstream:"+uri),
          "actor_hash":hid("bluesky_jetstream:"+did),
          "source_surface":"bluesky:search/"+query,
          "source_reliability":"PUBLIC_CRYPTO_KEYWORD_SEARCH_SPAM_PRONE",
          "published_at":published,
          "first_observed_at":observation_time,
          "linked_object_urls":sorted(urls)[:8],
          "semantic_tokens":toks,
          "text_excerpt":clean[:180],
          "has_exact_outbound_object":bool(urls)
        })
    return out

BLUESKY_SEARCH_TERMS=("memecoin","pumpfun")

CRYPTO_NATIVE_TERMS = re.compile(r"\b(memecoin|meme coin|pumpfun|pump\.fun|solana|cryptocurrency|bitcoin|crypto|token launch|launchpad)\b", re.I)

async def collect_public_bluesky_jetstream(observed, seconds=18):
    """A bounded *new-post* firehose window; keyword matches are only shadow evidence."""
    try:
        import websockets
    except ImportError:
        return [], {"surface":"bluesky:jetstream_crypto","ok":False,"error_type":"WEBSOCKETS_NOT_INSTALLED"}
    items={}
    messages=0
    started=time.monotonic()
    error=None
    try:
        async with websockets.connect(
          "wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post",
          max_size=1_000_000,ping_interval=20,ping_timeout=12,open_timeout=12,close_timeout=3
        ) as ws:
            while time.monotonic()-started<seconds:
                try:
                    raw=await asyncio.wait_for(ws.recv(),timeout=2)
                except asyncio.TimeoutError:
                    continue
                if not isinstance(raw,str):
                    continue
                messages+=1
                try:
                    evt=json.loads(raw)
                    commit=evt.get("commit") or {}
                    if evt.get("kind")!="commit" or commit.get("collection")!="app.bsky.feed.post" or commit.get("operation")!="create":
                        continue
                    rec=commit.get("record") or {}
                    text=str(rec.get("text") or "")
                    if not CRYPTO_NATIVE_TERMS.search(text):
                        continue
                    did=str(evt.get("did") or "")
                    rkey=str(commit.get("rkey") or "")
                    published=rec.get("createdAt")
                    if not did or not rkey or not timely_public_post(published,observed):
                        continue
                    raw_links=URLS.findall(text)
                    for facet in rec.get("facets") or []:
                        for feat in facet.get("features") or []:
                            if isinstance(feat,dict) and feat.get("uri"):
                                raw_links.append(feat["uri"])
                    emb=rec.get("embed") or {}
                    ext=emb.get("external") if isinstance(emb,dict) else {}
                    if isinstance(ext,dict) and ext.get("uri"):
                        raw_links.append(ext["uri"])
                    urls={object_url(u) for u in raw_links if isinstance(u,str)}
                    urls.discard(None)
                    clean = EMAIL.sub("[redacted-email]",
                          MENTION.sub("[mention]"," ".join(URLS.sub(" ",text).split())))
                    tokens=[]
                    for t in WORD.findall(clean.lower()):
                        if t not in STOP and not t.isdigit() and t not in tokens and len(t)<36:
                            tokens.append(t)
                        if len(tokens)>=24: break
                    uri="at://"+did+"/app.bsky.feed.post/"+rkey
                    p={
                      "post_hash":hid("bluesky_jetstream:"+uri),
                      "actor_hash":hid("bluesky_jetstream:"+did),
                      "source_surface":"bluesky:jetstream_crypto",
                      "source_reliability":"KEYWORD_ONLY_SPAM_PRONE_NOT_BUYER_PROOF",
                      "published_at":published,
                      "first_observed_at":observed,
                      "linked_object_urls":sorted(urls)[:8],
                      "semantic_tokens":tokens,
                      "text_excerpt":clean[:180],
                      "has_exact_outbound_object":bool(urls)
                    }
                    items[p["post_hash"]]=p
                    if len(items)>=55:
                        break
                except Exception:
                    continue
    except Exception as ex:
        error=type(ex).__name__
    return list(items.values()),{
       "surface":"bluesky:jetstream_crypto",
       "ok":error is None,"messages_seen":messages,
       "fresh_keyword_posts":len(items),
       "duration_s":round(time.monotonic()-started,1),
       "reliability":"LOW",
       **({"error_type":error} if error else {})
    }

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
    for instance, tag in MASTODON_TAGS:
        url = "https://"+instance+"/api/v1/timelines/tag/"+tag+"?limit=20"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent":UA,"Accept":"application/json"
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                blob = r.read(1_000_001)
            if len(blob)>1_000_000:
                raise ValueError("feed exceeds 1MB cap")
            posts = parse_mastodon_tag(blob,instance,tag,observed)
            for p in posts:
                items[p["post_hash"]] = p
            health.append({"surface":"mastodon:tag/"+tag+"@"+instance,
                           "ok":True,"observed":len(posts),"reliability":"LOW"})
        except Exception as ex:
            health.append({"surface":"mastodon:tag/"+tag+"@"+instance,
                           "ok":False,"error_type":type(ex).__name__})
    for term in BLUESKY_SEARCH_TERMS:
        try:
            from urllib.parse import urlencode
            qs=urlencode({"q":term,"sort":"latest","limit":"35"})
            req=urllib.request.Request(
              "https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?"+qs,
              headers={"User-Agent":UA,"Accept":"application/json"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                blob=resp.read(1_000_001)
            if len(blob)>1_000_000:
                raise ValueError("Bluesky search feed exceeds 1MB cap")
            posts=parse_bluesky_search(blob,term,observed)
            for post in posts:
                items[post["post_hash"]]=post
            health.append({"surface":"bluesky:search/"+term,"ok":True,
                           "fresh":len(posts),"reliability":"LOW"})
        except Exception as ex:
            health.append({"surface":"bluesky:search/"+term,"ok":False,
                           "error_type":type(ex).__name__})
    bsky_jet_items,bsky_health=asyncio.run(collect_public_bluesky_jetstream(observed,seconds=18))
    for post in bsky_jet_items:
        items[post["post_hash"]]=post
    health.append(bsky_health)
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
    test_masto='[{"url":"https://mastodon.social/@acct/1","account":{"id":"42"}, "content":"<p>#memecoin https://youtu.be/VidA123</p>","created_at":"2026-09-23T16:00:00Z"}]'.encode()
    masto=parse_mastodon_tag(test_masto,"mastodon.social","memecoin","2026-09-23T16:01:00Z")
    assert masto[0]["linked_object_urls"]==["youtube.com/video/VidA123"]
    assert masto[0]["actor_hash"] and "acct" not in masto[0]["text_excerpt"]
    bsky_fixture=json.dumps({"posts":[{"uri":"at://did:plc:alice/app.bsky.feed.post/q",
      "author":{"did":"did:plc:alice"},
      "record":{"createdAt":"2026-09-23T16:01:00Z",
                "text":"memecoin original https://x.com/test/status/123456789"}}]}).encode()
    b=parse_bluesky_search(bsky_fixture,"memecoin","2026-09-23T16:02:00Z")
    assert len(b)==1 and b[0]["linked_object_urls"]==["x.com/status/123456789"]
    assert not timely_public_post("2026-09-20T16:01:00Z","2026-09-23T16:02:00Z")
    print("PASS: self-post exclusion, exact links, fresh-only timestamps, privacy redaction, Bluesky parsing")

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
