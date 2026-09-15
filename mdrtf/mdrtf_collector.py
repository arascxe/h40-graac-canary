#!/usr/bin/env python3
"""Future-only collector for the Million-Dollar Right-Tail Factory.

This program is deliberately a census and resolver, not a trading bot. It freezes
attention events, chain-specific new-pool lanes, exact semantic candidate matches,
and reflexive-primitive rows before outcomes are known.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import io
import json
import math
import re
import sqlite3
import subprocess
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


GEOS = ("US", "TR", "GB", "JP", "DE")
NETWORKS = ("solana", "robinhood", "bsc", "base", "arbitrum", "monad", "eth")
MIN_CUT_INTERVAL_SECONDS = 90
FAMILY_WINDOW_HOURS = 48
PROBE_USD = 50.0
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
JUPITER_QUOTE = "https://lite-api.jup.ag/swap/v1/quote"
ROUTE_SLIPPAGE_BPS = 300
KYBER_ROUTES = "https://aggregator-api.kyberswap.com"
EVM_ROUTE_CONFIG = {
    "eth": {"slug": "ethereum", "stable": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "decimals": 6},
    "base": {"slug": "base", "stable": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913", "decimals": 6},
    "arbitrum": {"slug": "arbitrum", "stable": "0xaf88d065e77c8cc2239327c5edb3a432268e5831", "decimals": 6},
    "bsc": {"slug": "bsc", "stable": "0x55d398326f99059ff775485246999027b3197955", "decimals": 18},
}
MAX_CANDIDATE_ENRICHMENTS = 20
MAX_OUTCOME_REFRESHES = 20
MAX_TRADE_REFRESHES = 20
MAX_ROUTE_SIMULATIONS = 10
HT = "{https://trends.google.com/trending/rss}"
STOP = {
    "the", "and", "for", "with", "from", "today", "season", "jr", "fc", "f.c",
    "maç", "kadrosu", "sayılı", "kanun", "genel", "müdürlüğü", "burs", "本人確認",
}


@dataclass(frozen=True)
class FetchResult:
    key: str
    ok: bool
    body: bytes
    http_code: int
    seconds: float
    error: str = ""


def curl_fetch(key: str, url: str, timeout: int = 20) -> FetchResult:
    cmd = [
        "curl", "-sS", "--max-time", str(timeout), "-A", "MDRTF-FutureLedger/0.1",
        "--retry", "2", "--retry-delay", "3", "--retry-max-time", str(min(timeout, 18)),
        "-w", "\n__META__%{http_code}\t%{time_total}", url,
    ]
    try:
        cp = subprocess.run(cmd, check=False, capture_output=True, timeout=timeout + min(timeout, 18) + 5)
    except subprocess.TimeoutExpired:
        return FetchResult(key, False, b"", 0, float(timeout), "process_timeout")
    marker = b"\n__META__"
    if marker not in cp.stdout:
        return FetchResult(key, False, cp.stdout, 0, float(timeout), cp.stderr.decode("utf-8", "replace")[:200])
    body, meta = cp.stdout.rsplit(marker, 1)
    try:
        code_s, sec_s = meta.decode().split("\t", 1)
        code, seconds = int(code_s), float(sec_s)
    except Exception:
        code, seconds = 0, float(timeout)
    ok = code == 200 and bool(body)
    err = "" if ok else cp.stderr.decode("utf-8", "replace")[:200]
    return FetchResult(key, ok, body, code, seconds, err)


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> dt.datetime:
    if not value:
        raise ValueError("empty timestamp")
    if "," in value:
        parsed = email.utils.parsedate_to_datetime(value)
    else:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.astimezone(dt.timezone.utc)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return " ".join(re.findall(r"[^\W_]+", value, flags=re.UNICODE))


def semantic_tokens(value: str) -> set[str]:
    return {t for t in normalize(value).split() if t not in STOP and (len(t) >= 3 or not t.isascii())}


def stable_id(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:24]


def numeric(value):
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def address_from_id(value: str) -> str:
    return value.split("_", 1)[1] if "_" in value else value


def same_address(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return a.casefold() == b.casefold() if a.startswith("0x") and b.startswith("0x") else a == b


def estimated_cpmm_impact(reserve_usd: float | None, notional_usd: float = PROBE_USD) -> float | None:
    """Conservative one-leg constant-product impact using half the pool reserve."""
    if not reserve_usd or reserve_usd <= 0:
        return None
    quote_side = reserve_usd / 2.0
    return notional_usd / (quote_side + notional_usd)


def image_dhash(body: bytes) -> str | None:
    """Return a 64-bit perceptual dHash when Pillow is available."""
    try:
        from PIL import Image
        image = Image.open(io.BytesIO(body)).convert("L").resize((9, 8))
        px = list(image.getdata())
        bits = [px[y * 9 + x] > px[y * 9 + x + 1] for y in range(8) for x in range(8)]
        value = sum(int(bit) << index for index, bit in enumerate(bits))
        return f"{value:016x}"
    except Exception:
        return None


def hash_distance(a: str | None, b: str | None) -> int | None:
    if not a or not b:
        return None
    return (int(a, 16) ^ int(b, 16)).bit_count()


def match_score(event_title: str, pool_name: str) -> tuple[float, str]:
    base_name = pool_name.split(" / ", 1)[0]
    e_norm, p_norm = normalize(event_title), normalize(base_name)
    if not e_norm or not p_norm:
        return 0.0, "empty"
    if e_norm == p_norm:
        return 1.0, "exact_phrase"
    e, p = semantic_tokens(event_title), semantic_tokens(base_name)
    overlap = e & p
    if len(overlap) >= 2:
        return min(0.95, 0.60 + 0.10 * len(overlap)), "multi_token_overlap"
    if len(overlap) == 1:
        token = next(iter(overlap))
        if len(token) >= 6 and (p == {token} or e == {token}):
            return 0.72, "distinctive_exact_token"
    return 0.0, "no_exact_semantic_match"


def init_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS cuts (
          cut_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, mode TEXT NOT NULL,
          capital_state TEXT NOT NULL, source_health_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attention_events (
          cut_id TEXT NOT NULL, geo TEXT NOT NULL, rank INTEGER NOT NULL,
          title TEXT NOT NULL, normalized_title TEXT NOT NULL, published_at TEXT NOT NULL,
          PRIMARY KEY (cut_id, geo, rank)
        );
        CREATE TABLE IF NOT EXISTS attention_support (
          cut_id TEXT NOT NULL, geo TEXT NOT NULL, event_title TEXT NOT NULL,
          source_name TEXT NOT NULL, article_title TEXT, article_url TEXT,
          picture_url TEXT, event_picture_url TEXT,
          PRIMARY KEY (cut_id, geo, event_title, source_name, article_url)
        );
        CREATE TABLE IF NOT EXISTS pools (
          cut_id TEXT NOT NULL, network TEXT NOT NULL, pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL, dex_id TEXT, name TEXT NOT NULL, created_at TEXT NOT NULL,
          reserve_usd REAL, fdv_usd REAL, volume_h24 REAL, buyers_h24 INTEGER, sellers_h24 INTEGER,
          PRIMARY KEY (cut_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS semantic_matches (
          cut_id TEXT NOT NULL, geo TEXT NOT NULL, event_title TEXT NOT NULL,
          published_at TEXT NOT NULL, network TEXT NOT NULL, pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL, pool_name TEXT NOT NULL, pool_created_at TEXT NOT NULL,
          score REAL NOT NULL, reason TEXT NOT NULL,
          PRIMARY KEY (cut_id, geo, event_title, pool_id)
        );
        CREATE TABLE IF NOT EXISTS primitives (
          cut_id TEXT NOT NULL, slug TEXT NOT NULL, name TEXT NOT NULL, category TEXT,
          chains TEXT, total24h REAL, total30d REAL, change_1d REAL,
          change_7dover7d REAL, change_30dover30d REAL,
          PRIMARY KEY (cut_id, slug)
        );
        CREATE TABLE IF NOT EXISTS token_enrichment (
          cut_id TEXT NOT NULL, network TEXT NOT NULL, token_id TEXT NOT NULL,
          developer_address TEXT, image_url TEXT, image_dhash TEXT,
          websites_json TEXT, socials_json TEXT, description TEXT,
          holders_count INTEGER, top10_pct REAL, mint_authority TEXT,
          freeze_authority TEXT, honeypot TEXT, gt_verified INTEGER,
          metadata_event_link INTEGER NOT NULL, visual_event_link INTEGER NOT NULL,
          PRIMARY KEY (cut_id, network, token_id)
        );
        CREATE TABLE IF NOT EXISTS family_freezes (
          family_id TEXT PRIMARY KEY, frozen_cut_id TEXT NOT NULL, frozen_at TEXT NOT NULL,
          event_title TEXT NOT NULL, normalized_title TEXT NOT NULL,
          event_published_at TEXT NOT NULL, geos_json TEXT NOT NULL,
          news_sources_json TEXT NOT NULL, token_count INTEGER NOT NULL,
          developer_count INTEGER NOT NULL, deployer_gate TEXT NOT NULL,
          source_gate TEXT NOT NULL, family_state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS family_members (
          family_id TEXT NOT NULL, network TEXT NOT NULL, pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL, pool_name TEXT NOT NULL, pool_created_at TEXT NOT NULL,
          developer_address TEXT, semantic_score REAL NOT NULL,
          metadata_event_link INTEGER NOT NULL, visual_event_link INTEGER NOT NULL,
          PRIMARY KEY (family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS leader_observations (
          cut_id TEXT NOT NULL, family_id TEXT NOT NULL, network TEXT NOT NULL,
          pool_id TEXT NOT NULL, token_id TEXT NOT NULL, observed_at TEXT NOT NULL,
          price_usd REAL, reserve_usd REAL, fdv_usd REAL, market_cap_usd REAL,
          volume_h24 REAL, buyers_h24 INTEGER, sellers_h24 INTEGER,
          holder_count INTEGER, top10_pct REAL, estimated_impact REAL,
          execution_state TEXT NOT NULL, contract_state TEXT NOT NULL,
          leader_score REAL, leader_rank INTEGER,
          PRIMARY KEY (cut_id, family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS capital_flow_observations (
          cut_id TEXT NOT NULL, family_id TEXT NOT NULL, network TEXT NOT NULL,
          pool_id TEXT NOT NULL, token_id TEXT NOT NULL, observed_at TEXT NOT NULL,
          trade_count INTEGER NOT NULL, distinct_buyers INTEGER NOT NULL,
          distinct_sellers INTEGER NOT NULL, external_buy_usd REAL NOT NULL,
          external_sell_usd REAL NOT NULL, max_buyer_share REAL,
          developer_seen INTEGER NOT NULL, address_diversity_state TEXT NOT NULL,
          PRIMARY KEY (cut_id, family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS route_simulations (
          cut_id TEXT NOT NULL, family_id TEXT NOT NULL, network TEXT NOT NULL,
          pool_id TEXT NOT NULL, token_id TEXT NOT NULL, observed_at TEXT NOT NULL,
          probe_usd REAL NOT NULL, buy_out_raw TEXT, sell_out_usdc_raw TEXT,
          quoted_roundtrip_cost_pct REAL, worst_case_cost_pct REAL,
          buy_price_impact_pct REAL, sell_price_impact_pct REAL,
          buy_route_json TEXT NOT NULL, sell_route_json TEXT NOT NULL,
          route_state TEXT NOT NULL, failure_reason TEXT,
          PRIMARY KEY (cut_id, family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS outcomes (
          family_id TEXT NOT NULL, network TEXT NOT NULL, pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL, baseline_cut_id TEXT NOT NULL,
          baseline_at TEXT NOT NULL, baseline_price_usd REAL,
          high_multiple REAL, low_multiple REAL, first_3x_at TEXT,
          first_5x_at TEXT, first_10x_at TEXT, first_dd35_at TEXT,
          outcome_state TEXT NOT NULL, last_observed_at TEXT NOT NULL,
          PRIMARY KEY (family_id, network, pool_id)
        );
        """
    )
    existing = {row[1] for row in conn.execute("PRAGMA table_info(pools)")}
    for column in ("price_usd", "market_cap_usd"):
        if column not in existing:
            conn.execute(f"ALTER TABLE pools ADD COLUMN {column} REAL")
    return conn


