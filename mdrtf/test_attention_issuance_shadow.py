import datetime as dt
import sqlite3
import unittest

from attention_issuance_shadow import evaluate_attention_issuance_shadow
from pump_future_census import ingest_launch_snapshot


UTC = dt.timezone.utc


def event(title="new internet creature", geos=("US", "TR")):
    published = dt.datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
    return [
        {"title": title, "geo": geo, "published": published,
         "support": [{"source": f"publisher-{geo}"}]}
        for geo in geos
    ]


def launch(name, symbol, mint, created):
    return {
        "mint": mint, "creator": "creator", "created_timestamp": int(created.timestamp() * 1000),
        "program": "pump", "name": name, "symbol": symbol,
        "bonding_curve": "curve", "pool_address": "pool-" + mint, "complete": False,
    }


class AttentionIssuanceShadowTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.t0 = dt.datetime(2026, 9, 19, 12, 0, tzinfo=UTC)
        self.conn.executescript(
            """
            CREATE TABLE cuts(cut_id TEXT PRIMARY KEY,created_at TEXT,mode TEXT,capital_state TEXT,source_health_json TEXT);
            CREATE TABLE attention_events(cut_id TEXT,geo TEXT,rank INTEGER,title TEXT,normalized_title TEXT,published_at TEXT);
            """
        )
        ingest_launch_snapshot(
            self.conn, "baseline", self.t0 - dt.timedelta(seconds=90), ok=True, http_code=200,
            body=("[{\"mint\":\"base\",\"creator\":\"c\",\"created_timestamp\":"
                  + str(int((self.t0 - dt.timedelta(seconds=89)).timestamp() * 1000))
                  + ",\"program\":\"pump\",\"name\":\"baseline\",\"symbol\":\"BASE\"}]").encode(),
        )

    def complete_pump_cut(self, cut, when, launches=None):
        launches = launches or []
        overlap = launch("overlap", "OVER", "overlap-" + cut, when - dt.timedelta(seconds=90))
        return ingest_launch_snapshot(
            self.conn, cut, when, ok=True, http_code=200,
            body=__import__("json").dumps(launches + [overlap]).encode(),
        )

    def evaluate(self, cut, when, rows):
        self.conn.execute(
            "INSERT INTO cuts VALUES (?,?,?,?,?)", (cut, when.isoformat(), "FUTURE_ONLY", "CAPITAL_LOCKED", "{}")
        )
        for rank, row in enumerate(rows, 1):
            self.conn.execute(
                "INSERT INTO attention_events VALUES (?,?,?,?,?,?)",
                (cut, row["geo"], rank, row["title"], row["title"], row["published"].isoformat()),
            )
        return evaluate_attention_issuance_shadow(self.conn, cut, when, rows)

    def test_two_complete_future_cuts_create_due_diligence_candidate(self):
        self.complete_pump_cut("c1", self.t0)
        first = self.evaluate("c1", self.t0, event())
        self.assertEqual(first["state_counts"], {"PERSISTENCE_PENDING": 1})
        t1 = self.t0 + dt.timedelta(seconds=90)
        self.complete_pump_cut("c2", t1)
        second = self.evaluate("c2", t1, event())
        self.assertEqual(second["state_counts"], {"LAUNCH_DUE_DILIGENCE_CANDIDATE": 1})
        candidate = second["due_diligence_candidates"][0]
        self.assertEqual(candidate["canonicality_state"], "FUTURE_PUMP_WHITESPACE_ONLY")
        self.assertEqual(candidate["rights_state"], "UNVERIFIED")
        self.assertEqual(candidate["capital_state"], "CAPITAL_LOCKED")
        self.assertEqual(second["actionable_launches"], [])

    def test_semantic_launch_vetoes_candidate(self):
        self.complete_pump_cut("c1", self.t0)
        self.evaluate("c1", self.t0, event())
        t1 = self.t0 + dt.timedelta(seconds=90)
        linked = launch("New Internet Creature", "NIC", "linked", t1)
        self.complete_pump_cut("c2", t1, [linked])
        second = self.evaluate("c2", t1, event())
        self.assertEqual(second["state_counts"], {"TOKENIZATION_PRESENT": 1})

    def test_known_pre_attention_launch_also_vetoes_candidate(self):
        linked = launch(
            "New Internet Creature", "NIC", "early-linked",
            self.t0 - dt.timedelta(seconds=30),
        )
        self.complete_pump_cut("c1", self.t0, [linked])
        self.evaluate("c1", self.t0, event())
        t1 = self.t0 + dt.timedelta(seconds=90)
        self.complete_pump_cut("c2", t1)
        second = self.evaluate("c2", t1, event())
        self.assertEqual(second["state_counts"], {"TOKENIZATION_PRESENT": 1})

    def test_pump_gap_is_not_negative_evidence(self):
        self.complete_pump_cut("c1", self.t0)
        self.evaluate("c1", self.t0, event())
        t1 = self.t0 + dt.timedelta(seconds=90)
        ingest_launch_snapshot(
            self.conn, "c2", t1, ok=True, http_code=200,
            body=__import__("json").dumps([
                launch("late", "LATE", "late", t1 + dt.timedelta(seconds=1))
            ]).encode(),
        )
        second = self.evaluate("c2", t1, event())
        self.assertEqual(second["state_counts"], {"PUMP_COVERAGE_INSUFFICIENT": 1})

    def test_preexisting_attention_is_veto_only(self):
        old = self.t0 - dt.timedelta(days=2)
        self.conn.execute("INSERT INTO cuts VALUES (?,?,?,?,?)", ("old", old.isoformat(), "FUTURE_ONLY", "CAPITAL_LOCKED", "{}"))
        self.conn.execute(
            "INSERT INTO attention_events VALUES (?,?,?,?,?,?)",
            ("old", "US", 1, "new internet creature", "new internet creature", old.isoformat()),
        )
        self.complete_pump_cut("c1", self.t0)
        first = self.evaluate("c1", self.t0, event())
        t1 = self.t0 + dt.timedelta(seconds=90)
        self.complete_pump_cut("c2", t1)
        second = self.evaluate("c2", t1, event())
        self.assertEqual(first["state_counts"], {"PERSISTENCE_PENDING": 1})
        self.assertEqual(second["state_counts"], {"NOVELTY_VETO": 1})


if __name__ == "__main__":
    unittest.main()
