# FEE100K creator-fee access probe — frozen 2026-09-23 20:20 UTC

Status: ACCESS_PROBE_STARTED; on-chain receipts NOT verified. This is separate from the prospective 20-case cohort and does not estimate P(Y100).

## Selection protocol
Existing public.fee100k_right_tail_econ_v1 observations from 2026-09-23 19:00:00–20:00:00 UTC; latest observed row per mint with a non-null estimated fee. Two maximum and two minimum estimated-fee rows selected by SQL ORDER BY generated_fee_24h_est_usd; extreme proxy selection is intentional solely to test endpoint discrimination, not a causal matched outcome study. No fee distribution or user receipt is implied. This is not yet a matched same-age/source comparison.

| Probe role | Mint | Snapshot UTC | 24h volume proxy USD | Fee estimate USD | Effective rate assumed | Confidence |
|---|---|---|---:|---:|---:|---|
| upper proxy | BP4Wic5LNKsqpmiREW6uNVEC16juvFCSd4WzVBatpump | 19:52:15 | 4,062,429.91 | 38,593.08 | 0.950% | LOW |
| upper proxy | GTBxUiw6wJdmmkCGZgRHLyYxqu1vG4KtRpeox6yDpump | 19:58:10 | 7,303,632.90 | 21,910.90 | 0.300% | MEDIUM_HIGH |
| lower proxy | 7WRX5QGuRLhGCJszpQjYmw6ihb6z8KRdAEHQUhGJpump | 19:56:11 | 173.40 | 0.52 | 0.300% | MEDIUM_HIGH |
| lower proxy | ACtfUWtgvaXrQGNMiohTusi5jcx5RJf5zwu9aAxkpump | 19:57:11 | 25,741.27 | 205.93 | 0.800% | MEDIUM_HIGH |

## Access gate
- Existing fee100k_fee_distribution_v1, fee100k_fee_ledger_v1 and fee100k_launch_v1 each contain 0 rows at probe time. The external economics table has 3,268 distinct mints, but estimates only.
- Verify independently with an allowed free source: canonical pool identity; trade-level creator-fee amount/rate; creator-vault accrual; exact fee recipient and sharing/cashback mode; claim/collection transaction; USD conversion at event time. Record source URLs/transaction signatures and coverage limits.
- If there are no reliable fee events or recipient proofs for at least 2 upper and 2 lower proxy mints, declare ACCESS_FAIL. Do not relabel estimates as verified fees. Replace with another lawful source class or stop this historical lane.
- Timebox source access diagnosis to two research cycles / about 24 hours, without consuming heavy production DB resources. A subsequent matched historical denominator is licensed only after ACCESS_PASS.
- Immutable primary first-20 cohort, production selectors, creator wallet and capital remain untouched.

Official source references: https://pump.fun/docs/fees and https://github.com/pump-fun/pump-public-docs/blob/main/docs/instructions/COLLECT_CREATOR_FEE.md