def parse_trends(result: FetchResult) -> list[dict]:
    root = ET.fromstring(result.body)
    rows = []
    for rank, item in enumerate(root.findall(".//item"), start=1):
        title = (item.findtext("title") or "").strip()
        published = parse_time(item.findtext("pubDate") or "")
        support = []
        event_picture = (item.findtext(HT + "picture") or "").strip()
        for news in item.findall(HT + "news_item"):
            support.append({
                "source": (news.findtext(HT + "news_item_source") or "").strip(),
                "article_title": (news.findtext(HT + "news_item_title") or "").strip(),
                "article_url": (news.findtext(HT + "news_item_url") or "").strip(),
                "picture_url": (news.findtext(HT + "news_item_picture") or "").strip(),
            })
        rows.append({
            "geo": result.key.split(":", 1)[1], "rank": rank, "title": title,
            "published": published, "event_picture": event_picture, "support": support,
        })
    return rows


def parse_pools(result: FetchResult) -> list[dict]:
    network = result.key.split(":", 1)[1]
    payload = json.loads(result.body)
    rows = []
    for item in payload.get("data", []):
        a, rel = item.get("attributes", {}), item.get("relationships", {})
        tx = ((a.get("transactions") or {}).get("h24") or {})
        vol = ((a.get("volume_usd") or {}).get("h24"))
        rows.append({
            "network": network,
            "pool_id": item.get("id", ""),
            "token_id": (((rel.get("base_token") or {}).get("data") or {}).get("id", "")),
            "dex_id": (((rel.get("dex") or {}).get("data") or {}).get("id")),
            "name": a.get("name") or "",
            "created": parse_time(a.get("pool_created_at") or ""),
            "price": numeric(a.get("base_token_price_usd")),
            "reserve": float(a["reserve_in_usd"]) if a.get("reserve_in_usd") else None,
            "fdv": float(a["fdv_usd"]) if a.get("fdv_usd") else None,
            "market_cap": numeric(a.get("market_cap_usd")),
            "volume_h24": float(vol) if vol else None,
            "buyers_h24": tx.get("buyers"), "sellers_h24": tx.get("sellers"),
        })
    return rows


