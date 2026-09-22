#!/usr/bin/env python3
"""Universal discovery-envelope helpers for FEE100K DISCOVERY_ADAPTER_BUS_V2."""
import hashlib
import io
import math
import re
import statistics
import urllib.parse
import urllib.request

try:
    from PIL import Image
except Exception:
    Image = None

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_-]{2,}", re.I)
IMG_RE = re.compile(r"""(?:src|poster)=["'](https?://[^"']+)["']""", re.I)
TRACKING_KEYS = {
    "utm_source","utm_medium","utm_campaign","utm_term","utm_content",
    "fbclid","gclid","igshid","si","feature","ref","ref_src",
}
STOP = {
    "the","and","for","with","that","this","from","your","you","are","was","were","has","have","had",
    "will","would","could","should","about","into","over","under","after","before","more","most","some",
    "video","viral","clip","watch","link","post","reel","reels","tweet","thread","news","today","new",
    "official","original","youtube","tiktok","instagram","twitter","reddit","bluesky","http","https","www",
    "ago","day","days","hour","hours","minute","minutes","week","weeks","month","months","year","years",
    "views","view","posts","post","rank","popular","trending","trend",
}
DERIVATIVE_ORDER = ["remix","template","parody","derivative","reaction","meme","viral"]

_PHASH_CACHE = {}

def sha24(value):
    return hashlib.sha256(str(value or "").encode("utf-8","ignore")).hexdigest()[:24]

def normalize_object_url(url):
    if not url:
        return None
    try:
        raw = str(url).strip()
        if not raw.startswith(("http://","https://")):
            raw = "https://" + raw
        u = urllib.parse.urlparse(raw)
        host = (u.hostname or "").lower()
        if host.startswith("www."):
            host = host[4:]
        if host == "twitter.com":
            host = "x.com"
        path = re.sub(r"/+","/",u.path or "/").rstrip("/")

        # Stable social object IDs; discard username/query decoration.
        m = re.search(r"/status/(\d+)", path)
        if host == "x.com" and m:
            return f"x.com/status/{m.group(1)}"
        m = re.search(r"/video/(\d+)", path)
        if host in {"tiktok.com","vm.tiktok.com"} and m:
            return f"tiktok.com/video/{m.group(1)}"
        if host == "youtu.be":
            vid = path.strip("/").split("/")[0]
            if vid:
                return f"youtube.com/video/{vid}"
        if host == "youtube.com":
            if path.startswith("/shorts/"):
                vid = path.split("/")[2] if len(path.split("/")) > 2 else ""
                if vid:
                    return f"youtube.com/video/{vid}"
            if path == "/watch":
                vid = urllib.parse.parse_qs(u.query).get("v",[""])[0]
                if vid:
                    return f"youtube.com/video/{vid}"
        if host == "reddit.com":
            m = re.search(r"/comments/([a-z0-9]+)", path, re.I)
            if m:
                return f"reddit.com/comments/{m.group(1).lower()}"
        if host == "instagram.com":
            m = re.search(r"/(p|reel|reels)/([^/?#]+)", path, re.I)
            if m:
                return f"instagram.com/{m.group(1).lower()}/{m.group(2)}"

        query = urllib.parse.parse_qsl(u.query, keep_blank_values=False)
        query = [(k,v) for k,v in query if k.lower() not in TRACKING_KEYS]
        q = urllib.parse.urlencode(sorted(query)) if query else ""
        return host + (path or "/") + (("?" + q) if q else "")
    except Exception:
        return None

def canonical_host(canonical_url):
    if not canonical_url:
        return None
    return canonical_url.split("/",1)[0].lower()

def text_tokens(text, limit=24):
    toks = []
    seen = set()
    for tok in TOKEN_RE.findall((text or "").lower()):
        if tok in STOP or tok.isdigit() or len(tok) < 3:
            continue
        if tok not in seen:
            seen.add(tok)
            toks.append(tok)
        if len(toks) >= limit:
            break
    return toks

def simhash64(tokens):
    if not tokens:
        return None
    weights = [0] * 64
    for tok in tokens:
        x = int(hashlib.blake2b(tok.encode("utf-8"), digest_size=8).hexdigest(), 16)
        for i in range(64):
            weights[i] += 1 if ((x >> i) & 1) else -1
    value = 0
    for i,w in enumerate(weights):
        if w >= 0:
            value |= (1 << i)
    return format(value, "064b")

