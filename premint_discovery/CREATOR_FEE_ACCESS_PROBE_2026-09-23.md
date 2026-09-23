# FEE100K creator-fee access probe — frozen 2026-09-23 20:20 UTC

Status: ACCESS_PARTIAL; one creator-wallet AMM claim route verified, per-mint attribution and 2+2 endpoint coverage pending. This is separate from the prospective 20-case cohort and does not estimate P(Y100).

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

## 2026-09-23 21:00 UTC — bounded on-chain result

The isolated read-only [2+2 run](https://github.com/arascxe/h40-graac-canary/actions/runs/35919565298) queried official Solana public RPC for 20 recent signatures of each Pump-listed creator and inspected four spaced transactions per address. It did not mutate production or submit a transaction. Pump pages provide the public mint-to-creator mapping: [BP4W](https://pump.fun/coin/BP4Wic5LNKsqpmiREW6uNVEC16juvFCSd4WzVBatpump) -> `4b9eNunmdJCdbtYTPqMwU3wCVopEYaM8Dm5xBPK3G5Gb`; [GTBx](https://pump.fun/coin/GTBxUiw6wJdmmkCGZgRHLyYxqu1vG4KtRpeox6yDpump) -> `BS3FxZoEnDjt76iR3WhEkQZhLqLARVCDFu4dc4Z9dE3B`; [7WRX](https://pump.fun/coin/7WRX5QGuRLhGCJszpQjYmw6ihb6z8KRdAEHQUhGJpump) -> `BopmiQ2L2QVzoKQdEfbUZyy1GsLQZ7z3XJR16HCLddrX`; [ACtf](https://pump.fun/coin/ACtfUWtgvaXrQGNMiohTusi5jcx5RJf5zwu9aAxkpump) -> `BXAWg4JbaeyvAHpiyYQ3Xr3bUh6FsyDHwwSkB5dmyGF`.

A second [transaction-detail run](https://github.com/arascxe/h40-graac-canary/actions/runs/35919705502) verified two actual **Pump AMM creator fee collection** instructions for the BP4W-listed creator address. [Transaction 4WwW7...](https://solscan.io/tx/4WwW7dMHtRbSYsgTagyB2CTFNcRpudChmMwPEbGXRYE6Jvk7P6SBeitNPcqgrRf5MadsLnr7iT1cLyUeREQQBtdF) transferred 2.846219841 wrapped SOL from the AMM creator vault token account to the creator's temporary token account; closing that account left wallet SOL balance +2.846210752 net of 9,089 lamport transaction fee. [Transaction 4nNU3...](https://solscan.io/tx/4nNU3G9zBioKP7frGn2ekFSTAbHjbiAiLtdcasmaJzPSqHuB4aKnXUTiz5FEQNi2RvJvkgcDzyM6ZrUJ4e1mLRvo) similarly transferred 0.977812710 wrapped SOL, leaving wallet +0.977803621 net. Both call Pump AMM `CollectCoinCreatorFee`; combined transfer 3.824032551 SOL and combined net wallet increase 3.824014373 SOL in these two transactions. This verifies a **creator-level actual fee receipt mechanism**, not USD value, net lifetime profit, or attribution to BP4W specifically. The AMM creator vault is creator-address based and may aggregate several coins; claims cannot be allocated to one mint from the claim transaction alone.

The other sampled addresses had no proven collection in the four inspected transactions each. This is an insufficient sample, not proof of zero fees. One 7WRX-listed creator address showed `GetFees` instructions without a wallet credit; ACtf-listed creator had incoming SOL on Jupiter-related transactions that must not be counted as Pump fee claims. GTBx-listed creator's four inspected recent transactions had no claim. The frozen upper/lower cohort is a source-access probe, not a matched causal comparison or a user revenue claim.

**Confounder exposed:** the BP4W-listed creator Pump profile shows 53 followers and the GTBx-listed creator 865; their coin pages have outward links, while the ACtf-listed creator profile shows 42.1k followers despite this coin's low current volume. Follower count alone is neither a pre-mint independent distribution measure nor a fee predictor. These observed profiles cannot establish replicability for a no-audience creator. Control launch age and compare original external-object spread and trader independence before ranking mechanisms.

Next: obtain mint-specific canonical trade fee events and creator sharing state; reconcile aggregate vault inflow across all coins for each creator against collection times and claims. If free public RPC cannot give event-level attribution within the probe timebox, mark ACCESS_FAIL for mint-specific historical fees while retaining creator-level receipt verification. No inferred USD income or user-wallet receipts.
