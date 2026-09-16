import datetime as dt
import sqlite3
import unittest

from family_optionality_shadow import update_family_optionality_shadow


def observation(pool, rank, score, price, buy, buyers, share, sell=0.0, route="ROUTE_PASS", contract="PROXY_PASS"):
    return {
        "family_id": "family-1",
        "network": "solana",
        "pool_id": pool,
        "token_id": "token-" + pool,
        "rank": rank,
        "score": score,
        "price": price,
        "execution": route,
        "contract": contract,
        "route": {
            "route_state": route,
            "worst_case_cost_pct": 2.0,
            "quoted_roundtrip_cost_pct": 1.5,
        },
        "flow": {
            "distinct_buyers": buyers,
            "distinct_sellers": 1,
            "external_buy_usd": buy,
            "external_sell_usd": sell,
            "max_buyer_share": share,
            "address_diversity_state": "ADDRESS_DIVERSE",
        },
    }


class FamilyOptionalityShadowTest(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.now = dt.datetime(2026, 9, 16, 18, 0, tzinfo=dt.timezone.utc)

    def test_requires_two_fully_executable_members(self):
        rows = [
            observation("a", 1, 10, 1.0, 100, 4, 0.25),
            observation("b", 2, 9, 1.0, 80, 3, 0.30, route="NO_ROUTE"),
        ]
        result = update_family_optionality_shadow(self.conn, "c1", self.now, rows)
        self.assertEqual(result["opened_family_ids"], [])
        self.assertEqual(self.conn.execute("select count(*) from fos_baskets").fetchone()[0], 0)

    def test_opens_equal_weight_basket_then_rotates_only_on_convergence(self):
        first = [
            observation("a", 1, 10, 1.0, 55, 5, 0.25),
            observation("b", 2, 9, 1.0, 45, 5, 0.30),
        ]
        r1 = update_family_optionality_shadow(self.conn, "c1", self.now, first)
        self.assertEqual(r1["opened_family_ids"], ["family-1"])
        notionals = [r[0] for r in self.conn.execute(
            "select paper_notional_usd from fos_positions order by pool_id"
        )]
        self.assertEqual(notionals, [25.0, 25.0])
        self.assertEqual(r1["rotated_family_ids"], [])

        second = [
            observation("a", 1, 11, 1.2, 75, 8, 0.25),
            observation("b", 2, 8, 0.9, 25, 3, 0.30),
        ]
        r2 = update_family_optionality_shadow(
            self.conn, "c2", self.now + dt.timedelta(minutes=2), second
        )
        self.assertEqual(r2["rotated_family_ids"], ["family-1"])
        basket = self.conn.execute(
            "select state,rotated_pool_id,capital_state from fos_baskets"
        ).fetchone()
        self.assertEqual(basket, ("ROTATED_TO_LEADER", "a", "CAPITAL_LOCKED"))
        states = dict(self.conn.execute("select pool_id,state from fos_positions"))
        self.assertEqual(states, {"a": "ROTATED_LEADER", "b": "ROTATED_OUT"})

    def test_does_not_rotate_without_share_gain(self):
        rows = [
            observation("a", 1, 10, 1.0, 60, 5, 0.25),
            observation("b", 2, 9, 1.0, 40, 4, 0.30),
        ]
        update_family_optionality_shadow(self.conn, "c1", self.now, rows)
        flat = [
            observation("a", 1, 11, 1.1, 66, 6, 0.25),
            observation("b", 2, 8, 0.9, 44, 5, 0.30),
        ]
        result = update_family_optionality_shadow(
            self.conn, "c2", self.now + dt.timedelta(minutes=2), flat
        )
        self.assertEqual(result["rotated_family_ids"], [])
        self.assertEqual(
            self.conn.execute("select state from fos_baskets").fetchone()[0], "OPEN_BASKET"
        )

    def test_rank_one_must_be_consecutive(self):
        first = [
            observation("a", 1, 10, 1.0, 55, 5, 0.25),
            observation("b", 2, 9, 1.0, 45, 5, 0.30),
        ]
        update_family_optionality_shadow(self.conn, "c1", self.now, first)
        reversed_rank = [
            observation("a", 2, 8, 1.0, 35, 4, 0.25),
            observation("b", 1, 11, 1.0, 65, 7, 0.25),
        ]
        update_family_optionality_shadow(
            self.conn, "c2", self.now + dt.timedelta(minutes=2), reversed_rank
        )
        regained = [
            observation("a", 1, 12, 1.2, 80, 9, 0.25),
            observation("b", 2, 7, 0.8, 20, 2, 0.25),
        ]
        result = update_family_optionality_shadow(
            self.conn, "c3", self.now + dt.timedelta(minutes=4), regained
        )
        self.assertEqual(result["rotated_family_ids"], [])


if __name__ == "__main__":
    unittest.main()
