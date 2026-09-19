"""Future-only attention-to-issuance research shadow.

This module looks for a narrow condition: a newly observed external-attention
event with independent support and no semantically linked launch in the
continuously covered Pump future census.  It never launches a token, signs a
transaction, recommends an allocation, or treats an incomplete census as
negative evidence.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sqlite3
import unicodedata
from typing import Any


VERSION = "ATTENTION_ISSUANCE_SHADOW_V1_20260919"
CAPITAL_STATE = "CAPITAL_LOCKED"
MIN_OBSERVATION_CUTS = 2
MAX_ATTENTION_AGE_HOURS = 6
RECURRENCE_LOOKBACK_DAYS = 7
RECURRENCE_SEPARATION_HOURS = 24

STOP = {
    "the", "and", "for", "with", "from", "today", "season", "jr", "fc", "f.c",
    "maç", "kadrosu", "sayılı", "kanun", "genel", "müdürlüğü", "burs", "本人確認",
}


def _iso(value: dt.datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _time(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def normalize(value: str) -> str:
    folded = unicodedata.normalize("NFKD", value or "")
    folded = "".join(ch for ch in folded if not unicodedata.combining(ch)).lower()
    return " ".join(re.findall(r"[a-z0-9]+", folded))


def semantic_tokens(value: str) -> set[str]:
    return {token for token in normalize(value).split() if len(token) >= 3 and token not in STOP}


def semantic_link(event_title: str, launch_name: str, launch_symbol: str) -> bool:
    """Conservative lexical link; ambiguity is allowed to veto whitespace."""
    event_norm = normalize(event_title)
    candidates = [normalize(launch_name), normalize(launch_symbol)]
    if event_norm and event_norm in candidates:
        return True
    event = semantic_tokens(event_title)
    if not event:
        return False
    for value in (launch_name, launch_symbol):
        tokens = semantic_tokens(value)
        overlap = event & tokens
        if len(overlap) >= 2:
            return True
        if len(overlap) == 1:
            token = next(iter(overlap))
            if len(token) >= 6 and (tokens == {token} or event == {token}):
                return True
    return False


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS issuance_shadow_runtime (
          singleton INTEGER PRIMARY KEY CHECK(singleton=1),
          version TEXT NOT NULL, started_at TEXT NOT NULL,
          capital_state TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS issuance_attention_births (
          event_id TEXT PRIMARY KEY, first_seen_cut_id TEXT NOT NULL,
          first_seen_at TEXT NOT NULL, event_title TEXT NOT NULL,
          normalized_title TEXT NOT NULL, first_published_at TEXT NOT NULL,
          last_seen_at TEXT NOT NULL, observation_cuts INTEGER NOT NULL,
          geos_json TEXT NOT NULL, publishers_json TEXT NOT NULL,
          preexisting_at_start INTEGER NOT NULL,
          capital_state TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS issuance_birth_title
          ON issuance_attention_births(normalized_title, first_seen_at);
        CREATE TABLE IF NOT EXISTS issuance_candidate_observations (
          cut_id TEXT NOT NULL, event_id TEXT NOT NULL,
          observed_at TEXT NOT NULL, attention_age_seconds INTEGER NOT NULL,
          observation_cuts INTEGER NOT NULL, geo_count INTEGER NOT NULL,
          publisher_count INTEGER NOT NULL, future_launch_matches INTEGER NOT NULL,
          pump_coverage_state TEXT NOT NULL, novelty_state TEXT NOT NULL,
          canonicality_state TEXT NOT NULL, rights_state TEXT NOT NULL,
          candidate_state TEXT NOT NULL, reasons_json TEXT NOT NULL,
          capital_state TEXT NOT NULL,
          PRIMARY KEY(cut_id,event_id)
        );
        """
    )


def _event_id(normalized_title: str, first_seen_at: str) -> str:
    return hashlib.sha256(f"{normalized_title}|{first_seen_at}".encode()).hexdigest()[:24]


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def _coverage_since(conn: sqlite3.Connection, first_seen_at: str, observed_at: str) -> str:
    if not _table_exists(conn, "pump_census_cuts"):
        return "PUMP_COVERAGE_MISSING"
    rows = conn.execute(
        "SELECT source_state FROM pump_census_cuts "
        "WHERE request_started_at>=? AND request_started_at<=? ORDER BY request_started_at",
        (first_seen_at, observed_at),
    ).fetchall()
    if not rows:
        return "PUMP_COVERAGE_MISSING"
    states = [row[0] for row in rows]
    return "COMPLETE_INTERVAL" if all(state == "COMPLETE_INTERVAL" for state in states) else "PUMP_COVERAGE_GAP"


