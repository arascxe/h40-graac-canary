# FEE100K checkpoint — 2026-09-25 07:27 UTC

Repository: `arascxe/h40-graac-canary`  
Supabase: `iocirjhwncnhjanawgsm`

## Decision

`FIX / FAMILY_LANE_SHADOW_TIMEOUT_ROOTED / BOUNDED_SHADOW_CORE_PASS / CAPACITY_OSCILLATING / CRYPTO_DATA_GAP / PILOT_READY_FALSE`

## This session

- Re-read the autonomous operations contract, both Success Matrix V1 documents and the 03:25 UTC durable checkpoint.
- Audited Supabase logs for 03:25–07:24 UTC before database access.
- Issued two bounded, read-only catalog/measurement queries after the log plane showed 2,185 completions, 0 generic failure messages, 0 connection errors and only three periodic statement timeouts.
- Added a read-only optimized shadow core. No production function, cron, schema, data, threshold, immutable freeze, wallet or financial state changed.

## Capacity and compactor

A separate verified checkpoint at 05:35 UTC established that automatic job 96 reclaimed the database from ~480.96 MB to **364.24 MB** without manual action. At 07:24 UTC the database was **394,767,507 bytes (78.95%)** and `net._http_response` occupied **25,804,800 bytes**.

The post-compaction database grew ~30.53 MB in ~109 minutes (~16.8 MB/hour if treated linearly). This is an operational risk signal, not a forecast: automatic reclaim is proven once, but stable free-tier headroom is not yet proven.

## Periodic timeout root cause

All three statement timeouts occurred exactly at 06:25, 06:45 and 07:05 UTC. Cron history links every one to:

- job 101: `fee100k-family-lane-shadow-isolated-q20m`
- function: `fee100k_private.refresh_family_lane_guarded()`
- failure point: the family-lane aggregation/upsert
- duration: the full 120-second statement timeout

Production source/freeze jobs were not implicated by these three events. Job 96 succeeded throughout the same interval.

## Query-shape falsification

The missing-index hypothesis was rejected:

- `fee100k_right_tail_econ_v1` already has `(mint, observed_at desc)`.
- `fee100k_birth_seed_v1` already has a recent-created index and GIN index on `family_tokens`.
- Relevant sizes: 77,133 estimated birth rows / 88.37 MB; 20,232 econ rows / 14.33 MB; 8,457 family-lane rows / 9.49 MB.

The more likely cost is query shape: scanning/unnesting the 48-hour birth set, repeated per-family backfill checks and unconditional upsert of thousands of rows.

## Shadow improvement

Added [`family_lane_shadow_core_v1.sql`](family_lane_shadow_core_v1.sql), which preserves every frozen scoring threshold but:

1. materializes the 48-hour birth subset once,
2. resolves latest econ only for recent mints through the existing index,
3. computes backfill-contaminated families once,
4. performs no writes.

Live bounded test completed inside a 15-second database limit (connector wall: 7.2 seconds), versus job 101 repeatedly exhausting 120 seconds. It evaluated:

- 52,639 recent births and distinct mints,
- 5,322 families,
- 47 `VETO`,
- 3,635 `SHADOW`,
- 1,636 `COPY_SPAM_VETO`,
- 4 `FAMILY_EXPANSION_WATCH`,
- 0 `FAMILY_EXPANSION_STRONG`.

These are shadow classifications, not prospective successes or launch candidates.

Implementation commit: [281c4515](https://github.com/arascxe/h40-graac-canary/commit/281c451552c595e2a211ddfcba1f8d05366a1c35).

## Coverage and economics

Scheduled crypto workflow [36101180099](https://github.com/arascxe/h40-graac-canary/actions/runs/36101180099) succeeded at 06:04 UTC, but its Jetstream cursor ended at 2026-09-23 21:30:47 UTC: **32h 33m behind generation**. It reports `caught_up_near_live=false`, `PARTIAL_OR_BASELINE_UNKNOWN`, 0 fresh keyword posts, 2 items and 0 exact-object links. This remains `DATA_GAP`.

Creator-fee access remains `ACCESS_PARTIAL`; no user-controlled realized creator-fee receipt was verified.

## Next highest-information step

Do not replace job 101 in production yet. Build a write-free equivalence check comparing the current function's last successful output to the shadow core on the same observation time, then design a delta-only upsert and prove rollback/backfill behavior. Production integration remains blocked until semantic equivalence and stable post-compaction headroom are both demonstrated.
