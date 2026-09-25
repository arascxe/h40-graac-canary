# FEE100K checkpoint — 2026-09-25 11:13 UTC

Repository: `arascxe/h40-graac-canary`  
Supabase: `iocirjhwncnhjanawgsm`

## Decision

`PERSISTENT_MULTI_FAMILY_DB_INCIDENT / GITHUB_SCHEDULER_GAP / DATA_GAP / EQUIVALENCE_TEST_DEFERRED / PILOT_READY_FALSE`

## Fail-fast boundary

This session re-read the 07:27 UTC checkpoint and current GitHub/Supabase state. The independent log plane showed an active broad incident, so **zero PostgreSQL SQL**, cohort queries, EXPLAIN, reruns or workflow dispatches were issued. No production, cron, schema, threshold, freeze, evidence, alert, wallet or financial state changed.

## Database incident

For 2026-09-25 07:25–11:13 UTC, the log plane recorded:

- 1,854 completion messages,
- 179 timeout messages,
- 34 connection/SSL messages,
- 2 generic failure messages.

A previously intermittent family-lane statement timeout began at 08:45 UTC. At **10:38 UTC**, the incident expanded into a multi-family startup failure. Through 11:12 UTC, at least 18 cron IDs were affected:

`81, 82, 83, 85, 87, 88, 91, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 106`.

The grouped log counts include **132 cron startup timeouts** between 10:38 and 11:12 UTC, plus **44 statement timeout messages** across the wider window. SSL errors included at least 18 connection resets and 13 EOF events.

This breadth invalidates a job-101-only explanation for the current incident. Job 101 remains inefficient, but the present outage also affects source queueing, processing, outcome, compaction and related families. The 10:38–11:12 interval is `DATA_GAP`; absence of objects, crossovers or outcomes in it is not negative evidence.

## Deferred equivalence test

The planned write-free same-`as_of` comparison between the current family-lane output and `family_lane_shadow_core_v1.sql` was not run. Its safety gate requires a genuinely clean log window. Running it during multi-family startup and connection failures would add load and confound latency results.

## GitHub scheduling gap

The crypto workflow still declares four scheduled runs per hour, but [run 36101180099](https://github.com/arascxe/h40-graac-canary/actions/runs/36101180099), created at 06:03 UTC, remained the newest crypto run through this checkpoint. The effective schedule gap therefore exceeded five hours.

The latest published crypto snapshot is stale and `caught_up_near_live=false`; zero exact-object matches remains `DATA_GAP`. MDRTF run [36092388913](https://github.com/arascxe/h40-graac-canary/actions/runs/36092388913) was still in progress in its prospective-cut collection step in the latest inspected Actions state. Temporal overlap does not establish causality and does not authorize cancellation.

## Capacity and economics

Capacity was deliberately not re-queried during the incident. Last verified database size remains **412,036,243 bytes (82.41%) at 08:19 UTC** from the prior durable state. Automatic compaction has worked once, but current capacity is unknown.

Creator-fee access remains `ACCESS_PARTIAL`. No user-controlled realized fee receipt, independent audited crossover, pilot-ready candidate or revenue milestone was verified.

## Next highest-information step

Remain log-only until a clean interval is observed. Then:

1. verify whether startup failures and GitHub scheduled-run creation recover without intervention;
2. measure capacity once with a bounded query;
3. only after both gates pass, run the write-free same-`as_of` equivalence test for the family-lane shadow core.

Do not dispatch replacement collectors, cancel MDRTF solely on overlap, change cron cadence, delete evidence or alter immutable cohorts during the incident.
