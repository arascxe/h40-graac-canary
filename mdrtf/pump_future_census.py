"""Future-only Pump launch and trade census using first-party public endpoints.

The census is deliberately fail-closed.  A launch snapshot is complete only
when it overlaps the prior successful request boundary.  A token's trade
refresh is complete only when it reaches the previous head (or the token's
birth on its first refresh).  Missing overlap is recorded as a gap and is
never converted into negative evidence.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
from typing import Any


CENSUS_VERSION = "PUMP_FUTURE_CENSUS_V1_20260918"
PUMP_PROGRAM = "pump"
PUMP_PROGRAM_ID = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"
TRADE_WINDOW_MINUTES = 30


def _iso(value: dt.datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def _millis(value: dt.datetime) -> int:
    return int(value.timestamp() * 1000)


def _number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pump_census_runtime (
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          version TEXT NOT NULL, started_at TEXT NOT NULL,
          last_complete_request_at TEXT, last_complete_cut_id TEXT,
          capital_state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pump_census_cuts (
          cut_id TEXT PRIMARY KEY, request_started_at TEXT NOT NULL,
          source_http INTEGER NOT NULL, rows_seen INTEGER NOT NULL,
          oldest_created_at TEXT, newest_created_at TEXT,
          inserted_launches INTEGER NOT NULL, overlap_state TEXT NOT NULL,
          source_state TEXT NOT NULL, error TEXT
        );
        CREATE TABLE IF NOT EXISTS pump_launches (
          mint TEXT PRIMARY KEY, first_seen_cut_id TEXT NOT NULL,
          first_seen_at TEXT NOT NULL, created_at TEXT NOT NULL,
          creator TEXT NOT NULL, name TEXT, symbol TEXT,
          bonding_curve TEXT, associated_bonding_curve TEXT,
          pool_address TEXT, program TEXT NOT NULL,
          complete_at_first_seen INTEGER NOT NULL,
          source TEXT NOT NULL, raw_sha256 TEXT NOT NULL,
          last_trade_fetch_at TEXT, last_trade_head TEXT,
          trade_coverage_state TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pump_launch_created
          ON pump_launches(created_at, mint);
        CREATE TABLE IF NOT EXISTS pump_trade_fetches (
          cut_id TEXT NOT NULL, mint TEXT NOT NULL,
          fetched_at TEXT NOT NULL, pages INTEGER NOT NULL,
          rows_seen INTEGER NOT NULL, inserted_trades INTEGER NOT NULL,
          previous_head TEXT, newest_head TEXT,
          previous_head_reached INTEGER NOT NULL,
          coverage_state TEXT NOT NULL, http_state TEXT NOT NULL,
          error TEXT, PRIMARY KEY(cut_id, mint)
        );
        CREATE TABLE IF NOT EXISTS pump_raw_trades (
          trade_id TEXT PRIMARY KEY, first_seen_cut_id TEXT NOT NULL,
          mint TEXT NOT NULL, pool_address TEXT NOT NULL,
          creator TEXT NOT NULL, block_timestamp TEXT NOT NULL,
          wallet TEXT NOT NULL, kind TEXT NOT NULL,
          token_amount REAL NOT NULL, usd_value REAL NOT NULL,
          token_price_usd REAL, tx_signature TEXT NOT NULL,
          slot_index_id TEXT, source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pump_trade_mint_time
          ON pump_raw_trades(mint, block_timestamp, trade_id);
        """
    )


def _parse_launches(body: bytes) -> list[dict[str, Any]]:
    payload = json.loads(body)
    if not isinstance(payload, list):
        raise ValueError("launch_payload_not_list")
    rows = []
    for raw in payload:
        mint = str(raw.get("mint") or "")
        creator = str(raw.get("creator") or "")
        created_ms = raw.get("created_timestamp")
        program = str(raw.get("program") or "")
        if not mint or not creator or not isinstance(created_ms, (int, float)) or program != PUMP_PROGRAM:
            continue
        created = dt.datetime.fromtimestamp(float(created_ms) / 1000, tz=dt.timezone.utc)
        rows.append({
            "mint": mint, "creator": creator, "created": created,
            "name": str(raw.get("name") or ""), "symbol": str(raw.get("symbol") or ""),
            "bonding_curve": raw.get("bonding_curve"),
            "associated_bonding_curve": raw.get("associated_bonding_curve"),
            "pool_address": str(raw.get("pool_address") or raw.get("bonding_curve") or mint),
            "program": program, "complete": bool(raw.get("complete")),
            "raw_sha256": hashlib.sha256(
                json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
            ).hexdigest(),
        })
    return sorted(rows, key=lambda row: (row["created"], row["mint"]), reverse=True)


