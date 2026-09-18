import datetime as dt
import json
import sqlite3
import unittest

from pump_future_census import (
    ingest_launch_snapshot,
    ingest_trade_refresh,
    trade_targets,
)


UTC = dt.timezone.utc


def launch(mint, creator, created_ms):
    return {
        "mint": mint, "creator": creator, "created_timestamp": created_ms,
        "program": "pump", "name": mint, "symbol": mint[:3],
        "bonding_curve": "curve-" + mint, "pool_address": "pool-" + mint,
        "complete": False,
    }


def trade(index, timestamp, *, wallet="wallet", kind="buy"):
    return {
        "slotIndexId": f"slot-{index}", "tx": f"sig-{index}",
        "timestamp": timestamp, "userAddress": wallet, "type": kind,
        "baseAmount": "10", "amountUsd": "5", "fillPriceUsd": "0.5",
    }


class PumpFutureCensusTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.t0 = dt.datetime(2026, 9, 18, 12, 0, 0, tzinfo=UTC)

    def snapshot(self, cut, when, rows):
        return ingest_launch_snapshot(
            self.conn, cut, when, ok=True, http_code=200,
            body=json.dumps(rows).encode(),
        )

    def test_baseline_is_future_only_and_not_a_pass(self):
        result = self.snapshot("c0", self.t0, [
            launch("old", "dev-old", int((self.t0 - dt.timedelta(seconds=1)).timestamp() * 1000)),
            launch("new", "dev-new", int((self.t0 + dt.timedelta(seconds=1)).timestamp() * 1000)),
        ])
        self.assertEqual(result["coverage_state"], "BASELINE_ONLY")
        self.assertEqual(result["inserted_launches"], 1)
        self.assertEqual(self.conn.execute("select mint from pump_launches").fetchone()[0], "new")

    def test_overlap_is_required_and_gap_does_not_advance_boundary(self):
        first = self.snapshot("c0", self.t0, [
            launch("a", "dev", int((self.t0 + dt.timedelta(seconds=1)).timestamp() * 1000)),
        ])
        self.assertEqual(first["coverage_state"], "BASELINE_ONLY")
        t1 = self.t0 + dt.timedelta(seconds=90)
        complete = self.snapshot("c1", t1, [
            launch("b", "dev", int((t1 + dt.timedelta(seconds=1)).timestamp() * 1000)),
            launch("a", "dev", int((self.t0 - dt.timedelta(seconds=1)).timestamp() * 1000)),
        ])
        self.assertEqual(complete["coverage_state"], "COMPLETE_INTERVAL")
        t2 = t1 + dt.timedelta(seconds=90)
        gap = self.snapshot("c2", t2, [
            launch("c", "dev", int((t2 + dt.timedelta(seconds=1)).timestamp() * 1000)),
            launch("late", "dev", int((t1 + dt.timedelta(seconds=1)).timestamp() * 1000)),
        ])
        self.assertEqual(gap["coverage_state"], "GAP")
        boundary = self.conn.execute(
            "select last_complete_cut_id from pump_census_runtime where singleton=1"
        ).fetchone()[0]
        self.assertEqual(boundary, "c1")

    def test_trade_refresh_deduplicates_and_excludes_pre_start(self):
        self.snapshot("c0", self.t0, [
            launch("mint", "creator", int((self.t0 + dt.timedelta(seconds=1)).timestamp() * 1000)),
        ])
        target = trade_targets(self.conn, self.t0 + dt.timedelta(seconds=5), 1)[0]
        old = trade(0, (self.t0 - dt.timedelta(seconds=1)).isoformat())
        buy = trade(1, (self.t0 + dt.timedelta(seconds=2)).isoformat())
        sell = trade(2, (self.t0 + dt.timedelta(seconds=3)).isoformat(), kind="sell")
        summary, ppsc = ingest_trade_refresh(
            self.conn, "c0", self.t0 + dt.timedelta(seconds=5), target,
            [[buy, old, sell]], reached_end=True,
        )
        self.assertEqual(summary["coverage_state"], "COMPLETE_INTERVAL")
        self.assertEqual(summary["inserted_trades"], 2)
        self.assertEqual(len(ppsc), 2)
        target = trade_targets(self.conn, self.t0 + dt.timedelta(seconds=10), 1)[0]
        repeated, ppsc = ingest_trade_refresh(
            self.conn, "c1", self.t0 + dt.timedelta(seconds=10), target,
            [[trade(3, (self.t0 + dt.timedelta(seconds=8)).isoformat()), buy]],
            reached_end=False,
        )
        self.assertEqual(repeated["coverage_state"], "COMPLETE_INTERVAL")
        self.assertEqual(repeated["inserted_trades"], 1)
        self.assertEqual(len(ppsc), 1)

    def test_trade_gap_is_explicit(self):
        self.snapshot("c0", self.t0, [
            launch("mint", "creator", int(self.t0.timestamp() * 1000)),
        ])
        target = trade_targets(self.conn, self.t0 + dt.timedelta(seconds=1), 1)[0]
        ingest_trade_refresh(
            self.conn, "c0", self.t0 + dt.timedelta(seconds=2), target,
            [[trade(1, (self.t0 + dt.timedelta(seconds=1)).isoformat())]], reached_end=True,
        )
        target = trade_targets(self.conn, self.t0 + dt.timedelta(seconds=5), 1)[0]
        summary, _ = ingest_trade_refresh(
            self.conn, "c1", self.t0 + dt.timedelta(seconds=5), target,
            [[trade(99, (self.t0 + dt.timedelta(seconds=4)).isoformat())]], reached_end=False,
        )
        self.assertEqual(summary["coverage_state"], "PREVIOUS_HEAD_NOT_REACHED")


if __name__ == "__main__":
    unittest.main()
