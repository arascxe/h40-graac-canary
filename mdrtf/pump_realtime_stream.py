"""Optional first-party Pump NATS stream capture for future-only evidence.

The stream is additive and fail-closed: connection or schema failures never
become negative market evidence and never weaken the REST census gates. Public
subscriber configuration is read from Pump's own rendered page at runtime so
rotated browser credentials are not committed to the repository.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import hashlib
import json
import queue
import re
import sqlite3
import subprocess
import threading
from typing import Any


STREAM_VERSION = "PUMP_REALTIME_STREAM_V1_20260918"
SUBJECTS = ("unifiedCoinCreationEvent", "unifiedTradeEvent.processed")
MAX_BUFFERED_EVENTS = 50_000


def _iso(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_public_unified_config(rendered: str) -> dict[str, str]:
    rendered = rendered.replace('\\"', '"')
    block = re.search(r'"UNIFIED"\s*:\s*\{([^{}]+)\}', rendered)
    if not block:
        raise RuntimeError("unified_public_config_missing")
    values = {}
    for key in ("servers", "user", "pass"):
        match = re.search(rf'"{key}"\s*:\s*"([^"]+)"', block.group(1))
        if not match:
            raise RuntimeError(f"unified_public_{key}_missing")
        values[key] = match.group(1)
    if not values["servers"].startswith("wss://"):
        raise RuntimeError("unified_public_server_not_wss")
    return values


def _public_unified_config() -> dict[str, str]:
    cp = subprocess.run(
        ["curl", "-sS", "--max-time", "25", "-A", "MDRTF-FutureLedger/0.1", "https://pump.fun"],
        check=False, capture_output=True, timeout=30,
    )
    if cp.returncode != 0 or not cp.stdout:
        raise RuntimeError("pump_page_unavailable")
    return _parse_public_unified_config(cp.stdout.decode("utf-8", "replace"))


class PumpRealtimeStream:
    """Background NATS subscriber with a bounded, drain-only event queue."""

    def __init__(self) -> None:
        self._events: queue.Queue[dict[str, Any]] = queue.Queue(MAX_BUFFERED_EVENTS)
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._connected = False
        self._started_at: str | None = None
        self._last_event_at: str | None = None
        self._last_error = "NOT_STARTED"
        self._dropped = 0

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._started_at = _iso(dt.datetime.now(dt.timezone.utc))
        self._last_error = "CONNECTING"
        self._thread = threading.Thread(target=self._thread_main, name="pump-nats-stream", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=8)

    def _thread_main(self) -> None:
        try:
            asyncio.run(self._listen())
        except Exception as exc:
            with self._lock:
                self._connected = False
                self._last_error = f"{type(exc).__name__}:{str(exc)[:180]}"

    async def _listen(self) -> None:
        try:
            import nats
        except ImportError as exc:
            raise RuntimeError("nats_py_not_installed") from exc
        config = _public_unified_config()

        async def disconnected() -> None:
            with self._lock:
                self._connected = False

        async def reconnected() -> None:
            with self._lock:
                self._connected = True
                self._last_error = ""

        async def error_callback(exc: Exception) -> None:
            with self._lock:
                self._last_error = f"{type(exc).__name__}:{str(exc)[:180]}"

        nc = await nats.connect(
            config["servers"], user=config["user"], password=config["pass"],
            connect_timeout=10, allow_reconnect=True, max_reconnect_attempts=-1,
            reconnect_time_wait=2, disconnected_cb=disconnected,
            reconnected_cb=reconnected, error_cb=error_callback,
        )
        with self._lock:
            self._connected = True
            self._last_error = ""

        async def capture(message) -> None:
            received = _iso(dt.datetime.now(dt.timezone.utc))
            try:
                payload = json.loads(message.data)
            except Exception:
                payload = {"undecodable_sha256": hashlib.sha256(message.data).hexdigest(),
                           "raw_bytes": len(message.data)}
            event = {"subject": message.subject, "received_at": received, "payload": payload}
            try:
                self._events.put_nowait(event)
            except queue.Full:
                with self._lock:
                    self._dropped += 1
                    self._last_error = "BUFFER_FULL"
            with self._lock:
                self._last_event_at = received

        for subject in SUBJECTS:
            await nc.subscribe(subject, cb=capture)
        await nc.flush()
        while not self._stop.is_set():
            await asyncio.sleep(1)
        await nc.drain()
        with self._lock:
            self._connected = False

    def snapshot(self) -> dict[str, Any]:
        events = []
        while True:
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                break
        with self._lock:
            return {
                "version": STREAM_VERSION, "connected": self._connected,
                "started_at": self._started_at, "last_event_at": self._last_event_at,
                "last_error": self._last_error, "dropped_events": self._dropped,
                "events": events,
            }


def ensure_stream_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS pump_stream_events (
          event_id TEXT PRIMARY KEY, first_seen_cut_id TEXT NOT NULL,
          received_at TEXT NOT NULL, subject TEXT NOT NULL,
          payload_json TEXT NOT NULL, schema_state TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS pump_stream_subject_time
          ON pump_stream_events(subject,received_at,event_id);
        CREATE TABLE IF NOT EXISTS pump_stream_cuts (
          cut_id TEXT PRIMARY KEY, observed_at TEXT NOT NULL,
          connected INTEGER NOT NULL, events_seen INTEGER NOT NULL,
          events_inserted INTEGER NOT NULL, creation_events INTEGER NOT NULL,
          trade_events INTEGER NOT NULL, dropped_events INTEGER NOT NULL,
          coverage_state TEXT NOT NULL, last_event_at TEXT, error TEXT
        );
        """
    )


