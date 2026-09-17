"""Future-only Persistent Public-Skill Consensus (PPSC) shadow lane.

The lane learns wallet skill only from swaps observed after its own start time.
It records realized (sold) performance across independent tokens and permits a
consensus signal only when already-qualified wallets with verified independent
funding roots buy the same token.  It is paper-only and never signs a trade.
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from collections import defaultdict
from typing import Any


PPSC_VERSION = "PPSC_V1_20260917"
MIN_CLOSED_TOKENS = 3
MIN_PROFITABLE_TOKENS = 2
MIN_WIN_RATE = 0.60
MIN_PROFIT_FACTOR = 1.50
MAX_TOP_WINNER_SHARE = 0.70
MIN_CONSENSUS_WALLETS = 3
MIN_INDEPENDENT_ROOTS = 3
MAX_CONSENSUS_WALLET_SHARE = 0.50
MAX_UNCONSUMED_MULTIPLE = 3.0


def _iso(value: dt.datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS ppsc_runtime (
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          version TEXT NOT NULL, started_at TEXT NOT NULL,
          paper_only INTEGER NOT NULL, capital_state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ppsc_raw_trades (
          trade_id TEXT PRIMARY KEY, first_seen_cut_id TEXT NOT NULL,
          network TEXT NOT NULL, pool_id TEXT NOT NULL, token_id TEXT NOT NULL,
          wallet TEXT NOT NULL, block_timestamp TEXT NOT NULL, kind TEXT NOT NULL,
          token_amount REAL NOT NULL, usd_value REAL NOT NULL, token_price_usd REAL,
          developer_address TEXT, provenance_state TEXT NOT NULL,
          source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS ppsc_trade_wallet_time
          ON ppsc_raw_trades(wallet, block_timestamp, trade_id);
        CREATE TABLE IF NOT EXISTS ppsc_wallet_identities (
          network TEXT NOT NULL, wallet TEXT NOT NULL, funding_root TEXT,
          provenance_state TEXT NOT NULL, evidence_json TEXT NOT NULL,
          verified_at TEXT, PRIMARY KEY(network, wallet)
        );
        CREATE TABLE IF NOT EXISTS ppsc_wallet_qualifications (
          network TEXT NOT NULL, wallet TEXT NOT NULL,
          qualified_cut_id TEXT NOT NULL, qualified_at TEXT NOT NULL,
          closed_tokens INTEGER NOT NULL, profitable_tokens INTEGER NOT NULL,
          win_rate REAL NOT NULL, realized_pnl_usd REAL NOT NULL,
          profit_factor REAL NOT NULL, top_winner_share REAL NOT NULL,
          state TEXT NOT NULL, capital_state TEXT NOT NULL,
          PRIMARY KEY(network, wallet)
        );
        CREATE TABLE IF NOT EXISTS ppsc_candidate_observations (
          cut_id TEXT NOT NULL, observed_at TEXT NOT NULL,
          network TEXT NOT NULL, pool_id TEXT NOT NULL, token_id TEXT NOT NULL,
          price_usd REAL, first_price_usd REAL, move_multiple REAL,
          route_state TEXT NOT NULL, contract_state TEXT NOT NULL,
          PRIMARY KEY(cut_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS ppsc_consensus_signals (
          cut_id TEXT NOT NULL, observed_at TEXT NOT NULL,
          network TEXT NOT NULL, pool_id TEXT NOT NULL, token_id TEXT NOT NULL,
          qualified_wallets INTEGER NOT NULL, verified_funding_roots INTEGER NOT NULL,
          qualified_buy_usd REAL NOT NULL, top_wallet_share REAL,
          skill_state TEXT NOT NULL, independence_state TEXT NOT NULL,
          route_state TEXT NOT NULL, contract_state TEXT NOT NULL,
          move_multiple REAL, signal_state TEXT NOT NULL,
          capital_state TEXT NOT NULL,
          PRIMARY KEY(cut_id, network, pool_id)
        );
        """
    )


def _token_results(conn: sqlite3.Connection, network: str, wallet: str) -> list[dict[str, float]]:
    rows = conn.execute(
        "SELECT token_id,block_timestamp,trade_id,kind,token_amount,usd_value "
        "FROM ppsc_raw_trades WHERE network=? AND wallet=? AND provenance_state='DEVELOPER_CLEAR' "
        "ORDER BY block_timestamp,trade_id", (network, wallet),
    ).fetchall()
    grouped: dict[str, list[tuple]] = defaultdict(list)
    for row in rows:
        grouped[row[0]].append(row[1:])
    results = []
    for token_id, trades in grouped.items():
        units = cost = bought_units = sold_units = realized = proceeds = 0.0
        for _, _, kind, raw_units, raw_usd in trades:
            amount, usd = max(float(raw_units), 0.0), max(float(raw_usd), 0.0)
            if amount <= 0 or usd <= 0:
                continue
            if kind == "buy":
                units += amount
                bought_units += amount
                cost += usd
            elif kind == "sell" and units > 0:
                matched = min(units, amount)
                fraction = matched / amount
                average_cost = cost / units
                matched_cost = average_cost * matched
                matched_proceeds = usd * fraction
                realized += matched_proceeds - matched_cost
                proceeds += matched_proceeds
                units -= matched
                cost -= matched_cost
                sold_units += matched
        if bought_units > 0 and sold_units / bought_units >= 0.50:
            results.append({"token_id": token_id, "pnl": realized, "proceeds": proceeds})
    return results


