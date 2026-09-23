# FEE100K production state

## 2026-09-23 19:26 UTC — live audit checkpoint

Repository: `arascxe/h40-graac-canary`, default branch `main`. Supabase project `iocirjhwncnhjanawgsm`: `ACTIVE_HEALTHY` at project level, PostgreSQL 17.6.1. Project-level health does **not** imply job health. Database size 358 MB at 19:21 UTC.

Canonical first-20: `fee100k_private.success_matrix_pilot20_v1`, frozen 16:11:40 UTC, 10 `SIGNAL_ENRICHED` and 10 `MATCHED_CONTROL`. Its original freeze is immutable. At 19:24: 20 rows, 0 `verified_premint_eligible`, 0 populated 24h outcomes, 0 populated 7d outcomes. Separate `success_matrix_pilot_live_v1` exploratory cohorts must not be pooled into this trial.

Crypto sensor: last published `fee100k-crypto-crossover-data-v1/latest.json` generated 17:03:32 UTC, 35 screened items. Its Jetstream health reported successful cursor replay to near-live at that time (13,202 events examined, 26 crypto-keyword posts); this is **not** current coverage. Four Reddit communities show `REDDIT_EXPLICIT_APPROVAL_REQUIRED`; Bluesky AppView search `DISABLED_AFTER_403`; Mastodon low-confidence tags yielded 0/2/1/6 timely posts in that snapshot. None prove buyer intent. The latest five crypto workflow runs were push-triggered successes between 16:58 and 17:03 UTC. No newer scheduled crypto run was visible at audit time. Another scheduled MDRTF run (35887944671) remained in progress since 16:55 UTC, at the `Collect 208 prospective cuts` step; causal impact on other schedules is unknown.

Crypto bridge: 66 persisted `crypto_crossover_post_v1` rows, 0 `crypto_crossover_exact_match_v1`, 0 semantic review matches at 19:24 UTC. The last completed bridge record at 18:54 UTC and prior at 18:28 UTC reported `BRIDGE_HTTP_NULL`; the last 200 had source generation timestamp 17:03 UTC. A newer bridge row was queued with no processing result. Coverage is UNKNOWN, not negative.

Incident: multiple active FEE100K cron jobs report `job startup timeout` (including source queue and crypto shadow at 19:26). `premint-evidence` and `turnover-research-maint` have also timed out on `refresh_premint_post_tokens` and snapshot pruning respectively; retention timed out deleting `cron.job_run_details`. In the preceding 10 minutes at 19:24 there were 65 failed, 17 succeeded and 2 running cron executions. Fast freeze was succeeding at 19:26, so outage is partial. There are 19 active FEE100K jobs in the latest inventory. Do not claim healthy continuous observation.

Root-cause hypotheses (not established): excessive concurrent pg_cron workload; full 12-hour upsert in `refresh_premint_post_tokens`; global rank/delete over snapshot history every maintenance cycle; `cron.job_run_details` retention without a time index. Each needs isolated EXPLAIN, capacity and lock review before a change. Do not erase first freezes or evidence to recover capacity.

Economic status: no user-wallet creator-fee receipt was verified in this audit. Neither market volume nor graduation is counted as income. No launch, transaction, spending, schema mutation or production job change in this session.

Sources: [crypto run 35892979601](https://github.com/arascxe/h40-graac-canary/actions/runs/35892979601), [snapshot branch](https://github.com/arascxe/h40-graac-canary/blob/fee100k-crypto-crossover-data-v1/latest.json), database read-only inspection at the UTC times above.