def _launch_semantic_index(
    conn: sqlite3.Connection, observed_at: str,
) -> tuple[list[tuple[str, str, str]], dict[str, set[int]], dict[str, set[int]]]:
    """Load the known launch universe once per cut and index lexical candidates."""
    if not _table_exists(conn, "pump_launches"):
        return [], {}, {}
    records = [
        (str(mint), name or "", symbol or "")
        for mint, name, symbol in conn.execute(
            "SELECT mint,name,symbol FROM pump_launches WHERE created_at<=?",
            (observed_at,),
        )
    ]
    exact: dict[str, set[int]] = {}
    by_token: dict[str, set[int]] = {}
    for index, (_, name, symbol) in enumerate(records):
        for value in (name, symbol):
            normalized = normalize(value)
            if normalized:
                exact.setdefault(normalized, set()).add(index)
            for token in semantic_tokens(value):
                by_token.setdefault(token, set()).add(index)
    return records, exact, by_token


def _future_launch_matches(
    event_title: str,
    launch_index: tuple[list[tuple[str, str, str]], dict[str, set[int]], dict[str, set[int]]],
) -> list[str]:
    records, exact, by_token = launch_index
    candidate_indexes = set(exact.get(normalize(event_title), set()))
    for token in semantic_tokens(event_title):
        candidate_indexes.update(by_token.get(token, set()))
    return [
        records[index][0]
        for index in candidate_indexes
        if semantic_link(event_title, records[index][1], records[index][2])
    ]


def _prior_attention_state(
    conn: sqlite3.Connection, normalized_title: str, started_at: str,
) -> tuple[bool, str]:
    """Use old future-only rows only as a veto; never backfill a candidate."""
    if not _table_exists(conn, "attention_events") or not _table_exists(conn, "cuts"):
        return False, "NOVELTY_HISTORY_UNAVAILABLE"
    previous = conn.execute(
        "SELECT MIN(c.created_at),MAX(c.created_at) FROM attention_events a "
        "JOIN cuts c ON c.cut_id=a.cut_id "
        "WHERE a.normalized_title=? AND julianday(c.created_at)<julianday(?)",
        (normalized_title, started_at),
    ).fetchone()
    if previous and previous[0]:
        return True, "PREEXISTING_AT_SHADOW_START"
    return False, "NEW_SINCE_SHADOW_START"