def _score_wallet(conn: sqlite3.Connection, network: str, wallet: str) -> dict[str, Any]:
    results = _token_results(conn, network, wallet)
    wins = [r["pnl"] for r in results if r["pnl"] > 0]
    losses = [-r["pnl"] for r in results if r["pnl"] < 0]
    gross_profit, gross_loss = sum(wins), sum(losses)
    realized = gross_profit - gross_loss
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (999.0 if gross_profit > 0 else 0.0)
    top_share = max(wins, default=0.0) / gross_profit if gross_profit > 0 else 1.0
    closed, profitable = len(results), len(wins)
    win_rate = profitable / closed if closed else 0.0
    qualifies = bool(
        closed >= MIN_CLOSED_TOKENS
        and profitable >= MIN_PROFITABLE_TOKENS
        and win_rate >= MIN_WIN_RATE
        and realized > 0
        and profit_factor >= MIN_PROFIT_FACTOR
        and top_share <= MAX_TOP_WINNER_SHARE
    )
    return {
        "closed_tokens": closed, "profitable_tokens": profitable,
        "win_rate": win_rate, "realized_pnl_usd": realized,
        "profit_factor": profit_factor, "top_winner_share": top_share,
        "state": "QUALIFIED" if qualifies else "INSUFFICIENT_PERSISTENCE",
    }


