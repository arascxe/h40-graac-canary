# FEE100K multi-family incident overlap — shadow load-shedding decision

Observed window: 2026-09-24 17:40:00–19:07:00 UTC.

This is an offline, read-only decision record. It does not change a cron,
database row, function, threshold, freeze, source collector, or workflow.

## Evidence

The independent PostgreSQL log stream reported:

- 103 statement-timeout events across 56 distinct minutes;
- 73 connection/SSL errors across 32 distinct minutes;
- 326 cron startup timeouts across 15 job IDs.

The incident was still active at 19:06 UTC. Highest startup-timeout counts:

| Job | Known role | Failures | Affected minutes | Decision |
|---|---|---:|---:|---|
| 94 | fast freeze | 60 | 52 | preserve; chronology-critical |
| 81 | source queue | 47 | 47 | preserve; raw coverage-critical |
| 98 | discovery processing | 43 | 43 | preserve; raw processing-critical |
| 95 | turnover outcome probe | 35 | 33 | first shadow load-shedding candidate |
| 100 | discovery adapter bus | 27 | 21 | preserve; source continuity-critical |
| 82 | source processing | 19 | 19 | preserve; raw coverage-critical |
| 103 | crypto crossover | 17 | 17 | already coverage-ineligible; do not rerun |
| 106 | exploration20 crossover | 13 | 13 | preserve state; no negative inference |
| 97 | discovery queue | 13 | 13 | preserve; raw coverage-critical |
| 87 | right-tail forensics | 12 | 12 | derived, but dependency proof incomplete |
| 85 | watchdog | 10 | 10 | preserve during incident |
| 102 | prospective control freeze | 10 | 10 | preserve immutable chronology |
| 91 | turnover maintenance | 8 | 8 | derived, but may own retention |
| 99 | discovery evidence | 8 | 8 | preserve evidence |
| 96 | storage compactor | 5 | 5 | do not alter under >90% capacity |
| 88 | role not captured | 5 | 5 | unknown; ineligible for change |
| 101 | family-lane shadow | 4 | 4 | already known intermittent derived load |
| 83 | role not captured | 1 | 1 | unknown; ineligible for change |

## One-candidate decision

`job 95 / turnover outcome probe` is the first load-shedding candidate, not an
authorized production change.

Why it leads:

1. It is downstream/derived work; raw observations and immutable first freezes
   should already exist before an outcome probe runs.
2. Missed outcomes can in principle be backfilled from preserved evidence,
   unlike lost source observations or first-seen chronology.
3. It was the fourth-largest startup-timeout family, so reducing its overlap
   could be measurable.
4. Job 91 is not preferred because it may contain retention/maintenance
   ownership while database capacity is above 90%.

## Hard blockers before any production change

- Capture job 95's exact current schedule, command and active flag after the
  incident clears.
- Prove every input is durable and every output is deterministic/backfillable.
- Prove no freeze, candidate admission, notification or creator-fee receipt
  gate depends synchronously on job 95.
- Pre-write exact rollback SQL restoring the captured schedule and active flag.
- Change only one family, then require a clean comparison window covering at
  least two original cadences; do not treat fewer failures during missing
  coverage as improvement.

Until all blockers pass: `SHADOW_CANDIDATE_ONLY / NO_PRODUCTION_CHANGE`.
