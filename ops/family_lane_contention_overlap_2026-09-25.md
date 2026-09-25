# Family-lane contention overlap — 2026-09-25

Scope: read-only reconstruction from Supabase's independent log plane and completed GitHub Actions logs. No PostgreSQL SQL, EXPLAIN, job rerun, production change, cohort query, or freeze mutation was performed for this analysis.

## Observed sequence

| UTC | Family-lane state | Nearby database evidence |
|---|---|---|
| 07:23–08:03 | Three natural successes, about 9.7–10.9s | Same live function and cadence; no deployment |
| 08:45 | SQLSTATE 57014 timeout | Outcome probe waited for ShareLock and acquired after 4.275s |
| 09:05 | SQLSTATE 57014 timeout | Turnover maintenance near this phase took 39.61s; outcome probe had recently waited 7.551s |
| 09:25 | SQLSTATE 57014 timeout | Turnover maintenance runs in the preceding phase took 35.98–42.88s; outcome probe lock waits included 6.026s and 4.281s |

The failing statement in all three new cases was `select fee100k_private.refresh_family_lane_guarded();`, failing inside the existing wide `refresh_family_lane()` aggregation/upsert.

Across 08:42–09:22 UTC, `turnover_research_maintenance()` completion durations ranged from about 12.9s to 42.9s. Separate `turnover_outcome_probe_tick()` executions logged ShareLock waits of about 4.3–9.8s. Premint refresh/evidence work took roughly 10–13s in overlapping phases, and `process_cycle` reached about 10–14s.

## Interpretation

- The unchanged live family-lane function can both succeed quickly and time out at 120 seconds. Query shape is therefore not a sufficient deterministic root cause.
- The resumed failures coincide with measurable lock waits and longer runtimes in other database job families. This supports a shared workload/contention phase as part of the mechanism.
- No direct family-lane lock-wait record identifies one blocking statement. A single culprit, exact lock chain, cache effect, or causal GitHub workflow is **not proven**.
- Long GitHub source workflows overlapped both successful and failed family-lane periods, so workflow overlap alone is not discriminating evidence.
- The existing read-only shadow core remains a risk-reduction candidate, not a deployable replacement, until same-`as_of` semantic equivalence, delta-write behavior, consumer compatibility, deterministic backfill, and one-command rollback pass.

## Source coverage observed in the same window

- Discovery adapter run 36097104891 completed 160 cycles and published at 09:09 UTC: 40 items, 32 independent actors, 38 platform links, 10 creative-evidence items.
- Propagation run 36095967968 completed 180 cycles and published at 09:29 UTC: 91 items, 71 independent actors, 83 links.
- TikTok run 36098133354 completed 24 cycles but every cycle remained at two hashtags and zero videos. Direct TikTok Creative Center calls in adapter logs continued to return code `40101`.
- Reddit RSS showed intermittent HTTP 429 on some communities; this is partial source access, not a universal Reddit failure.
- Crypto-native run 36101180099 remains the newest snapshot. Its cursor ended at 2026-09-23 21:30:47.437 UTC and it was already about 32h33m stale at publication. Zero exact-object matches remain `DATA_GAP`.

## Safety decision

`PERIODIC_FAMILY_LANE_FAILURE_RECURRED / SHARED_CONTENTION_SUPPORTED_NOT_PROVEN / SOURCE_WINDOWS_COMPLETE_PARTIAL_ACCESS / CRYPTO_DATA_GAP / NO_PRODUCTION_CHANGE`.

Current database size was deliberately not queried because multiple live timeouts were present. The last verified checkpoint remains 412,036,243 bytes at 08:19 UTC. No pilot, user-wallet creator-fee receipt, or revenue milestone is established.


## 10:27 UTC counterexample update

A fourth failure occurred at 09:45 UTC after the 09:43 start. The same unchanged function then completed naturally at 10:03:08 and 10:23:08 UTC in about 8.6s and 7.9s.

Outcome-probe ShareLock waits on `fee100k_http_request_v1` continued at 09:50, 09:56, 10:02, 10:14, 10:20 and 10:26 UTC. Retention also logged a ShareLock wait on `fee100k_remix_family_snapshot_v1` at 10:07 UTC. The 10:03 family-lane success immediately followed a logged outcome-probe wait at 10:02; the 10:23 success occurred while the broader periodic wait pattern remained present.

This counterexample rejects `OUTCOME_PROBE_HTTP_ROW_LOCK_WAIT_IS_SUFFICIENT_DISCRIMINATOR`. Shared load/contention remains plausible at a broader resource level, but these row-lock messages alone do not separate family-lane success from failure. The next admissible diagnostic must distinguish query-input/resource state at family-lane start, not merely the presence of unrelated row-lock waits.

The workflow still declares a 15-minute crypto schedule (`7,22,37,52 * * * *`), but no run appeared after 36101180099 at 06:03 UTC through 10:27 UTC. MDRTF run 36092388913 remained in `Collect 208 prospective cuts`, with no new Actions run created after 06:03 UTC. This is an effective scheduling/freshness gap; it is not an economic negative.