def evaluate_public_skill_consensus(
    conn: sqlite3.Connection,
    cut_id: str,
    observed_at: dt.datetime | str,
    trades: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    """Ingest one cut and return a fail-closed, non-actionable PPSC summary."""
    ensure_schema(conn)
    timestamp = _iso(observed_at)
    conn.execute(
        "INSERT OR IGNORE INTO ppsc_runtime VALUES (1,?,?,?,?)",
        (PPSC_VERSION, timestamp, 1, "CAPITAL_LOCKED"),
    )
    started_at = conn.execute("SELECT started_at FROM ppsc_runtime WHERE singleton=1").fetchone()[0]
    start_dt, observed_dt = _time(started_at), _time(timestamp)

    inserted = 0
    for trade in trades:
        try:
            block_dt = _time(str(trade["block_timestamp"]))
            kind = str(trade["kind"]).lower()
            if block_dt < start_dt or block_dt > observed_dt or kind not in {"buy", "sell"}:
                continue
            wallet = str(trade.get("wallet") or "")
            developer = str(trade.get("developer_address") or "")
            if not wallet:
                continue
            provenance = "DEVELOPER_EXCLUDED" if developer and wallet.casefold() == developer.casefold() else (
                "DEVELOPER_CLEAR" if developer else "DEVELOPER_UNVERIFIED"
            )
            before = conn.total_changes
            conn.execute(
                "INSERT OR IGNORE INTO ppsc_raw_trades VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (str(trade["trade_id"]), cut_id, str(trade["network"]), str(trade["pool_id"]),
                 str(trade["token_id"]), wallet, _iso(block_dt), kind,
                 float(trade["token_amount"]), float(trade["usd_value"]),
                 float(trade["token_price_usd"]) if trade.get("token_price_usd") is not None else None,
                 developer or None, provenance, str(trade.get("source") or "GECKOTERMINAL_PUBLIC")),
            )
            inserted += int(conn.total_changes > before)
        except (KeyError, TypeError, ValueError):
            continue

    # A signal may use only wallets qualified before this cut.
    prior_qualified = {
        (r[0], r[1]): r[2] for r in conn.execute(
            "SELECT network,wallet,qualified_at FROM ppsc_wallet_qualifications WHERE qualified_at < ? AND state='QUALIFIED'",
            (timestamp,),
        )
    }
    candidate_keys = {(c["network"], c["token_id"]): c for c in candidates}
    current_buys: dict[tuple[str, str], dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for network, token_id, wallet, usd in conn.execute(
        "SELECT network,token_id,wallet,usd_value FROM ppsc_raw_trades "
        "WHERE first_seen_cut_id=? AND kind='buy' AND provenance_state='DEVELOPER_CLEAR'", (cut_id,),
    ):
        if (network, wallet) in prior_qualified:
            current_buys[(network, token_id)][wallet] += float(usd)

    signals = []
    for candidate in candidates:
        network, token_id = candidate["network"], candidate["token_id"]
        price = candidate.get("price_usd")
        first = conn.execute(
            "SELECT first_price_usd FROM ppsc_candidate_observations WHERE network=? AND token_id=? "
            "AND first_price_usd IS NOT NULL ORDER BY observed_at LIMIT 1", (network, token_id),
        ).fetchone()
        first_price = float(first[0]) if first else (float(price) if price else None)
        move = float(price) / first_price if price and first_price else None
        route_state = str(candidate.get("route_state") or "NOT_EVALUATED")
        contract_state = str(candidate.get("contract_state") or "UNVERIFIED")
        conn.execute(
            "INSERT OR REPLACE INTO ppsc_candidate_observations VALUES (?,?,?,?,?,?,?,?,?,?)",
            (cut_id, timestamp, network, candidate["pool_id"], token_id, price, first_price, move,
             route_state, contract_state),
        )
        wallets = current_buys.get((network, token_id), {})
        roots = set()
        verified_wallets = set()
        for wallet in wallets:
            identity = conn.execute(
                "SELECT funding_root,provenance_state FROM ppsc_wallet_identities WHERE network=? AND wallet=?",
                (network, wallet),
            ).fetchone()
            if identity and identity[0] and identity[1] == "INDEPENDENT_VERIFIED":
                roots.add(identity[0])
                verified_wallets.add(wallet)
        total = sum(wallets.values())
        top_share = max(wallets.values(), default=0.0) / total if total else None
        skill_state = "PASS" if len(wallets) >= MIN_CONSENSUS_WALLETS else "INSUFFICIENT_QUALIFIED_WALLETS"
        independence = "PASS" if len(roots) >= MIN_INDEPENDENT_ROOTS and len(verified_wallets) >= MIN_CONSENSUS_WALLETS else "FUNDING_ROOTS_UNVERIFIED"
        if skill_state != "PASS":
            state = "NO_CONSENSUS"
        elif independence != "PASS":
            state = "CONSENSUS_INDEPENDENCE_UNVERIFIED"
        elif top_share is None or top_share > MAX_CONSENSUS_WALLET_SHARE:
            state = "CONSENSUS_CONCENTRATED"
        elif move is None or move > MAX_UNCONSUMED_MULTIPLE:
            state = "MOVE_CONSUMED_OR_UNKNOWN"
        elif route_state != "ROUTED_QUOTE_PASS" or contract_state != "PROXY_PASS":
            state = "CONSENSUS_PENDING_EXECUTION"
        else:
            state = "PAPER_PROBE_CANDIDATE"
        row = {
            "network": network, "pool_id": candidate["pool_id"], "token_id": token_id,
            "qualified_wallets": len(wallets), "verified_funding_roots": len(roots),
            "qualified_buy_usd": total, "top_wallet_share": top_share,
            "skill_state": skill_state, "independence_state": independence,
            "route_state": route_state, "contract_state": contract_state,
            "move_multiple": move, "signal_state": state,
        }
        signals.append(row)
        conn.execute(
            "INSERT OR REPLACE INTO ppsc_consensus_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cut_id, timestamp, network, candidate["pool_id"], token_id, len(wallets), len(roots),
             total, top_share, skill_state, independence, route_state, contract_state, move,
             state, "CAPITAL_LOCKED"),
        )

    wallets = conn.execute(
        "SELECT DISTINCT network,wallet FROM ppsc_raw_trades WHERE provenance_state='DEVELOPER_CLEAR'"
    ).fetchall()
    newly_qualified = []
    for network, wallet in wallets:
        if conn.execute(
            "SELECT 1 FROM ppsc_wallet_qualifications WHERE network=? AND wallet=?", (network, wallet)
        ).fetchone():
            continue
        score = _score_wallet(conn, network, wallet)
        if score["state"] == "QUALIFIED":
            conn.execute(
                "INSERT INTO ppsc_wallet_qualifications VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (network, wallet, cut_id, timestamp, score["closed_tokens"], score["profitable_tokens"],
                 score["win_rate"], score["realized_pnl_usd"], score["profit_factor"],
                 score["top_winner_share"], score["state"], "CAPITAL_LOCKED"),
            )
            newly_qualified.append(wallet)

    counts = {
        "raw_trades": conn.execute("SELECT COUNT(*) FROM ppsc_raw_trades").fetchone()[0],
        "qualified_wallets": conn.execute("SELECT COUNT(*) FROM ppsc_wallet_qualifications").fetchone()[0],
        "verified_identities": conn.execute(
            "SELECT COUNT(*) FROM ppsc_wallet_identities WHERE provenance_state='INDEPENDENT_VERIFIED'"
        ).fetchone()[0],
    }
    candidates_out = [s for s in signals if s["signal_state"] == "PAPER_PROBE_CANDIDATE"]
    return {
        "version": PPSC_VERSION, "paper_only": True, "capital_state": "CAPITAL_LOCKED",
        "started_at": started_at, "inserted_trades": inserted, **counts,
        "newly_qualified_wallets": sorted(newly_qualified),
        "signal_states": {state: sum(s["signal_state"] == state for s in signals)
                          for state in sorted({s["signal_state"] for s in signals})},
        "paper_probe_candidates": candidates_out,
    }