def ingest_launch_snapshot(
    conn: sqlite3.Connection,
    cut_id: str,
    request_started_at: dt.datetime,
    *,
    ok: bool,
    http_code: int,
    body: bytes = b"",
    error: str = "",
) -> dict[str, Any]:
    """Ingest one first-party launch snapshot without backfilling before t0."""
    ensure_schema(conn)
    request_started_at = request_started_at.astimezone(dt.timezone.utc)
    timestamp = _iso(request_started_at)
    conn.execute(
        "INSERT OR IGNORE INTO pump_census_runtime VALUES (1,?,?,?,?,?)",
        (CENSUS_VERSION, timestamp, None, None, "CAPITAL_LOCKED"),
    )
    runtime = conn.execute(
        "SELECT started_at,last_complete_request_at FROM pump_census_runtime WHERE singleton=1"
    ).fetchone()
    started_at = _time(runtime[0])
    previous_complete = _time(runtime[1]) if runtime[1] else None

    rows: list[dict[str, Any]] = []
    parse_error = ""
    if ok:
        try:
            rows = _parse_launches(body)
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            parse_error = f"parse:{type(exc).__name__}:{str(exc)[:120]}"
    source_ok = bool(ok and rows and not parse_error)
    oldest = min((row["created"] for row in rows), default=None)
    newest = max((row["created"] for row in rows), default=None)
    if not source_ok:
        overlap_state, source_state = "UNKNOWN", "SOURCE_ERROR"
    elif previous_complete is None:
        overlap_state, source_state = "BASELINE_ESTABLISHED", "BASELINE_ONLY"
    elif oldest <= previous_complete <= newest:
        overlap_state, source_state = "OVERLAP_VERIFIED", "COMPLETE_INTERVAL"
    else:
        overlap_state, source_state = "NO_OVERLAP", "GAP"

    inserted = 0
    if source_ok:
        for row in rows:
            if row["created"] < started_at:
                continue
            before = conn.total_changes
            conn.execute(
                "INSERT OR IGNORE INTO pump_launches VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (row["mint"], cut_id, timestamp, _iso(row["created"]), row["creator"],
                 row["name"], row["symbol"], row["bonding_curve"], row["associated_bonding_curve"],
                 row["pool_address"], row["program"], int(row["complete"]),
                 "PUMP_FIRST_PARTY_LAUNCHES", row["raw_sha256"], None, None,
                 "PENDING",),
            )
            inserted += int(conn.total_changes > before)

    conn.execute(
        "INSERT OR REPLACE INTO pump_census_cuts VALUES (?,?,?,?,?,?,?,?,?,?)",
        (cut_id, timestamp, int(http_code), len(rows), _iso(oldest) if oldest else None,
         _iso(newest) if newest else None, inserted, overlap_state, source_state,
         parse_error or error or None),
    )
    if source_state in {"BASELINE_ONLY", "COMPLETE_INTERVAL"}:
        conn.execute(
            "UPDATE pump_census_runtime SET last_complete_request_at=?,last_complete_cut_id=? WHERE singleton=1",
            (timestamp, cut_id),
        )
    return {
        "version": CENSUS_VERSION, "capital_state": "CAPITAL_LOCKED",
        "started_at": runtime[0], "source": "PUMP_FIRST_PARTY_LAUNCHES",
        "source_http": int(http_code), "rows_seen": len(rows),
        "inserted_launches": inserted, "overlap_state": overlap_state,
        "coverage_state": source_state,
        "oldest_created_at": _iso(oldest) if oldest else None,
        "newest_created_at": _iso(newest) if newest else None,
        "total_future_launches": conn.execute("SELECT COUNT(*) FROM pump_launches").fetchone()[0],
    }


def trade_targets(conn: sqlite3.Connection, observed_at: dt.datetime, limit: int) -> list[dict[str, str]]:
    """Oldest-due active launches first; no outcome-based selection."""
    ensure_schema(conn)
    cutoff = _iso(observed_at.astimezone(dt.timezone.utc) - dt.timedelta(minutes=TRADE_WINDOW_MINUTES))
    rows = conn.execute(
        "SELECT mint,pool_address,creator,created_at,last_trade_head FROM pump_launches "
        "WHERE created_at>=? ORDER BY (last_trade_fetch_at IS NOT NULL),"
        "COALESCE(last_trade_fetch_at,created_at),created_at,mint LIMIT ?",
        (cutoff, int(limit)),
    ).fetchall()
    return [dict(zip(("mint", "pool_address", "creator", "created_at", "previous_head"), row)) for row in rows]


def trade_page_url(mint: str, cursor: str = "0", limit: int = 100) -> str:
    from urllib.parse import urlencode

    return f"https://swap-api.pump.fun/v2/coins/{mint}/trades?" + urlencode({
        "limit": min(max(int(limit), 1), 100), "cursor": cursor, "program": PUMP_PROGRAM,
    })


