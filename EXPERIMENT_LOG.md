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
## 2026-09-24 04:24–04:25 UTC — passive capacity/cron checkpoint

Log-first check found two family-lane timeouts (03:25, 03:45 UTC), so the database rule limited this session to one five-second read-only probe. That probe showed job 101 recovered with successes at 04:03 and 04:23, while compactor job 96 continued ten-minute technical successes without activating below 460 MiB. Database size increased to 439,717,011 bytes. No repeat dependency scan, EXPLAIN, compactor call, full-table count or cohort experiment was run.

GitHub/source countercheck: long discovery/TikTok/propagation jobs completed, but no crypto replay run followed 00:49 UTC; the exact-object lane therefore remained stale and zero matches remained missing-coverage evidence only. Frozen primary 20 and exploratory 20 counts were unchanged. Decision remains `CRITICAL_CAPACITY / INTERMITTENT_FAMILY_TIMEOUT / CRYPTO_DATA_GAP`; do not tune scores or admit economic evidence from technical job success.

## 2026-09-24 05:31–05:41 UTC — scheduled replay catch-up test

**Question.** Did the next genuine scheduled crypto-native run reduce the known replay backlog enough to make exact-object absence interpretable?

**Method.** Read project health and independent timeout logs before database access. Read the scheduled run, its job-step result, and the immutable published snapshot; compared the prior and current cursor timestamps without rewriting first-observed times. The bounded database checkpoint was aborted after two immediate identifier/schema rejections and was not retried a third time. No workload, score, source, cadence, schema, cron, alert or freeze was changed.

