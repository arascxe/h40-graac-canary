# MDRTF — PERSISTENT PUBLIC-SKILL CONSENSUS V1

Frozen: 2026-09-17 UTC

Status: future-only, paper-only research. `CAPITAL_LOCKED`; no signing, submission,
automatic trade, threshold tuning, or historical winner seeding.

## Hypothesis

Public transactions may reveal a small set of persistently skilled actors, but
one lucky wallet, one famous winner, address count, and copied/same-funded
wallets are not evidence. The tested mechanism is:

`REALIZED REPEAT SKILL -> VERIFIED INDEPENDENT ROOTS -> SAME-TOKEN CONVERGENCE -> UNCONSUMED MOVE -> OWN-SIZE ROUND TRIP`

## Point-in-time rules

- The lane starts with an empty ledger. Trades before `ppsc_runtime.started_at`
  are rejected, even if the public endpoint returns them.
- Raw swaps are immutable and deduplicated by provider trade ID.
- Only sold inventory contributes realized PnL. Mark-to-market gains do not.
- A wallet qualified in a cut becomes usable only on later cuts.
- Outcomes after a convergence signal cannot change its membership or gates.
- The zero-cost pilot denominator is the single newest public Pump.fun Solana
  pool on every fifth MDRTF cut. Pump.fun is frozen in advance because its
  public coin endpoint exposes creator provenance. This is an explicit
  deterministic sample, not full-market coverage. Unsampled launches and other
  launchpads cannot be counted as negatives.

## Frozen wallet qualification

A wallet needs all of the following from developer-clear observed swaps:

- at least 3 tokens with at least 50% of observed acquired units sold;
- at least 2 profitable closed tokens;
- closed-token win rate at least 60%;
- positive total realized PnL;
- realized profit factor at least 1.50;
- no single winning token above 70% of gross realized profit.

Developer/creator trades are excluded. Unknown developer provenance is retained
for coverage accounting but cannot establish skill.

For Pump.fun mints the public Pump coin endpoint supplies the creator address.
If a launchpad has no equivalent public creator evidence, its swaps remain
`DEVELOPER_UNVERIFIED` and cannot qualify a wallet.

## Frozen consensus gate

- at least 3 previously qualified wallets buy the same token in the same cut;
- at least 3 distinct funding roots with `INDEPENDENT_VERIFIED` evidence;
- the largest qualified wallet supplies no more than 50% of qualified buy USD;
- the token is no more than 3x its first future-only observed price;
- catastrophic contract/distribution checks clear;
- an exact own-size buy and reverse-sell route passes the existing MDRTF limits.

Missing funding provenance is `CONSENSUS_INDEPENDENCE_UNVERIFIED`, never PASS.
Missing route/contract evidence is `CONSENSUS_PENDING_EXECUTION`, never PASS.

## Output and capital

The highest possible output is `PAPER_PROBE_CANDIDATE`. It proposes no real
transaction. Any later `$10–50` diagnostic probe still requires an independent
prospective admission decision and explicit user authorization. All rows retain
`CAPITAL_LOCKED`.

## Closure test

The lane must be judged without changing thresholds:

- compare future 10x-before-35%-drawdown incidence with an activity-matched
  random-wallet/token baseline;
- include fees, quoted slippage, failed sells, and missing coverage;
- report results after removing the three largest winners;
- close if pre-trade separation is absent, execution-adjusted expectancy is
  non-positive, or the result depends on the three largest winners.

This lane does not revive blind smart-wallet copying, first-block sniping,
insider following, paid data, CEX execution, leverage, or backfill.
