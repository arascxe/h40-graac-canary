"""Outcome-blind Family Optionality Shadow policy for MDRTF.

The lane records a small equal-weight paper basket at the first fully executable
family checkpoint, then rotates the paper value into a leader only after two
consecutive, independently recorded capital-routing checkpoints.  It never
signs a transaction and cannot alter the canonical AFT decision.
"""

from __future__ import annotations

import datetime as dt
import json
import sqlite3
from typing import Any


FOS_VERSION = "FOS_V1_20260916"
FAMILY_PAPER_BUDGET_USD = 50.0
MAX_BASKET_MEMBERS = 3
MAX_BUYER_SHARE = 0.35
MIN_SHARE_GAIN = 0.05


def _iso(value: dt.datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS fos_baskets (
          family_id TEXT PRIMARY KEY,
          version TEXT NOT NULL,
          opened_cut_id TEXT NOT NULL,
          opened_at TEXT NOT NULL,
          total_notional_usd REAL NOT NULL,
          eligible_member_count INTEGER NOT NULL,
          selected_member_count INTEGER NOT NULL,
          selection_rule TEXT NOT NULL,
          state TEXT NOT NULL,
          rotated_pool_id TEXT,
          rotated_at TEXT,
          capital_state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fos_positions (
          family_id TEXT NOT NULL,
          network TEXT NOT NULL,
          pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL,
          opened_cut_id TEXT NOT NULL,
          opened_at TEXT NOT NULL,
          entry_rank INTEGER NOT NULL,
          entry_score REAL NOT NULL,
          entry_price_usd REAL NOT NULL,
          paper_notional_usd REAL NOT NULL,
          entry_roundtrip_cost_pct REAL NOT NULL,
          virtual_units REAL NOT NULL,
          state TEXT NOT NULL,
          PRIMARY KEY (family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS fos_checkpoints (
          cut_id TEXT NOT NULL,
          family_id TEXT NOT NULL,
          network TEXT NOT NULL,
          pool_id TEXT NOT NULL,
          token_id TEXT NOT NULL,
          observed_at TEXT NOT NULL,
          leader_rank INTEGER NOT NULL,
          leader_score REAL NOT NULL,
          price_usd REAL,
          route_state TEXT NOT NULL,
          contract_state TEXT NOT NULL,
          distinct_buyers INTEGER NOT NULL,
          external_buy_usd REAL NOT NULL,
          external_sell_usd REAL NOT NULL,
          max_buyer_share REAL,
          address_diversity_state TEXT NOT NULL,
          family_buy_share REAL NOT NULL,
          family_buyer_share REAL NOT NULL,
          paper_liquidation_usd REAL,
          PRIMARY KEY (cut_id, family_id, network, pool_id)
        );
        CREATE TABLE IF NOT EXISTS fos_rotations (
          family_id TEXT PRIMARY KEY,
          trigger_cut_id TEXT NOT NULL,
          triggered_at TEXT NOT NULL,
          leader_network TEXT NOT NULL,
          leader_pool_id TEXT NOT NULL,
          leader_token_id TEXT NOT NULL,
          previous_cut_id TEXT NOT NULL,
          buy_share_gain REAL NOT NULL,
          buyer_share_gain REAL NOT NULL,
          sibling_share_loss INTEGER NOT NULL,
          pre_rotation_value_usd REAL NOT NULL,
          rotation_cost_pct REAL NOT NULL,
          leader_price_usd REAL NOT NULL,
          leader_virtual_units REAL NOT NULL,
          trigger_json TEXT NOT NULL,
          capital_state TEXT NOT NULL
        );
        """
    )


def _route_cost(observation: dict[str, Any]) -> float | None:
    route = observation.get("route") or {}
    value = route.get("worst_case_cost_pct")
    if value is None:
        value = route.get("quoted_roundtrip_cost_pct")
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if 0 <= value <= 3.0 else None


def _eligible(observation: dict[str, Any]) -> bool:
    return bool(
        observation.get("price")
        and float(observation["price"]) > 0
        and observation.get("execution") == "ROUTE_PASS"
        and observation.get("contract") == "PROXY_PASS"
        and _route_cost(observation) is not None
    )


def _family_shares(rows: list[dict[str, Any]]) -> dict[tuple[str, str], tuple[float, float]]:
    total_buy = sum(max(float((o.get("flow") or {}).get("external_buy_usd") or 0.0), 0.0) for o in rows)
    total_buyers = sum(max(int((o.get("flow") or {}).get("distinct_buyers") or 0), 0) for o in rows)
    result = {}
    for o in rows:
        flow = o.get("flow") or {}
        buy = max(float(flow.get("external_buy_usd") or 0.0), 0.0)
        buyers = max(int(flow.get("distinct_buyers") or 0), 0)
        result[(o["network"], o["pool_id"])] = (
            buy / total_buy if total_buy > 0 else 0.0,
            buyers / total_buyers if total_buyers > 0 else 0.0,
        )
    return result


def _paper_value(observation: dict[str, Any], position: sqlite3.Row | tuple) -> float | None:
    price = observation.get("price")
    cost = _route_cost(observation)
    if not price or cost is None:
        return None
    units = float(position["virtual_units"] if isinstance(position, sqlite3.Row) else position[0])
    return units * float(price) * (1.0 - cost / 100.0)


def update_family_optionality_shadow(
    conn: sqlite3.Connection,
    cut_id: str,
    observed_at: dt.datetime | str,
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Persist one FOS checkpoint and return a non-actionable summary."""
    ensure_schema(conn)
    timestamp = _iso(observed_at)
    families = sorted({o["family_id"] for o in observations})
    opened, rotated = [], []

    for family_id in families:
        rows = [o for o in observations if o["family_id"] == family_id]
        shares = _family_shares(rows)
        basket = conn.execute(
            "SELECT state,rotated_pool_id FROM fos_baskets WHERE family_id=?", (family_id,)
        ).fetchone()

        if basket is None:
            eligible = sorted(
                (o for o in rows if _eligible(o)),
                key=lambda o: (-float(o.get("score") or 0.0), o["network"], o["pool_id"]),
            )
            if len(eligible) >= 2:
                selected = eligible[:MAX_BASKET_MEMBERS]
                per_member = FAMILY_PAPER_BUDGET_USD / len(selected)
                conn.execute(
                    "INSERT INTO fos_baskets VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (family_id, FOS_VERSION, cut_id, timestamp, FAMILY_PAPER_BUDGET_USD,
                     len(eligible), len(selected), "TOP3_CONTEMPORANEOUS_SCORE_EQUAL_WEIGHT",
                     "OPEN_BASKET", None, None, "CAPITAL_LOCKED"),
                )
                for o in selected:
                    cost = float(_route_cost(o))
                    entry_value = per_member * (1.0 - cost / 100.0)
                    units = entry_value / float(o["price"])
                    conn.execute(
                        "INSERT INTO fos_positions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (family_id, o["network"], o["pool_id"], o["token_id"], cut_id, timestamp,
                         int(o["rank"]), float(o["score"]), float(o["price"]), per_member,
                         cost, units, "OPEN_BASKET"),
                    )
                opened.append(family_id)
                basket = ("OPEN_BASKET", None)

        if basket is None:
            continue

        positions = conn.execute(
            "SELECT network,pool_id,virtual_units,state FROM fos_positions WHERE family_id=?",
            (family_id,),
        ).fetchall()
        position_map = {(p[0], p[1]): p for p in positions}
        checkpoint_rows = []
        for o in rows:
            flow = o.get("flow") or {}
            buy_share, buyer_share = shares[(o["network"], o["pool_id"])]
            position = position_map.get((o["network"], o["pool_id"]))
            liquidation = _paper_value(o, (position[2],)) if position and position[3] in {
                "OPEN_BASKET", "ROTATED_LEADER"
            } else None
            checkpoint_rows.append((
                cut_id, family_id, o["network"], o["pool_id"], o["token_id"], timestamp,
                int(o["rank"]), float(o["score"]), o.get("price"), o.get("execution", "UNKNOWN"),
                o.get("contract", "UNKNOWN"), int(flow.get("distinct_buyers") or 0),
                float(flow.get("external_buy_usd") or 0.0), float(flow.get("external_sell_usd") or 0.0),
                flow.get("max_buyer_share"), flow.get("address_diversity_state", "UNAVAILABLE"),
                buy_share, buyer_share, liquidation,
            ))
        conn.executemany("INSERT OR REPLACE INTO fos_checkpoints VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", checkpoint_rows)

        state = basket[0]
        if state != "OPEN_BASKET":
            continue
        leader = next((o for o in rows if int(o.get("rank") or 0) == 1 and _eligible(o)), None)
        if not leader:
            continue
        flow = leader.get("flow") or {}
        if (flow.get("address_diversity_state") != "ADDRESS_DIVERSE"
                or int(flow.get("distinct_buyers") or 0) < 2
                or float(flow.get("external_buy_usd") or 0.0) <= float(flow.get("external_sell_usd") or 0.0)
                or flow.get("max_buyer_share") is None
                or float(flow["max_buyer_share"]) > MAX_BUYER_SHARE):
            continue

        previous_cut = conn.execute(
            "SELECT cut_id FROM fos_checkpoints WHERE family_id=? AND cut_id<>? "
            "ORDER BY observed_at DESC LIMIT 1", (family_id, cut_id),
        ).fetchone()
        previous = conn.execute(
            "SELECT cut_id,distinct_buyers,family_buy_share,family_buyer_share FROM fos_checkpoints "
            "WHERE family_id=? AND network=? AND pool_id=? AND cut_id=? AND leader_rank=1",
            (family_id, leader["network"], leader["pool_id"], previous_cut[0] if previous_cut else ""),
        ).fetchone()
        if not previous:
            continue
        current_buy_share, current_buyer_share = shares[(leader["network"], leader["pool_id"])]
        buy_gain = current_buy_share - float(previous[2])
        buyer_gain = current_buyer_share - float(previous[3])
        if int(flow.get("distinct_buyers") or 0) <= int(previous[1]):
            continue
        if buy_gain < MIN_SHARE_GAIN or buyer_gain < 0:
            continue
        sibling_loss = conn.execute(
            "SELECT COUNT(*) FROM fos_checkpoints cur JOIN fos_checkpoints prev "
            "ON prev.family_id=cur.family_id AND prev.network=cur.network AND prev.pool_id=cur.pool_id "
            "WHERE cur.cut_id=? AND prev.cut_id=? AND cur.family_id=? AND cur.pool_id<>? "
            "AND cur.family_buy_share < prev.family_buy_share",
            (cut_id, previous[0], family_id, leader["pool_id"]),
        ).fetchone()[0]
        if sibling_loss < 1:
            continue

        values = [r[18] for r in checkpoint_rows if r[18] is not None]
        if len(values) != len(positions):
            continue
        pre_rotation = sum(values)
        rotation_cost = float(_route_cost(leader))
        post_cost_value = pre_rotation * (1.0 - rotation_cost / 100.0)
        leader_units = post_cost_value / float(leader["price"])
        trigger = {
            "same_rank1_consecutive": True,
            "distinct_buyers_increased": True,
            "address_diverse": True,
            "net_external_buy_positive": True,
            "max_buyer_share_lte": MAX_BUYER_SHARE,
            "buy_share_gain_gte": MIN_SHARE_GAIN,
            "sibling_share_loss": sibling_loss,
        }
        conn.execute(
            "INSERT INTO fos_rotations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (family_id, cut_id, timestamp, leader["network"], leader["pool_id"], leader["token_id"],
             previous[0], buy_gain, buyer_gain, sibling_loss, pre_rotation, rotation_cost,
             float(leader["price"]), leader_units, json.dumps(trigger, sort_keys=True), "CAPITAL_LOCKED"),
        )
        conn.execute(
            "UPDATE fos_positions SET state=CASE WHEN pool_id=? THEN 'ROTATED_LEADER' ELSE 'ROTATED_OUT' END "
            "WHERE family_id=?", (leader["pool_id"], family_id),
        )
        conn.execute(
            "UPDATE fos_positions SET virtual_units=? WHERE family_id=? AND pool_id=?",
            (leader_units, family_id, leader["pool_id"]),
        )
        conn.execute(
            "UPDATE fos_baskets SET state='ROTATED_TO_LEADER',rotated_pool_id=?,rotated_at=? WHERE family_id=?",
            (leader["pool_id"], timestamp, family_id),
        )
        rotated.append(family_id)

    counts = dict(conn.execute(
        "SELECT state,COUNT(*) FROM fos_baskets GROUP BY state"
    ).fetchall())
    return {
        "version": FOS_VERSION,
        "capital_state": "CAPITAL_LOCKED",
        "paper_only": True,
        "opened_family_ids": opened,
        "rotated_family_ids": rotated,
        "basket_states": counts,
    }
