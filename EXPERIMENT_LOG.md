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

### 19:42 snapshot freshness recheck

Fetched the current snapshot branch after the incident checkpoint, rather than reusing the 17:03 audit. A new 19:42:30 UTC snapshot exists (blob `4f5948c7b3a34478c10c1441c8888ea6c0326cb1`), with 8 published items and zero exact outbound-object URL flags. The Jetstream source itself labels catch-up false and baseline unknown after an 80,000-message time-limited replay; 0 fresh keyword posts. This falsifies the narrow hypothesis that no newer GitHub snapshot exists. It does not establish complete coverage or a working Supabase bridge, and cannot validate 0 crossover in the frozen cohort.

Cursor-unit sanity check: interpreted Jetstream microseconds as Unix time (`us/1000` milliseconds). Start 17:03:20.429, end 17:29:52.937 UTC; generated 19:42:30.003 UTC, giving ~2h12m37s end-cursor lag. This is a deterministic transform of snapshot fields, not an estimated social signal.

## 2026-09-23 — external evidence correction / decision audit

Rechecked the primary source behind a class of Pump graduation statistics. The current arXiv v5 of https://arxiv.org/pdf/2607.02823 (Kamat, *Auditing Collector-Generated Graduation Labels on Pump.fun*) says its v1.3 headline 24-hour graduation rate, cross-regime decline and associated interpretations are withdrawn; collector-observed terminal labels cannot simply be equated to platform-side graduation, and a prespecified model failed temporal generalization. This does not measure creator-fee Y100, nor prove zero opportunity. It invalidates using those withdrawn rates or social-link lift as a calibrated prior for FEE100K. Appended an evidence correction to FEE100K_SUCCESS_MATRIX_V1.md without changing any frozen prospective gate or production score. The alternate Marino and copycat findings were not independently re-audited in this session. Decision relevance: retain a bounded no-money research option; reject any confidence claim derived from graduation proxies until actual fee receipts and matched prospective outcomes exist.

## 2026-09-23 20:17–20:22 UTC — creator-fee access probe initialized, not completed

Supabase PostgreSQL log store had zero 57014/08006 records in 20:07–20:17 UTC, so a bounded SQL schema/data probe was run. Existing `fee100k_right_tail_econ_v1` has 3,268 distinct mints; 24h slice had 5,469 rows/1,286 mints, 4,392 estimated-fee values. But `fee100k_fee_distribution_v1`, `fee100k_fee_ledger_v1`, and `fee100k_launch_v1` each have **0 rows**. Existing data cannot verify a single fee receipt. Frozen a 2-upper/2-lower estimated-proxy access sample from the 19:00–20:00 UTC slice in `premint_discovery/CREATOR_FEE_ACCESS_PROBE_2026-09-23.md` (commit 4add666a24052293af575ad26f4b002753ab1c88). Labels deliberately say proxy, not successful/failed verified outcomes. The four-hour research automation now has an explicit two-cycle/~24h on-chain recipient/source access gate. Outcome currently ACCESS_PENDING; no historical mechanism inference or code deployment was performed. No primary prospective cohort or production service changed.

## 2026-09-23 — method-agnostic goal admission

User direction broadened success from FEE100K fee-only to verified net USD 100k across lawful methods. Created `NET100K_ROUTE_TOURNAMENT_V1.md`, appended contract clarification, and updated the four-hour research automation. Current priority remains original launch/creator fees because a production research base exists; transparent realized inventory gains and a specific voluntary paid digital product route are comparison lanes, while earlier trader-side ideas require genuinely new evidence. This is a preregistered research decision, not an experiment result or a P($100K) estimate. First hard economic milestone is independent net USD 100, and the four-mint/wallet fee access gates remain pending.

## 2026-09-23 20:52–21:05 UTC — freshness and actual creator-fee audit