def ingest_stream_snapshot(
    conn: sqlite3.Connection, cut_id: str, observed_at: dt.datetime, snapshot: dict[str, Any]
) -> dict[str, Any]:
    ensure_stream_schema(conn)
    inserted = creations = trades = 0
    events = snapshot.get("events") or []
    for event in events:
        subject = str(event.get("subject") or "")
        payload_json = json.dumps(event.get("payload"), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        received = str(event.get("received_at") or _iso(observed_at))
        event_id = hashlib.sha256(f"{subject}\0{received}\0{payload_json}".encode()).hexdigest()
        before = conn.total_changes
        conn.execute(
            "INSERT OR IGNORE INTO pump_stream_events VALUES (?,?,?,?,?,?)",
            (event_id, cut_id, received, subject, payload_json, "RAW_UNVALIDATED"),
        )
        inserted += int(conn.total_changes > before)
        creations += int(subject == "unifiedCoinCreationEvent")
        trades += int(subject == "unifiedTradeEvent.processed")
    if not snapshot.get("connected"):
        coverage = "STREAM_UNAVAILABLE"
    elif snapshot.get("dropped_events"):
        coverage = "BUFFER_GAP"
    elif not events:
        coverage = "CONNECTED_NO_EVENTS_UNVERIFIED"
    else:
        coverage = "RAW_CAPTURE_ACTIVE"
    conn.execute(
        "INSERT OR REPLACE INTO pump_stream_cuts VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (cut_id, _iso(observed_at), int(bool(snapshot.get("connected"))), len(events), inserted,
         creations, trades, int(snapshot.get("dropped_events") or 0), coverage,
         snapshot.get("last_event_at"), snapshot.get("last_error") or None),
    )
    return {
        "version": STREAM_VERSION, "coverage_state": coverage,
        "connected": bool(snapshot.get("connected")), "events_seen": len(events),
        "events_inserted": inserted, "creation_events": creations,
        "trade_events": trades, "dropped_events": int(snapshot.get("dropped_events") or 0),
        "last_event_at": snapshot.get("last_event_at"),
        "error": snapshot.get("last_error") or None,
        "capital_state": "CAPITAL_LOCKED", "schema_state": "RAW_UNVALIDATED",
    }
