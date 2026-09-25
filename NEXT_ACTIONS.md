# FEE100K next actions

## Highest-value next step — recover measured coverage safely

1. Recheck the last 5–10 minutes of cron statuses and the latest GitHub schedule event. Capture exact timestamps, job duration, `pg_stat_activity`, wait events and slow query plans. Audit free plan compute and database storage headroom. Do not infer a schedule is working from push-triggered success.
2. In a read-only or shadow session, EXPLAIN the three identified expensive operations: 12-hour token upsert, snapshot global rank/delete, old cron history cleanup. Propose bounded incremental updates or indexed retention with a migration and rollback plan. Test against a small real slice and preserve first-freeze and evidence rows. Only then alter production, one intervention at a time; confirm job success and observation freshness afterward.
3. Determine why the crypto workflow generated no scheduled snapshot after 17:03 UTC. GitHub Actions schedules are best effort; inspect workflow enablement/queue and the long MDRTF job. Do not mislabel stale snapshots as live. A missed-run monitor should publish `COVERAGE_UNKNOWN`, never a false zero.
4. Reddit: use the official approval route if eligible, with purpose and proposed commercial use disclosed; no anonymous hosted-runner retry. Keep it excluded from measured coverage pending permission. Maintain lawful alternative public crypto-native sources with exact-object URLs and timestamped provenance.
5. Continue the exact frozen 20 IDs and distinct exploratory 20 under their original protocols. Audit exact-object URL normalization against the source objects, and manually adjudicate the first apparent cross-surface match for independent actor, source, observation-before-mint timing and absence of self/related promotion. Keep weak semantic hints separate.
6. At 24h and 7d, record mature outcomes and matching source coverage per object. Treat undocumented tokenization as UNKNOWN. Only prepare a rights-safe pilot when full original Demand-Proof, semantic vacancy, independent pre-mint crossover, distribution and exact fee-owner route all pass.

Current decision: FIX. No `P($100K)` estimate, pilot-ready finding or verified revenue. The next user approval is needed only for a specific live mint, transaction, funds or paid service after a reviewable pilot package exists.

## 2026-09-23 19:40 UTC — narrowed immediate action

Priority 1: Restore trustworthy observation freshness, not candidate volume. The crypto workflow declares `7,22,37,52 * * * *`, but no scheduled run has appeared since the 17:03 push run. Inspect workflow scheduling/queue independently of database load; test with one bounded, non-financial, shadow/dispatch run only after confirming free capacity and no overlapping long job. Validate a newly timestamped snapshot and bridge 200 before treating crossover counts as measured negatives. Do not backfill missed Jetstream observations as if seen live.

Priority 2: Isolate database pressure without repeated heavy probes. Capture a narrow per-job failure summary and single-function plans when connections stabilize. Compare schedule collision times with active long queries. Prepare a bounded incremental maintenance proposal and rollback; first test a small actual slice in read-only/shadow, then verify cron success and freshness before any production job or schema change. Repeated full-scan counts timed out/consumed ~50s and should not be retried unchanged.

Priority 3: Once coverage recovers, evaluate the same 20 primary IDs against their ten matched controls and the separate 20 exploration IDs. At the first apparent exact-object match, manually verify original source URL, independent crypto actor/community, post publication and observation times before mint, and semantic vacancy. Absence under current gaps is UNKNOWN.

Security footnote: `fee100k_private` has disabled RLS warnings, but anon/auth schema USAGE is false. Review Data API exposure and table privileges before any RLS migration; preserve bridge compatibility. No automatic security migration based solely on the advisory.

## 2026-09-23 19:45 UTC — incident-aware next step

1. On the next session, inspect independent PostgreSQL logs first. If multiple 57014/connection timeouts continue, make at most one bounded SQL probe and stop on timeout; do not repeat full scans or stack another workload. Establish whether the incident has cleared before code or cron intervention.
2. When stable, compare individual job duration and wait events with schedule collisions. Prioritize a single small shadow rewrite of snapshot pruning or 12-hour token refresh, with unchanged evidence retention and explicit rollback. Test on real bounded data, then measure job latency and source freshness before any production rollout.
3. Independently verify a fresh scheduled crypto workflow snapshot and bridge response; a past push success does not close the data gap. Resume frozen 20-vs-control evaluation only in periods with timestamped source coverage. Keep separate exploration cohort and no inferred fee income.
4. The hourly automation now uses log-first fail-fast during database incidents and checks overlap with the four-hour development task. This is a task-prompt change, not a repair to production services.

### Snapshot correction

GitHub source publication resumed at 19:42:30 UTC, so investigate why the 95-second/80,000-message Jetstream replay still did not catch up and why its eight published items contain zero exact external-object URLs. First verify the 19:42 snapshot's bridge request status using a single small SQL probe only after connection health recovers, or independent non-Postgres logs if available. Keep coverage PARTIAL/UNKNOWN until cursor lag, source completeness and bridge ingestion are measured. Do not retry Reddit/AppView access controls.

Jetstream replay is the immediate highest-information bottleneck: end cursor is 17:29:52 UTC at 19:42:30 generation, ~2h12m37s lag despite 80,000 messages/95s. Inspect collector's cursor checkpoint, run frequency and per-run budget in source; model whether the current allowed throughput can ever catch up with incoming events. Test a bounded source-only change in shadow with no retroactive `first_observed_at` rewrite. Do not interpret snapshot generated time as post freshness.

Source inspection: `crypto_native_crossover/collect_v1.py` calls `capture_events(seconds=95,max_messages=80000)`; `jetstream_replay_v1.py` stops on either bound and marks `caught_up_near_live` only near the current clock. The 19:42 run hit 80,000 messages while advancing the cursor only 26m32s (17:03:20→17:29:52). This is consistent with backlog and intermittent scheduling; neither a permanent throughput deficit nor a Jetstream bug has yet been proven. Measure the next two actual scheduled runs and their cursor delta versus elapsed wall time before increasing budgets or cadence. A source-only shadow throughput test should preserve old cursor, no retroactive freeze and free-tier limits.

## 2026-09-23 — complementary live-tail shadow experiment

