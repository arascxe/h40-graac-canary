# MDRTF — RIGHT-TAIL ISSUER V1

Frozen: 2026-09-19 UTC

Status: economics measurement only; `PAPER_ONLY / CAPITAL_LOCKED`.

## Objective

Measure whether a selective issuer can prospectively reach the economically
relevant right tail instead of copying high-volume launch spam:

`FUTURE-ONLY ATTENTION -> VERIFIED TOKEN INTENT -> CAPITAL APPROACH -> ISSUANCE -> EXTERNAL VOLUME -> CREATOR ECONOMICS`

The target labels are `$5,000` observed creator economics per admitted launch
and `$100,000` across the admitted portfolio. A target is not a forecast,
guarantee, or permission to launch.

## Frozen economics rules

- Creator and same-address trades are excluded from external volume.
- Missing funding-root linkage may not be called independent capital.
- Fee-floor reporting uses 0.30%; 0.95% is only a theoretical ceiling because
  the actual Pump fee varies with pool and market-cap state.
- A token is a floor hit only after observed external volume reaches
  `$1,666,666.67`; a ceiling hit requires `$526,315.79`.
- `PENDING`, truncated and source-error trade histories remain incomplete.
- Incomplete rows may describe observed volume but may not enter a failure-rate
  denominator or establish a negative outcome.
- Paper valuation of creator inventory is not revenue. Only realized proceeds
  with an observed executable sell route may be counted in a later version.
- Historical rows may estimate mechanism and base rate but may not tune and
  validate the same admission threshold.

## Admission boundary

V1 produces an economics audit only. It cannot deploy, sign, promote, trade,
recommend a coin, or change AFT/issuance admission. `actionable_launches` is
always empty and capital remains locked.