def bands64(bits):
    if not bits or len(bits) != 64:
        return [None,None,None,None]
    return [int(bits[i:i+16],2) for i in (0,16,32,48)]

def pick_media_url(values):
    for raw in values or []:
        if not isinstance(raw,str):
            continue
        candidates = [raw] if raw.startswith("http") else []
        candidates += IMG_RE.findall(raw)
        for c in candidates:
            lc = c.lower()
            if any(ext in lc for ext in (".jpg",".jpeg",".png",".webp",".avif")) or any(
                h in lc for h in ("i.ytimg.com","pbs.twimg.com","tiktokcdn","redd.it","preview.redd.it","cdninstagram")
            ):
                return c[:1000]
    return None

def _download(url, timeout=5, limit=3_000_000):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/*,*/*;q=0.8"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read(limit + 1)
        if len(data) > limit:
            return None
        return data

def image_phash64(url):
    if not url or Image is None:
        return None
    if url in _PHASH_CACHE:
        return _PHASH_CACHE[url]
    try:
        data = _download(url)
        if not data:
            _PHASH_CACHE[url] = None
            return None
        img = Image.open(io.BytesIO(data)).convert("L").resize((32,32), Image.Resampling.LANCZOS)
        px = list(img.getdata())
        # Low-frequency 8x8 2-D DCT. 64*1024 ~= 65k ops/image; bounded and deterministic.
        coeffs = []
        for u in range(8):
            for v in range(8):
                s = 0.0
                for x in range(32):
                    cx = math.cos((2*x+1)*u*math.pi/64.0)
                    row = x*32
                    for y in range(32):
                        s += px[row+y] * cx * math.cos((2*y+1)*v*math.pi/64.0)
                coeffs.append(s)
        med = statistics.median(coeffs[1:])
        bits = "".join("1" if c > med else "0" for c in coeffs)
        _PHASH_CACHE[url] = bits
        return bits
    except Exception:
        _PHASH_CACHE[url] = None
        return None

def derivative_types(buckets):
    b = set(buckets or [])
    return [x for x in DERIVATIVE_ORDER if x in b]

def build_envelope(*, source, post_hash, actor_hash, published_at, first_observed_at,
                   last_observed_at, text, links, buckets, media_url=None, parent_url=None,
                   engagement_snapshot=None, source_metadata=None):
    clean = (text or "").strip()
    toks = text_tokens(clean)
    tfp = simhash64(toks)
    normalized_links = [x for x in (normalize_object_url(u) for u in (links or [])) if x]
    canonical = normalized_links[0] if normalized_links else None
    ph = image_phash64(media_url) if media_url else None
    derivatives = derivative_types(buckets)
    adapter = source.split(":",1)[0]
    image_bands = bands64(ph)
    text_bands = bands64(tfp)
    object_hint = (
        ("img:" + ph) if ph else
        ("url:" + sha24(canonical)) if canonical else
        ("txt:" + (tfp or post_hash))
    )
    return {
        # Backward-compatible fields used by existing smoke/selection code.
        "post_hash": post_hash,
        "actor_hash": actor_hash,
        "created_at": published_at,
        "first_observed_at": first_observed_at,
        "last_observed_at": last_observed_at,
        "text": clean[:500],
        "links": (links or [])[:12],
        "buckets": sorted(set(buckets or [])),
        "source": source,

        # Universal envelope V2.
        "envelope_version": "DISCOVERY_ENVELOPE_V2",
        "source_adapter": adapter,
        "source_surface": source,
        "source_item_hash": post_hash,
        "published_at": published_at,
        "canonical_url": canonical,
        "canonical_host": canonical_host(canonical),
        "text_fingerprint": tfp,
        "text_bands": text_bands,
        "semantic_tokens": toks,
        "media_url": media_url,
        "image_phash": ph,
        "image_bands": image_bands,
        "derivative_type": derivatives[0] if derivatives else None,
        "derivative_types": derivatives,
        "parent_object_url": normalize_object_url(parent_url),
        "object_hint_key": object_hint,
        "engagement_snapshot": engagement_snapshot or {},
        "source_metadata": source_metadata or {},
        "provenance": {
            "public_only": True,
            "actor_identifier_hashed": True,
            "post_mint_market_data_used": False,
            "fingerprints_computed_at_observation": True,
        },
    }