New hypothesis: backlog replay and current-time observation should be separated while cursor catch-up is impaired. Jetstream's upstream README says an absent cursor starts at the live tail. In a **separate shadow run**, connect without a cursor for a short bounded window and record event-time vs first-observed-time lag, message count, independently relevant crypto posts with exact object links, and network/runtime cost. Preserve the existing replay cursor, snapshot branch, immutable freezes and source-health label. Never stitch skipped history into the 20-case cohort or report full coverage from a live-tail sample. Negative control: compare source timestamp lag and duplicate IDs to the unchanged replay on the same wall-clock window; reject if live tail still has material lag or no usable exact-object data. Do not change production collector/schedule until two prospective shadow samples meet freshness and capacity bounds and integration tests pass. If they do, propose a dual-lane source schema: REPLAY_PARTIAL (history) and LIVE_TAIL_BOUNDED (new observation), with explicit gap intervals; avoid a misleading global COVERED status. This is a design/test proposal, not a deployed fix or a financial signal.

## Evidence quality gate — 2026-09-23

Do not use withdrawn Kamat v1.3 graduation/social-link figures in expected-fee projections. Audit each external study's label construction, temporal validation and creator-fee relevance before promoting its feature weight. The current 20-case trial is a measurement feasibility probe, not a statistical validation of Y100. At its seven-day checkpoint, decide whether coverage/independent crossover is measurable; if not, stop infrastructure expansion and seek a different lawful data/attention-transfer route rather than polishing the same proxy.

## 2026-09-23 — parallel economic mechanism audit (no-money)

Do not wait solely for the first 20 outcomes. Run a separate **historical mechanism discovery** lane, explicitly excluded from prospective calibration. Fail-fast first: verify free on-chain access to launch time, canonical trades, creator-vault/fee-sharing recipient, actual fee collection or accrued vault and event-level attribution on a tiny 2+2 sample. Pump's current official fee schedule is 0.30% creator fee on bonding curve, market-cap-tiered canonical PumpSwap rates, and 0% creator fee on non-canonical pools; vault accrual and recipient receipt must be separately recorded. Do not model total platform fee as creator revenue or treat an unclaimed vault as user wallet receipts.

If access is valid, freeze a **time-window denominator** of launches across several non-overlapping periods, then select high-fee outcomes and same-window/source matched low/zero-fee controls without making one winner the prototype. Blindly reconstruct only information publicly observable before each token mint: specific external object's birth, independent transformed spread, pre-mint crypto-native references, prior competing token/leader, and creator's genuine distribution route. Classify both successes and false-positive near-misses. Test whether the attention-first path actually recurs among high-fee launches, versus direct creator audience/insider/self-generated flow. Historical findings generate hypotheses only; do not tune the frozen 20 or claim prospective lift. If high-fee cases mostly require unavailable audience/collusion or pre-mint evidence cannot be reconstructed, downgrade AFT as primary and seek a different lawful creator-value capture route.

The next economic milestone is a small **verified fee-receipt pilot** with real third-party turnover after review and explicit user authorization, not the $100K target directly. Track funnel: qualifying object -> independent crypto crossover -> original packaging/distribution -> canonical third-party volume -> actual creator vault -> net receipt. For each transition record denominator, conversion, latency, and failure cause. Do not mint to generate experiment data while core demand gates or fee-route verification fail.

## 2026-09-23 — user-supplied launch-operator wallet lead

Prioritize the read-only forensic access gate in `premint_discovery/WALLET_CASE_2392B8_2026-09-23.md` alongside the four-mint creator-fee access probe. The social $2–2.5m claim and adjacent rug description are not verified. First establish whether gains (if any) were creator-fee receipts, inventory sales, or transfers; only the first is directly relevant to FEE100K. If this case is predominantly dev selling/rug, use it as an adversarial negative mechanism and compare a genuinely fee-driven wallet instead of copying it. No funds, token, or public promotion action follows from this case.

## 2026-09-23 20:52 UTC — first live-tail shadow observation

