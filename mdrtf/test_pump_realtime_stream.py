import datetime as dt
import sqlite3
import unittest

from pump_realtime_stream import _parse_public_unified_config, ingest_stream_snapshot


class PumpRealtimeStreamTests(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.now = dt.datetime(2026, 9, 18, 12, 0, tzinfo=dt.timezone.utc)

    def test_raw_events_are_immutable_and_not_promoted(self):
        event = {
            "subject": "unifiedTradeEvent.processed",
            "received_at": "2026-09-18T12:00:00Z",
            "payload": {"unknown": "shape", "value": 1},
        }
        first = ingest_stream_snapshot(self.conn, "c1", self.now, {
            "connected": True, "events": [event], "dropped_events": 0,
            "last_event_at": event["received_at"], "last_error": "",
        })
        second = ingest_stream_snapshot(self.conn, "c2", self.now, {
            "connected": True, "events": [event], "dropped_events": 0,
            "last_event_at": event["received_at"], "last_error": "",
        })
        self.assertEqual(first["coverage_state"], "RAW_CAPTURE_ACTIVE")
        self.assertEqual(first["schema_state"], "RAW_UNVALIDATED")
        self.assertEqual(first["events_inserted"], 1)
        self.assertEqual(second["events_inserted"], 0)
        self.assertEqual(self.conn.execute("select count(*) from pump_stream_events").fetchone()[0], 1)
        self.assertEqual(
            self.conn.execute("select schema_state from pump_stream_events").fetchone()[0],
            "RAW_UNVALIDATED",
        )

    def test_public_rendered_config_is_parsed_without_persisting_credentials(self):
        rendered = r'prefix \"UNIFIED\":{\"timeout\":5000,\"servers\":\"wss://example.invalid\",\"user\":\"subscriber\",\"pass\":\"rotating\"} suffix'
        self.assertEqual(_parse_public_unified_config(rendered), {
            "servers": "wss://example.invalid", "user": "subscriber", "pass": "rotating",
        })

    def test_disconnect_and_buffer_drop_fail_closed(self):
        unavailable = ingest_stream_snapshot(self.conn, "c1", self.now, {
            "connected": False, "events": [], "dropped_events": 0,
            "last_error": "dns_failure",
        })
        self.assertEqual(unavailable["coverage_state"], "STREAM_UNAVAILABLE")
        gap = ingest_stream_snapshot(self.conn, "c2", self.now, {
            "connected": True, "events": [], "dropped_events": 2,
            "last_error": "BUFFER_FULL",
        })
        self.assertEqual(gap["coverage_state"], "BUFFER_GAP")


if __name__ == "__main__":
    unittest.main()
