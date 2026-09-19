"""Outcome-blind economics audit for the future-only Pump launch census.

The audit measures observed external volume and fee bounds.  It deliberately
does not predict profit, select a launch, or unlock capital.  Incomplete trade
coverage remains explicit and can never become a negative example.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


VERSION = "CREATOR_ECONOMICS_AUDIT_V1_20260919"
CAPITAL_STATE = "CAPITAL_LOCKED"
CREATOR_FEE_FLOOR = 0.003
CREATOR_FEE_CEILING = 0.0095
PER_LAUNCH_TARGET_USD = 5_000.0
PORTFOLIO_TARGET_USD = 100_000.0


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * fraction))]


def audit_creator_economics(conn: sqlite3.Connection) -> dict[str, Any]:
    tables = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    required = {"pump_launches", "pump_raw_trades"}
    if not required.issubset(tables):
        return {
            "version": VERSION,
            "evidence_state": "SOURCE_TABLES_MISSING",
            "capital_state": CAPITAL_STATE,
            "actionable_launches": [],
        }

    rows = conn.execute(
        """
        SELECT l.mint,l.creator,l.trade_coverage_state,
               COUNT(t.trade_id),
               COUNT(DISTINCT CASE WHEN t.wallet<>l.creator THEN t.wallet END),
               COALESCE(SUM(CASE WHEN t.wallet<>l.creator THEN t.usd_value ELSE 0 END),0),
               COALESCE(SUM(CASE WHEN t.wallet=l.creator THEN t.usd_value ELSE 0 END),0)
        FROM pump_launches l
        LEFT JOIN pump_raw_trades t ON t.mint=l.mint
        GROUP BY l.mint,l.creator,l.trade_coverage_state
        """
    ).fetchall()

    states: dict[str, int] = {}
    creator_totals: dict[str, dict[str, float | int]] = {}
    external_volumes: list[float] = []
    complete_volumes: list[float] = []
    token_floor_hits = 0
    token_ceiling_hits = 0

    for mint, creator, coverage, trades, wallets, external, creator_volume in rows:
        del mint, trades, wallets, creator_volume
        external = float(external)
        external_volumes.append(external)
        states[coverage] = states.get(coverage, 0) + 1
        if coverage == "COMPLETE_INTERVAL":
            complete_volumes.append(external)
        token_floor_hits += external * CREATOR_FEE_FLOOR >= PER_LAUNCH_TARGET_USD
        token_ceiling_hits += external * CREATOR_FEE_CEILING >= PER_LAUNCH_TARGET_USD
        item = creator_totals.setdefault(creator, {"launches": 0, "external_volume": 0.0})
        item["launches"] = int(item["launches"]) + 1
        item["external_volume"] = float(item["external_volume"]) + external

    ordered = sorted(external_volumes, reverse=True)
    total_external = sum(external_volumes)
    top_one_count = max(1, len(ordered) // 100) if ordered else 0
    top_ten_count = max(1, len(ordered) // 10) if ordered else 0
    creator_floor_hits = sum(
        float(item["external_volume"]) * CREATOR_FEE_FLOOR >= PER_LAUNCH_TARGET_USD
        for item in creator_totals.values()
    )
    repeat_floor_hits = sum(
        int(item["launches"]) >= 2
        and float(item["external_volume"]) * CREATOR_FEE_FLOOR
            >= 2 * PER_LAUNCH_TARGET_USD
        for item in creator_totals.values()
    )
    max_creator = max(
        (float(item["external_volume"]) for item in creator_totals.values()),
        default=0.0,
    )
    complete_count = states.get("COMPLETE_INTERVAL", 0)
    evidence_state = (
        "COMPLETE_COHORT" if rows and complete_count == len(rows)
        else "PARTIAL_TRADE_COVERAGE"
    )

    return {
        "version": VERSION,
        "evidence_state": evidence_state,
        "capital_state": CAPITAL_STATE,
        "launches_observed": len(rows),
        "creators_observed": len(creator_totals),
        "coverage_states": states,
        "external_volume_usd": round(total_external, 2),
        "complete_launches": complete_count,
        "complete_zero_external_volume_share": round(
            sum(value == 0 for value in complete_volumes) / len(complete_volumes), 6
        ) if complete_volumes else None,
        "complete_below_1k_external_volume_share": round(
            sum(value < 1_000 for value in complete_volumes) / len(complete_volumes), 6
        ) if complete_volumes else None,
        "complete_external_volume_p50": round(_percentile(complete_volumes, 0.50), 2),
        "complete_external_volume_p90": round(_percentile(complete_volumes, 0.90), 2),
        "complete_external_volume_p99": round(_percentile(complete_volumes, 0.99), 2),
        "max_token_external_volume_usd": round(max(external_volumes, default=0.0), 2),
        "token_5k_hits_at_fee_floor": token_floor_hits,
        "token_5k_hits_at_fee_ceiling": token_ceiling_hits,
        "creator_aggregate_5k_hits_at_fee_floor": creator_floor_hits,
        "creator_repeat_5k_equivalent_hits_at_fee_floor": repeat_floor_hits,
        "max_creator_observed_fee_floor_usd": round(max_creator * CREATOR_FEE_FLOOR, 2),
        "max_creator_observed_fee_ceiling_usd": round(max_creator * CREATOR_FEE_CEILING, 2),
        "portfolio_observed_fee_floor_usd": round(total_external * CREATOR_FEE_FLOOR, 2),
        "portfolio_observed_fee_ceiling_usd": round(total_external * CREATOR_FEE_CEILING, 2),
        "top_1pct_external_volume_share": round(
            sum(ordered[:top_one_count]) / total_external, 6
        ) if total_external else None,
        "top_10pct_external_volume_share": round(
            sum(ordered[:top_ten_count]) / total_external, 6
        ) if total_external else None,
        "per_launch_target_usd": PER_LAUNCH_TARGET_USD,
        "portfolio_target_usd": PORTFOLIO_TARGET_USD,
        "economic_admission_state": "NOT_EVALUABLE" if evidence_state != "COMPLETE_COHORT" else "MEASURED_ONLY",
        "actionable_launches": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    conn = sqlite3.connect(args.db)
    try:
        report = audit_creator_economics(conn)
    finally:
        conn.close()
    Path(args.out).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