Read-only isolated [GitHub run 35918786819](https://github.com/arascxe/h40-graac-canary/actions/runs/35918786819) connected to the official public Jetstream legacy subscribe endpoint without a cursor for 20 seconds. It observed 1,232 post messages, two crypto keyword posts, zero crypto posts with an exact external-object URL, median provider-to-observer lag ~0.01 seconds, maximum ~0.12 seconds, no transport errors. Only aggregate metrics were logged; no author data, raw posts, production state or prior replay cursor was changed. Official upstream documents no cursor as live-tail operation: https://github.com/bluesky-social/jetstream-legacy

Interpretation: a low-lag source lane is technically reachable. This sample is too short and its zero exact-object links cannot establish the frequency of usable candidates, independent demand or selector lift. Repeat a separate prospective 20–60s shadow slice to test reliability and usable URL rate, then only if it holds implement a separate explicitly partial live-tail lane alongside replay with gap intervals; never rewrite missed first-observed timestamps. Before any real mint, verify source-to-bridge freshness and creator fee-owner/claim route. This narrows the prior freshness blocker, not the economic bottleneck.

## 2026-09-23 21:03 UTC — second live-tail observation and source decision

A second isolated [60-second run](https://github.com/arascxe/h40-graac-canary/actions/runs/35919837843) observed 2,914 Bluesky posts, one crypto-keyword post, zero exact outbound external-object links, median source lag ~0.02 seconds, maximum ~0.07 seconds, no errors. Together with the first 20-second run (1,232 posts, two crypto-keyword posts, zero exact links), this establishes technical live freshness in two windows, **not useful independent crossover yield**. Do not move this keyword lane into production merely for low latency; it cannot repair the core candidate evidence with these observations. Broaden the source/method family: test creator-led original internet objects and legitimate organic utility/community distribution against AFT external-object tokenization. First audit the pre-mint origins of the two upper fee-proxy cases and same-age controls. Continue mint-specific fee event access, because actual creator wallet claims now exist in one upper creator but vault attribution remains unresolved. Keep all prospective frozen thresholds unchanged.

## 2026-09-23 21:56 UTC — single immediate safe engineering decision

Prioritize the proven adapter-bus interruption mechanism before adding another source or increasing cadence: in a shadow workflow/static check, narrow the `premint_discovery/**` push trigger so research-note edits do not cancel a 4-hour collector. Preserve schedule, manual dispatch, true collector-code push testing, snapshot schema and `cancel-in-progress` semantics for actual code changes. Before a production workflow edit, verify current run duration, GitHub free-minute headroom and interaction with the four-hour development task; require a test showing documentation-only edits no longer trigger the bus and code edits still do. Roll back by restoring the previous workflow file if freshness or scheduling worsens. Do not change it merely on this audit.

Separately, keep the crypto-crossover lane `DATA_GAP`: latest snapshot 19:42:30 UTC, Jetstream cursor 17:29:52 UTC, no newer run visible by 21:56. Determine schedule delay/enablement without backdating observations or rerunning a long collector against impaired capacity. On Supabase, one family-lane 57014 remains in the last hour; monitor independent logs before any heavier SQL or intervention. Primary frozen 20 and exploratory 20 stay separate; 24h outcomes are not due yet. No user launch action is justified.

## 2026-09-23 22:22 UTC — frozen same-window creator-fee mechanism check

Read `fee_audit/SAME_WINDOW_SHADOW_2026-09-23.md` before another high/low comparison. A clean, bounded GitHub runner could download the earlier 564MB MDRTF artifact but SQLite reported `database disk image is malformed`; do not rely on that artifact. Independent Pump first-party [run 35927052834](https://github.com/arascxe/h40-graac-canary/actions/runs/35927052834) froze 210 new launches over ~7.5 minutes (artifact retained seven days). A mint-sorted 12-case early-trade sample matured in [run 35927416350](https://github.com/arascxe/h40-graac-canary/actions/runs/35927416350): 11 complete first pages, one truncated/UNKNOWN. Four contrasting cases in [run 35927736130](https://github.com/arascxe/h40-graac-canary/actions/runs/35927736130) show Grand Theft Clout $9,362.47 first-5m gross with $6,660.88 from its direct creator address (71.14%); NOTHING $2,092.72 with only $8.81 direct creator-address gross; 164 Bucky zero early trades. This is a mechanism clue, not independent people, 24h turnover or fee receipt. At/after 2026-09-24 22:13 UTC, follow the same frozen 210 IDs for 24h outcomes and UNKNOWN coverage, then select same-age high/low pairs, inspect timestamped pre-mint distribution and mint-specific fee flow. Prioritize diagnosis of malformed large artifact separately, without touching production collector state. No launch or capital decision follows from the early sample.

## 2026-09-23 22:40 UTC — income decision takes priority

Read [the current no-go decision](fee_audit/INCOME_DECISION_2026-09-23.md). Do not expand generic source or trader-dashboard infrastructure in the next work session. At/after 2026-09-24 22:13 UTC, follow the exact frozen 210 mints for same-window 24h outcomes and unknown coverage, compare high cases to low controls, attribute independent creator-excluded turnover and exact fee recipient/claims. If no solo no-audience acquisition mechanism survives, report UNSUPPORTED_FOR_THIS_OPERATING_SETUP and switch the next first-dollar study away from creator-fee launching. No live mint, public promotion or capital action without a reviewable candidate and user approval.


## 2026-09-23 22:41 UTC — capacity gate before any new source run

Do **not** launch another shadow or rerun yet. GitHub metadata showed three long workflows still `in_progress` (pre-mint adapter bus run 35924345727 since 21:45, TikTok adapter 35911657263 since 19:47, public propagation bridge 35910703156 since 19:38) and MDRTF run 35921125436 still `pending` since 21:13. Between 19:42 and 22:27 the 15-minute crypto schedule produced only two visible runs, while its replay cursor fell from ~2h12m to 4h32m behind. This establishes insufficient **effective** scheduling capacity/freshness, although the exact GitHub queue cause is not proven.

The single highest-value safe engineering candidate remains narrowing pre-mint adapter-bus push paths so research-note commits cannot cancel and restart its four-hour collector. Before a production edit, require a static trigger test and wait for the current bus/pending MDRTF state to clear. Acceptance: documentation-only changes do not trigger; collector code/config changes still do; schedule, dispatch, snapshot schema and data branch remain identical. Rollback is restoration of the prior workflow file.

Do not add cadence or another live-tail sample until capacity clears. Economic priority remains the frozen 210 follow-up at/after 2026-09-24 22:13 UTC and the current no-go decision. Database rule remains log-first: family-lane 57014 repeated at 21:45 and 22:05; during continued multi-timeout pressure allow at most one small read-only SQL probe and no EXPLAIN/full count/rerun.


## 2026-09-23 — fixed 210-launch distribution checkpoint

The first-party 210-mint baseline is frozen in GitHub Actions run 35927052834. Twelve mint-sorted cases had mature first-five-minute trade observations in run 35927416350. The same twelve were checked against Pump's `/coins-v2/{mint}` metadata at approximately 22:52 UTC; the exact field snapshot and comparison are in `fee_audit/premint_distribution_12_metadata_2026-09-23.json` and `fee_audit/PREMINT_DISTRIBUTION_12_CASES_2026-09-23.md`. There are zero **verified** independent pre-mint attention-to-buyer transitions in that small sample; this is not evidence none exist. One high-volume case was creator-address dominated, one linked X post followed mint by ~0.5s, and one pre-mint linked X post had zero observed early trades. Do not admit social-link presence as demand proof.

At or after 2026-09-24 22:13 UTC (2026-09-25 01:13 Türkiye), read the same 210 frozen mints' 24-hour outcomes with explicit source completeness and match high/low outcome cases. Separately reconstruct timestamped pre-mint independent distribution and mint-specific creator fee receipts; 24-hour volume alone cannot identify buyer origin or user income. Do not retune inclusion or treat unavailable social posts as no demand. If no independent distribution mechanism survives, report `NO_VALIDATED_ROUTE` and reassess the creator-fee hypothesis rather than launch on gross-volume proxies.


## 2026-09-23 — bounded $100K route decision, immediate next job

Do not spend the next research cycle adding a general score or another broad collector. Close the existing `ACCESS_PARTIAL` economic gate in `premint_discovery/CREATOR_FEE_ACCESS_PROBE_2026-09-23.md`: in one bounded read-only 2+2 probe, trace a canonical trade-to-creator-vault event and exact recipient/sharing state for the three remaining frozen mints (GTBx, 7WRX, ACtf), alongside the already verified BP4W positive. Keep mint-specific accrual separate from aggregate creator claims; record exact signatures and source gaps. Declare `ACCESS_PASS` only if event-level attribution is reliable in both high and low examples, otherwise `ACCESS_FAIL` for this source within the pre-registered ~24-hour access timebox. Do not repeat failed endpoints or infer income from 24h volume.

If access passes, use the frozen 210-mint baseline and, at or after 2026-09-24 22:13 UTC, select high/low 24h outcomes with explicit missingness. For a small matched contrast, reconstruct independent public pre-mint attention, actual distribution, unrelated first buyers, and creator fee flow. The business decision gate is whether a solo no-audience, no-paid-distribution creator can reproduce an observed path. A single outlier, linked social field, creator self-volume, or claim from multiple coins does not pass. Within seven days, either produce a reviewable low-cost pilot with original rights-safe object, pre-mint third-party crypto crossover, vacancy, exact fee recipient, and a credible first $100 receipt hypothesis, or label `NO_VALIDATED_ROUTE` for the urgent $100K fee objective and stop expanding its infrastructure. No automatic mint, promotion or funds.

## Checkpoint 2026-09-23 23:47 UTC — next highest-value action

1. Do not add another collector or increase cadence. Verify run [35935251897](https://github.com/arascxe/h40-graac-canary/actions/runs/35935251897) publishes a valid first cycle, then verify the next genuine four-hour schedule starts without an intervening research-note restart. If it fails, inspect that job once; do not rerun blindly.
2. Keep the crypto exact-object lane classified `DATA_GAP`: the latest published snapshot is 22:28 UTC but its source cursor ends 17:55 UTC. Zero exact matches is not a negative result.
3. Preserve the canonical 20, its matched controls, the distinct exploratory 20 and the frozen 210-launch cohort. The 210-launch 24-hour outcome gate cannot be evaluated before 2026-09-24 22:13 UTC; do not duplicate it hourly.
4. After current long Actions jobs clear, complete the remaining three preselected mint-specific creator-vault/recipient/claim access checks. Do not open a broad historical study until the 2+2 access gate is closed.
5. No capital action is licensed. A real pilot still requires a manually verified independent pre-mint exact-object crossover, family vacancy, canonical fee route and explicit user approval.

### 23:48 UTC follow-up refinement

First-cycle publication for 35935251897 passed. Do not rerun it. The remaining operational proof is passive: confirm that research-note commits no longer create adapter-bus runs and that the next genuine schedule proceeds without cancellation. Continue prioritizing the separate stale crypto cursor and the remaining three fee-access cases only after long jobs clear.
## Checkpoint 2026-09-24 02:55 UTC — capacity incident takes precedence

1. Treat database capacity as the immediate engineering blocker: 433,630,355 bytes is ~86.7% of the current 500 MB Free allowance. Do not add ingestion, tables, cadence or broad scans.
2. Before deleting anything, identify every cron/function that reads `net._http_response`, verify its existing six-hour boundary, and calculate a dry-run reclaim for a shorter horizon. Only propose a guarded retention change if completed responses are already consumed and immutable evidence is stored elsewhere. Preserve a one-migration rollback and validate bridge delivery before/after. Never purge evidence tables or first freezes to gain space.
3. Keep crypto crossover `DATA_GAP`: run 35940133028 ended 6h28m40s stale and the next declared schedules did not appear by 02:52 UTC. Do not raise the 80,000-message budget while long Actions jobs remain active. Prior two live-tail shadows were fresh but produced zero usable exact-object URLs, so do not repeat them without a different source/matching hypothesis.
4. Preserve primary 20, matched controls, separate exploratory 20 and frozen 210 launches. Do not evaluate the 210 cohort before 2026-09-24 22:13 UTC or re-run it hourly.
5. Capital action remains unlicensed. Verified user-wallet creator-fee receipts remain zero; the remaining three 2+2 fee-access cases wait until capacity is safe.
### 2026-09-24 03:19 UTC — compaction safety gate

Do not manually call or lower the threshold of `compact_ephemeral_storage()` yet. It is already scheduled every ten minutes at 460 MiB, but preserves only unprocessed `fee100k_http_request_v1` responses and rebuilds the turnover feature table under an exclusive truncate path. First inventory response IDs still needed by every active cron family, including non-FEE100K legacy consumers; close only demonstrably stale FEE100K requests through their existing typed closer; and dry-run the exact expanded keep rule. Acceptance for a threshold change: zero at-risk response IDs, post-compaction database estimate below 75%, bounded lock/rebuild time under current load, unchanged bridge/crossover counts, and a one-migration threshold rollback. Do not touch immutable evidence or frozen cohorts.
### 2026-09-24 04:25 UTC — unchanged safety decision

Keep new ingestion and broad SQL frozen while database use is ~87.9%. Do not manually run the existing compactor: its irreversible response deletion is not yet safe for all active consumers. Continue the active-consumer census and prepare, but do not deploy, an expanded keep rule plus earlier threshold. Treat family-lane failures as intermittent and isolate their query plan only after capacity is safe. Do not repeat the frozen cohort analysis before its scheduled maturity gate.

### 2026-09-24 05:41 UTC — replay divergence gate

Do not treat scheduled crypto run 35960321559 as coverage recovery: it published 10h43m49s behind live time and added only 27m06s of cursor progress in roughly 4h42m. Keep exact-object crossover at `DATA_GAP`; do not repeat the same full keyword replay, raise its message budget, or count its zero links as a prospective negative while four long Actions jobs overlap.

The single next safe development candidate is an offline/static guard that makes any `caught_up_near_live=false` snapshot ineligible to emit or update negative exact-match conclusions, while preserving the snapshot, cursor and gap interval for audit. Validate it against the two existing stale snapshots and a synthetic near-live control before proposing a workflow change. It must not alter first freezes, cohort membership, thresholds, source collection, alerts or production cadence; rollback is a one-commit revert.

Capacity remains the prerequisite. Resume the response-consumer census only after the long jobs clear and logs no longer show repeated family-lane timeout pressure. Correct the read-only checkpoint query from repository schema definitions before the next probe; do not discover identifiers by broad catalog scans under current load. The 210-launch 24-hour gate remains 2026-09-24 22:13 UTC; do not re-run it earlier. No capital action is licensed.

### 2026-09-24 06:20 UTC — active incident gate

Treat the three consecutive family-lane timeouts and 89.2% database use as an active capacity incident. Add no ingestion, replay budget, cadence, table, broad query or cohort refresh. Do not manually invoke the compactor or lower its threshold while legacy response consumers remain unmapped.

Do not pause job 101 solely from its failures: the repository does not contain a sufficient versioned definition/dependency map to prove that a pause is backward-compatible. The single next safe test remains a read-only ownership/consumer census after timeout pressure eases, limited to the function/job definitions and pending response IDs required to specify an expanded keep rule and a reversible pause/threshold plan. Acceptance requires zero at-risk consumer responses, bounded lock/rebuild time and unchanged evidence/bridge counts.

Continue passive GitHub/source observation only. Crypto exact-match zero remains `DATA_GAP`; discovery freshness does not substitute for it. Preserve all frozen cohorts and wait for the 210-launch maturity gate at 22:13 UTC.

### 2026-09-24 07:50 UTC — reclaim classification gate

Family-lane has recovered for five consecutive runs, so do not pause job 101 now. Capacity remains the blocker at ~89.6%; do not interpret cron recovery as permission to add work.

Before any compactor or retention change, version the response ownership rule that separates referenced unprocessed FEE100K IDs, recent legacy/in-flight IDs and completed/unreferenced candidates. Dry-run only after the keep rule covers `WATCHDOG_TELEGRAM`, turnover debug, SOL-price and the four identified legacy processors. Require a post-reclaim estimate below 75%, bounded lock/rebuild time, unchanged bridge/evidence counts and a tested threshold rollback. Do not delete first freezes or durable evidence.

Do not repeat primary-20, exploratory-20, exact-match or 210-launch analysis before a new checkpoint or the 22:13 UTC maturity gate. Continue passive source observation; crypto remains `DATA_GAP` and no financial action is licensed.

### 2026-09-24 09:46 UTC — scheduler recovery gate

The modest database-size decline does not clear `CRITICAL_CAPACITY`; keep all new ingestion, compactor and retention mutations frozen. A single family-lane timeout recurred after three successes, so continue log-first observation and do not pause job 101 without the missing versioned dependency/rollback proof.

Three long Actions jobs have completed, yet the declared 15-minute crypto schedule still produced no run after 05:31 UTC. Do not manually rerun the unchanged 80,000-message replay: it is already diverging from live time. The next safe test is passive and bounded—confirm whether a genuine scheduled crypto run appears after runner capacity cleared; if it does, compare cursor progress to wall time and accept recovery only if `caught_up_near_live=true`. If it does not, inspect scheduler/run metadata once without dispatching. Preserve primary 20, controls, exploratory 20 and frozen 210; wait for the 22:13 UTC maturity gate. No capital action is licensed.

### 2026-09-24 11:07 UTC — replay method must change

Scheduled run 35987232148 closes the scheduler-liveness question but fails the catch-up gate: cursor lag grew to 15h12m36s. Do not manually dispatch, increase the 80,000-message budget, or treat zero exact objects as a negative result. Freeze further full-stream replay experiments until method class changes.

The next safe engineering candidate is an offline/static eligibility guard: snapshots with `caught_up_near_live=false` must be preserved with their cursor/gap metadata but must be incapable of emitting or updating negative exact-match conclusions. Test only against the existing stale snapshots plus a synthetic near-live control; avoid a production-code push while database pressure remains ~88.5% and family-lane timeouts are intermittent. Preserve all frozen cohorts and wait for the 22:13 UTC 210-launch maturity gate. No capital action is licensed.

### 2026-09-24 11:17 UTC — guard verified; integration remains deferred

The fail-closed coverage guard now exists and its self-test passed independently. Keep it shadow-only: do not wire it into scheduled collection, alerts or database writes while storage remains near 88.5%, family-lane timeouts are intermittent and the replay cursor is diverging. The next checkpoint is passive health observation or the frozen 210-launch maturity gate at 22:13 UTC, whichever supplies new evidence first. Do not repeat existing snapshot/cohort counts and do not treat guard PASS as economic validation.


### 2026-09-24 13:58 UTC — hard capacity hold above 90%

Database use has crossed 90% while family-lane produced three consecutive timeouts before recovering. Treat this as an active capacity incident: do not add ingestion, integrate the coverage guard, increase replay budget, dispatch missed jobs, lower the compactor threshold or run broad/cohort SQL. The current compactor remains unsafe to accelerate until every legacy/in-flight response owner is covered by a versioned keep rule and rollback.

Continue log-first passive observation. A later technical success does not clear the incident unless storage falls materially and timeout recurrence stops. Crypto-native zero remains `DATA_GAP` with an approximately 18h44m gap; discovery freshness does not substitute for exact-object coverage. Preserve primary 20, controls, exploratory 20 and frozen 210, and wait for the pre-registered 22:13 UTC maturity gate. No capital action is licensed.


### 2026-09-24 15:25 UTC — publication incident follow-up

Keep the >90% capacity hold and the response-owner safety gate from the 15:14 census. The TikTok failure in run 36007889742 is diagnosed as GitHub HTTP 500 on publishing cycle six after successful collection; inspect the next natural scheduled publication and branch timestamp before considering a bounded retry mechanism. Do not blindly rerun the failed four-hour job, treat the two hashtags as demand, or count its zero videos as absence. Discovery is independently fresh, while the crypto-native cursor remains >20 hours stale; keep exact-object zero `DATA_GAP` and do not increase replay load. Preserve all freezes and defer the frozen 210 24-hour analysis until 22:13 UTC. No financial action is licensed.


### 2026-09-24 16:28 UTC — stop unchanged replay class

Run 36020296375 confirms that the unchanged 80,000-message full replay cannot catch live time: it gained 26m50s while 5h00m48s elapsed and published 19h46m34s behind. Do not manually rerun it, raise its message budget or use its zero exact objects as a negative. The next crypto work must change method class and first prove, in a bounded shadow, that cursor progress exceeds elapsed wall time or starts from a lawful near-live feed; until then retain `DATA_GAP`.

Keep the >90% capacity hold. Do not integrate collectors, lower compactor thresholds or delete completed responses until the versioned keep rule resolves all unowned/legacy response consumers and demonstrates rollback plus a post-reclaim estimate below 75%. Continue passive observation of the next natural TikTok publication after the GitHub 500. Preserve all cohorts and wait for the frozen 210 maturity gate at 22:13 UTC. No capital action is licensed.


### 2026-09-24 18:03 UTC — active multi-family incident hold

Switch to log-only observation while startup timeouts, 57014s or connection resets remain active. Do not run more database probes in the current incident window, dispatch jobs, integrate the crypto guard, add collection, lower the compactor threshold, delete responses or evaluate cohort absence. Mark source queue, processing, freeze, outcome, discovery, exact crossover and exploration outputs from the affected interval as `DATA_GAP`.

After pressure clearly subsides, the next safe test is an offline/versioned overlap analysis using the captured cron definitions and incident timestamps. It must identify the smallest noncritical derived-work family whose cadence could be reduced or paused with explicit dependency mapping, backward compatibility and one-change rollback. Do not change production until that proof exists. The frozen 210 maturity gate remains 22:13 UTC, but its analysis must also wait for healthy coverage; calendar maturity alone is insufficient. No capital action is licensed.


### 2026-09-24 19:08 UTC — recovery requires versioned load-shedding proof

Keep the log-only incident hold: startup timeouts, 57014s and connection failures were still active at 19:05 UTC. Do not query cohorts at the 22:13 maturity time merely because the clock passed; outcome validity requires healthy collection and processing coverage.

The dominant timeout families are now known, but no safe pause is authorized. Before any production change, export/version the exact live definitions and dependencies for `process_cycle`, discovery bus, crypto crossover, premint refresh, turnover maintenance/outcome probe and their cron entries. Build an offline minute-overlap table and select at most one noncritical derived-work family for a reversible cadence reduction. Acceptance requires preserved source ingestion/first freezes, no new backlog growth, materially fewer timeout/connection events over a predeclared window, and a one-command rollback. Until those conditions exist, do not pause jobs, compact, delete responses, increase replay or add collectors. No capital action is licensed.


### 2026-09-24 20:35 UTC — maintain incident hold; unchanged replay is now definitively ineligible

Keep the log-only hold until a clean observation window proves startup/statement/connection errors have stopped; the latest statement timeout was 20:05 UTC. Do not query the matured 210 cohort, run a database probe, compact storage, pause a job or modify cadence while this condition holds.

Do not dispatch or enlarge crypto run 36048283198: its 80,000-message pass moved only 27m13s and ended ~23h20m stale. Preserve the snapshot solely as coverage-gap evidence. The next crypto experiment must change method class and first demonstrate cursor progress greater than elapsed wall time or lawful near-live initialization in an offline/bounded shadow. Job 95 remains only a shadow load-shedding candidate; no production change is allowed until its exact live definition, durable inputs, synchronous consumers and one-command rollback are versioned after pressure clears. No capital action is licensed.


### 2026-09-24 21:48 UTC — capacity remains the stop gate

Do not treat the clean 73-minute log window as recovery while database use is ~92.25% and three long Actions jobs remain in progress. Add no collector, replay, cadence, schema, compaction or retention mutation. Keep the matured 210 analysis deferred until both database processing and relevant source coverage are demonstrably healthy.

Job 95's exact current schedule, command and active state are now captured at commit `0f1c4ff`, but a pause/cadence change is still forbidden. The next safe step is a narrowly scoped function/dependency export after another clean window, proving durable inputs, deterministic backfill, no synchronous freeze/alert/receipt consumers and exact restoration of the captured state. If that evidence cannot be produced without broad catalog load, remain passive. No financial action is licensed.


### 2026-09-25 00:04 UTC — reject job-95 pause; capacity recovery is provisional

Do not pause or slow job 95. Its live wrapper couples canonical outcomes, economic outcomes, probe queueing and turnover model-state refresh; repository definitions for the four children remain incomplete. A pause is not a narrow load-shed and could suppress mature economic evidence. Preserve its 59-second baseline and require full written-table/consumer/backfill closure before reconsideration.

Treat the decline to 419,335,315 bytes (~83.87%) as provisional recovery only; the cause is unproven and storage remains high. Continue passive capacity/log monitoring and do not lower compactor thresholds, delete responses or add ingestion. Do not repeat the unchanged crypto replay: run 36068795919 ended ~26h06m stale and is coverage-ineligible. Three replacement propagation/adapter/TikTok runs are in progress and MDRTF is active; wait for completed snapshots rather than interpreting starts as recovery. Primary 20, controls, exploration 20 and frozen 210 remain closed until healthy end-to-end coverage. No capital action is licensed.


### 2026-09-25 01:31 UTC — recovery claim withdrawn

Withdraw any recovery inference from the earlier quiet window: statement timeouts recurred through 01:05 UTC. Return to log-first observation and send no PostgreSQL probe while recurrence is active. Do not open the matured 210 cohort merely because its clock gate passed; relevant processing and source coverage remain unhealthy.

Do not run the unchanged crypto replay again or increase its 80,000-message budget. Run 36079643535 moved ~26m21s while the wall clock advanced more than two hours and ended ~27h53m stale. The next admissible crypto work must change method class and prove near-live initialization or cursor progress faster than wall time in a bounded offline shadow. Continue waiting for completed propagation, adapter and TikTok snapshots; starts/in-progress states are not coverage recovery. Job 95 remains unchanged and its pause remains rejected. No capital action is licensed.


### 2026-09-25 02:56 UTC — immediate capacity gate

1. Treat **478,702,739 bytes / 500,000,000 bytes (95.74%)** as a hard capacity incident. Do not add ingestion, replay, reruns, cohort scans, or new collectors.
2. Do **not** manually invoke the compactor or lower its 460 MiB threshold. The shared HTTP-response consumer set, exclusive rebuild behavior, and deterministic rollback remain unproven.
3. On the next checkpoint, read project status and the separate log plane first. If the system is quiet, permit at most one tiny size/status probe to determine whether the existing automatic guard fired naturally.
4. If automatic compaction occurs, verify it through capacity movement, compactor logs, pending-response safety, downstream freshness, and backlog behavior before declaring recovery. Do not infer success from a technical cron PASS.
5. Do not analyze the primary 20, matched controls, exploration cohort, or frozen 210-launch outcomes until database and source coverage are stable enough to prevent false negatives.
6. Continue to classify stale crypto-native zero matches as `DATA_GAP`. No mint, signature, transfer, trade, paid service, or other financial action is authorized.


### 2026-09-25 03:58 UTC — compactor verification gate

1. Keep the hard capacity hold at **480,808,083 bytes (96.16%)**. Add no ingestion, replay, rerun, cohort scan, collector, or schema work.
2. Do not manually invoke job 96 or lower its 460 MiB guard. Six technical completions did not reclaim space, and the logs do not prove the rebuild branch executed.
3. On the next checkpoint, inspect the separate log plane first. If timeout-free, permit at most one tiny database-size probe to determine whether natural growth crossed 482,344,960 bytes and whether the existing guard then reclaimed space.
4. If size falls, require evidence of actual reclaim plus downstream/pending-response safety before clearing the incident. A one-row cron completion alone is not compaction success.
5. Treat propagation and adapter coverage as fresh but partial. TikTok video coverage remains missing and the direct API remains `40101`; crypto-native exact-object coverage remains stale. Do not open the primary 20, controls, exploration cohort, or frozen 210 outcomes under these gaps.
6. No coin mint, wallet signature, transfer, trade, paid service, or other financial action is authorized.


### 2026-09-25 05:35 UTC — post-compaction safety window

1. Record **364,235,923 bytes (72.85%)** as the immutable post-compaction capacity checkpoint. Do not manually rerun compaction or change its 460 MiB guard.
2. Keep new collectors, replay expansion, schema changes, and broad cohort scans closed until at least one clean observation window verifies that pending-response processing, existing source freshness, and job backlogs did not regress after the 05:25 reclaim.
3. Allow the already scheduled propagation, adapter, TikTok, and MDRTF workflows to finish naturally. Do not dispatch duplicates or interpret starts as recovery.
4. Crypto-native exact-object coverage remains stale and ineligible; do not repeat the rejected unchanged replay or count zero matches as negatives.
5. Preserve primary 20, matched controls, exploration cohort, and frozen 210. Reopen prospective outcome analysis only after database stability and relevant source coverage are jointly verified.
6. No mint, wallet signature, transfer, trade, paid service, or other financial action is authorized.


## 2026-09-25 06:45 UTC — next safe gate after post-compaction recurrence

- Treat the 06:25 and 06:45 UTC failures as an active family-lane incident. Do not run the 210-launch outcome scan, cohort refresh, EXPLAIN, full counts, or manual job retries until a later independent-log window is clean.
- Do not blame or manually rerun job 96: the logged failing statement is `refresh_family_lane_guarded()`; automatic compaction only overlapped in time and had already reclaimed capacity successfully.
- Highest-information safe development is an **offline, versioned shadow rewrite plan** for `refresh_family_lane()`: preserve identical output semantics and evidence timestamps, bound source ranges or stage latest-economic rows incrementally, document every consumer, and provide a one-command rollback to the captured live definition. Validate on fixtures or an isolated branch first; do not deploy or EXPLAIN against production during active timeouts.
- Recheck capacity only after a clean log gate. Current point-in-time size is 384,642,195 bytes (76.93%), already +20,406,272 bytes since the 05:25 reclaim; measure whether this growth rate persists before changing retention or the compactor threshold.
- Keep the unchanged 80,000-message crypto replay method rejected. Run 36101180099 remained ~32h33m stale and produced no fresh keyword posts; all zero exact-object output remains `DATA_GAP`.
- Wait for propagation, adapter-bus, TikTok and MDRTF to finish naturally; do not count starts or technical PASS as restored end-to-end coverage. Preserve the primary 20, controls, exploratory cohort and 210 freeze unchanged.


## 2026-09-25 07:42 UTC — family-lane shadow admission gate

- Preserve job 101 unchanged. The read-only shadow core is a promising optimization result, not permission to replace the live function.
- Next single highest-information test, only after an independent-log window without active recurring timeouts, is a **same-observation write-free equivalence test**: freeze one `as_of` timestamp, compare every family key and scoring field from the shadow with the last successful live output, and fail on any missing/extra key, threshold drift, leader change, backfill-contamination change or evidence-timestamp mutation.
- After equivalence passes, design a delta-only upsert shadow with an explicit unchanged-row count, deterministic backfill procedure, downstream consumer inventory and one-command rollback to the captured current function definition. Do not deploy, reschedule or disable job 101 before these gates pass.
- Treat the externally measured 394,767,507 bytes (78.95%) at 07:24 UTC as a point-in-time capacity observation, not a new stable baseline. Do not repeat a size probe while the 20-minute timeout sequence is active.
- Discovery is current at 07:42 UTC, but TikTok remains two hashtags/zero videos and crypto-native remains ~32h33m stale. Do not convert discovery freshness into exact-object coverage or count zero crypto matches as negatives.
- Keep primary 20, controls, exploration cohort and frozen 210 closed. No mint, wallet signature, transfer, trade, paid service or other financial action is authorized.


## 2026-09-25 08:19 UTC — revised family-lane diagnosis gate

- Do not deploy the shadow core merely because it was faster once. The unchanged live function also completed three consecutive natural runs in about 10 seconds after three 120-second failures; query shape alone is not a sufficient root-cause explanation.
- Highest-information next test is a read-only **failure-versus-success overlap matrix** after a longer clean window: compare concurrent cron families, long GitHub source windows, lock waits, database size and cache-sensitive inputs around 06:23–07:05 failures versus 07:23–08:03 successes. Use existing logs/history first and avoid broad SQL.
- Keep the same-observation semantic-equivalence and delta-write/rollback gates for the shadow, but run them only after the intermittent contention mechanism is narrowed. Preserve every frozen threshold and `prospective_since` value.
- Treat 412,036,243 bytes (82.41%) as the current point-in-time capacity checkpoint. Do not lower the compactor threshold, manually compact, or add ingestion. Recheck only after a clean log gate.
- Discovery is current, while TikTok video coverage and crypto-native near-live coverage remain missing. Do not count zero exact-object matches or absent cohort outcomes as negatives.
- Keep primary 20, controls, exploration cohort and frozen 210 closed. No mint, signature, transfer, trade, paid service or other financial action is authorized.


## 2026-09-25 09:37 UTC — contention-phase diagnostic gate

- Treat the 08:45, 09:05 and 09:25 UTC family-lane `57014` sequence as an active recurring incident. Send no PostgreSQL SQL, EXPLAIN, cohort scan, full count, manual compaction or job rerun until an independent-log window is clean.
- Preserve job 101 and the faster shadow core unchanged. Current evidence supports an intermittent shared-load/contention component but does not identify a single culprit or authorize deployment.
- The next single highest-information test is **log-plane-only phase comparison** using the versioned overlap matrix in `ops/family_lane_contention_overlap_2026-09-25.md`. Require at least one later natural success/failure pair, then compare maintenance duration, outcome-probe lock waits, premint/process-cycle occupancy and family-lane start/end timing. Fail the single-cause hypothesis if the proposed marker does not separate successes from failures.
- Only after the incident is quiet may the previously specified same-`as_of`, write-free semantic-equivalence test run. Delta-only write behavior, every consumer, deterministic backfill and one-command rollback remain mandatory before any production replacement.
- Do not treat completed source workflows as complete coverage: TikTok is still two hashtags/zero videos with direct API code `40101`, some Reddit RSS feeds return intermittent 429, and crypto-native remains stale. Zero exact-object matches and missing prospective outcomes remain `DATA_GAP`.
- Do not remeasure database size during the active sequence. The last verified point is 412,036,243 bytes (82.41%) at 08:19 UTC. Preserve primary 20, controls, exploration cohort and frozen 210.
- No mint, wallet signature, transfer, trade, paid service or other financial action is authorized.


## 2026-09-25 10:27 UTC — revised diagnostic and scheduling gate

- Do not use the presence of `turnover_outcome_probe_tick()` row-lock waits as a family-lane failure trigger. The 10:03 and 10:23 UTC successes occurred while that wait pattern persisted, so it is not a sufficient discriminator.
- Keep job 101 and the shadow core unchanged. Continue log-first observation; after a genuinely clean window, the next single safe test is a bounded, write-free same-`as_of` comparison that also records query-input cardinalities and output hashes. Do not run it during renewed timeout activity, and do not deploy until semantic equivalence, delta-write behavior, consumer compatibility, backfill and rollback gates pass.
- Treat the absent crypto schedules as a critical coverage issue: the workflow declares four runs per hour, yet no run appeared for more than four hours after 06:03 UTC. Do not dispatch a replacement or enlarge replay. First wait for the current MDRTF run to finish naturally or reach its own timeout, then verify whether scheduled crypto creation resumes without intervention.
- Do not cancel MDRTF solely from temporal overlap; source workflows have both succeeded and failed while long workflows were present. Record its `Collect 208 prospective cuts` duration and final conclusion before causal attribution.
- Continue classifying crypto exact-object absence, TikTok zero-video output, intermittent Reddit 429s and unqueried cohort results as `DATA_GAP`.
- Current capacity remains unknown under the fail-fast gate; last verified 412,036,243 bytes at 08:19 UTC. Preserve primary 20, controls, exploration cohort and frozen 210.
- No mint, signature, transfer, trade, paid service or other financial action is authorized.



## 2026-09-25 11:19 UTC — incident hold and isolated MDRTF runtime repair gate

- Treat the 10:30–11:19 UTC sequence as an active **multi-family database incident**, not a family-lane-only failure. With 148 startup timeouts, 48 statement timeouts and 34 connection failures still extending through 11:18 UTC, send no PostgreSQL SQL, EXPLAIN, full count, cohort/freeze scan, manual compaction or job rerun until the independent log plane shows a genuinely clean window.
- Keep every affected result `DATA_GAP`. Source queueing, processing, fast-freeze, discovery, crypto crossover, control/auxiliary crossover, premint, outcome and maintenance families all lost starts or timed out; missing observations must not become negative economic outcomes.
- Do not manually dispatch, cancel or retry a workflow while Actions creation is stalled. First verify that natural scheduled-run creation resumes after the MDRTF run ended. The declared 15-minute crypto schedule produced no run after 06:03 UTC through 11:19 UTC.
- The next single highest-information safe development is an **isolated MDRTF dependency smoke gate**, only after scheduled Actions creation resumes and the database log gate is clean:
  1. on a non-production branch/local runner, install the exact workflow dependencies plus a pinned compatible `aiohttp` version;
  2. fail fast on `python -c "import aiohttp"`;
  3. add a no-network test that initializes the NATS aiohttp transport path actually used by the live Pump stream;
  4. run the existing MDRTF tests and the new transport smoke test;
  5. inspect the workflow-only diff, dependency compatibility and rollback to the captured pre-change workflow;
  6. merge no workflow change unless the test fails before and passes after.
- Do **not** edit `.github/workflows/mdrtf-future-only.yml` during the active incident. Its push paths include the workflow and `mdrtf/**`, so an edit could launch another roughly six-hour run before capacity recovery is established.
- Preserve the 565,638,843-byte `mdrtf-state` artifact as incident evidence for now. Do not delete it or shorten retention ad hoc. Before a future state-size reduction, prove resume compatibility, deterministic reconstruction, bounded artifact size and rollback to the current archive format.
- After infrastructure recovery, require a fresh near-live crypto snapshot and source-time evidence before any exact-object conclusion. The current cursor is about 37h48m stale; TikTok has zero videos and discovery is over two hours old. Zero matches remain `DATA_GAP`.
- Current database capacity is unknown under the fail-fast gate; last verified is 412,036,243 bytes (82.41%) at 08:19 UTC. Preserve primary 20, matched controls, exploration cohort, frozen 210, thresholds and `prospective_since` values.
- No mint, wallet signature, transfer, trade, paid service or other financial action is authorized.



## 2026-09-25 12:37 UTC — active-incident hold after Actions recovery

- Actions scheduling resumed naturally, but do not interpret run creation or crypto technical success as database recovery or economic validation. The database log plane still produced multi-family timeouts through 12:35 UTC.
- Continue the hard incident hold: no PostgreSQL SQL, EXPLAIN, capacity probe, cohort/freeze scan, manual compaction, job rerun or cadence increase until the independent log plane has a genuinely clean window.
- Treat the new crypto snapshot as **near-live but coverage-ineligible for negative conclusions**. It is `PARTIAL_OR_BASELINE_UNKNOWN`, began from unknown prehistory, lacks Reddit and Bluesky search coverage, and uses low-reliability keyword-only observations. It cannot fill the prior missing window.
- Reject the lone exact outbound URL as a pilot: the 11:40:04 UTC Bluesky item links retrospective Pons fee commentary, not an external object independently observed before mint. Preserve it as source evidence only.
- Do not edit or restart MDRTF while run 36129078052 is already in progress. The highest-information development remains the isolated fail-before/pass-after `aiohttp` transport smoke gate and pinned dependency repair, but it stays deferred until the database incident is quiet and the current run has ended.
- After the incident clears, first execute the dependency smoke in a non-production branch/local runner: prove `import aiohttp` fails under the current workflow set, add a pinned compatible dependency, initialize the actual no-network NATS aiohttp transport path, run existing MDRTF tests, and prove rollback to the captured workflow. Do not merge from an import-only PASS.
- Current capacity remains unknown; last verified is 412,036,243 bytes (82.41%) at 08:19 UTC. Keep primary 20, matched controls, exploration cohort, frozen 210, thresholds and `prospective_since` values immutable.
- No mint, wallet signature, transfer, trade, paid service or other financial action is authorized.



## 2026-09-25 13:57 UTC — intensified-incident hold

- Continue the hard incident hold. The 12:37–13:57 UTC window contains 126 statement timeouts and 79 connection/protocol failures through 13:56:59 UTC. Send no PostgreSQL SQL, EXPLAIN, size probe, cohort scan, manual compaction, job rerun or cadence increase.
- Do not localize the incident to family lane or stop one job based on frequency alone. Discovery, premint and process account for 72/107 identifiable cron timeouts, but outcome, crypto, maintenance, retention and auxiliary crossover are also affected. Safe load shedding still lacks dependency/backfill/rollback proof.
- Treat new workflow starts as observation only. Propagation 36142478858 and discovery 36144111241 are running but have not published completed snapshots; MDRTF 36129078052 remains in the same long collection step.
- Keep the latest crypto snapshot `DATA_GAP` for historical and negative conclusions. Near-live keyword coverage does not restore unknown prehistory, approval-gated Reddit or disabled Bluesky search.
- The next single safe development remains the isolated MDRTF `aiohttp` fail-before/pass-after transport test, but do not execute or merge it until the database log plane is clean and the current MDRTF run ends. Preserve the workflow rollback and artifact-resume gates.
- Current database capacity is unknown; last verified is 412,036,243 bytes (82.41%) at 08:19 UTC. Preserve primary 20, matched controls, exploration cohort, frozen 210, thresholds and `prospective_since`.
- No mint, wallet signature, transfer, trade, paid service or other financial action is authorized.