def parse_pool_detail(result: FetchResult) -> dict:
    payload = json.loads(result.body)
    original = payload.get("data")
    payload["data"] = [original] if original else []
    wrapped = FetchResult("pools:" + result.key.split(":", 2)[1], True, json.dumps(payload).encode(), 200, result.seconds)
    rows = parse_pools(wrapped)
    if not rows:
        raise ValueError("empty pool detail")
    return rows[0]


def parse_primitives(result: FetchResult) -> list[dict]:
    payload = json.loads(result.body)
    rows = []
    for p in payload.get("protocols", []):
        day, change = p.get("total24h") or 0, p.get("change_30dover30d")
        if day < 50_000 or change is None or change < 500:
            continue
        rows.append({
            "slug": p.get("slug") or p.get("name") or "", "name": p.get("name") or "",
            "category": p.get("category"), "chains": ",".join(p.get("chains") or []),
            "total24h": day, "total30d": p.get("total30d"), "change_1d": p.get("change_1d"),
            "change_7dover7d": p.get("change_7dover7d"), "change_30dover30d": change,
        })
    return sorted(rows, key=lambda x: x["change_30dover30d"], reverse=True)


def parse_token_info(result: FetchResult) -> dict:
    a = (json.loads(result.body).get("data") or {}).get("attributes") or {}
    holders = a.get("holders") or {}
    distribution = holders.get("distribution_percentage") or {}
    websites = a.get("websites") or []
    socials = {
        key: a.get(key) for key in
        ("twitter_handle", "telegram_handle", "discord_url", "farcaster_url", "zora_url")
        if a.get(key)
    }
    return {
        "developer": a.get("developer_address"), "image_url": a.get("image_url"),
        "websites": websites, "socials": socials, "description": a.get("description") or "",
        "holders_count": holders.get("count"), "top10_pct": numeric(distribution.get("top_10")),
        "mint_authority": a.get("mint_authority"), "freeze_authority": a.get("freeze_authority"),
        "honeypot": a.get("is_honeypot") or "unknown", "gt_verified": bool(a.get("gt_verified")),
    }


def metadata_links_event(event_title: str, info: dict) -> bool:
    haystack = " ".join([
        info.get("description") or "", json.dumps(info.get("websites") or [], ensure_ascii=False),
        json.dumps(info.get("socials") or {}, ensure_ascii=False),
    ])
    event_tokens, metadata_tokens = semantic_tokens(event_title), semantic_tokens(haystack)
    overlap = event_tokens & metadata_tokens
    return bool(event_tokens) and (event_tokens <= metadata_tokens or len(overlap) >= 2)


def parse_trade_flow(result: FetchResult, developer: str | None) -> dict:
    trades = json.loads(result.body).get("data") or []
    buyer_volume, sellers = {}, set()
    external_sell_usd = 0.0
    developer_seen = False
    for trade in trades:
        a = trade.get("attributes") or {}
        wallet = a.get("tx_from_address") or ""
        volume = numeric(a.get("volume_in_usd")) or 0.0
        if same_address(wallet, developer):
            developer_seen = True
            continue
        if a.get("kind") == "buy" and wallet:
            buyer_volume[wallet] = buyer_volume.get(wallet, 0.0) + volume
        elif a.get("kind") == "sell" and wallet:
            sellers.add(wallet)
            external_sell_usd += volume
    external_buy_usd = sum(buyer_volume.values())
    max_share = max(buyer_volume.values(), default=0.0) / external_buy_usd if external_buy_usd else None
    if not developer:
        state = "DEVELOPER_UNVERIFIED"
    elif len(buyer_volume) >= 5 and external_buy_usd >= 5 * PROBE_USD and max_share is not None and max_share <= 0.50:
        state = "ADDRESS_DIVERSE"
    else:
        state = "INSUFFICIENT_DIVERSITY"
    return {
        "trade_count": len(trades), "distinct_buyers": len(buyer_volume),
        "distinct_sellers": len(sellers), "external_buy_usd": external_buy_usd,
        "external_sell_usd": external_sell_usd, "max_buyer_share": max_share,
        "developer_seen": developer_seen, "address_diversity_state": state,
    }


def quote_url(input_mint: str, output_mint: str, amount: str) -> str:
    return JUPITER_QUOTE + "?" + urllib.parse.urlencode({
        "inputMint": input_mint, "outputMint": output_mint, "amount": amount,
        "slippageBps": ROUTE_SLIPPAGE_BPS, "restrictIntermediateTokens": "true",
    })


def route_labels(payload: dict) -> list[str]:
    return [str(((leg.get("swapInfo") or {}).get("label") or "UNKNOWN")) for leg in payload.get("routePlan") or []]


def parse_jupiter_leg(result: FetchResult) -> dict:
    payload = json.loads(result.body)
    if payload.get("error") or not payload.get("outAmount") or not payload.get("routePlan"):
        raise ValueError(str(payload.get("error") or "no_route"))
    return payload


