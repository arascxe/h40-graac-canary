# Job 95 turnover outcome probe — load-shedding safety gate

Captured: 2026-09-24 21:48 UTC; dependency follow-up: 2026-09-24 23:09 UTC
Supabase project: iocirjhwncnhjanawgsm
Status: SHADOW_CANDIDATE_REJECTED_FOR_NOW / NO_PRODUCTION_CHANGE

## Live point-in-time baseline

A single bounded read-only query, after a 73-minute log window with no startup,
statement or connection timeout, returned:

- job ID: `95`
- schedule: `59 seconds`
- active: `true`
- command: `select fee100k_private.turnover_outcome_probe_tick();`
- database size: `461270163` bytes (~92.25% of the 500,000,000-byte Free limit)

This capture did not authorize changing the job.

## Dependency follow-up

The independent log stream contained no startup, statement or connection error
after 20:05 UTC through the 23:08 UTC checkpoint. One new three-second-bounded
read-only query captured the live wrapper definition and recent executions:

- database size: `419335315` bytes (~83.87% of the Free limit);
- latest 12 job-95 executions: all succeeded;
- the wrapper calls four separate functions in sequence:
  1. `process_turnover_outcome_canonical()`
  2. `process_turnover_outcome_econ()`
  3. `queue_turnover_outcome_probes()`
  4. `refresh_turnover_model_state()`

This falsifies the narrow assumption that job 95 is merely a disposable,
single-purpose probe queue. It couples canonical and economic processing,
queueing and model-state refresh. Pausing it without the four dependency
definitions could silently suppress mature outcomes or model state.

Capacity also fell by 41,934,848 bytes from the 21:48 measurement. The cause of
that decline is not attributed without evidence, but the immediate >92% trigger
for speculative load shedding no longer holds.

## Repository evidence

Default-branch code search still contains no versioned definitions for the four
called functions and no versioned job-95 declaration. Therefore inputs, writes,
synchronous consumers and deterministic backfill remain unproven.

## Admission gate before any future pause or cadence reduction

1. Version the four direct function definitions and their written tables after a
   clean log window; do not scan broad catalogs during pressure.
2. Prove source observations, immutable first freezes, mature outcomes and
   creator-fee receipt state cannot be suppressed.
3. Pre-register one change, a comparison window spanning at least two original
   cadences, backlog/coverage metrics, and exact restoration of schedule,
   command and active state.
4. Reject the intervention if error counts fall only because source coverage or
   processing stops.
5. Do not combine it with compaction, retention, collector, threshold, schema,
   alert or cohort changes.

Until these gates pass: preserve job 95 unchanged. No coin, trade, wallet,
transfer or paid action is authorized.


## 2026-09-25 03:25 UTC — dependency snapshot and renewed capacity gate

Read-only observation only; no cron, schema, data, threshold, freeze, or funds changed.

- Database size: **480,496,787 bytes** (~96.10% of the 500 MB free quota), up **61,161,472 bytes** from the 419,335,315-byte recovery checkpoint. The unexplained recovery was therefore not durable; additional database probing stopped after this bounded query.
- Log window 2026-09-24 23:09–2026-09-25 03:24 UTC: 2,290 completion events, 206 job-95 completions, 0 job-95 failures, 6 statement-timeout messages and 1 connection-reset message. The timeouts clustered at 00:44–00:45 UTC, with isolated events at 01:05 and 02:45 UTC. This is degraded/recurrent pressure, not the earlier broad multi-family outage.
- Latest 12 job-95 executions all succeeded. Runtime was normally sub-second; one observed execution took ~3.63 seconds.

Direct function-definition audit:

1. `process_turnover_outcome_canonical()` consumes completed canonical HTTP responses, mutates prospective token-link state, may immediately queue DexScreener economic probes, and marks request rows processed.
2. `process_turnover_outcome_econ()` consumes economic responses, writes 24-hour turnover/estimated-fee maturity fields, and marks request rows processed.
3. `queue_turnover_outcome_probes()` creates up to four external HTTP requests per tick for matured eligible links and increments probe state/attempt counters.
4. `refresh_turnover_model_state()` recomputes aggregate training/model readiness state from accumulated outcome tables.

Decision: **whole-job pause remains rejected**. The only plausible future load-shed seam is the queueing subfunction, but it is not independently scheduled and skipping it would delay future-only outcomes. Any refactor needs a shadow wrapper test, explicit backlog/backfill proof, and a database-capacity safety margin before production use. At current capacity no refactor or additional collector is authorized.

State: `CAPACITY_REBOUND_CRITICAL / JOB95_DEPENDENCIES_CLASSIFIED / WHOLE_JOB_PAUSE_REJECTED / NO_PRODUCTION_CHANGE`.
