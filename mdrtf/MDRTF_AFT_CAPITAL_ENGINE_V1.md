# MDRTF — AFT CAPITAL ENGINE V1

Frozen: 2026-09-16 UTC

Status: research and measurement only; capital remains locked until the live
admission contract below passes. No automatic signing or trading.

## Objective

The engine is not a generic new-token ranker. It seeks one narrow information
asymmetry:

`LOW-BASE EXTERNAL ATTENTION -> PARALLEL TOKENIZATION -> EXTERNAL CAPITAL ROUTING -> FAMILY LEADER -> EXECUTABLE CONVEX RUNNER`

The unit of analysis is an attention event and its complete token family, not
an isolated coin. Raw social presence, low market cap, wallet count, creator
self-buy, price momentum, CTO status, or one smart wallet can never admit a
trade by themselves.

## Why this lane

Public launch feeds are overwhelmingly low-base-rate and adversarial. Competing
on first-seconds latency also conflicts with the zero-cost constraint. AFT moves
the clock earlier: independent attention must exist before the token family,
then capital routing among siblings supplies the leader-selection evidence.

The engine buys information in stages. It does not wait for certainty, and it
does not place meaningful capital before the market supplies evidence.

## Frozen state machine

### S0 — ATTENTION BIRTH

Required:

- event timestamp precedes every admitted token pool;
- at least two named independent publishers, or two independent attention
  surfaces/geographies;
- low-base novelty: the event is not merely a recurring evergreen phrase;
- exact semantic entity linkage, not vague thematic similarity.

Capital: `$0`.

### S1 — FAMILY FREEZE

Required:

- at least two distinct token contracts linked to the same frozen event;
- at least two distinct creator/developer identities when the chain exposes
  that evidence;
- every sibling, including dead ends, is frozen before outcomes are read;
- missing metadata is `CANDIDATE_COVERAGE_INSUFFICIENT`, never a negative or a
  pass.

Capital: `$0`.

### S2 — EXTERNAL CAPITAL ROUTING

Required at consecutive checkpoints:

- developer-excluded buy flow;
- increasing distinct external buyers;
- no single buyer dominates the new inflow;
- family-relative first-choice capital and buyer share move toward one member;
- the leader's share rises while at least one sibling loses share;
- flow is not explainable solely by same-funder, internal rotation, incentives,
  or a persistent sniper ring.

Wallet diversity alone remains `ADDRESS_DIVERSE_ONLY`; it is not proof of
economic independence.

Capital: a `$10-$25` diagnostic micro-probe may be proposed, but still requires
explicit user authorization.

### S3 — EXECUTABLE LEADER

Required:

- exact own-size buy and immediate reverse sell route;
- quoted round-trip cost no more than 3% at the diagnostic size;
- buy and sell price impact no more than 2% per leg;
- contract, mint/freeze/admin, holder concentration, honeypot and route checks
  do not veto the token;
- the move retains valuation runway; a late leader is rejected even when it is
  genuine.

Capital ladder after explicit authorization:

- PROBE: at most `0.25%` of bankroll;
- CONFIRM: cumulative cost at most `1.0%` after a successful real sellability
  probe and one more independent capital checkpoint;
- SCALE: cumulative cost at most `3.0%` after persistent leader capture;
- RUNNER: cumulative cost at most `7.5%`; expansion beyond 3% must come from
  realized strategy profits, not untouched principal.

### S4 — RUNNER MANAGEMENT

- At 2x on the weighted position, recover original deployed cost unless doing
  so would fail the route/liquidity constraint.
- The remaining position is the convex runner.
- Exit on route deterioration, leader-share reversal, buyer-growth failure,
  provenance failure, creator/distribution veto, or sibling recapture.
- Price drawdown alone is not the primary exit; causal-state invalidation is.

## Portfolio mathematics

The target requires right-tail capture rather than a high win rate. With a
7.5% maximum-cost position, one 20x winner changes the portfolio by roughly
2.4x before losses and slippage. Reaching 100x therefore requires several
independent large runners or one exceptional runner plus successful
reinvestment. This is possible but rare; the engine cannot guarantee it.

Losses must remain small enough for repeated attempts. A failed probe may not
be averaged down. A token that never reaches S3 may never receive scale capital.

## Operational admission contract

Before the seven-day edge window starts, the runtime must pass a continuous
24-hour operational tape:

- at least 95% of scheduled cuts begin within 30 seconds of target cadence;
- no unexplained gap exceeds five minutes;
- every configured live endpoint passes an exact chain/network canary;
- at least 95% of cuts have attention quorum and Solana lane coverage;
- all injected non-market canaries are captured and timestamped;
- a deliberately failing endpoint produces the expected lane-local UNKNOWN,
  not a global false negative;
- SQLite integrity remains `ok` and state survives a fresh job restore.

Failure restarts the 24-hour operational tape. It does not extend or contaminate
the seven-day edge window.

## Seven-day future-only decision contract

Thresholds and family membership are frozen before outcomes. At day seven:

1. If fewer than two complete AFT families occurred, the lane is
   `TOO_INFREQUENT_FOR_URGENT_OBJECTIVE` and is closed for this mission.
2. If events occurred but the runtime missed their required evidence, the
   result is `OPERATIONAL_FAIL`; no retrospective PASS is allowed.
3. If complete families occurred but leaders did not separate from siblings,
   the result is `NO_SELECTION_EDGE`.
4. If executable leaders were identified prospectively, every proposed probe,
   fill, reverse-sell test and later 3x/5x/10x-before-35%-drawdown outcome is
   retained, including failures.
5. Promotion beyond diagnostic probes requires positive realized execution and
   a prospective leader advantage; thresholds may not be tuned on the same
   seven-day outcomes.

No indefinite extension is permitted. The decision window ends with an
explicit `ADMIT`, `CLOSE`, or `DATA_TOO_SPARSE_FOR_URGENT_OBJECTIVE` result.

## Explicit exclusions

- no CEX lane;
- no raw CTO-to-buy rule;
- no blind smart-wallet copy trading;
- no first-seconds sniper competition;
- no paid API, paid runtime or credit dependency;
- no historical winner tuning;
- no automatic transaction signing;
- no alert unless a state changes to S2, S3, INVALIDATE, or operational FAIL.