def routed_state(buy: dict, sell: dict, probe_raw: int) -> dict:
    sell_out = int(sell["outAmount"])
    sell_floor = int(sell.get("otherAmountThreshold") or sell_out)
    quoted_cost = 1.0 - sell_out / probe_raw
    worst_cost = 1.0 - sell_floor / probe_raw
    buy_impact = numeric(buy.get("priceImpactPct"))
    sell_impact = numeric(sell.get("priceImpactPct"))
    passes = (quoted_cost <= 0.03 and buy_impact is not None and sell_impact is not None and
              buy_impact <= 0.02 and sell_impact <= 0.02)
    return {
        "buy_out_raw": str(buy["outAmount"]), "sell_out_usdc_raw": str(sell_out),
        "quoted_roundtrip_cost_pct": quoted_cost, "worst_case_cost_pct": worst_cost,
        "buy_price_impact_pct": buy_impact, "sell_price_impact_pct": sell_impact,
        "buy_routes": route_labels(buy), "sell_routes": route_labels(sell),
        "route_state": "ROUTED_QUOTE_PASS" if passes else "ROUTED_QUOTE_FAIL",
        "failure_reason": None if passes else "cost_or_price_impact",
    }


def kyber_quote_url(network: str, input_token: str, output_token: str, amount: str) -> str:
    cfg = EVM_ROUTE_CONFIG[network]
    return f"{KYBER_ROUTES}/{cfg['slug']}/api/v1/routes?" + urllib.parse.urlencode({
        "tokenIn": input_token, "tokenOut": output_token, "amountIn": amount,
    })


def parse_kyber_leg(result: FetchResult) -> dict:
    payload = json.loads(result.body)
    route = ((payload.get("data") or {}).get("routeSummary") or {})
    if payload.get("code") != 0 or not route.get("amountOut") or not route.get("route"):
        raise ValueError(str(payload.get("message") or "no_route"))
    return route


def kyber_labels(route: dict) -> list[str]:
    return [str(leg.get("exchange") or leg.get("poolType") or "UNKNOWN")
            for branch in route.get("route") or [] for leg in branch]


def evm_routed_state(buy: dict, sell: dict, probe_raw: int) -> dict:
    sell_out = int(sell["amountOut"])
    gas_usd = sum(numeric(x.get("gasUsd")) or 0.0 for x in (buy, sell))
    l1_usd = sum(numeric(x.get("l1FeeUsd")) or 0.0 for x in (buy, sell))
    quoted_cost = 1.0 - sell_out / probe_raw + (gas_usd + l1_usd) / PROBE_USD
    worst_cost = quoted_cost + 2 * ROUTE_SLIPPAGE_BPS / 10_000
    passes = quoted_cost <= 0.03
    return {
        "buy_out_raw": str(buy["amountOut"]), "sell_out_usdc_raw": str(sell_out),
        "quoted_roundtrip_cost_pct": quoted_cost, "worst_case_cost_pct": worst_cost,
        "buy_price_impact_pct": None, "sell_price_impact_pct": None,
        "buy_routes": kyber_labels(buy), "sell_routes": kyber_labels(sell),
        "route_state": "ROUTED_QUOTE_PASS" if passes else "ROUTED_QUOTE_FAIL",
        "failure_reason": None if passes else "gas_inclusive_roundtrip_cost",
    }


def unavailable_route(state: str, reason: str) -> dict:
    return {
        "buy_out_raw": None, "sell_out_usdc_raw": None,
        "quoted_roundtrip_cost_pct": None, "worst_case_cost_pct": None,
        "buy_price_impact_pct": None, "sell_price_impact_pct": None,
        "buy_routes": [], "sell_routes": [], "route_state": state,
        "failure_reason": reason,
    }


def leader_score(row: dict, flow: dict | None = None) -> float:
    """Ranking only; never upgrades unverifiable capital into verified capital."""
    reserve = max(row.get("reserve") or 0.0, 0.0)
    volume = max(row.get("volume_h24") or 0.0, 0.0)
    buyers, sellers = row.get("buyers_h24") or 0, row.get("sellers_h24") or 0
    participation = buyers + sellers
    balance = buyers / max(participation, 1)
    flow = flow or {}
    external_buy = max(flow.get("external_buy_usd") or 0.0, 0.0)
    distinct_buyers = max(flow.get("distinct_buyers") or 0, 0)
    return round(1.4 * math.log1p(reserve) + math.log1p(volume) + 0.4 * math.log1p(participation) +
                 balance + 0.8 * math.log1p(external_buy) + 0.5 * math.log1p(distinct_buyers), 6)


def outcome_state(first_10x_at: str | None, first_dd35_at: str | None) -> str:
    if first_10x_at and first_dd35_at:
        if first_10x_at == first_dd35_at:
            return "ORDER_AMBIGUOUS"
        return "10X_BEFORE_DD35" if first_10x_at < first_dd35_at else "DD35_BEFORE_10X"
    if first_10x_at:
        return "10X_BEFORE_DD35"
    if first_dd35_at:
        return "DD35_BEFORE_10X"
    return "OPEN"