Two independent, read-only Jetstream live-tail shadow samples succeeded: [20s](https://github.com/arascxe/h40-graac-canary/actions/runs/35918786819), 1,232 posts, two crypto-keyword posts, zero exact external-object links, p50 lag ~0.01s; [60s](https://github.com/arascxe/h40-graac-canary/actions/runs/35919837843), 2,914 posts, one crypto-keyword post, zero exact links, p50 lag ~0.02s. A fast pipe is possible, but useful object-linked crypto-native yield was unproven; no production promotion or cohort reclassification. This argues against spending effort solely on optimizing replay throughput.

The frozen 2+2 fee-access [RPC sample](https://github.com/arascxe/h40-graac-canary/actions/runs/35919565298) found Pump AMM `CollectCoinCreatorFee` in two actual transactions for the BP4W-listed creator. [Detailed audit](https://github.com/arascxe/h40-graac-canary/actions/runs/35919705502) reconciled two wrapped SOL vault transfers (2.846219841 + 0.977812710 = **3.824032551 SOL**) to the creator and wallet net credits (2.846210752 + 0.977803621 = **3.824014373 SOL**), with 9,089 lamport transaction fee each. Creator vault aggregates potential multiple coins; **BP4W mint attribution and USD gains are unknown**. Other creators' four sampled transactions each did not provide comparable proof, which is not proof of absence. The sample supports creator-level fee receipts as a real mechanism, not our revenue, creator profits, buyer independence, or no-audience repeatability. Full specifics in `premint_discovery/CREATOR_FEE_ACCESS_PROBE_2026-09-23.md`.

Converted the observed AMM claim pattern into `fee_audit/creator_receipt_v1.py`: bounded, read-only official RPC auditor; verifies Pump AMM instruction/log, wrapped SOL vault transfer, close-to-creator and exact amount minus network fee versus wallet credit; emits `mint_attribution=UNKNOWN`. [Real-chain acceptance run](https://github.com/arascxe/h40-graac-canary/actions/runs/35920220374) passed two positive claims plus an unrelated wallet inflow negative control. No funds, token, production job, primary freeze, or fee table changed. Next bottleneck: mint-specific fee event allocation and independently acquired attention. Do not scale the low-yield Bluesky keyword lane on speed alone; compare original creator-owned object/utility versus AFT using prelaunch and same-period control evidence.

## 2026-09-23 21:54–21:56 UTC — fail-fast source and cancellation audit

Hypothesis: repeated non-collector pushes under `premint_discovery/**` can interrupt the continuous adapter bus without improving source coverage. Negative control: compare the separate crypto-crossover snapshot and the primary 20-row cohort; a fresh discovery snapshot alone must not be treated as exact crossover or outcome evidence. Method: one bounded project-status check, independent 60-minute PostgreSQL/PostgREST log aggregation, one lightweight activity query, one small three-table cohort count query, GitHub workflow definition and last-100 run metadata, and two public branch snapshots. No full-table scan, EXPLAIN, rerun or production mutation.

Result: workflow `premint-discovery-v2-bridge.yml` has broad `premint_discovery/**` push trigger and `cancel-in-progress: true`; repeated Sep 23 push runs ended `cancelled`, including run 35920657734 at 21:45 UTC when 35924345727 started. The latter was still in progress and published cycle-7 discovery data at 21:54:48 UTC (23 items; one Bluesky connection-close error). Separate crypto crossover remained at 19:42:30 UTC with a 17:29:52 UTC cursor and no new visible workflow run; `0` exact matches is `DATA_GAP`, not a failed opportunity. Primary frozen 20: eligible 0, mature-24h 0; exploratory 20 distinct. Log window 20:54–21:54 UTC had one pg_cron 57014 (`refresh_family_lane_guarded`, 21:45), not active multi-timeout. The lightweight SQL checks completed; no new manual pre-mint match was available for independent timestamp adjudication. No verified user-wallet fee receipt.

Decision: retain the freeze and production settings. Highest-value safe prospective engineering test is a shadow/static test of narrowing the push path to collector code/config rather than research notes, while preserving scheduled/dispatch collection, identical snapshot schema, cancellation behavior on genuine collector-code changes, free-tier runtime and a one-commit workflow rollback. Do not deploy that workflow change until a small real-run baseline and capacity check establish no conflicting continuous job. This session performed the fail-fast observation only, not the workflow intervention. Commit/run references: read-only audit against `main` 961b0db; GitHub runs 35924345727, 35920657734, 35911059465. No new experiment cohort or economic PASS.


## 2026-09-23 22:27–22:38 UTC — scheduled crossover recovery vs backlog divergence

**Hypothesis.** A resumed scheduled crypto-native collector run may restore observation freshness; technical workflow PASS must be rejected if the event cursor still loses ground to wall clock. Negative controls were exact outbound-object yield and the unchanged frozen cohorts; zero matches under partial coverage is not a demand negative.

**Method / fail-fast.** Supabase project status and the independent log stream were checked first for 20:30–22:36 UTC. Logs contained repeated pg_cron SQLSTATE 57014 statement timeouts for `fee100k_private.refresh_family_lane_guarded()` at 21:45 and 22:05 UTC. Per incident rule, exactly one bounded read-only SQL probe (`statement_timeout=5s`, latest 40 `cron.job_run_details`) was made; it completed, so no EXPLAIN, count, rerun or additional database query was attempted. GitHub run metadata, the published crossover snapshot and job logs were then inspected independently.

**Result.** Automatic production activity produced scheduled [run 35928460206](https://github.com/arascxe/h40-graac-canary/actions/runs/35928460206), successful at 22:28 UTC. The snapshot generated at 22:28:08 UTC, but its Jetstream cursor ended at 17:55:38 UTC: **4h32m30s lag**. It processed the 80,000-message cap and advanced only 25m58s from the 17:29:40 prior cursor while 2h45m38s of wall time elapsed. Thus the backlog grew by about 2h19m40s between snapshots; workflow success is not coverage success. It yielded five low-reliability Mastodon items, zero exact outbound objects and zero fresh Jetstream keyword posts. Reddit remained approval-gated and Bluesky search remained disabled after 403. Exact-object/match absence remains `DATA_GAP`.

The one database probe showed many other cron successes around 22:34–22:37 UTC, but this does not erase the two repeated 120-second family-lane timeouts. The failing family-lane job is isolated as the observed error family; production state was not modified.

A separate automatic read-only origin shadow [run 35929298234](https://github.com/arascxe/h40-graac-canary/actions/runs/35929298234), from source commit [89bb033](https://github.com/arascxe/h40-graac-canary/commit/89bb033c5066eb4bac1704c7e4a3f4c9284cd511), verified four exact mint metadata records. Only Grand Theft Clout exposed a project X account and website; NOTHING and GRANDPA'S INVESTMENT exposed no external social/website fields, while 164 Bucky pointed to a deployer post and an unrelated source page. This is post-mint metadata, not independently timestamped pre-mint demand, and does not validate a pilot.

**Tests / decision.** Snapshot schema/privacy self-tests and both GitHub jobs passed. Economic gate failed: no independent pre-mint exact-object crossover and no user-wallet creator-fee receipt. Primary 20, matched controls, separate discovery cohort and the 210-launch freeze were not altered or pooled. Decision: **FIX / DATA_GAP**. Highest-information safe next test is a source-only shadow dual-lane comparison that starts at live tail while preserving the replay cursor and explicit gap interval; reject if two bounded samples again produce no usable exact-object URL. No production workflow, schema, alert, launch or financial action changed in this session.

## 2026-09-23 23:47 UTC — narrow discovery workflow trigger (production-safe restart-loop fix)

**Hypothesis.** The broad `push.paths: premint_discovery/**` rule causes research Markdown and outcome-audit commits to cancel the four-hour adapter bus under `cancel-in-progress: true`. Restricting push triggers to executable collector inputs will preserve scheduled observation time without changing data semantics.

**Fail-fast evidence.** Actions history showed repeated push-run cancellations, including 35920657734 and 35924345727. At the new checkpoint, scheduled run 35931272889 was active and the latest discovery snapshot was current (23:45:27 UTC), while the exact crypto lane remained stale/partial. This made avoiding further unnecessary restarts higher information value than adding a source or cadence.

**Method/change.** In `.github/workflows/premint-discovery-v2-bridge.yml`, replace the directory wildcard with:
- `premint_discovery/collect_v2.py`
- `premint_discovery/envelope_v2.py`
- the workflow file itself

No schedule, threshold, freeze, source implementation, output contract, credentials, cron, schema or alert route changed.

**Tests.** PyYAML load succeeded. Path-match controls passed: two research Markdown files => no trigger; both executable inputs and the workflow file => trigger. `git diff --check` passed. Production commit: [89f29d518b10a31a4c05400e1c5f083b683a9014](https://github.com/arascxe/h40-graac-canary/commit/89f29d518b10a31a4c05400e1c5f083b683a9014).

**Runtime result.** The workflow-file change intentionally caused one final push run [35935251897](https://github.com/arascxe/h40-graac-canary/actions/runs/35935251897), which entered `in_progress`; concurrency cancelled predecessor scheduled run [35931272889](https://github.com/arascxe/h40-graac-canary/actions/runs/35931272889). This is a technical-start PASS only. Completion and the first published cycle still require observation. Rollback: revert commit 89f29d5.

**Economic result.** None. Primary 20 and separate exploratory 20 remain frozen and distinct; exact matches remain zero under incomplete coverage; no verified user-wallet creator-fee receipt or pilot candidate.

### 23:48 UTC runtime verification

Run 35935251897 published a schema-valid cycle-1 snapshot at 23:48:29 UTC (66 items, 57 actor hashes). First-cycle publication PASS closes the immediate technical smoke test. Direct TikTok Creative Center remained unavailable (40101), one Reddit feed returned 429, and this did not repair the separate stale crypto exact-object lane. No economic conclusion or candidate promotion.
## 2026-09-24 02:45–02:55 UTC — storage attribution and replay divergence fail-fast

**Hypotheses.** (1) The next successful crypto run might reduce the replay backlog. (2) The rapid database-size increase might be attributable to one bounded, non-evidence response-retention surface that can later be reduced without touching immutable freezes.

**Method.** Checked Supabase project status and independent 01:45–02:50 UTC logs first. Logs contained one pg_cron 57014 for `refresh_family_lane_guarded()` at 01:45, not an active multi-family timeout storm. Ran one five-second-bounded read-only state query and one five-second-bounded relation-size probe; both completed. The initial combined state query had a harmless schema-name error (`object_key` vs `object_id`) and was corrected without running a heavy scan, EXPLAIN or job rerun. Read the latest 15 GitHub Actions runs and both public source snapshots. Frozen cohorts and thresholds were not edited.

**Results.** Hypothesis 1 rejected. Scheduled run 35940133028 succeeded, but cursor lag worsened from 4h32m30s at the 22:28 snapshot to 6h28m40s at the 00:49 snapshot. Cursor progress was ~25m16s during ~2h21m wall time, increasing backlog by ~1h56m. No later crypto run was visible by 02:52. Exact-object yield remained zero under explicitly partial coverage, so this is `DATA_GAP`, not a negative prospective result.

Hypothesis 2 remains a viable capacity lead. Database size was 433,630,355 bytes. `net._http_response` was the largest relation at 91,512,832 bytes, ahead of `fee100k_birth_seed_v1` at 63,610,880 bytes. The response table contained 6,708 rows spanning 20:54–02:54 UTC, of which 5,589 were older than one hour; no row was older than six hours. This age boundary suggests an existing retention mechanism, but that is an inference and must be verified from actual cron/function ownership before changing it. Negative control: no prospective evidence table, primary-20 row, matched-control label or discovery case was deleted or reclassified.

**Decision / next test.** Do not add a collector, cadence or replay budget. The single highest-information safe change candidate is a guarded shortening of `net._http_response` retention, but only after a read-only consumer/cron dependency audit proves completed responses older than the proposed horizon are not used and a dry-run count/byte estimate plus one-commit migration rollback are documented. Acceptance requires keeping bridge delivery intact and bringing database usage below 75% without touching evidence/freezes; reject if any active consumer depends on older responses. No production mutation was made in this session.

Identifiers: crypto run 35940133028; discovery run 35935251897; source main `8e1afb9074e3598088783230b2cbc6a1822648d4`. Economic status unchanged: no pilot candidate and no verified user-wallet creator-fee receipt.
## 2026-09-24 03:17–03:19 UTC — ephemeral-compactor dependency audit

**Question.** Can database pressure be relieved immediately by shortening or triggering `net._http_response` retention without losing an unprocessed bridge result or disturbing evidence?

**Fail-fast method.** Project/log health first: no timeout-class row in 02:50–03:17 UTC. Then two five-second-bounded, read-only catalog/state queries inspected response ages/sizes, function references, the active compaction cron, the exact compactor definition, pending requests and a dry-run keep/reclaim split. No EXPLAIN, full evidence scan, job rerun or mutation.

**Result.** The existing compactor is active every ten minutes but deliberately waits for 460 MiB. Its current keep rule would retain 13 unprocessed FEE100K response rows and discard 6,679 processed/untracked rows, potentially reclaiming most of the 91.5 MB relation. Immediate intervention is rejected for now: 59 requests remain unprocessed (51 older than one hour), non-FEE100K legacy processors also read the same response table, and the compactor performs an exclusive truncate plus a 19,096-row derived-feature rebuild. A lower threshold is operationally attractive but not yet a safe reversible change; deleted ephemeral responses cannot be restored by merely reverting the function.

**Decision.** Preserve the current job and do not manually dispatch it. The single next safe test is a read-only active-consumer census: map every pending response ID across active cron families, separate stale/missing from genuinely awaiting consumers, and require zero at-risk non-FEE100K responses before proposing a lower threshold. The migration rollback would restore the old threshold; evidence rollback is impossible, so a consumer-safe keep rule is mandatory before deployment. No economic result, candidate or receipt was produced.
