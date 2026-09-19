import sqlite3
import unittest

from creator_economics_audit import audit_creator_economics


class CreatorEconomicsAuditTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.executescript(
            """
            CREATE TABLE pump_launches(
              mint TEXT PRIMARY KEY, creator TEXT, trade_coverage_state TEXT
            );
            CREATE TABLE pump_raw_trades(
              trade_id TEXT PRIMARY KEY, mint TEXT, wallet TEXT, usd_value REAL
            );
            """
        )

    def test_creator_trades_are_excluded_and_incomplete_is_explicit(self):
        self.conn.executemany("INSERT INTO pump_launches VALUES (?,?,?)", [
            ("a", "creator-a", "COMPLETE_INTERVAL"),
            ("b", "creator-a", "PENDING"),
        ])
        self.conn.executemany("INSERT INTO pump_raw_trades VALUES (?,?,?,?)", [
            ("1", "a", "creator-a", 900_000),
            ("2", "a", "external-1", 500_000),
            ("3", "a", "external-2", 1_200_000),
            ("4", "b", "external-3", 100),
        ])
        report = audit_creator_economics(self.conn)
        self.assertEqual(report["evidence_state"], "PARTIAL_TRADE_COVERAGE")
        self.assertEqual(report["external_volume_usd"], 1_700_100)
        self.assertEqual(report["token_5k_hits_at_fee_floor"], 1)
        self.assertEqual(report["token_5k_hits_at_fee_ceiling"], 1)
        self.assertEqual(report["actionable_launches"], [])
        self.assertEqual(report["capital_state"], "CAPITAL_LOCKED")

    def test_fee_ceiling_does_not_become_exact_revenue(self):
        self.conn.execute(
            "INSERT INTO pump_launches VALUES (?,?,?)", ("a", "creator", "COMPLETE_INTERVAL")
        )
        self.conn.execute(
            "INSERT INTO pump_raw_trades VALUES (?,?,?,?)", ("1", "a", "external", 600_000)
        )
        report = audit_creator_economics(self.conn)
        self.assertEqual(report["evidence_state"], "COMPLETE_COHORT")
        self.assertEqual(report["token_5k_hits_at_fee_floor"], 0)
        self.assertEqual(report["token_5k_hits_at_fee_ceiling"], 1)
        self.assertEqual(report["economic_admission_state"], "MEASURED_ONLY")

    def test_missing_tables_fail_closed(self):
        report = audit_creator_economics(sqlite3.connect(":memory:"))
        self.assertEqual(report["evidence_state"], "SOURCE_TABLES_MISSING")
        self.assertEqual(report["actionable_launches"], [])


if __name__ == "__main__":
    unittest.main()