def run(db_path: Path) -> dict:
    now, cut_id = utc_now(), iso(utc_now())
    conn = init_db(db_path)
    last_row = conn.execute("SELECT created_at FROM cuts ORDER BY created_at DESC LIMIT 1").fetchone()
    if last_row:
        elapsed = (now - parse_time(last_row[0])).total_seconds()
        if elapsed < MIN_CUT_INTERVAL_SECONDS:
            return {
                "cut_id": cut_id,
                "capital_state": "CAPITAL_LOCKED",
                "decision": "SKIP_RATE_GUARD",
                "seconds_since_last_cut": elapsed,
                "minimum_cut_interval_seconds": MIN_CUT_INTERVAL_SECONDS,
            }
    jobs = []
    for geo in GEOS:
        url = "https://trends.google.com/trending/rss?" + urllib.parse.urlencode({"geo": geo})
        jobs.append((f"trends:{geo}", url))
    for network in NETWORKS:
        jobs.append((f"pools:{network}", f"https://api.geckoterminal.com/api/v2/networks/{network}/new_pools?page=1"))
    jobs.append(("fees", "https://api.llama.fi/overview/fees?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true&dataType=dailyFees"))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(curl_fetch, key, url): key for key, url in jobs}
        fetched = {futures[f]: f.result() for f in concurrent.futures.as_completed(futures)}

    health = {k: {"ok": v.ok, "http": v.http_code, "seconds": round(v.seconds, 3), "error": v.error} for k, v in fetched.items()}
    events, pools, primitives = [], [], []
    for key, result in fetched.items():
        if not result.ok:
            continue
        try:
            if key.startswith("trends:"):
                events.extend(parse_trends(result))
            elif key.startswith("pools:"):
                pools.extend(parse_pools(result))
            elif key == "fees":
                primitives = parse_primitives(result)
        except Exception as exc:
            health[key]["ok"] = False
            health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"

    matches = []
    for event in events:
        for pool in pools:
            delta = pool["created"] - event["published"]
            if delta.total_seconds() < 0 or delta > dt.timedelta(hours=FAMILY_WINDOW_HOURS):
                continue
            score, reason = match_score(event["title"], pool["name"])
            if score >= 0.72:
                matches.append({**event, **pool, "score": score, "reason": reason})

    prior_members = [dict(zip(
        ("family_id", "network", "pool_id", "token_id", "pool_name", "pool_created_at", "developer"), row
    )) for row in conn.execute(
        "SELECT family_id,network,pool_id,token_id,pool_name,pool_created_at,developer_address FROM family_members"
    )]
    family_titles = {row[0]: row[1] for row in conn.execute("SELECT family_id,event_title FROM family_freezes")}

    # Candidate and already-frozen tokens get auditable contract/deployer enrichment.
    target_pairs = sorted({(m["network"], m["token_id"]) for m in matches} |
                          {(m["network"], m["token_id"]) for m in prior_members})
    enrichment_truncated = len(target_pairs) > MAX_CANDIDATE_ENRICHMENTS
    target_pairs = target_pairs[:MAX_CANDIDATE_ENRICHMENTS]
    info_jobs = []
    for network, token_id in target_pairs:
        address = address_from_id(token_id)
        info_jobs.append((f"tokeninfo:{network}:{token_id}",
                          f"https://api.geckoterminal.com/api/v2/networks/{network}/tokens/{address}/info"))
    info_results = {}
    if info_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in info_jobs}
            info_results = {futures[f]: f.result() for f in concurrent.futures.as_completed(futures)}
    enrichments = {}
    for key, result in info_results.items():
        health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
        if not result.ok:
            continue
        try:
            _, network, token_id = key.split(":", 2)
            enrichments[(network, token_id)] = parse_token_info(result)
        except Exception as exc:
            health[key]["ok"] = False
            health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    if enrichment_truncated:
        health["candidate_enrichment_capacity"] = {
            "ok": False, "http": 0, "seconds": 0.0,
            "error": f"{len(target_pairs)}+ targets exceed cap {MAX_CANDIDATE_ENRICHMENTS}",
        }

    # Metadata links are event-specific. Visual evidence is deliberately strict:
    # only near-identical perceptual hashes count, never vague subject similarity.
    event_titles_by_token = {}
    pictures_by_token = {}
    for m in matches:
        key = (m["network"], m["token_id"])
        event_titles_by_token.setdefault(key, set()).add(m["title"])
        if m.get("event_picture"):
            pictures_by_token.setdefault(key, set()).add(m["event_picture"])
    for member in prior_members:
        key = (member["network"], member["token_id"])
        if member["family_id"] in family_titles:
            event_titles_by_token.setdefault(key, set()).add(family_titles[member["family_id"]])

    image_urls = {info.get("image_url") for info in enrichments.values() if info.get("image_url")}
    image_urls |= {url for urls in pictures_by_token.values() for url in urls}
    image_hashes = {}
    if image_urls:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(curl_fetch, "image", url, 12): url for url in image_urls}
            for future in concurrent.futures.as_completed(futures):
                result, url = future.result(), futures[future]
                if result.ok:
                    image_hashes[url] = image_dhash(result.body)
    for key, info in enrichments.items():
        titles = event_titles_by_token.get(key, set())
        info["metadata_event_link"] = any(metadata_links_event(title, info) for title in titles)
        token_hash = image_hashes.get(info.get("image_url"))
        distances = [hash_distance(token_hash, image_hashes.get(url)) for url in pictures_by_token.get(key, set())]
        info["image_dhash"] = token_hash
        info["visual_event_link"] = any(d is not None and d <= 6 for d in distances)

    grouped_matches = {}
    for match in matches:
        grouped_matches.setdefault(normalize(match["title"]), []).append(match)
    family_evaluations, new_freezes, new_members = [], [], []
    for normalized_title, group in grouped_matches.items():
        previous = conn.execute(
            "SELECT MIN(published_at) FROM attention_events WHERE normalized_title=?", (normalized_title,)
        ).fetchone()[0]
        timestamps = [m["published"] for m in group]
        if previous:
            timestamps.append(parse_time(previous))
        event_published = min(timestamps)
        family_id = stable_id(normalized_title, iso(event_published))
        geos = sorted({m["geo"] for m in group})
        news_sources = sorted({normalize(s["source"]) for m in group for s in m.get("support", []) if s.get("source")})
        best_by_token = {}
        for member in group:
            current = best_by_token.get(member["token_id"])
            if current is None or (member.get("reserve") or 0) > (current.get("reserve") or 0):
                best_by_token[member["token_id"]] = member
        developers = {enrichments.get((m["network"], m["token_id"]), {}).get("developer")
                      for m in best_by_token.values()}
        developers.discard(None)
        source_gate = len(geos) >= 2 or len(news_sources) >= 2
        token_gate = len(best_by_token) >= 2
        deployer_gate = len(developers) >= 2
        eligible = source_gate and token_gate and deployer_gate
        state = "FROZEN" if eligible else (
            "SOURCE_UNVERIFIED" if not source_gate else
            "TOKEN_FAMILY_TOO_SMALL" if not token_gate else "DEPLOYER_UNVERIFIED"
        )
        evaluation = {
            "family_id": family_id, "event": normalized_title, "geos": geos,
            "news_sources": news_sources, "token_count": len(best_by_token),
            "developer_count": len(developers), "state": state,
        }
        family_evaluations.append(evaluation)
        exists = conn.execute("SELECT 1 FROM family_freezes WHERE family_id=?", (family_id,)).fetchone()
        if eligible and not exists:
            exemplar = min(group, key=lambda m: m["published"])
            new_freezes.append({**evaluation, "event_title": exemplar["title"], "event_published": event_published})
            for member in best_by_token.values():
                info = enrichments.get((member["network"], member["token_id"]), {})
                new_members.append({
                    "family_id": family_id, **member, "developer": info.get("developer"),
                    "metadata_event_link": bool(info.get("metadata_event_link")),
                    "visual_event_link": bool(info.get("visual_event_link")),
                })

    all_members = prior_members + [{
        "family_id": m["family_id"], "network": m["network"], "pool_id": m["pool_id"],
        "token_id": m["token_id"], "pool_name": m["name"], "pool_created_at": iso(m["created"]),
        "developer": m["developer"],
    } for m in new_members]
    current_pool_map = {(p["network"], p["pool_id"]): p for p in pools}
    missing_members = [m for m in all_members if (m["network"], m["pool_id"]) not in current_pool_map]
    outcome_truncated = len(missing_members) > MAX_OUTCOME_REFRESHES
    missing_members = missing_members[:MAX_OUTCOME_REFRESHES]
    detail_jobs = []
    for member in missing_members:
        address = address_from_id(member["pool_id"])
        detail_jobs.append((f"outcome:{member['network']}:{member['pool_id']}",
                            f"https://api.geckoterminal.com/api/v2/networks/{member['network']}/pools/{address}"))
    if detail_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in detail_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        detail = parse_pool_detail(result)
                        current_pool_map[(detail["network"], detail["pool_id"])] = detail
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    if outcome_truncated:
        health["outcome_refresh_capacity"] = {
            "ok": False, "http": 0, "seconds": 0.0,
            "error": f"more than {MAX_OUTCOME_REFRESHES} missing frozen pools",
        }

    trade_members = all_members[:MAX_TRADE_REFRESHES]
    trade_truncated = len(all_members) > MAX_TRADE_REFRESHES
    trade_jobs = []
    for member in trade_members:
        address = address_from_id(member["pool_id"])
        trade_jobs.append((f"trades:{member['network']}:{member['pool_id']}",
                           f"https://api.geckoterminal.com/api/v2/networks/{member['network']}/pools/{address}/trades"))
    trade_flows = {}
    if trade_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in trade_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        _, network, pool_id = key.split(":", 2)
                        member = next(m for m in trade_members if m["network"] == network and m["pool_id"] == pool_id)
                        trade_flows[(network, pool_id)] = parse_trade_flow(result, member.get("developer"))
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    if trade_truncated:
        health["trade_refresh_capacity"] = {
            "ok": False, "http": 0, "seconds": 0.0,
            "error": f"more than {MAX_TRADE_REFRESHES} frozen pools",
        }

    # Solana execution gate: quote a real $50 USDC -> token route, then immediately
    # feed the quoted raw token output through the reverse token -> USDC route.
    # No transaction is signed or submitted.
    routable_members = [m for m in all_members if m["network"] == "solana" or m["network"] in EVM_ROUTE_CONFIG]
    route_truncated = len(routable_members) > MAX_ROUTE_SIMULATIONS
    selected_route_members = routable_members[:MAX_ROUTE_SIMULATIONS]
    solana_members = [m for m in selected_route_members if m["network"] == "solana"]
    probe_raw = int(round(PROBE_USD * 1_000_000))
    buy_results = {}
    buy_jobs = []
    for member in solana_members:
        mint = address_from_id(member["token_id"])
        buy_jobs.append((f"jupiter_buy:{member['pool_id']}", quote_url(USDC_MINT, mint, str(probe_raw))))
    if buy_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in buy_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        buy_results[key.split(":", 1)[1]] = parse_jupiter_leg(result)
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    sell_jobs = []
    for member in solana_members:
        buy = buy_results.get(member["pool_id"])
        if buy:
            mint = address_from_id(member["token_id"])
            sell_jobs.append((f"jupiter_sell:{member['pool_id']}", quote_url(mint, USDC_MINT, str(buy["outAmount"]))))
    route_simulations = {}
    if sell_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in sell_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                pool_id = key.split(":", 1)[1]
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        sell = parse_jupiter_leg(result)
                        route_simulations[("solana", pool_id)] = routed_state(buy_results[pool_id], sell, probe_raw)
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    for member in solana_members:
        if (member["network"], member["pool_id"]) not in route_simulations:
            route_simulations[(member["network"], member["pool_id"])] = unavailable_route("NO_ROUTE", "buy_or_sell_quote_unavailable")

    evm_members = [m for m in selected_route_members if m["network"] in EVM_ROUTE_CONFIG]
    evm_buys = {}
    evm_buy_jobs = []
    for member in evm_members:
        cfg = EVM_ROUTE_CONFIG[member["network"]]
        raw = int(round(PROBE_USD * 10 ** cfg["decimals"]))
        token = address_from_id(member["token_id"])
        evm_buy_jobs.append((f"kyber_buy:{member['network']}:{member['pool_id']}",
                             kyber_quote_url(member["network"], cfg["stable"], token, str(raw))))
    if evm_buy_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in evm_buy_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        _, network, pool_id = key.split(":", 2)
                        evm_buys[(network, pool_id)] = parse_kyber_leg(result)
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    evm_sell_jobs = []
    for member in evm_members:
        buy = evm_buys.get((member["network"], member["pool_id"]))
        if buy:
            cfg = EVM_ROUTE_CONFIG[member["network"]]
            token = address_from_id(member["token_id"])
            evm_sell_jobs.append((f"kyber_sell:{member['network']}:{member['pool_id']}",
                                  kyber_quote_url(member["network"], token, cfg["stable"], str(buy["amountOut"]))))
    if evm_sell_jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
            futures = {ex.submit(curl_fetch, key, url): key for key, url in evm_sell_jobs}
            for future in concurrent.futures.as_completed(futures):
                result, key = future.result(), futures[future]
                _, network, pool_id = key.split(":", 2)
                health[key] = {"ok": result.ok, "http": result.http_code, "seconds": round(result.seconds, 3), "error": result.error}
                if result.ok:
                    try:
                        sell = parse_kyber_leg(result)
                        cfg = EVM_ROUTE_CONFIG[network]
                        raw = int(round(PROBE_USD * 10 ** cfg["decimals"]))
                        route_simulations[(network, pool_id)] = evm_routed_state(evm_buys[(network, pool_id)], sell, raw)
                    except Exception as exc:
                        health[key]["ok"] = False
                        health[key]["error"] = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    for member in evm_members:
        if (member["network"], member["pool_id"]) not in route_simulations:
            route_simulations[(member["network"], member["pool_id"])] = unavailable_route("NO_ROUTE", "buy_or_sell_quote_unavailable")
    selected_keys = {(m["network"], m["pool_id"]) for m in selected_route_members}
    for member in all_members:
        if member["network"] not in EVM_ROUTE_CONFIG and member["network"] != "solana":
            route_simulations[(member["network"], member["pool_id"])] = unavailable_route("ROUTER_UNSUPPORTED", "no_admitted_public_roundtrip_router")
        elif (member["network"], member["pool_id"]) not in selected_keys:
            route_simulations[(member["network"], member["pool_id"])] = unavailable_route("CAPACITY_SKIPPED", "route_simulation_cap")
    if route_truncated:
        health["route_simulation_capacity"] = {
            "ok": False, "http": 0, "seconds": 0.0,
            "error": f"more than {MAX_ROUTE_SIMULATIONS} routable frozen pools",
        }

    observations = []
    for member in all_members:
        pool = current_pool_map.get((member["network"], member["pool_id"]))
        if not pool:
            continue
        info = enrichments.get((member["network"], member["token_id"]), {})
        if not info:
            row = conn.execute(
                "SELECT holders_count,top10_pct,mint_authority,freeze_authority,honeypot FROM token_enrichment "
                "WHERE network=? AND token_id=? ORDER BY cut_id DESC LIMIT 1",
                (member["network"], member["token_id"]),
            ).fetchone()
            if row:
                info = dict(zip(("holders_count", "top10_pct", "mint_authority", "freeze_authority", "honeypot"), row))
        impact = estimated_cpmm_impact(pool.get("reserve"))
        route = route_simulations.get((member["network"], member["pool_id"]))
        if route:
            execution = route["route_state"]
        else:
            execution = "PROXY_PASS" if impact is not None and impact <= 0.05 and (pool.get("sellers_h24") or 0) >= 3 else "PROXY_FAIL"
        if str(info.get("honeypot")).lower() == "true" or (info.get("top10_pct") or 0) >= 90:
            contract = "VETO"
        elif member["network"] == "solana" and (info.get("mint_authority") or info.get("freeze_authority")):
            contract = "VETO"
        elif info.get("holders_count") is None or str(info.get("honeypot", "unknown")).lower() == "unknown":
            contract = "UNVERIFIED"
        else:
            contract = "PROXY_PASS"
        flow = trade_flows.get((member["network"], member["pool_id"]), {})
        observations.append({**member, **pool, "holder_count": info.get("holders_count"),
                             "top10_pct": info.get("top10_pct"), "impact": impact,
                             "execution": execution, "contract": contract, "flow": flow, "route": route,
                             "score": leader_score(pool, flow)})
    for family_id in {o["family_id"] for o in observations}:
        ranked = sorted((o for o in observations if o["family_id"] == family_id), key=lambda o: o["score"], reverse=True)
        for rank, observation in enumerate(ranked, 1):
            observation["rank"] = rank

    with conn:
        conn.execute("INSERT INTO cuts VALUES (?,?,?,?,?)", (cut_id, iso(now), "FUTURE_ONLY", "CAPITAL_LOCKED", json.dumps(health, sort_keys=True)))
        conn.executemany("INSERT INTO attention_events VALUES (?,?,?,?,?,?)", [
            (cut_id, e["geo"], e["rank"], e["title"], normalize(e["title"]), iso(e["published"])) for e in events
        ])
        conn.executemany("INSERT INTO attention_support VALUES (?,?,?,?,?,?,?,?)", [
            (cut_id, e["geo"], e["title"], s["source"], s["article_title"], s["article_url"],
             s["picture_url"], e["event_picture"]) for e in events for s in e.get("support", [])
            if s.get("source") and s.get("article_url")
        ])
        conn.executemany(
            "INSERT INTO pools (cut_id,network,pool_id,token_id,dex_id,name,created_at,reserve_usd,fdv_usd,"
            "volume_h24,buyers_h24,sellers_h24,price_usd,market_cap_usd) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, p["network"], p["pool_id"], p["token_id"], p["dex_id"], p["name"], iso(p["created"]),
             p["reserve"], p["fdv"], p["volume_h24"], p["buyers_h24"], p["sellers_h24"],
             p["price"], p["market_cap"]) for p in pools])
        conn.executemany("INSERT INTO semantic_matches VALUES (?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, m["geo"], m["title"], iso(m["published"]), m["network"], m["pool_id"], m["token_id"],
             m["name"], iso(m["created"]), m["score"], m["reason"]) for m in matches
        ])
        conn.executemany("INSERT INTO primitives VALUES (?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, p["slug"], p["name"], p["category"], p["chains"], p["total24h"], p["total30d"],
             p["change_1d"], p["change_7dover7d"], p["change_30dover30d"]) for p in primitives
        ])
        conn.executemany("INSERT INTO token_enrichment VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, network, token_id, info.get("developer"), info.get("image_url"), info.get("image_dhash"),
             json.dumps(info.get("websites") or [], ensure_ascii=False), json.dumps(info.get("socials") or {}, ensure_ascii=False),
             info.get("description"), info.get("holders_count"), info.get("top10_pct"), info.get("mint_authority"),
             info.get("freeze_authority"), info.get("honeypot"), int(bool(info.get("gt_verified"))),
             int(bool(info.get("metadata_event_link"))), int(bool(info.get("visual_event_link"))))
            for (network, token_id), info in enrichments.items()
        ])
        conn.executemany("INSERT INTO family_freezes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (f["family_id"], cut_id, iso(now), f["event_title"], f["event"], iso(f["event_published"]),
             json.dumps(f["geos"]), json.dumps(f["news_sources"], ensure_ascii=False), f["token_count"],
             f["developer_count"], "PASS", "PASS", "FROZEN") for f in new_freezes
        ])
        conn.executemany("INSERT INTO family_members VALUES (?,?,?,?,?,?,?,?,?,?)", [
            (m["family_id"], m["network"], m["pool_id"], m["token_id"], m["name"], iso(m["created"]),
             m["developer"], m["score"], int(m["metadata_event_link"]), int(m["visual_event_link"]))
            for m in new_members
        ])
        conn.executemany("INSERT INTO leader_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, o["family_id"], o["network"], o["pool_id"], o["token_id"], iso(now), o.get("price"),
             o.get("reserve"), o.get("fdv"), o.get("market_cap"), o.get("volume_h24"), o.get("buyers_h24"),
             o.get("sellers_h24"), o.get("holder_count"), o.get("top10_pct"), o.get("impact"),
             o["execution"], o["contract"], o["score"], o["rank"]) for o in observations
        ])
        conn.executemany("INSERT INTO capital_flow_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, o["family_id"], o["network"], o["pool_id"], o["token_id"], iso(now),
             o["flow"].get("trade_count", 0), o["flow"].get("distinct_buyers", 0),
             o["flow"].get("distinct_sellers", 0), o["flow"].get("external_buy_usd", 0.0),
             o["flow"].get("external_sell_usd", 0.0), o["flow"].get("max_buyer_share"),
             int(bool(o["flow"].get("developer_seen"))),
             o["flow"].get("address_diversity_state", "UNAVAILABLE"))
            for o in observations
        ])
        conn.executemany("INSERT INTO route_simulations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", [
            (cut_id, o["family_id"], o["network"], o["pool_id"], o["token_id"], iso(now), PROBE_USD,
             o["route"].get("buy_out_raw"), o["route"].get("sell_out_usdc_raw"),
             o["route"].get("quoted_roundtrip_cost_pct"), o["route"].get("worst_case_cost_pct"),
             o["route"].get("buy_price_impact_pct"), o["route"].get("sell_price_impact_pct"),
             json.dumps(o["route"].get("buy_routes") or []), json.dumps(o["route"].get("sell_routes") or []),
             o["route"].get("route_state", "NO_ROUTE"), o["route"].get("failure_reason"))
            for o in observations if o.get("route") is not None
        ])
        for o in observations:
            old = conn.execute(
                "SELECT baseline_cut_id,baseline_at,baseline_price_usd,high_multiple,low_multiple,first_3x_at,"
                "first_5x_at,first_10x_at,first_dd35_at FROM outcomes WHERE family_id=? AND network=? AND pool_id=?",
                (o["family_id"], o["network"], o["pool_id"]),
            ).fetchone()
            price = o.get("price")
            if old:
                baseline_cut, baseline_at, baseline_price, high, low, first3, first5, first10, firstdd = old
            else:
                baseline_cut, baseline_at, baseline_price = cut_id, iso(now), price
                high, low, first3, first5, first10, firstdd = 1.0, 1.0, None, None, None, None
            multiple = price / baseline_price if price and baseline_price and baseline_price > 0 else None
            if multiple is not None:
                high, low = max(high or multiple, multiple), min(low or multiple, multiple)
                first3 = first3 or (iso(now) if multiple >= 3 else None)
                first5 = first5 or (iso(now) if multiple >= 5 else None)
                first10 = first10 or (iso(now) if multiple >= 10 else None)
                firstdd = firstdd or (iso(now) if multiple <= 0.65 else None)
            state = outcome_state(first10, firstdd)
            conn.execute(
                "INSERT OR REPLACE INTO outcomes VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (o["family_id"], o["network"], o["pool_id"], o["token_id"], baseline_cut, baseline_at,
                 baseline_price, high, low, first3, first5, first10, firstdd, state, iso(now)),
            )

    lanes = {}
    for network in NETWORKS:
        rows = sorted((p for p in pools if p["network"] == network), key=lambda x: x["created"], reverse=True)
        span = (rows[0]["created"] - rows[-1]["created"]).total_seconds() if len(rows) > 1 else None
        lanes[network] = {
            "rows": len(rows), "page_span_seconds": span,
            "approx_births_per_minute": round(60 * (len(rows) - 1) / span, 2) if span and span > 0 else None,
        }

    event_geos = {}
    for e in events:
        event_geos.setdefault(normalize(e["title"]), set()).add(e["geo"])
    multi_geo = sorted(k for k, geos in event_geos.items() if len(geos) >= 2)
    hype_pass = [f["family_id"] for f in family_evaluations if f["state"] == "FROZEN"]
    leader_shortlist = [{
        "family_id": o["family_id"], "network": o["network"], "pool_id": o["pool_id"],
        "token_id": o["token_id"], "leader_rank": o["rank"], "leader_score": o["score"],
        "execution_state": o["execution"], "contract_state": o["contract"],
        "external_capital_state": (
            "ADDRESS_DIVERSE_ONLY" if o["flow"].get("address_diversity_state") == "ADDRESS_DIVERSE"
            else o["flow"].get("address_diversity_state", "UNAVAILABLE")
        ),
    } for o in observations if o["rank"] == 1]

    coverage_complete = all(item["ok"] for item in health.values())
    if not coverage_complete:
        decision = "COVERAGE_INSUFFICIENT"
    elif hype_pass:
        decision = "REVIEW_REQUIRED"
    else:
        decision = "NO_TRADE"

    summary = {
        "cut_id": cut_id, "capital_state": "CAPITAL_LOCKED", "sources_ok": sum(1 for h in health.values() if h["ok"]),
        "sources_total": len(health), "events": len(events), "pools": len(pools), "semantic_candidates": len(matches),
        "attention_support_rows": sum(len(e.get("support", [])) for e in events),
        "multi_geo_events": multi_geo, "family_evaluations": family_evaluations,
        "newly_frozen_families": [f["family_id"] for f in new_freezes],
        "hype_birth_pass": hype_pass, "leader_shortlist": leader_shortlist,
        "actionable_leaders": [], "outcome_observations": len(observations),
        "primitive_scouts": [p["name"] for p in primitives],
        "lanes": lanes, "coverage_complete": coverage_complete,
        "failed_sources": sorted(k for k, item in health.items() if not item["ok"]),
        "decision": decision,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("mdrtf_future_ledger.sqlite3"))
    parser.add_argument("--loop", action="store_true", help="run continuously; emits one JSON object per cut")
    parser.add_argument("--interval", type=int, default=MIN_CUT_INTERVAL_SECONDS,
                        help=f"seconds between completed cuts (minimum {MIN_CUT_INTERVAL_SECONDS})")
    parser.add_argument("--max-cuts", type=int, default=0, help="stop after N loop cuts; 0 means unlimited")
    args = parser.parse_args()
    if not args.loop:
        print(json.dumps(run(args.db.resolve()), ensure_ascii=False, indent=2, sort_keys=True))
        return
    interval = max(args.interval, MIN_CUT_INTERVAL_SECONDS)
    completed = 0
    while not args.max_cuts or completed < args.max_cuts:
        started = time.monotonic()
        try:
            result = run(args.db.resolve())
        except Exception as exc:
            result = {
                "cut_id": iso(utc_now()), "capital_state": "CAPITAL_LOCKED",
                "decision": "RUNTIME_ERROR", "error": f"{type(exc).__name__}:{str(exc)[:300]}",
            }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
        completed += 1
        if not args.max_cuts or completed < args.max_cuts:
            time.sleep(max(0.0, interval - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