**Run/test identifiers.** GitHub Actions [35960321559](https://github.com/arascxe/h40-graac-canary/actions/runs/35960321559), source main `07cebbdd44c5cc5e479fcc4aed2e223c7a2f3360`, published data commit [66b91de4358f65ccd6ce990c37aae9a2b6c3bd08](https://github.com/arascxe/h40-graac-canary/commit/66b91de4358f65ccd6ce990c37aae9a2b6c3bd08). All workflow steps and payload/privacy bounds passed technically.

**Result.** Catch-up hypothesis rejected. Cursor end was 18:48:00 UTC versus snapshot generation 05:31:50 UTC, a 10h43m49s gap. Relative to the preceding 00:49 snapshot, cursor progress was only 27m06s over about 4h42m wall time. The 80,000-message cap was exhausted, `fresh_keyword_posts=0`, and retained items had zero exact outbound objects. Because `caught_up_near_live=false`, no apparent zero may enter prospective economic evidence. No candidate was eligible for manual independent pre-mint verification.

**Operational result.** One new family-lane 57014 occurred at 05:25 UTC. Four long Actions workflows overlapped. Database capacity was not re-measured because the fail-fast state query did not resolve its identifiers; the prior 439,717,011-byte checkpoint remains the last verified value. Decision: `CRITICAL_CAPACITY / CRYPTO_REPLAY_DIVERGING / DATA_GAP`. No economic result or verified receipt.

## 2026-09-24 06:19–06:20 UTC — fail-fast capacity and pause-safety checkpoint

**Question.** Has the capacity incident crossed into active repeated job failure, and can the failing family-lane job be safely paused from versioned evidence alone?

**Method.** Read project status and independent 05:15–06:20 UTC timeout logs first. Because multiple recent timeouts were active, ran exactly one three-second-bounded read-only query containing only database size and recent job 96/101 history. Then stopped database access and searched the repository statically for the job/function definition. No cohort query, relation scan, EXPLAIN, rerun or mutation.

**Results.** Database size was 446,123,155 bytes (~89.2%). Job 101 failed at 05:25, 05:45 and 06:05 UTC; job 96 succeeded every ten minutes but did not trigger reclaim below 460 MiB. The repository contained state references but no versioned definition sufficient to prove job 101 ownership, downstream dependency or rollback. Therefore the pause-safety hypothesis is unresolved and no cron intervention was made. This diagnoses the prior failure pattern rather than repeating the replay or cohort experiments.

**Independent source check.** Discovery run 35958159932 remained fresh at cycle 51, while crypto run 35960321559 remained the newest crypto snapshot and stayed `DATA_GAP`. Four long Actions jobs still overlapped. No exact-object candidate entered manual adjudication.

**Decision.** `CRITICAL_CAPACITY / ACTIVE_FAMILY_TIMEOUT / NO_SAFE_MUTATION_PROVEN`. Freeze new workload and preserve evidence. No pilot, fee receipt or economic validation.

## 2026-09-24 07:10–07:50 UTC — consumer census and passive recovery verification

**Automatic work before this session.** A separate bounded consumer census recorded by main commit `2b150e90672665e26f72dd987280981768cb1cf0` found 36 functions reading `net._http_response`, including four legacy public processors and two `net` internals. It measured 6,585 response rows/92,594,176 relation bytes and 72 unprocessed FEE100K requests, including 54 stale `WATCHDOG_TELEGRAM` requests omitted from the typed closer. It changed no rows, cron, function or threshold.

**This session's question/method.** Did timeout recovery persist while capacity remained below the automatic compactor threshold? Read independent logs first, then ran one three-second read-only query limited to database size and job 96/101 history. Read current GitHub runs and public snapshots. Did not repeat the frozen cohort or exact-match database counts.

**Result.** No timeout-class log appeared after 06:15 UTC. Job 101 completed five consecutive runs from 06:23 through 07:43 UTC; job 96 also continued succeeding. Database size nevertheless increased to 448,195,731 bytes (~89.6%). Discovery remained fresh at 07:49, but crypto-native coverage did not advance beyond the stale 05:31 snapshot. Technical recovery therefore does not close `CRITICAL_CAPACITY` or `CRYPTO_DATA_GAP`.

**Decision/test status.** The consumer census rejects an immediate unguarded threshold reduction or manual compactor call. The next classification query was not run under near-90% storage because its legacy/in-flight ownership rules are not yet versioned; repeating counts would add little information. No economic validation, candidate or receipt.

## 2026-09-24 09:45–09:46 UTC — passive scheduler/capacity checkpoint

**Question.** Did completion of the long GitHub jobs restore the declared crypto schedule, and did database pressure cross either the compactor or plan-limit gate?

**Method/test.** Read Supabase project health and independent timeout logs first. Because the known family-lane timeout recurred at 09:45 UTC, ran exactly one three-second-bounded read-only query limited to database size and recent job 96/101 history, then stopped database access. Read the Actions run ledger plus the immutable crypto and discovery snapshots. No cohort or exact-match database query was repeated. Source/documentation parent: `96cdbf37293bf55244fe9dc156b95503d3b05fb4`; relevant automatic run IDs: discovery 35958159932, TikTok 35959415471, propagation 35956538166, crypto 35960321559 and MDRTF 35952394065.

**Result.** Database size declined to 446,712,979 bytes (~89.3%), but stayed critical. Job 101 succeeded at 08:43, 09:03 and 09:23 before one 120-second 57014 at 09:45; job 96 continued technical success without reaching its 482,344,960-byte activation threshold. Three long Actions jobs completed by 09:22, but no crypto run appeared after 05:31. The last crypto cursor remained at 18:48 UTC and was about 14h59m behind by the checkpoint. Discovery completed with a fresh 09:05 snapshot, but it supplied no eligible exact-object crossover.

**Decision.** Scheduler restoration hypothesis rejected; capacity recovery remains unproven. Do not dispatch the missed job, raise replay budget, or repeat the same stale full-stream experiment. Keep zero exact matches as `DATA_GAP`. No production, freeze, threshold, alert or financial change; no pilot or verified receipt.

## 2026-09-24 10:26–11:07 UTC — genuine schedule recovery / replay catch-up falsification

**Question.** Once runner capacity cleared, would the next genuine scheduled crypto run both appear and reduce the live coverage gap?

**Method/test.** Read Supabase project health and independent logs first. Logs showed three consecutive family-lane 57014 timeouts, so exactly one three-second-bounded read-only query measured only database size and job 96/101 history; no further SQL was run. Read the Actions ledger and immutable crypto snapshot, verified event=`schedule`, and compared cursor progress against the preceding scheduled snapshot without changing first-observed times or cohort membership. Run under test: [35987232148](https://github.com/arascxe/h40-graac-canary/actions/runs/35987232148); predecessor: 35960321559; source/documentation commit: `d8f821c91e0f4838c3274f0ac8b68f731dd073bd`.

**Result.** Scheduler-liveness sub-hypothesis passed: the run appeared and completed technically. Catch-up sub-hypothesis failed: 80,000 messages moved the cursor only ~26m22s over ~4h55m wall time, increasing publication lag to 15h12m36s. The snapshot remained `caught_up_near_live=false`, yielded zero fresh keyword posts and zero exact outbound objects among six retained low-reliability items. Family-lane failed at 09:45, 10:05 and 10:25, then succeeded at 10:43 and 11:03. Database size fell to 442,576,019 bytes (~88.5%) but remained critical.

**Decision.** `SCHEDULER_LIVE / REPLAY_DIVERGING / DATA_GAP / CRITICAL_CAPACITY`. Do not repeat or enlarge the full replay and do not use its zero result as economic evidence. The next safe engineering candidate remains an offline eligibility guard that rejects `caught_up_near_live=false` snapshots from negative exact-match conclusions; do not deploy it while capacity and timeout pressure remain unresolved. No pilot, receipt or financial result.

## 2026-09-24 11:15–11:17 UTC — fail-closed coverage guard shadow verification

**Automatic work before this session.** Commit [4dc46de](https://github.com/arascxe/h40-graac-canary/commit/4dc46de1aaf280f7813a2f46019e6fc61d33400c) added the repository-only `crypto_native_crossover/coverage_eligibility_v1.py` guard. Commit [8f35e9a](https://github.com/arascxe/h40-graac-canary/commit/8f35e9a12de59a3e4a7a7b6ae09291b99429b714) recorded its shadow result. The guard is not wired into the collector, cron, alerts or database.

**This session's verification.** Read Supabase status/logs and GitHub/source state; no new timeout-class log appeared from 11:00–11:17 UTC and no new Actions or source snapshot followed run 35987232148. Did not repeat SQL or cohort analysis because the 11:07 checkpoint was unchanged. Independently executed the committed module's built-in self-test from the fetched main-branch source; exit code 0 and output `PASS: stale replay rejected; synthetic near-live control accepted`.

**Result/decision.** Shadow guard PASS is independently reproduced. Existing stale snapshots remain negative-ineligible; positive exact-object candidates still require manual verification. Production integration remains deferred under `CRITICAL_CAPACITY / INTERMITTENT_FAMILY_TIMEOUT / REPLAY_DIVERGING`. No economic result, pilot or receipt.


## 2026-09-24 13:55–13:58 UTC — 90% capacity gate / passive freshness checkpoint

**Question.** Did the temporary database-size decline hold, and did either family-lane stability or crypto-native freshness recover enough to resume deferred work?

**Method/test.** Read Supabase project status and independent logs first. Logs showed three consecutive family-lane SQLSTATE 57014 timeouts, so exactly one three-second-bounded read-only transaction measured only database size and recent job 96/101 history; no further SQL, EXPLAIN, cohort count or rerun was performed. Read the current Actions ledger and immutable crypto/discovery snapshots. Primary 20, matched controls, exploratory 20 and frozen 210 were not repeated. Parent/source commit before this note: `dacb9eddacc7c7f79299c7f08fe14820ffde561c`; relevant automatic runs: crypto 35987232148, discovery 36006820076, TikTok 36007889742, propagation 36006170183 and MDRTF 35992199079.

**Result.** Database size rose to 450,989,203 bytes (~90.2%), 8,413,184 bytes above the 11:07 checkpoint. Job 101 failed at 12:05, 12:25 and 12:45 UTC, then succeeded at 13:03, 13:23 and 13:43; job 96 kept succeeding below its activation threshold. No new crypto run followed 35987232148, leaving its cursor at 2026-09-23 19:14:22 UTC and the effective gap near 18h44m. Discovery was current at 13:56 with 36 items/33 actor hashes, but did not supply a manually verified exact-object crossover or pilot.

**Decision.** `CRITICAL_CAPACITY_GT_90 / INTERMITTENT_FAMILY_TIMEOUT / CRYPTO_DATA_GAP`. Do not integrate the coverage guard, add ingestion, rerun the replay, lower the compactor threshold or repeat frozen analyses. Technical cron successes are not economic validation. No production or financial mutation was made; no pilot or verified receipt exists.


## 2026-09-24 15:22–15:25 UTC — publication failure isolation and passive capacity check

**Question/method.** Did the recent TikTok failure reflect a blocked source, or a later delivery fault? Read the independent Supabase log store before one three-second-bounded read-only database size/job-96/101 probe. Inspected the failed GitHub job log and current immutable discovery/crypto branch snapshots. No repeated cohort query, collector rerun, EXPLAIN, deletion or mutation. Parent checkpoint commits: `90a901ff` (capacity) and independent `9a40f878` (response census); automatic run IDs: TikTok 36007889742, discovery 36006820076, crypto 35987232148.

**Result/test.** Log window 13:52–15:24 UTC had zero observed 57014/timeout records; SQL returned 451,013,779 database bytes (~90.2%) and four recent job-101 successes. TikTok log shows cycles one through five each collected two hashtags/zero videos and published. Cycle six collected successfully at 14:37:21 but branch push failed at 14:37:22 with GitHub `Internal Server Error`; the job exited 1. This distinguishes a transient GitHub delivery failure from a TikTok access failure, while leaving post-14:26 TikTok coverage unknown. Discovery published cycle 71 at 15:23:51 (39 items, 33 actor hashes). Crypto branch still generated at 10:26:58 with cursor 19:14:22 on 23 September, `caught_up_near_live=false`, no exact outbound object; current missing coverage is not a negative sample.

**Decision.** `GITHUB_PUBLICATION_TRANSIENT / CRITICAL_CAPACITY / CRYPTO_DATA_GAP`. Passive next natural run is the falsifiable delivery retest; no manual rerun while load and storage remain high. Frozen primary 20, separate controls and exploratory 20 and 210 launches unchanged. Technical health or publication does not validate economics; no candidate or wallet receipt.


## 2026-09-24 15:27–16:28 UTC — scheduled replay catch-up falsification, repeated by natural run

**Question/method.** Could the next natural scheduled execution of the unchanged crypto replay reduce the live gap without a manual dispatch or larger budget? Read Supabase project/log health first, then one three-second-bounded read-only database-size/job-96/101 probe. Compared immutable snapshots from runs 35987232148 and [36020296375](https://github.com/arascxe/h40-graac-canary/actions/runs/36020296375) using their generation times and cursor microseconds. No cohort query, job rerun, EXPLAIN or mutation. Parent documentation commit: `2c14fc7`; state/action commits from this checkpoint: `3870e14`, `0185a52`.

**Result/test.** The run technically succeeded, examined 80,000 messages and retained seven low-reliability items, but produced zero fresh keyword posts and zero exact outbound objects. Cursor progress was 1,610.002 seconds versus 18,048.305 seconds elapsed, a catch-up ratio of ~0.089; publication lag increased to 71,194.025 seconds (19h46m34s). The snapshot remained `caught_up_near_live=false / PARTIAL_OR_BASELINE_UNKNOWN`. Supabase logs showed no timeout-class event in 15:20–16:27 UTC; the single probe returned 451,800,211 database bytes (~90.36%) and four recent job-101 successes. Discovery independently remained fresh at 16:25, so it does not repair the crypto-native gap.

**Decision.** `UNCHANGED_REPLAY_CLASS_REJECTED / DATA_GAP / CRITICAL_CAPACITY`. Natural repetition confirms the prior failure mechanism; do not repeat it again until the method class changes. Zero exact objects is coverage-ineligible and not an economic result. Primary 20, controls, exploratory 20 and frozen 210 unchanged; no candidate or wallet receipt.


## 2026-09-24 17:40–18:03 UTC — multi-family database incident blast-radius isolation

**Question/method.** Did the prior quiet window persist, and which job families were affected if not? Read project health and the independent log store first. Active repeated failures triggered the fail-fast rule. Ran exactly one three-second-bounded read-only probe limited to database size and names/command heads for job IDs already visible in logs; then stopped database SQL. Inspected current Actions and immutable source snapshots without repeating cohort analysis. Parent checkpoint commit: `7fbb42f`; automatic runs in view: discovery 36006820076, MDRTF 36029144279, propagation 36006170183 and crypto 36020296375. State/action commits: `9f8eb21`, `8a064c0`.

**Result/test.** Log aggregation from 17:40–18:03 UTC counted 82 cron startup timeouts (17:40:14–18:01:03), 19 SQLSTATE 57014 events (17:41:05–18:00:30) and 23 connection errors (17:44:14–18:01:03). The bounded probe succeeded at 452,865,171 database bytes (~90.57%) and mapped affected jobs to source queue/process, watchdog, right-tail, turnover maintenance/outcomes, fast freeze, discovery queue/process/evidence/bus, control freeze, crypto crossover and exploration20. Discovery completed at 17:40:13 after publishing a fresh snapshot at 17:40:09; the near-simultaneous incident onset is correlation, not proof of causation. Crypto and TikTok source gaps remained unchanged.

**Decision.** `ACTIVE_MULTI_FAMILY_DB_INCIDENT / DATA_GAP / CRITICAL_CAPACITY`. The hypothesis that the earlier quiet period represented recovery is rejected. Do not repeat SQL or mutate production under active pressure. Next safe work, after recovery, is offline cadence-overlap/dependency analysis with a reversible single-family load-shedding proposal. No cohort negative, pilot or verified receipt.


## 2026-09-24 18:30–19:08 UTC — log-only timeout hotspot profiling

**Question/method.** While the multi-family incident remained active, could independent logs isolate a bounded load-shedding candidate without adding database load? Read Supabase project/log status first. Because failures were active and numerous, issued zero Postgres SQL probes. Aggregated 57014 records by pg_cron query and inspected their logged PL/pgSQL contexts. Searched the repository tree/default-branch code for the live cron/function definitions and rollback evidence. No cohort, outcome, exact-match or capacity query; no rerun or mutation. Parent checkpoint commit: `81fd555`; automatic runs in view: discovery 36006820076, propagation 36006170183, MDRTF 36029144279 and crypto 36020296375. State/action commits: `e94711c`, `46d88af`.

**Result/test.** Rolling logs through 19:05 UTC showed 283 startup timeouts, 92 SQLSTATE 57014s and 43 connection errors. In 18:30–19:08, pg_cron 57014 counts were process cycle 16, discovery bus 10, crypto crossover 5, premint refresh 3, turnover maintenance 3, outcome probe 2 and retention 1. Logged contexts expose concurrent full/range scans, inserts/deletes and shared response-table updates, not a single proven culprit. Repository search returned no versioned live definitions sufficient to prove a safe pause, dependency closure or rollback.

**Decision.** Hotspot isolation passes, but production load-shedding admission fails for missing versioned definitions. Remain `ACTIVE_MULTI_FAMILY_DB_INCIDENT / DATA_GAP / NO_SAFE_MUTATION`. The next test is offline definition export plus minute-overlap/dependency analysis after pressure subsides. Calendar maturity alone does not validate the frozen 210 outcomes. No pilot or verified receipt.


## 2026-09-24 20:35 UTC — fail-fast incident extension and crypto freshness falsification

**Hypothesis.** The prior multi-family database incident may have subsided after 19:07 UTC, and the next natural crypto run may show effective catch-up despite earlier replay divergence.

**Method.** Read Supabase project health and the independent log plane for 19:05–20:35 UTC before any database access. Because active timeout evidence was present, execute zero PostgreSQL SQL, EXPLAIN, cohort query or job rerun. Inspect natural GitHub Actions since 19:05, then read the completed crypto job log for run [36048283198](https://github.com/arascxe/h40-graac-canary/actions/runs/36048283198). Frozen thresholds, primary 20, matched controls, exploration cohort and frozen 210 were not opened or changed. State/action commits: `4b3880b3`, `ca34241c`.

**Result/test.** Project health was `ACTIVE_HEALTHY`, but log-plane falsification failed recovery: 208 timeout mentions occurred after 19:05 and the last statement timeout was 20:05:00 UTC. From 19:35 onward, 18 statement-timeout cancellations and repeated startup failures affected multiple job IDs. Crypto run 36048283198 passed its workflow/self-tests and consumed 80,000 messages, yet its cursor advanced only 27m13s (2026-09-23 19:41:00→20:08:13 UTC) and was ~23h19m49s stale at publication. It reported `caught_up_near_live=false`, zero fresh keyword posts and partial/unknown coverage. This is a technical PASS but a freshness FAIL.

**Decision.** Reject the unchanged replay as prospective evidence and retain all zero exact-object output as `DATA_GAP`. Continue `ACTIVE_MULTI_FAMILY_DB_INCIDENT / NO_SAFE_SQL / NO_PRODUCTION_MUTATION`. The single safe candidate remains offline/versioned dependency and rollback proof for job 95 after a clean log window. No pilot, wallet receipt or economic validation.


## 2026-09-24 21:48 UTC — recovery gate probe and job-95 rollback baseline

**Hypothesis.** Timeout pressure may have subsided enough for one bounded read-only probe, and the selected downstream outcome job may have a capturable baseline sufficient to advance—but not yet authorize—the load-shedding experiment.

**Method.** First query only the independent Supabase log plane for 20:35–21:48 UTC. After zero startup, statement and connection errors, run one exact-row SQL probe for database size and cron job 95's schedule, active flag and command. Perform default-branch static searches for the function, job declaration and schedule. Do not query cohorts, outcomes, freezes, receipts or broad catalogs; do not rerun or mutate a job. Automatic GitHub states observed separately: runs 36051648754, 36052052398 and 36052572065 in progress; 36060305687 pending.

**Result/test.** The 73-minute log window was clean. Database size was 461,270,163 bytes (~92.25%), an 8,404,992-byte increase from the prior verified 452,865,171-byte checkpoint. Job 95 was `active=true`, scheduled every `59 seconds`, command `select fee100k_private.turnover_outcome_probe_tick();`. Repository search found no versioned definition or schedule, so dependency/backfill/rollback closure failed. The point-in-time gate is commit `0f1c4ff`; state/action commits are `2f503f5` and `2637378`.

**Decision.** Probe PASS; production-change admission FAIL. Preserve job 95 unchanged. Remain `CRITICAL_CAPACITY / SHADOW_CANDIDATE_ONLY`; require a narrow function/dependency export after another clean window before any cadence change. No pilot, verified receipt or economic validation.


## 2026-09-25 00:04 UTC — job-95 pause falsification and provisional capacity recovery

**Hypothesis.** After a multi-hour clean log window, job 95 may be a narrow downstream family that can be paused reversibly, while storage pressure may have recovered enough to permit the decision.

**Method.** Use the previously bounded live-definition/cron probe recorded in commits `3d0d789` and `1fb3d75`; independently verify the next natural crypto job log for run [36068795919](https://github.com/arascxe/h40-graac-canary/actions/runs/36068795919). Read only the separate log plane for 22:34–00:04 and GitHub run state. Run no new PostgreSQL SQL, cohort query, EXPLAIN, job rerun or mutation in this session.

**Result/test.** Logs remained free of startup, statement and connection errors. The prior bounded probe measured 419,335,315 bytes (~83.87%), but did not establish why storage fell. Job 95's wrapper calls `process_turnover_outcome_canonical()`, `process_turnover_outcome_econ()`, `queue_turnover_outcome_probes()` and `refresh_turnover_model_state()`; latest 12 executions were successful. This rejects the narrow/disposable-job assumption. Crypto run 36068795919 passed workflow tests but exhausted 80,000 messages, advanced only 27m45s, ended at 2026-09-23 20:35:46 UTC and published ~26h05m53s stale with `caught_up_near_live=false`, zero fresh keyword posts and partial/unknown coverage.

**Decision.** Job-95 pause candidate rejected; unchanged crypto replay remains rejected. State is `PROVISIONAL_CAPACITY_RECOVERY / CRYPTO_DATA_GAP / NO_PRODUCTION_CHANGE`. No exact-object pilot, verified receipt or economic validation.


## 2026-09-25 01:31 UTC — recovery falsification and passive crypto divergence confirmation

**Hypothesis.** The prior multi-hour quiet interval may represent durable database recovery; the next natural crypto schedule may at least stop losing ground without changing the already rejected replay method.

**Method.** Read the independent Supabase log plane for 00:10–01:31 UTC before database access. On observing multiple statement timeouts, execute zero PostgreSQL SQL, cohort queries, EXPLAIN, reruns or mutations. Inspect the natural crypto run [36079643535](https://github.com/arascxe/h40-graac-canary/actions/runs/36079643535) and its decoded job log. This is passive confirmation of a rejected method, not a new trial or new cohort.

**Result/test.** Recovery hypothesis failed: five statement timeouts occurred 00:44–01:05 UTC plus one connection reset. Crypto workflow tests passed, but 80,000 messages advanced the cursor only ~26m21s to 2026-09-23 21:01:55 UTC; publication lag was ~27h52m43s. It reported `caught_up_near_live=false`, zero fresh keyword posts and partial/unknown coverage. No exact-object absence is admissible. State/action commits: `a72f1dd`, `aa65f08`.

**Decision.** `RECOVERY_REJECTED / DATA_GAP / NO_SAFE_SQL`. Do not repeat or enlarge the unchanged replay. Freeze/cohort state and economic conclusions remain unchanged; no pilot or verified receipt.


### 2026-09-25 02:56 UTC — fail-fast capacity probe at imminent compactor threshold

**Method**
- Read Supabase project state and the separate log plane before touching the database.
- Reviewed 01:31–02:56 UTC for cron-startup timeouts, `57014`/statement timeouts, and connection errors.
- Because the window contained only one statement timeout (02:45 UTC) and no active multi-timeout pattern, executed exactly one bounded read-only probe: `select pg_database_size(current_database()) as database_bytes;`.
- Reviewed natural GitHub workflow state without dispatching or rerunning jobs.

**Result**
- Database size: **478,702,739 bytes** = **95.74%** of the 500,000,000-byte free allowance.
- Increase from the prior verified 419,335,315-byte checkpoint: **59,367,424 bytes**.
- Remaining free headroom: **21,297,261 bytes**.
- Distance to the already-existing 460 MiB automatic compactor trigger (482,344,960 bytes): **3,642,221 bytes (~3.47 MiB)**.
- Propagation `36071394891`, adapter-bus `36071756803`, and TikTok `36072567786` were still in progress. No new completed source snapshot or valid exact-object crossover evidence appeared.
- Primary/cohort freezes were not queried or mutated. No pilot candidate, user-wallet creator-fee receipt, or economic validation was produced.

**Safety / test**
- PASS: fail-fast ordering honored.
- PASS: exactly one small read-only SQL statement; no EXPLAIN, full-table count, cohort scan, job rerun, or mutation.
- PASS: production jobs, cron, schema, compactor threshold, alert routing, and financial state unchanged.
- HOLD: manual compaction and threshold changes remain blocked until shared HTTP-response consumers and rollback safety are proven.
- Durable state commits: `f4f7f3d4f7b9252c5d790f3af5ffb071a6a9e058` and `32a036cef7d2964c23789eb7053ca26c034ab14d`.


### 2026-09-25 03:58 UTC — natural compactor and source-completion verification

**Hypothesis**
The database may naturally cross the existing 460 MiB guard and reclaim space without intervention, while the three long-running source workflows may restore enough end-to-end coverage for exact-object or pilot evaluation.

**Method**
- Read Supabase project state and the separate 02:56–03:58 UTC log plane first.
- Verified all job-96 start/completion records and timeout/connection patterns.
- Because the window contained no active timeout pattern, executed exactly one bounded read-only SQL statement: `select pg_database_size(current_database()) as database_bytes;`.
- Read the completed job logs for TikTok run `36072567786`, adapter-bus run `36071756803`, and propagation run `36071394891`.
- Did not query cohorts, freezes, outcomes, receipts, broad catalogs, or rerun any job.

**Result**
- Job 96 technically completed six times (03:05–03:55 UTC), but database size reached **480,808,083 bytes (96.16%)**, 2,105,344 bytes above the 02:56 checkpoint and only 1,536,877 bytes below the 460 MiB guard. No storage reclaim is evidenced.
- TikTok completed 24 cycles but ended with two hashtags and zero videos. The adapter completed 160 cycles and ended with 40 items/36 independent actors; direct TikTok API code `40101` persisted. Propagation completed 180 cycles and ended with 73 items/67 actors at 03:51 UTC.
- Fresh public propagation and adapter output are restored, but TikTok video coverage and near-live crypto-native exact-object coverage are not. No exact-object pilot or fee receipt is admissible.

**Safety / test**
- PASS: log-first fail-fast order.
- PASS: one small read-only SQL statement and no additional database load.
- PASS: no production, cron, schema, threshold, routing, freeze, or financial mutation.
- FAIL: compactor technical completion is not storage-reclaim evidence.
- FAIL: complete end-to-end source coverage is not restored.
- Durable state/action commits: `1df53855237595ffbe6ae7745cfbba3207851e12`, `3f128f53216a9f594c44c6ff424cdfe6e7020d8e`.

**Decision**
`CRITICAL_CAPACITY_96_16_PERCENT / COMPACTOR_RECLAIM_UNPROVEN / PARTIAL_SOURCE_RECOVERY / DATA_GAP`. Preserve all immutable cohorts and economic conclusions.


### 2026-09-25 05:35 UTC — natural compaction reclaim verification

**Hypothesis**
The existing automatic 460 MiB guard may reclaim storage safely after natural growth crosses the threshold, without manual invocation or a threshold change.

**Method**
- Read Supabase project status and the independent 04:16–05:35 UTC log plane first.
- With no timeout/connection pattern active, execute two bounded read-only probes only: current database size and the latest four job-96 run records.
- Inspect natural GitHub workflow state without reruns, dispatches, cohort queries, or mutations.

**Result**
- The log window was free of startup, statement, `57014`, and connection errors.
- Job 96 run `215856` started at 05:25:00 UTC and succeeded at 05:25:03 UTC; surrounding runs were successful short guard returns.
- Database size measured **364,235,923 bytes (72.85%)**, down **116,719,616 bytes** from the preceding 480,955,539-byte measurement and leaving 135,764,077 bytes of headroom.
- The timing and size discontinuity verify natural automatic reclaim. They do not independently prove loss-free processing for every shared-response consumer.
- Propagation `36095967968`, adapter `36097104891`, TikTok `36098133354`, and MDRTF `36092388913` were in progress. No new crypto-native snapshot, exact-object candidate, pilot, or wallet receipt appeared.

**Safety / test**
- PASS: automatic threshold behavior reclaimed measured capacity with no manual trigger or configuration change.
- PASS: fail-fast log-first ordering and bounded read-only verification.
- PASS: no production, schema, cron, alert, freeze, or financial mutation.
- HOLD: downstream consumer/backlog/source-freshness safety after reclaim remains to be observed.
- Durable state/action commits: `3deafc19a297083170b905d3ef8d60aaae9c768e`, `6603e5b67c9d0bbbd22185362a15b2cc4dffc43e`.

**Decision**
`CAPACITY_RECLAIM_VERIFIED / POST_COMPACTION_OBSERVATION_REQUIRED / DATA_GAP / NO_ECONOMIC_VALIDATION`.


### 2026-09-25 06:45 UTC — post-compaction family-lane attribution and crypto freshness check

**Hypothesis**
The verified 05:25 UTC automatic reclaim may have removed the database pressure, and the next natural crypto-native run may have restored admissible near-live exact-object coverage.

**Method**
- Read Supabase project state and the independent 05:35–06:45 UTC log plane before database access.
- Attribute the 06:25 and 06:45 timeout contexts by failing function and concurrent job family.
- Because two active statement timeouts were present, execute exactly one small read-only SQL probe: `select pg_database_size(current_database())`; then stop all database querying.
- Inspect natural GitHub Actions and decode the completed crypto-native run [36101180099](https://github.com/arascxe/h40-graac-canary/actions/runs/36101180099). No rerun, cohort query, freeze read, EXPLAIN, or mutation.

**Result / test**
- Supabase remained `ACTIVE_HEALTHY`, but recovery was falsified by SQLSTATE `57014` at 06:25:00 and 06:45:00 UTC. Both contexts name `refresh_family_lane_guarded()` / `refresh_family_lane()`; compactor job 96 only overlapped and is not the logged failing statement.
- Adapter-bus work waited ~1.77 seconds on a lock for `fee100k_http_request_v1` and then proceeded. This supports concurrent contention but does not establish a sole root cause.
- Database size was **384,642,195 bytes (76.93%)**, +20,406,272 bytes from the verified 364,235,923-byte post-compaction checkpoint, with 115,357,805 bytes remaining.
- Crypto run 36101180099 passed workflow tests and consumed 80,000 messages, but advanced the cursor only 29m03.5s (2026-09-23 21:01:43.893→21:30:47.437 UTC) and published ~32h33m15s stale. It reported `caught_up_near_live=false`, zero fresh keyword posts and partial/unknown coverage. Exact-object absence remains `DATA_GAP`.
- Propagation 36095967968, adapter-bus 36097104891, TikTok 36098133354 and MDRTF 36092388913 were still in progress when observed. Their start state is not economic validation.

**Safety / decision**
- PASS: log-first ordering and one-probe ceiling honored; no further SQL after active multiple timeouts.
- PASS: no production job, cron, compactor, schema, threshold, alert, freeze or financial mutation.
- FAIL: post-compaction database recovery is durable.
- FAIL: crypto-native near-live coverage is restored.
- Next safe test is an offline/versioned shadow rewrite and rollback specification for the family-lane function, only after capturing dependencies without stressing production.
- State commit: `aa3fe72e5ca22667006eb8a33f2383469ca2d7af`; next-action commit: `9807961c91bfdd6bd5996108237e57d91795aa2a`; automatic run ID: `36101180099`.

**Decision:** `POST_COMPACTION_FAMILY_LANE_TIMEOUT_RECURRENCE / CAPACITY_REGROWTH_76_93_PERCENT / CRYPTO_DATA_GAP / NO_PRODUCTION_CHANGE`. No pilot, verified creator-fee receipt, or revenue milestone.


### 2026-09-25 07:42 UTC — third timeout and external read-only shadow-core review

**Hypothesis**
The 06:25/06:45 family-lane failures may have been transient; independently produced read-only shadow evidence may isolate a safe optimization without authorizing a production change.

**Method**
- Read Supabase project state and the independent 06:45–07:42 UTC log plane first.
- Because the timeout sequence continued, issue zero PostgreSQL SQL, EXPLAIN, cohort query or rerun in this session.
- Inspect GitHub Actions job states, the current discovery and crypto immutable branch snapshots, commits `281c4515` / `b12a6e8`, and the added read-only `ops/family_lane_shadow_core_v1.sql`.
- Keep work from the separate 07:24–07:27 Work activity distinct from automatic production and this session.

**Result / test**
- Job 101 produced a third identical SQLSTATE `57014` at 07:05 UTC in `refresh_family_lane_guarded()` / `refresh_family_lane()`. No other timeout or connection-error family appeared through 07:42 UTC.
- Separate Work activity—not this session and not automatic production—measured 394,767,507 database bytes (78.95%) and executed a bounded write-free shadow core. It completed under a 15-second statement limit (about 7.2 seconds connector wall time) across 52,639 recent births and 5,322 families.
- Shadow states were 47 `VETO`, 3,635 `SHADOW`, 1,636 `COPY_SPAM_VETO`, 4 `FAMILY_EXPANSION_WATCH` and 0 `FAMILY_EXPANSION_STRONG`. These results are not admitted prospective cases and do not alter any freeze.
- Existing indexes reject the simple missing-index hypothesis. The leading explanation is query shape: unnecessary global latest-econ work, repeated backfill checks and unconditional wide upsert. Same-observation semantic equivalence and delta-write/rollback safety remain untested.
- Discovery snapshot cycle 103 was current at 07:42:30 UTC with 46 items/40 actors, but TikTok bridge still had two hashtags/zero videos. Runs 36095967968, 36097104891, 36098133354 and 36092388913 remained in progress. Crypto run 36101180099 remained coverage-ineligible at ~32h33m stale with zero fresh keyword posts.

**Safety / decision**
- PASS: this session honored fail-fast with zero PostgreSQL SQL under recurring timeout evidence.
- PASS: no production function, cron, schema, threshold, alert, cohort, freeze or financial mutation.
- PASS: the read-only shadow materially narrows the performance hypothesis.
- HOLD: do not deploy until same-`as_of` field-by-field equivalence, delta-only write behavior, consumer compatibility, deterministic backfill and one-command rollback pass.
- Production-state commit: `264efd4bce25acde7d25dedf79523d64c8f8f2cb`; next-action commit: `6f62027a3a57f08fb30657992bc9d67fdfefbf3a`; shadow implementation commit: `281c451552c595e2a211ddfcba1f8d05366a1c35`; automatic crypto run ID: `36101180099`.

**Decision:** `FAMILY_LANE_THIRD_TIMEOUT / READ_ONLY_SHADOW_CORE_PASS / EQUIVALENCE_UNPROVEN / DISCOVERY_FRESH_CRYPTO_STALE / PILOT_READY_FALSE`. No verified creator-fee receipt or revenue milestone.


### 2026-09-25 08:19 UTC — unchanged live-function recovery falsifies single-cause diagnosis

**Hypothesis**
The optimized read-only query shape may explain the three family-lane timeouts by itself; alternatively, unchanged production success would require an intermittent load/contention component.

**Method**
- Read Supabase project status and the independent 07:42–08:19 UTC log plane first.
- After a timeout-free window, run exactly one transaction-local three-second-bounded read-only probe for database size and the latest six job-101 records.
- Inspect current Actions states and immutable discovery/crypto snapshots. Do not run the shadow again, perform equivalence, query cohorts, use EXPLAIN, or mutate/rerun production.

**Result / test**
- The log window had zero new timeout/57014/connection-error records.
- Unchanged job 101 succeeded at 07:23, 07:43 and 08:03 UTC in ~9.7–10.9 seconds, following three 120-second failures at 06:25, 06:45 and 07:05. No live function or cadence change occurred.
- Therefore `QUERY_SHAPE_IS_SOLE_DETERMINISTIC_CAUSE` is rejected. Query shape remains a risk reducer candidate, while intermittent concurrent load, cache or lock/resource contention remains necessary to explain the transition.
- Database size was **412,036,243 bytes (82.41%)**, +17,268,736 bytes from 07:24 and +47,800,320 bytes from the verified post-compaction checkpoint.
- Discovery cycle 127 was fresh at 08:19:02 UTC with 40 items/35 actors; TikTok still had two hashtags/zero videos. Runs 36095967968, 36097104891, 36098133354 and 36092388913 remained active. Crypto run 36101180099 remained stale and coverage-ineligible.

**Safety / decision**
- PASS: log-first gate and one small probe only.
- PASS: natural job-101 recovery established without intervention.
- FAIL: durable database/capacity recovery; storage continued to regrow.
- HOLD: shadow deployment and equivalence remain blocked until failure/success concurrency overlap is isolated and rollback compatibility is proven.
- Production-state commit: `9f22591babb09bddcb4e49f38c46cdb6c6b1be49`; next-action commit: `201037e9a6c59760a7e4ee79dc900c0ff73a4338`; automatic run IDs in view: `36095967968`, `36097104891`, `36098133354`, `36092388913`, `36101180099`.

**Decision:** `JOB101_THREE_NATURAL_SUCCESSES / QUERY_SHAPE_NOT_SOLE_CAUSE / CAPACITY_REGROWTH_82_41_PERCENT / CRYPTO_DATA_GAP / PILOT_READY_FALSE`. No verified receipt or revenue milestone.


### 2026-09-25 09:37 UTC — family-lane success/failure phase overlap audit

**Hypothesis**

If the unchanged family-lane query shape is the sole deterministic cause, its three natural successes should not be followed by identical 120-second failures without a code change. If shared contention is part of the mechanism, failure phases should show independent lock-wait or runtime pressure in other job families.

**Method**

- Read Supabase project state and the independent 08:19–09:37 UTC log plane before database access.
- After detecting multiple active SQLSTATE `57014` events, send zero PostgreSQL SQL, EXPLAIN, cohort query or rerun.
- Reconstruct family-lane timing against existing pg_cron completion durations and lock-wait messages in the log plane.
- Inspect completed GitHub Actions logs and published discovery, propagation, TikTok and crypto snapshots.
- Persist the bounded read-only reconstruction in `ops/family_lane_contention_overlap_2026-09-25.md`.

**Result / test**

- Job 101 timed out at 08:45, 09:05 and 09:25 UTC in the same `refresh_family_lane_guarded()` / `refresh_family_lane()` path, after unchanged successes at 07:23, 07:43 and 08:03.
- `turnover_research_maintenance()` ran for up to about 42.9s during the resumed failure phase. Separate outcome-probe executions logged ShareLock waits of about 4.3–9.8s. Premint refresh/evidence and process-cycle work also occupied overlapping intervals.
- PASS: the observed transition continues to reject `QUERY_SHAPE_IS_SOLE_DETERMINISTIC_CAUSE`.
- SUPPORT, NOT PROOF: independent lock waits and longer maintenance runtimes make shared workload/contention a stronger explanation. No direct family-lane lock record establishes a single blocker.
- Long GitHub source workflows overlap both successes and failures, so workflow overlap alone fails as a causal discriminator.
- Adapter run 36097104891 published 40 items/32 actors at 09:09 UTC. Propagation run 36095967968 published 91 items/71 actors at 09:29 UTC. TikTok run 36098133354 completed 24 cycles with two hashtags/zero videos; direct API code `40101` persisted. Some Reddit RSS feeds intermittently returned HTTP 429.
- Crypto run 36101180099 remains the latest and coverage-ineligible; its cursor ended 2026-09-23 21:30:47.437 UTC. Zero exact-object output remains `DATA_GAP`.
- Current capacity was intentionally not probed. Last verified size remains 412,036,243 bytes at 08:19 UTC.
- PASS: no production, cron, schema, threshold, routing, freeze, cohort or financial mutation.
- Report commit: `29eec43a9eabed0f7ada8995e3b99723d67b6904`; production-state commit: `93c4d177a430bb252d38a1f61e22e6f85e7eb95d`; next-action commit: `eedb69819abf3fd6dc25983600e9752d69a82216`.

**Decision**

`PERIODIC_FAMILY_LANE_FAILURE_RECURRED / SHARED_CONTENTION_SUPPORTED_NOT_PROVEN / SOURCE_WINDOWS_COMPLETE_PARTIAL_ACCESS / CRYPTO_DATA_GAP / NO_PRODUCTION_CHANGE`. No pilot, verified creator-fee receipt or revenue milestone.


### 2026-09-25 10:27 UTC — row-lock discriminator falsification and schedule-health audit

**Hypothesis**

The repeated outcome-probe ShareLock waits may distinguish family-lane failure periods from success periods. Separately, a declared 15-minute crypto schedule should create new runs if effective Actions scheduling capacity is healthy.

**Method**

- Read Supabase project status and the independent 09:25–10:27 UTC log plane first.
- Because another family-lane timeout appeared inside the active incident window, execute zero PostgreSQL SQL, cohort query, EXPLAIN or rerun.
- Compare job-101 start/completion events against existing lock-wait records without querying production tables.
- Inspect the current workflow schedule, the latest 30 Actions runs, MDRTF job steps and immutable crypto/discovery snapshots.

**Result / test**

- Family lane failed at 09:45 UTC after its 09:43 start, then completed unchanged at 10:03:08 and 10:23:08 UTC in ~8.6s and ~7.9s.
- Outcome-probe ShareLock waits continued at 09:50, 09:56, 10:02, 10:14, 10:20 and 10:26 UTC. Retention also logged a lock wait at 10:07.
- FAIL: `OUTCOME_PROBE_HTTP_ROW_LOCK_WAIT_IS_SUFFICIENT_DISCRIMINATOR`. A 10:03 success immediately followed the same wait signature. Broader contention remains possible, but this marker alone is non-predictive.
- The crypto workflow still declares `7,22,37,52 * * * *`; nevertheless, run 36101180099 at 06:03 UTC remained the newest through 10:27 UTC. Its snapshot remained stale and `caught_up_near_live=false`.
- No Actions run of any family was created after 06:03 UTC. MDRTF run 36092388913 remained in progress at `Collect 208 prospective cuts`. This is an effective scheduling/freshness failure, not proof that MDRTF is the sole cause.
- PASS: zero PostgreSQL SQL under the incident gate; no production, workflow, cron, schema, threshold, freeze, cohort, alert or financial mutation.
- Overlap-report commit: `eebd0a1dc9b67574b2a1f4edd8f1c5b7aafa3044`; production-state commit: `1da47b68ce0028eb102df23c1ac8e6dcfbef59c8`; next-action commit: `e42b1de138e883571dc1bd9107a8cd2103f57534`; observed run IDs: `36101180099`, `36092388913`.

**Decision**

`FAMILY_LANE_INTERMITTENT_FAILURE / HTTP_ROW_LOCK_MARKER_REJECTED / CRYPTO_SCHEDULE_GAP_GT_4H / DATA_GAP / NO_PRODUCTION_CHANGE`. No pilot, verified creator-fee receipt or revenue milestone.



### 2026-09-25 11:19 UTC — multi-family incident and MDRTF live-transport audit

**Hypothesis**

The renewed failures may remain localized to family lane, and MDRTF's prospective cadence should remain operational if its runtime dependency set covers the live Pump transport. A healthy 15-minute schedule should also continue creating crypto runs.

**Method**

- Read Supabase project status and the independent 10:30–11:19 UTC log plane before any database access.
- Aggregate startup, SQLSTATE `57014` and connection errors by job family and time.
- Because multiple active timeout families were present, execute zero PostgreSQL SQL, EXPLAIN, table count, cohort query or job rerun.
- Inspect GitHub Actions run creation, MDRTF job steps/logs, the versioned workflow dependency installation, the latest immutable source snapshots and run artifacts.
- Preserve all freezes and distinguish automatic production activity from this Work session's read-only inspection.

**Result / test**

- FAIL: localized-family-lane hypothesis. The window contained 148 startup timeouts, 48 statement timeouts and 34 connection failures through 11:18 UTC, spanning source queueing, processing, fast-freeze, discovery, crypto/auxiliary/control crossover, premint, outcome, maintenance, compactor, retention and family lane.
- Job 101 succeeded at 10:23 UTC and then received startup timeouts at 10:44 and 11:03; its behavior sits inside the broader incident.
- FAIL: Actions schedule-health gate. No Actions run was created after crypto run 36101180099 at 06:03 UTC through 11:19 UTC despite the declared four-per-hour crypto schedule.
- FAIL: MDRTF operational-cadence gate. Run 36092388913 ended near its configured 355-minute boundary with `Collect 208 prospective cuts` cancelled, runtime health failed, and repeated `coverage_complete=false` / `COVERAGE_INSUFFICIENT` cuts.
- VERIFIED DEFECT: every live Pump-stream attempt failed with `ImportError: Could not import aiohttp transport`. The workflow installs `nats-py==2.11.0` but not `aiohttp`; existing tests do not exercise the live transport initialization.
- Capacity note: run 36092388913 uploaded a 565,638,843-byte `mdrtf-state` artifact with seven-day retention. A causal link to schedule starvation is not proven.
- Crypto cursor 2026-09-23 21:30:47.437 UTC was about 37h48m stale at 11:19 UTC and `caught_up_near_live=false`. Discovery's latest snapshot was 09:09 UTC; TikTok remained zero-video. All absent exact-object and prospective observations remain `DATA_GAP`.
- PASS: zero PostgreSQL SQL under the incident rule; no production, workflow, cron, schema, compactor, threshold, routing, freeze, cohort, alert or financial mutation.
- Incident report commit: `9fdd8c010e92d572fe53f1d58c683b4e902b1568`; production-state commit: `2ce4ef82286f4ecde4a141b92862c1509b6e4a7c`; next-action commit: `d57bdb89f4ebb4f7b84282fe43212d149ceba8f0`; observed runs: `36101180099`, `36092388913`.

**Decision**

`CRITICAL_MULTI_FAMILY_DB_INCIDENT / ACTIONS_SCHEDULER_GAP / MDRTF_OPERATIONAL_CADENCE_FAIL / AIOHTTP_RUNTIME_DEFECT_VERIFIED / DATA_GAP / NO_PRODUCTION_CHANGE`. The selected next development is the isolated, fail-before/pass-after aiohttp transport smoke gate, deferred until database and Actions scheduling recovery. No pilot, verified creator-fee receipt or revenue milestone.



### 2026-09-25 12:37 UTC — incident continuation and partial crypto-recovery audit

**Hypothesis**

Natural Actions scheduling recovery may restore reliable crypto coverage, while the earlier broad database event may have subsided after 11:19 UTC.

**Method**

- Read Supabase project status and the independent 11:19–12:37 UTC log plane before database access.
- Aggregate SQLSTATE `57014` and connection/protocol failures by application and pg_cron query family.
- Because multi-family errors remained active, execute zero PostgreSQL SQL, EXPLAIN, capacity query, cohort/freeze scan or rerun.
- Inspect new Actions creation, crypto run 36130856236 job logs and its immutable published snapshot; inspect MDRTF run 36129078052 state.
- Manually classify every exact outbound URL in the new crypto snapshot against the pre-mint requirement.

**Result / test**

- FAIL: database recovery. The window contained 107 `57014` events and 61 connection/protocol errors, with errors continuing through 12:35 UTC.
- The 95 identifiable pg_cron timeouts spanned discovery adapter bus 26, process cycle 26, premint TikTok/discovery 23, crypto crossover 6, premint refresh/evidence 4, turnover maintenance 3, family lane 3, outcome probe 2, control freeze 1 and forensic maintenance 1.
- PASS: Actions run creation resumed naturally. MDRTF run 36129078052 began at 11:23 UTC; crypto run 36130856236 began at 11:42 UTC and completed successfully.
- PARTIAL ONLY: crypto processed 41,894 Jetstream messages, published 47 items and reached near-live, but declared `PARTIAL_OR_BASELINE_UNKNOWN` / `LOW_UNVERIFIED_CRYPTO_KEYWORD_ONLY`. Reddit remained approval-gated, Bluesky search remained disabled after 403, and the run began from `BASELINE_16M_UNKNOWN_PREHISTORY`.
- MANUAL REJECTION: the snapshot's only exact outbound URL was in an 11:40:04 UTC Bluesky post linking retrospective Pons fee commentary. It is not a new external object independently observed before token mint and is not a crossover candidate.
- HOLD: MDRTF dependency repair. Run 36129078052 is already executing with the unchanged dependency set while the database incident is active.
- PASS: no production, workflow, cron, schema, compactor, threshold, routing, freeze, cohort, alert or financial mutation.
- Incident report commit: `7e58ba9dede42daef6b691d1a66384f7700cf1df`; production-state commit: `5de669f9abebdc678e6ea7f26abb8f81cdbc331c`; next-action commit: `16b83ce92e878f4758ed925f4d0f71ee64448cb9`; observed runs: `36130856236`, `36129078052`.

**Decision**

`DB_INCIDENT_ACTIVE / ACTIONS_SCHEDULER_RECOVERED / CRYPTO_NEAR_LIVE_PARTIAL_BASELINE_UNKNOWN / NO_PREMINT_EXACT_OBJECT / MDRTF_DEFECT_REPAIR_DEFERRED / DATA_GAP / NO_PRODUCTION_CHANGE`. No pilot, verified creator-fee receipt or revenue milestone.
