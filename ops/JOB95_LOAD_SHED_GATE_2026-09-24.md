# Job 95 turnover outcome probe — load-shedding safety gate

Captured: 2026-09-24 21:48 UTC
Supabase project: iocirjhwncnhjanawgsm
Status: SHADOW_CANDIDATE_ONLY / NO_PRODUCTION_CHANGE

## Live point-in-time baseline

A single bounded read-only query, after a 73-minute log window with no startup,
statement or connection timeout, returned:

- job ID: `95`
- schedule: `59 seconds`
- active: `true`
- command: `select fee100k_private.turnover_outcome_probe_tick();`
- database size: `461270163` bytes (~92.25% of the 500,000,000-byte Free limit)

This capture does not authorize changing the job. The independent log stream was
quiet from 20:35 through 21:48 UTC, but three long GitHub Actions jobs remained
in progress and a new MDRTF job remained pending. A quiet log window is not
proof of durable recovery.

## Repository evidence

Default-branch code search returned no versioned definition for
`turnover_outcome_probe_tick`, no versioned job-95 declaration and no matching
`59 seconds` schedule. Therefore inputs, writes, synchronous consumers,
backfill determinism and an exact rollback cannot yet be proven from the repo.

## Admission gate before any pause or cadence reduction

1. Export the exact live function definition and all direct dependencies only
   after another clean log window; do not scan broad catalogs during pressure.
2. Prove source observations and immutable first freezes do not depend on this
   job, and that missed outcomes are deterministically backfillable.
3. Pre-register one change, a comparison window spanning at least two original
   cadences, backlog and coverage acceptance metrics, and exact restoration of
   the captured schedule/command/active state.
4. Reject the intervention if error counts fall only because source coverage or
   processing stops.
5. Do not combine this experiment with compaction, retention, collector,
   threshold, schema, alert or cohort changes.

Until these gates pass: preserve job 95 unchanged. No coin, trade, wallet,
transfer or paid action is authorized.
