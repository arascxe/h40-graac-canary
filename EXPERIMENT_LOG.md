# FEE100K experiment log

## 2026-09-23 — audit, no intervention

Question: Is the pre-mint crossover sensor collecting independent, fresh evidence for the frozen first-20 cohort?

Observed: primary cohort 10 enriched + 10 matched controls, frozen 16:11:40 UTC. At 19:24 UTC: 66 persisted crypto posts, 0 exact matches, 0 semantic review hints, 0 verified pre-mint eligibility and no mature 24h or 7d outcomes. The observation window is less than four hours old; no success-rate estimate is possible.

Negative control: the matched controls remain separately labeled. Missing Reddit/Bluesky-search coverage, stalled GitHub schedule and bridge errors prohibit calling absence of matches a true negative. No frozen gate or score changed.

Source diagnosis: the latest snapshot (17:03 UTC) shows official public Bluesky Jetstream replay working for that bounded run; AppView search had returned 403 and remains disabled; Reddit hosted-runner access requires explicit approval and OAuth. Reddit's current official policy requires approved access and forbids unauthorized collection; do not retry anonymous feeds or route around 403. Mastodon tag success is low-confidence keyword coverage. The sensor's latest five successful runs were triggered by pushes, not by its 15-minute schedule.

Database diagnosis: the project reports healthy at platform level, but 65 cron failures in the 10 minutes preceding 19:24 UTC. Latest failures include startup timeouts and two expensive statement timeouts. The snapshot maintenance function ranks the entire snapshot table and deletes rows beyond 18 per object every cycle; token refresh upserts all posts seen over 12 hours every cycle; retention deletes old cron history without a time index. These are plausible load contributors, not a proven sole cause. No mutation was attempted because the execution path and capacity are still under investigation.

Cohort quality audit: direct inspection of frozen rows found generic news, sports, profile/hashtag URLs and SEO-like material in both groups. For example enriched rows included an ACMilan hashtag and an Axios news link; the control group included a sports playoff hashtag and an Elementor template advert. This is an observed classifier-quality concern, not a retrospective edit to the frozen trial. Record categorical veto and exact-object resolution errors separately when outcomes mature.

Decision: FIX coverage and database health before a launchability claim; preserve all first-freeze records. Fail condition for the next bounded check: if freshness and bridge health remain insufficient, label crossover outcome `DATA_GAP`, not `NO_CROSSOVER`.

No code, schedule, schema, threshold, funds, alert routing or token launch changed in this checkpoint.

### Read-only plan probe, ~19:30 UTC

`EXPLAIN (FORMAT JSON)` for the snapshot pruning DELETE (without executing it) shows a window over an estimated 21,973 snapshot rows, incremental sort, then a full sequential scan and hash join of the snapshot table for deletion. A read-only count found 4,228 object keys and **zero** keys above the 18-row cap at that moment; this full pruning operation was therefore doing no useful deletion in that sample. The count itself took about 50 seconds under current load. A subsequent function-definition query failed with a connection timeout. This supports load triage but does not establish sole causality or justify dropping the immutable retention rule. No changes made.

## 2026-09-23 19:36–19:40 UTC — hourly fail-fast probe

Hypothesis: the prior coverage outage might have resolved, allowing the frozen cohort to be evaluated. Test: inspect the latest crypto workflow event and snapshot timestamp, five latest bridge records, narrow cron status distribution, activity sample, and compact cohort/match counts. Negative control: retain the original ten matched-control labels and classify missed source windows as missing, not negative.

Result: hypothesis rejected. The workflow still has a 15-minute cron declaration but latest eight crypto runs were push events, latest published snapshot remained 17:03:32 UTC, and bridge request 83874 processed at 19:34:03 returned `BRIDGE_HTTP_NULL`. Since 19:26, cron history showed 64 failed/30 succeeded/6 running at the sample; two recent failures specifically said `job startup timeout`. A compact database query found 20 original rows, 20 separate exploratory rows, 66 old crypto posts, 0 exact matches, 0 semantic hints, and 0 mature 24h labels. Several larger or concurrent read-only queries timed out, so database load is itself an observed diagnostic constraint. No candidate or revenue result can be drawn from the zeros.

Security countercheck: table inventory warned of disabled RLS, while `has_schema_privilege` returned false for anon/auth USAGE on `fee100k_private`. Public exposure is not demonstrated. Do not blindly change RLS or grants; verify the Data API boundary and bridge role first.

Decision: FIX, no production mutation. No code, migration, run dispatch, threshold change, financial action or new cohort. This session's identifiers: bridge request 83874; crypto run 35892979601 (prior push run, **not** this session's run); scheduled public propagation run 35910703156 (external production activity, not a crypto run). Documentation-only GitHub commits follow this entry.

## 2026-09-23 19:44–19:45 UTC — database-independent failure discrimination

Hypothesis: the prior SQL timeouts might be confined to one maintenance statement. Small probe: ten-minute status aggregate succeeded at 19:44 UTC (51 failed, 24 succeeded, 5 running; 19 active FEE100K jobs). Three follow-up narrow diagnostic SQL calls returned INVALID_ARGUMENT; a standalone simple `cron.job` listing reported connection timeout. Stopped SQL probing. Independent ClickHouse log query for 19:35–19:50 UTC found pg_cron 57014=14 and PostgREST 57014=12. Distinct pg_cron contexts show queue_shadow_outcomes, discovery bus update, premint token refresh, snapshot prune, token/market summaries and turnover links. The hypothesis of a single isolated statement is rejected; shared saturation or contention remains an inference, not an established cause. Negative control: a prior GitHub crypto workflow run's success was verified by run 35892979601 jobs, but is not evidence of a new scheduled snapshot. No prospective cohort outcome is advanced; missing coverage is UNKNOWN. Intervention: hourly automation 6ab42a0f629c819197e9f28f46417bbe prompt gained a fail-fast log-first rule; no production database code or cron changed. Verification: automation update returned success and preserved hourly enabled schedule. Next experiment waits for database responsiveness or uses log-only classification, then isolates one load path in shadow with a rollback before production change.
