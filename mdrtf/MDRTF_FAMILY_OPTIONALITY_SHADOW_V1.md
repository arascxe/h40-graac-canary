# MDRTF — FAMILY OPTIONALITY SHADOW V1

Frozen: 2026-09-16 UTC  
Status: paper-only, outcome-blind, capital unconditionally locked.

## Question

Can a tiny family-level paper basket capture the right tail earlier than waiting
for a fully resolved canonical leader, while limiting the cost of choosing the
wrong sibling?

This is an isolated policy comparison. It does not change AFT S0–S4 admission,
family membership, source gates, leader rules, or the seven-day decision.

## Entry clock

The first eligible checkpoint after a canonical `family_freezes` row exists is
the only entry clock. No historical family and no later-known winner may be
backfilled.

Eligibility per member:

- contemporaneous price is known and positive;
- exact simulated own-size route state is `ROUTE_PASS`;
- catastrophic contract state is `PROXY_PASS`, never UNKNOWN;
- worst-case round-trip cost is at most 3%;
- at least two eligible siblings exist.

Selection is deterministic and outcome-blind: rank by the contemporaneous
leader score, break ties by network/pool ID, retain at most three, and allocate
an equal share of a `$50` total paper budget. The existing exact `$50` route is
used as a conservative capacity gate; the smaller equal-weight paper legs are
not represented as exact fills.

## Rotation gate

The paper basket rotates into one member only when all are true:

1. the same member is rank 1 at two recorded checkpoints;
2. distinct external buyers increase;
3. developer-excluded external buy exceeds external sell;
4. address diversity is present and the largest buyer share is at most 35%;
5. family-relative external-buy share rises by at least five percentage points;
6. family-relative buyer share does not fall;
7. at least one sibling loses external-buy share;
8. the leader remains exactly routable and contract-pass at rotation time.

Rotation is paper accounting only. All siblings are marked `ROTATED_OUT`; their
current conservatively haircutted paper value is converted into virtual units of
the leader using its current route cost.

## Frozen outputs

- `fos_baskets`: one immutable entry clock per family;
- `fos_positions`: selected siblings, entry values and current paper state;
- `fos_checkpoints`: point-in-time routing and family-share evidence;
- `fos_rotations`: exact convergence proof and paper rotation;
- collector JSON: `family_optionality_shadow` summary.

Every row retains `CAPITAL_LOCKED`. The lane cannot emit an actionable signal,
sign a transaction, change canonical AFT state, or authorize capital.

## Comparison after the future-only window

Compare, without retuning:

- family-basket value before rotation;
- rotated-leader value after executable costs;
- canonical S2/S3 wait-policy value from its own first eligible clock;
- 3x/5x/10x-before-35%-drawdown capture;
- loss per failed family and top-winner-removed geometric return;
- opportunity latency from family freeze to paper entry and leader rotation.

If complete families are too rare, coverage is insufficient, or the early
basket loses more through wrong siblings than it gains through earlier right-
tail exposure, close this lane. Do not rescue it with post-outcome threshold
changes.
