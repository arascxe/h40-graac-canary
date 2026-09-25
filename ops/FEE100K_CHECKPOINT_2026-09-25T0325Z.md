# FEE100K checkpoint — 2026-09-25 03:25 UTC

Repository: `arascxe/h40-graac-canary`  
Supabase: `iocirjhwncnhjanawgsm`

## Decision

`FIX / CAPACITY_REBOUND_CRITICAL / CRYPTO_DATA_GAP / ACCESS_PARTIAL / PILOT_READY_FALSE`

## This session

- Re-read the autonomous operations contract and current durable state.
- Audited Supabase logs for 2026-09-24 23:09–2026-09-25 03:24 UTC before issuing one bounded read-only SQL query.
- Classified all four direct subfunctions called by cron job 95.
- Made no production, schema, cron, threshold, freeze, data-deletion, wallet, launch, promotion, or paid-plan change.

## Operational evidence

- Database size at 03:25 UTC: **480,496,787 bytes**, approximately **96.10%** of the 500 MB free quota.
- This is **61,161,472 bytes larger** than the 419,335,315-byte recovery checkpoint. The earlier capacity recovery was not durable.
- Log window: 2,290 completion events; 6 statement timeouts; 1 connection reset.
- Timeout cluster: 00:44–00:45 UTC; isolated timeouts at 01:05 and 02:45 UTC.
- Job 95: 206 completion messages, 0 failure messages in the window; latest 12 database run records all succeeded.
- The newest scheduled crypto workflow [run 36079643535](https://github.com/arascxe/h40-graac-canary/actions/runs/36079643535) succeeded, but success does not imply current observation coverage.

## Job 95 dependency result

The wrapper is not a disposable queue job. It combines:

1. canonical outcome-response processing,
2. economic outcome-response processing,
3. creation of up to four new outcome HTTP probes per tick,
4. aggregate model-state refresh.

A whole-job pause would silently delay or lose prospective future-only outcomes and is rejected. The queueing subfunction is the only plausible future load-shed seam, but separating it requires a shadow wrapper, backlog/backfill proof and sufficient capacity margin. None exists at 96.10% quota use.

Detailed gate: [JOB95_LOAD_SHED_GATE_2026-09-24.md](JOB95_LOAD_SHED_GATE_2026-09-24.md).

## Coverage and economics

Latest crypto snapshot generated 2026-09-25 00:54:38 UTC, but its Jetstream cursor ended at 2026-09-23 21:01:55 UTC: **27h 52m 43s behind**. It reports `caught_up_near_live=false`, `PARTIAL_OR_BASELINE_UNKNOWN`, 0 fresh keyword posts, 5 items and 0 exact-object links. Zero exact matches remains `DATA_GAP`, not negative evidence.

Creator-fee access remains `ACCESS_PARTIAL`: existing BP4W evidence verifies a mint→canonical pool→creator vault route and creator-level claim signatures, but not four-mint mint-specific attribution or user-controlled realized receipts. No verified revenue milestone exists.

## Next highest-information step

Do not add collectors or refactor production while capacity remains critical. First determine, with log-first bounded observation, why the database rebounded by ~61 MB and whether the response compactor is oscillating around its threshold. Only after a stable safety margin should a shadow split of job 95 queueing versus processing be tested.