def parse_trade_page(body: bytes) -> tuple[list[dict[str, Any]], str | None, bool]:
    payload = json.loads(body)
    trades = payload.get("trades")
    pagination = payload.get("pagination")
    if not isinstance(trades, list) or not isinstance(pagination, dict):
        raise ValueError("malformed_trade_page")
    next_cursor = pagination.get("nextCursor") or pagination.get("next_cursor")
    return trades, str(next_cursor) if next_cursor else None, bool(pagination.get("hasMore"))


def ingest_trade_refresh(
    conn: sqlite3.Connection,
    cut_id: str,
    observed_at: dt.datetime,
    target: dict[str, str],
    pages: list[list[dict[str, Any]]],
    *,
    reached_end: bool,
    http_state: str = "OK",
    error: str = "",
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Store normalized trades and return rows suitable for the PPSC evaluator."""
    ensure_schema(conn)
    timestamp = _iso(observed_at)
    started_at = _time(conn.execute(
        "SELECT started_at FROM pump_census_runtime WHERE singleton=1"
    ).fetchone()[0])
    previous_head = target.get("previous_head")
    raw_rows = [row for page in pages for row in page]
    ids = [str(row.get("slotIndexId") or row.get("tx") or "") for row in raw_rows]
    previous_reached = bool(previous_head and previous_head in ids)
    first_refresh_complete = bool(not previous_head and reached_end)
    if http_state != "OK":
        coverage = "SOURCE_ERROR"
    elif previous_reached or first_refresh_complete:
        coverage = "COMPLETE_INTERVAL"
    elif previous_head:
        coverage = "PREVIOUS_HEAD_NOT_REACHED"
    else:
        coverage = "FIRST_WINDOW_TRUNCATED"
    newest_head = ids[0] if ids else previous_head
    inserted = 0
    ppsc_rows = []
    for raw in raw_rows:
        trade_id = str(raw.get("slotIndexId") or raw.get("tx") or "")
        signature = str(raw.get("tx") or "")
        wallet = str(raw.get("userAddress") or "")
        kind = str(raw.get("type") or "").lower()
        block_timestamp = str(raw.get("timestamp") or "")
        amount = _number(raw.get("baseAmount"))
        usd = _number(raw.get("amountUsd"))
        price = _number(raw.get("fillPriceUsd") or raw.get("priceUsd"))
        try:
            block_dt = _time(block_timestamp)
        except (TypeError, ValueError):
            continue
        if (not trade_id or not signature or not wallet or kind not in {"buy", "sell"}
                or amount is None or amount <= 0 or usd is None or usd <= 0
                or block_dt < started_at or block_dt > observed_at.astimezone(dt.timezone.utc)):
            continue
        before = conn.total_changes
        conn.execute(
            "INSERT OR IGNORE INTO pump_raw_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (trade_id, cut_id, target["mint"], target["pool_address"], target["creator"],
             _iso(block_dt), wallet, kind, amount, usd, price, signature,
             str(raw.get("slotIndexId") or "") or None, "PUMP_FIRST_PARTY_SWAP_API"),
        )
        was_inserted = conn.total_changes > before
        inserted += int(was_inserted)
        if was_inserted:
            ppsc_rows.append({
                "trade_id": trade_id, "network": "solana",
                "pool_id": f"solana_{target['pool_address']}",
                "token_id": f"solana_{target['mint']}", "wallet": wallet,
                "block_timestamp": _iso(block_dt), "kind": kind,
                "token_amount": amount, "usd_value": usd,
                "token_price_usd": price, "developer_address": target["creator"],
                "source": "PUMP_FIRST_PARTY_SWAP_API",
            })
    conn.execute(
        "INSERT OR REPLACE INTO pump_trade_fetches VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (cut_id, target["mint"], timestamp, len(pages), len(raw_rows), inserted,
         previous_head, newest_head, int(previous_reached or first_refresh_complete),
         coverage, http_state, error or None),
    )
    conn.execute(
        "UPDATE pump_launches SET last_trade_fetch_at=?,last_trade_head=?,trade_coverage_state=? WHERE mint=?",
        (timestamp, newest_head, coverage, target["mint"]),
    )
    return ({
        "mint": target["mint"], "pages": len(pages), "rows_seen": len(raw_rows),
        "inserted_trades": inserted, "coverage_state": coverage,
        "previous_head_reached": bool(previous_reached or first_refresh_complete),
    }, ppsc_rows)


def census_totals(conn: sqlite3.Connection) -> dict[str, Any]:
    ensure_schema(conn)
    states = dict(conn.execute(
        "SELECT trade_coverage_state,COUNT(*) FROM pump_launches GROUP BY trade_coverage_state"
    ).fetchall())
    return {
        "total_future_launches": conn.execute("SELECT COUNT(*) FROM pump_launches").fetchone()[0],
        "total_future_trades": conn.execute("SELECT COUNT(*) FROM pump_raw_trades").fetchone()[0],
        "trade_coverage_by_state": states,
        "capital_state": "CAPITAL_LOCKED",
    }