def evaluate_attention_issuance_shadow(
    conn: sqlite3.Connection,
    cut_id: str,
    observed_at: dt.datetime,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    """Persist future-only issuance observations and return a cut summary."""
    ensure_schema(conn)
    observed_at = observed_at.astimezone(dt.timezone.utc)
    observed_iso = _iso(observed_at)
    conn.execute(
        "INSERT OR IGNORE INTO issuance_shadow_runtime VALUES (1,?,?,?)",
        (VERSION, observed_iso, CAPITAL_STATE),
    )
    started_at = conn.execute(
        "SELECT started_at FROM issuance_shadow_runtime WHERE singleton=1"
    ).fetchone()[0]

    grouped: dict[str, dict[str, Any]] = {}
    for event in events:
        title = str(event.get("title") or "").strip()
        normalized = normalize(title)
        if not normalized:
            continue
        row = grouped.setdefault(normalized, {
            "title": title, "normalized": normalized, "published": event.get("published"),
            "geos": set(), "publishers": set(),
        })
        row["geos"].add(str(event.get("geo") or "UNKNOWN"))
        for support in event.get("support") or []:
            source = normalize(str(support.get("source") or ""))
            if source:
                row["publishers"].add(source)
        published = event.get("published")
        if published and (not row["published"] or published < row["published"]):
            row["published"] = published

    observations = []
    launch_index = None
    for grouped_event in grouped.values():
        normalized = grouped_event["normalized"]
        active = conn.execute(
            "SELECT event_id,first_seen_at,observation_cuts,geos_json,publishers_json,"
            "preexisting_at_start FROM issuance_attention_births "
            "WHERE normalized_title=? ORDER BY first_seen_at DESC LIMIT 1",
            (normalized,),
        ).fetchone()
        if active:
            event_id, first_seen_at, prior_cuts, geos_json, publishers_json, preexisting = active
            geos = set(json.loads(geos_json)) | grouped_event["geos"]
            publishers = set(json.loads(publishers_json)) | grouped_event["publishers"]
            observation_cuts = prior_cuts + 1
            conn.execute(
                "UPDATE issuance_attention_births SET last_seen_at=?,observation_cuts=?,"
                "geos_json=?,publishers_json=? WHERE event_id=?",
                (observed_iso, observation_cuts, json.dumps(sorted(geos)),
                 json.dumps(sorted(publishers)), event_id),
            )
        else:
            first_seen_at = observed_iso
            preexisting, novelty = _prior_attention_state(conn, normalized, started_at)
            event_id = _event_id(normalized, first_seen_at)
            geos, publishers = grouped_event["geos"], grouped_event["publishers"]
            observation_cuts = 1
            published = grouped_event["published"]
            published_iso = _iso(published) if published else observed_iso
            conn.execute(
                "INSERT INTO issuance_attention_births VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (event_id, cut_id, first_seen_at, grouped_event["title"], normalized,
                 published_iso, observed_iso, observation_cuts, json.dumps(sorted(geos)),
                 json.dumps(sorted(publishers)), int(preexisting), CAPITAL_STATE),
            )

        age = max(0, int((observed_at - _time(first_seen_at)).total_seconds()))
        coverage = _coverage_since(conn, first_seen_at, observed_iso)
        if coverage == "COMPLETE_INTERVAL":
            if launch_index is None:
                launch_index = _launch_semantic_index(conn, observed_iso)
            matches = _future_launch_matches(grouped_event["title"], launch_index)
        else:
            matches = []
        if preexisting:
            novelty_state = "PREEXISTING_AT_SHADOW_START"
        else:
            recurrence_cutoff = _iso(
                observed_at - dt.timedelta(days=RECURRENCE_LOOKBACK_DAYS)
            )
            separated_cutoff = _iso(
                observed_at - dt.timedelta(hours=RECURRENCE_SEPARATION_HOURS)
            )
            recurring = conn.execute(
                "SELECT 1 FROM attention_events a JOIN cuts c ON c.cut_id=a.cut_id "
                "WHERE a.normalized_title=? AND julianday(c.created_at)>=julianday(?) "
                "AND julianday(c.created_at)<julianday(?) LIMIT 1",
                (normalized, recurrence_cutoff, separated_cutoff),
            ).fetchone()
            novelty_state = "RECURRING_BASE_VETO" if recurring else "LOW_BASE_PROVISIONAL"

        reasons = []
        quorum = len(geos) >= 2 or len(publishers) >= 2
        if observation_cuts < MIN_OBSERVATION_CUTS:
            state = "PERSISTENCE_PENDING"
            reasons.append("requires_two_future_only_cuts")
        elif age > MAX_ATTENTION_AGE_HOURS * 3600:
            state = "ATTENTION_WINDOW_EXPIRED"
            reasons.append("attention_older_than_six_hours")
        elif not quorum:
            state = "ATTENTION_QUORUM_PENDING"
            reasons.append("requires_two_geos_or_publishers")
        elif novelty_state != "LOW_BASE_PROVISIONAL":
            state = "NOVELTY_VETO"
            reasons.append(novelty_state.lower())
        elif coverage != "COMPLETE_INTERVAL":
            state = "PUMP_COVERAGE_INSUFFICIENT"
            reasons.append(coverage.lower())
        elif matches:
            state = "TOKENIZATION_PRESENT"
            reasons.append("semantic_pump_launch_already_observed")
        else:
            state = "LAUNCH_DUE_DILIGENCE_CANDIDATE"
            reasons.extend([
                "future_only_attention_quorum",
                "continuous_pump_interval_without_semantic_launch",
                "historical_universe_and_rights_still_unverified",
            ])

        canonicality = (
            "FUTURE_PUMP_WHITESPACE_ONLY" if state == "LAUNCH_DUE_DILIGENCE_CANDIDATE"
            else "NOT_ESTABLISHED"
        )
        conn.execute(
            "INSERT OR REPLACE INTO issuance_candidate_observations VALUES "
            "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (cut_id, event_id, observed_iso, age, observation_cuts, len(geos),
             len(publishers), len(matches), coverage, novelty_state, canonicality,
             "UNVERIFIED", state, json.dumps(reasons, sort_keys=True), CAPITAL_STATE),
        )
        observations.append({
            "event_id": event_id, "event_title": grouped_event["title"],
            "candidate_state": state, "attention_age_seconds": age,
            "observation_cuts": observation_cuts, "geo_count": len(geos),
            "publisher_count": len(publishers), "future_launch_matches": len(matches),
            "pump_coverage_state": coverage, "novelty_state": novelty_state,
            "canonicality_state": canonicality, "rights_state": "UNVERIFIED",
            "capital_state": CAPITAL_STATE,
        })

    counts: dict[str, int] = {}
    for row in observations:
        counts[row["candidate_state"]] = counts.get(row["candidate_state"], 0) + 1
    candidates = [row for row in observations if row["candidate_state"] == "LAUNCH_DUE_DILIGENCE_CANDIDATE"]
    return {
        "version": VERSION, "capital_state": CAPITAL_STATE,
        "automatic_launch": False, "automatic_signing": False,
        "events_evaluated": len(observations), "state_counts": counts,
        "due_diligence_candidates": candidates,
        "actionable_launches": [],
    }
