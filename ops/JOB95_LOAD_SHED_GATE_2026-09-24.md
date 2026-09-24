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
