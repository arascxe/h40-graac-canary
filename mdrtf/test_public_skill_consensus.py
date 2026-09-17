import datetime as dt
import sqlite3
import unittest
from unittest.mock import patch

from mdrtf_collector import discover_solana_funding_root
from public_skill_consensus import ensure_schema, evaluate_public_skill_consensus


NOW = dt.datetime(2026, 9, 17, 15, 0, tzinfo=dt.timezone.utc)


def trade(tid, wallet, token, kind, units, usd, minute, developer="dev"):
    return {
        "trade_id": tid, "network": "solana", "pool_id": "pool-" + token,
        "token_id": token, "wallet": wallet,
        "block_timestamp": (NOW + dt.timedelta(minutes=minute)).isoformat(),
        "kind": kind, "token_amount": units, "usd_value": usd,
        "token_price_usd": usd / units, "developer_address": developer,
    }


def candidate(token="target", route="NOT_EVALUATED", contract="PROXY_PASS", price=1.0):
    return {"network": "solana", "pool_id": "pool-" + token, "token_id": token,
            "price_usd": price, "route_state": route, "contract_state": contract}


class PublicSkillConsensusTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        evaluate_public_skill_consensus(self.conn, "start", NOW, [], [])

    def histories(self, wallet, offset=1):
        rows = []
        outcomes = [(100, 180), (100, 150), (100, 50)]
        for index, (buy, sell) in enumerate(outcomes):
            token = f"{wallet}-t{index}"
            rows += [
                trade(f"{wallet}-{index}-b", wallet, token, "buy", 100, buy, offset + index * 2),
                trade(f"{wallet}-{index}-s", wallet, token, "sell", 100, sell, offset + index * 2 + 1),
            ]
        return rows

    def test_rejects_prestart_deduplicates_and_excludes_developer(self):
        old = trade("old", "w", "t", "buy", 10, 10, -1)
        valid = trade("new", "w", "t", "buy", 10, 10, 1)
        dev = trade("devtrade", "dev", "t", "buy", 10, 10, 1)
        result = evaluate_public_skill_consensus(
            self.conn, "c1", NOW + dt.timedelta(minutes=2), [old, valid, valid, dev], [candidate("t")]
        )
        self.assertEqual(result["inserted_trades"], 2)
        states = dict(self.conn.execute("select trade_id,provenance_state from ppsc_raw_trades"))
        self.assertEqual(states, {"new": "DEVELOPER_CLEAR", "devtrade": "DEVELOPER_EXCLUDED"})

    def test_qualifies_only_realized_repeat_skill(self):
        result = evaluate_public_skill_consensus(
            self.conn, "c1", NOW + dt.timedelta(minutes=10), self.histories("w"), []
        )
        self.assertEqual(result["newly_qualified_wallets"], ["w"])
        row = self.conn.execute(
            "select closed_tokens,profitable_tokens,realized_pnl_usd,state,capital_state "
            "from ppsc_wallet_qualifications"
        ).fetchone()
        self.assertEqual(row[:2], (3, 2))
        self.assertAlmostEqual(row[2], 80.0)
        self.assertEqual(row[3:], ("QUALIFIED", "CAPITAL_LOCKED"))

    def test_consensus_requires_prior_skill_verified_roots_and_execution(self):
        histories = sum((self.histories(w) for w in ("w1", "w2", "w3")), [])
        evaluate_public_skill_consensus(
            self.conn, "qualify", NOW + dt.timedelta(minutes=10), histories, []
        )
        ensure_schema(self.conn)
        for i, wallet in enumerate(("w1", "w2", "w3"), 1):
            self.conn.execute(
                "insert into ppsc_wallet_identities values (?,?,?,?,?,?)",
                ("solana", wallet, f"root-{i}", "INDEPENDENT_VERIFIED", "{}",
                 (NOW + dt.timedelta(minutes=11)).isoformat()),
            )
        buys = [trade(f"sig-{w}", w, "target", "buy", 10, 10, 12) for w in ("w1", "w2", "w3")]
        pending = evaluate_public_skill_consensus(
            self.conn, "signal", NOW + dt.timedelta(minutes=13), buys, [candidate()]
        )
        self.assertEqual(pending["signal_states"], {"CONSENSUS_PENDING_EXECUTION": 1})
        passed = evaluate_public_skill_consensus(
            self.conn, "route", NOW + dt.timedelta(minutes=14), [],
            [candidate(route="ROUTED_QUOTE_PASS")],
        )
        # A route-only later cut cannot manufacture fresh consensus.
        self.assertEqual(passed["paper_probe_candidates"], [])

    def test_unverified_funding_roots_never_pass(self):
        histories = sum((self.histories(w) for w in ("a", "b", "c")), [])
        evaluate_public_skill_consensus(self.conn, "q", NOW + dt.timedelta(minutes=10), histories, [])
        buys = [trade(f"x-{w}", w, "target", "buy", 10, 10, 12) for w in ("a", "b", "c")]
        result = evaluate_public_skill_consensus(
            self.conn, "s", NOW + dt.timedelta(minutes=13), buys,
            [candidate(route="ROUTED_QUOTE_PASS")],
        )
        self.assertEqual(result["signal_states"], {"CONSENSUS_INDEPENDENCE_UNVERIFIED": 1})
        self.assertEqual(result["paper_probe_candidates"], [])

    @patch("mdrtf_collector.solana_rpc")
    def test_funding_root_requires_complete_history_and_decoded_funder(self, rpc):
        rpc.side_effect = [
            [{"signature": "oldest"}],
            {
                "transaction": {"message": {"accountKeys": [
                    {"pubkey": "wallet", "signer": False},
                    {"pubkey": "root", "signer": True},
                ]}},
                "meta": {"preBalances": [0, 1000], "postBalances": [500, 400]},
            },
        ]
        result = discover_solana_funding_root("wallet")
        self.assertEqual(result["state"], "INDEPENDENT_VERIFIED")
        self.assertEqual(result["funding_root"], "root")

    @patch("mdrtf_collector.solana_rpc")
    def test_funding_root_fails_closed_when_history_is_truncated(self, rpc):
        rpc.return_value = [{"signature": f"s{i}"} for i in range(1000)]
        result = discover_solana_funding_root("wallet", max_pages=1)
        self.assertEqual(result["state"], "HISTORY_TRUNCATED")
        self.assertIsNone(result["funding_root"])


if __name__ == "__main__":
    unittest.main()
