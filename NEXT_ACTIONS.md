# FEE100K next actions

## Highest-value next step — recover measured coverage safely

1. Recheck the last 5–10 minutes of cron statuses and the latest GitHub schedule event. Capture exact timestamps, job duration, `pg_stat_activity`, wait events and slow query plans. Audit free plan compute and database storage headroom. Do not infer a schedule is working from push-triggered success.
2. In a read-only or shadow session, EXPLAIN the three identified expensive operations: 12-hour token upsert, snapshot global rank/delete, old cron history cleanup. Propose bounded incremental updates or indexed retention with a migration and rollback plan. Test against a small real slice and preserve first-freeze and evidence rows. Only then alter production, one intervention at a time; confirm job success and observation freshness afterward.
3. Determine why the crypto workflow generated no scheduled snapshot after 17:03 UTC. GitHub Actions schedules are best effort; inspect workflow enablement/queue and the long MDRTF job. Do not mislabel stale snapshots as live. A missed-run monitor should publish `COVERAGE_UNKNOWN`, never a false zero.
4. Reddit: use the official approval route if eligible, with purpose and proposed commercial use disclosed; no anonymous hosted-runner retry. Keep it excluded from measured coverage pending permission. Maintain lawful alternative public crypto-native sources with exact-object URLs and timestamped provenance.
5. Continue the exact frozen 20 IDs and distinct exploratory 20 under their original protocols. Audit exact-object URL normalization against the source objects, and manually adjudicate the first apparent cross-surface match for independent actor, source, observation-before-mint timing and absence of self/related promotion. Keep weak semantic hints separate.
6. At 24h and 7d, record mature outcomes and matching source coverage per object. Treat undocumented tokenization as UNKNOWN. Only prepare a rights-safe pilot when full original Demand-Proof, semantic vacancy, independent pre-mint crossover, distribution and exact fee-owner route all pass.

Current decision: FIX. No `P($100K)` estimate, pilot-ready finding or verified revenue. The next user approval is needed only for a specific live mint, transaction, funds or paid service after a reviewable pilot package exists.

## 2026-09-23 19:40 UTC — narrowed immediate action

Priority 1: Restore trustworthy observation freshness, not candidate volume. The crypto workflow declares `7,22,37,52 * * * *`, but no scheduled run has appeared since the 17:03 push run. Inspect workflow scheduling/queue independently of database load; test with one bounded, non-financial, shadow/dispatch run only after confirming free capacity and no overlapping long job. Validate a newly timestamped snapshot and bridge 200 before treating crossover counts as measured negatives. Do not backfill missed Jetstream observations as if seen live.

Priority 2: Isolate database pressure without repeated heavy probes. Capture a narrow per-job failure summary and single-function plans when connections stabilize. Compare schedule collision times with active long queries. Prepare a bounded incremental maintenance proposal and rollback; first test a small actual slice in read-only/shadow, then verify cron success and freshness before any production job or schema change. Repeated full-scan counts timed out/consumed ~50s and should not be retried unchanged.

Priority 3: Once coverage recovers, evaluate the same 20 primary IDs against their ten matched controls and the separate 20 exploration IDs. At the first apparent exact-object match, manually verify original source URL, independent crypto actor/community, post publication and observation times before mint, and semantic vacancy. Absence under current gaps is UNKNOWN.

Security footnote: `fee100k_private` has disabled RLS warnings, but anon/auth schema USAGE is false. Review Data API exposure and table privileges before any RLS migration; preserve bridge compatibility. No automatic security migration based solely on the advisory.

## 2026-09-23 19:45 UTC — incident-aware next step

1. On the next session, inspect independent PostgreSQL logs first. If multiple 57014/connection timeouts continue, make at most one bounded SQL probe and stop on timeout; do not repeat full scans or stack another workload. Establish whether the incident has cleared before code or cron intervention.
2. When stable, compare individual job duration and wait events with schedule collisions. Prioritize a single small shadow rewrite of snapshot pruning or 12-hour token refresh, with unchanged evidence retention and explicit rollback. Test on real bounded data, then measure job latency and source freshness before any production rollout.
3. Independently verify a fresh scheduled crypto workflow snapshot and bridge response; a past push success does not close the data gap. Resume frozen 20-vs-control evaluation only in periods with timestamped source coverage. Keep separate exploration cohort and no inferred fee income.
4. The hourly automation now uses log-first fail-fast during database incidents and checks overlap with the four-hour development task. This is a task-prompt change, not a repair to production services.
