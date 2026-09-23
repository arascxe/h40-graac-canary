# FEE100K next actions

## Highest-value next step — recover measured coverage safely

1. Recheck the last 5–10 minutes of cron statuses and the latest GitHub schedule event. Capture exact timestamps, job duration, `pg_stat_activity`, wait events and slow query plans. Audit free plan compute and database storage headroom. Do not infer a schedule is working from push-triggered success.
2. In a read-only or shadow session, EXPLAIN the three identified expensive operations: 12-hour token upsert, snapshot global rank/delete, old cron history cleanup. Propose bounded incremental updates or indexed retention with a migration and rollback plan. Test against a small real slice and preserve first-freeze and evidence rows. Only then alter production, one intervention at a time; confirm job success and observation freshness afterward.
3. Determine why the crypto workflow generated no scheduled snapshot after 17:03 UTC. GitHub Actions schedules are best effort; inspect workflow enablement/queue and the long MDRTF job. Do not mislabel stale snapshots as live. A missed-run monitor should publish `COVERAGE_UNKNOWN`, never a false zero.
4. Reddit: use the official approval route if eligible, with purpose and proposed commercial use disclosed; no anonymous hosted-runner retry. Keep it excluded from measured coverage pending permission. Maintain lawful alternative public crypto-native sources with exact-object URLs and timestamped provenance.
5. Continue the exact frozen 20 IDs and distinct exploratory 20 under their original protocols. Audit exact-object URL normalization against the source objects, and manually adjudicate the first apparent cross-surface match for independent actor, source, observation-before-mint timing and absence of self/related promotion. Keep weak semantic hints separate.
6. At 24h and 7d, record mature outcomes and matching source coverage per object. Treat undocumented tokenization as UNKNOWN. Only prepare a rights-safe pilot when full original Demand-Proof, semantic vacancy, independent pre-mint crossover, distribution and exact fee-owner route all pass.

Current decision: FIX. No `P($100K)` estimate, pilot-ready finding or verified revenue. The next user approval is needed only for a specific live mint, transaction, funds or paid service after a reviewable pilot package exists.
