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
