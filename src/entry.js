import worker from './index.js';

const SCHEMA = [
  `CREATE TABLE IF NOT EXISTS source_checkpoints(
    source TEXT NOT NULL, chain TEXT NOT NULL, stream_id TEXT NOT NULL,
    cursor TEXT, block_or_slot INTEGER, source_time INTEGER,
    updated_at INTEGER NOT NULL, state_json TEXT NOT NULL,
    PRIMARY KEY(source,chain,stream_id)
  )`,
  `CREATE TABLE IF NOT EXISTS coverage_windows(
    coverage_key TEXT PRIMARY KEY, source TEXT NOT NULL, chain TEXT NOT NULL,
    event_class TEXT NOT NULL, stream_id TEXT NOT NULL,
    window_start INTEGER NOT NULL, window_end INTEGER NOT NULL,
    status TEXT NOT NULL, cursor_start TEXT, cursor_end TEXT,
    request_count INTEGER NOT NULL DEFAULT 0, rate_limit_429_count INTEGER NOT NULL DEFAULT 0,
    provider_error_count INTEGER NOT NULL DEFAULT 0, recovery_complete INTEGER NOT NULL DEFAULT 0,
    source_latency_ms REAL, poll_lag_s REAL, notes_json TEXT NOT NULL, recorded_at INTEGER NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS recall_windows(
    recall_id TEXT PRIMARY KEY, source TEXT NOT NULL, chain TEXT NOT NULL,
    stream_id TEXT NOT NULL, event_class TEXT NOT NULL,
    window_start INTEGER NOT NULL, window_end INTEGER NOT NULL,
    event_count INTEGER NOT NULL, success_count INTEGER NOT NULL,
    coverage_key TEXT, metadata_json TEXT NOT NULL, recorded_at INTEGER NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS raw_batches(
    batch_id TEXT PRIMARY KEY,
    event_time_start INTEGER NOT NULL,
    event_time_end INTEGER NOT NULL,
    ingest_time INTEGER NOT NULL,
    source TEXT NOT NULL,
    chain TEXT NOT NULL,
    event_class TEXT NOT NULL,
    item_count INTEGER NOT NULL,
    coverage_key TEXT,
    payload_json TEXT NOT NULL
  )`,
  `CREATE TABLE IF NOT EXISTS canary_runs(
    run_time INTEGER PRIMARY KEY, result_json TEXT NOT NULL
  )`
];

async function ensureSchema(db) {
  await db.batch(SCHEMA.map(sql => db.prepare(sql)));
}

export default {
  async scheduled(controller, env, ctx) {
    await ensureSchema(env.DB);
    return worker.scheduled(controller, env, ctx);
  },
  async fetch(request, env, ctx) {
    await ensureSchema(env.DB);
    return worker.fetch(request, env, ctx);
  }
};
