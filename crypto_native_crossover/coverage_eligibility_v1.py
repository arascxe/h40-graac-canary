#!/usr/bin/env python3
"""Fail-closed eligibility guard for crypto-crossover negative conclusions.

This module does not collect data, alter freezes, or emit trading signals.  It only
classifies whether a saved observation snapshot has enough temporal coverage to
support a *negative* exact-object conclusion.  Positive matches still require
manual provenance review.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


def _timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
        timezone.utc
    ).timestamp()


def assess(snapshot: dict, max_cursor_lag_seconds: int = 300) -> dict:
    reasons: list[str] = []
    if snapshot.get("schema") != "fee100k_crypto_native_crossover_v1":
        reasons.append("WRONG_SCHEMA")

    jet = next(
        (
            h
            for h in snapshot.get("source_health", [])
            if h.get("surface") == "bluesky:jetstream_crypto"
        ),
        None,
    )
    lag_seconds = None
    if not jet:
        reasons.append("JETSTREAM_HEALTH_MISSING")
    else:
        if not jet.get("ok"):
            reasons.append("JETSTREAM_NOT_OK")
        if not jet.get("caught_up_near_live"):
            reasons.append("JETSTREAM_NOT_CAUGHT_UP")
        if jet.get("coverage_status") in {
            "PARTIAL_OR_BASELINE_UNKNOWN",
            "STREAM_UNAVAILABLE",
        }:
            reasons.append("JETSTREAM_PARTIAL")

    try:
        cursor_us = snapshot.get("jetstream_cursor_us")
        if not isinstance(cursor_us, int):
            raise TypeError("cursor must be integer microseconds")
        lag_seconds = max(
            0.0, _timestamp(snapshot["generated_at"]) - cursor_us / 1_000_000
        )
        if lag_seconds > max_cursor_lag_seconds:
            reasons.append("CURSOR_STALE")
    except (KeyError, TypeError, ValueError):
        reasons.append("CURSOR_LAG_UNKNOWN")

    reddit_blocked = any(
        str(h.get("surface", "")).startswith("reddit:") and not h.get("ok")
        for h in snapshot.get("source_health", [])
    )
    if reddit_blocked:
        reasons.append("REDDIT_COVERAGE_MISSING")

    jetstream_negative_eligible = not any(
        r
        in {
            "WRONG_SCHEMA",
            "JETSTREAM_HEALTH_MISSING",
            "JETSTREAM_NOT_OK",
            "JETSTREAM_NOT_CAUGHT_UP",
            "JETSTREAM_PARTIAL",
            "CURSOR_STALE",
            "CURSOR_LAG_UNKNOWN",
        }
        for r in reasons
    )
    return {
        "schema": "fee100k_crossover_coverage_eligibility_v1",
        "jetstream_negative_eligible": jetstream_negative_eligible,
        # A global absence claim also requires currently missing Reddit coverage.
        "global_negative_eligible": jetstream_negative_eligible and not reddit_blocked,
        "cursor_lag_seconds": lag_seconds,
        "reason_codes": sorted(set(reasons)),
        "positive_matches_require_manual_review": True,
        "mutates_freezes": False,
    }


def self_test() -> None:
    stale = {
        "schema": "fee100k_crypto_native_crossover_v1",
        "generated_at": "2026-09-24T10:26:58+00:00",
        "jetstream_cursor_us": 1790190862000000,
        "source_health": [
            {
                "surface": "bluesky:jetstream_crypto",
                "ok": True,
                "caught_up_near_live": False,
                "coverage_status": "PARTIAL_OR_BASELINE_UNKNOWN",
            },
            {"surface": "reddit:r/solana", "ok": False},
        ],
    }
    result = assess(stale)
    assert not result["jetstream_negative_eligible"]
    assert not result["global_negative_eligible"]
    assert "CURSOR_STALE" in result["reason_codes"]
    assert "JETSTREAM_NOT_CAUGHT_UP" in result["reason_codes"]

    live_cursor = int(_timestamp("2026-09-24T10:26:40+00:00") * 1_000_000)
    live = {
        "schema": "fee100k_crypto_native_crossover_v1",
        "generated_at": "2026-09-24T10:26:58+00:00",
        "jetstream_cursor_us": live_cursor,
        "source_health": [
            {
                "surface": "bluesky:jetstream_crypto",
                "ok": True,
                "caught_up_near_live": True,
                "coverage_status": "COVERED_NEAR_LIVE",
            },
            {"surface": "reddit:r/solana", "ok": True},
        ],
    }
    result = assess(live)
    assert result["jetstream_negative_eligible"]
    assert result["global_negative_eligible"]
    assert result["cursor_lag_seconds"] == 18
    print("PASS: stale replay rejected; synthetic near-live control accepted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot", nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.snapshot:
        parser.error("snapshot path required outside --self-test")
    with open(args.snapshot, encoding="utf-8") as handle:
        print(json.dumps(assess(json.load(handle)), sort_keys=True))


if __name__ == "__main__":
    main()
