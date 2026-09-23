# FEE100K Success Matrix V1 — Evidence-weighted, prospective calibration

Date: 2026-09-23
Status: RESEARCH SPEC ONLY. Does not change production thresholds, cron, launch automation, or capital deployment.
Primary endpoint: verified cumulative creator-fee receipts >= $100,000 from qualifying canonical trades.
Secondary endpoints: graduation; 24h qualifying turnover; 24h creator-fee receipts; 7d retained turnover.
Rule: no score may be described as a calibrated probability until enough prospective labeled cases exist.

## Evidence classes
A = directly supported by large launch-level empirical study / official mechanism.
B = supported by related empirical diffusion or crypto research but not directly $100K creator-fee endpoint.
C = our prospective hypothesis; must be calibrated with matched positives/negatives.

## Matrix

### PRE-MINT: mandatory opportunity quality
1. Independent transformed replication [C]
   Current prospective gate: actor_count >= 3; creative_actor_count >= 2; actor_dominance <= 0.67.
   Rationale: excludes a single account broadcasting copies; tests genuine independent adoption.
   Do not lower to manufacture positives.

2. Structural/community diversity [B/C]
   Desired: >=2 independent source adapters AND >=3 distinct communities/surfaces where measurable.
   Track adoption entropy / largest-community dominance, not raw mention count.
   Literature: early community dispersion predicts future meme virality better than early popularity alone.

3. Replication acceleration [B/C]
   Track unique independent actors and transformed variants in 5m/15m/30m windows.
   Use acceleration relative to each source's baseline, not a universal raw-view threshold.
   Raw audience size alone is not a hard gate.

4. Semantic vacancy / leader absence [C]
   Hard veto if an already-recognized canonical token dominates the exact object/family.
   Measure exact and semantic-family token references, leader concentration, token age and actual trading.
   "First mint" alone is not sufficient.

5. Crypto-native crossover before mint [C]
   Require independent references from crypto-native participants/communities before our launch.
   Exclude our own accounts, paid promotion, related wallets, syndication and obvious bots.
   Initial research gate: >=2 independent crypto-native communities/actors; calibrate prospectively.

6. Object nominability / packaging legibility [B/C]
   Exact object must be explainable in one short phrase and visually recognizable at small icon size.
   Metadata has modest predictive information among graduated memecoins, but text alone is insufficient.
   Blind tests should score 2-second recognition, uniqueness and object fidelity.

### CREATOR / DISTRIBUTION PROFILE
7. Prepared social presence [A as graduation proxy, NOT causal $100K proof]
   Public launch research found advertised Telegram / multi-social presence strongly associated with
   fast-regime graduation. Treat as evidence of distribution readiness, not a reason to fabricate socials.
   Measure real audience and engagement, not existence of a link.

8. Creator history [A/B as graduation proxy]
   External data: prior graduation + >=7d quiet creator cohort showed 12.01% graduation vs 1.71% baseline,
   but the same operator's live trading probe achieved 6.5% and lost money.
   For our own creator strategy this feature is initially unavailable; build reputation only via genuine launches.
   Never use wallet cycling to fake history.

9. No serial-launch spam [B]
   High launch frequency without sustained outcomes is a negative quality signal.
   One coherent high-conviction object is preferable to indiscriminate minting.

### POST-MINT: continuation / kill gate (not pre-mint selection)
10. Bonding-curve state [A]
    Graduation probability rises mechanically with vSOL / curve progress.
    Never count this as pre-mint edge.

11. Liquidity accumulation velocity [A]
    At the same bonding-curve state, reaching it in fewer trades is the strongest predictor reported
    in Marino et al. 2026. Interpret as concentrated real demand; validate unique maker composition.

12. Human / non-bot participation [A]
    Higher non-bot share is associated with better graduation odds; bot-dominated turnover is weaker.
    Implement maker independence and route/bot heuristics; never manufacture transactions.

13. Unique-maker breadth + retention [A/B]
    Require growth in genuinely independent makers and continued turnover after the first burst.
    Kill if activity is creator-related, circular, highly concentrated or immediately decays.

14. Canonical fee routing [A]
    Only qualifying canonical trading pays creator fees under the documented schedule.
    Verify exact fee-owner wallet and receipts before treating volume as revenue.

## What is NOT yet statistically defensible
- A universal follower-count threshold.
- A universal number of views/likes guaranteeing graduation or $100K fees.
- A universal actor-count threshold that has been proven to maximize $100K outcomes.
- "KOL present" as a positive by itself.
- First-to-mint as a moat.
- Graduation as equivalent to creator-fee success.
- Our current research_priority_score as P($100K).

## Target labels for prospective calibration
Y0 = graduated.
Y1 = 24h qualifying canonical turnover >= $1m.
Y2 = 24h verified creator fees >= $10k.
Y3 = 7d verified cumulative creator fees >= $100k (primary economic right-tail).
For every candidate freeze T-1 features before mint/tokenization and never backfill them with later data.

## Statistical procedure
- Case-control sampling from same time/source regime; preserve negatives.
- Time-split evaluation only; never random split across a changing market regime.
- Use monotonic / regularized models first (logistic, calibrated GBM) and report precision-recall,
  Brier score, lift over base rate, confidence intervals and calibration.
- Estimate interactions, especially:
  transformed replication x community diversity;
  crypto crossover x semantic vacancy;
  packaging legibility x distribution readiness;
  post-mint liquidity velocity x non-bot unique-maker breadth.
- Pre-register threshold changes before seeing outcomes.
- Promote a feature to production only after prospective lift replicates in >=2 non-overlapping windows.

## Current evidence-based hypothesis for highest-quality launch state
PRE-MINT:
real object + >=3 independent actors + >=2 creative actors + low actor dominance
+ cross-community/cross-platform dispersion + positive acceleration
+ no established canonical token leader
+ independent crypto-native crossover
+ immediately legible/original packaging + real distribution channel readiness.

POST-MINT continuation:
rapid curve progression with relatively few genuine trades
+ expanding independent maker breadth
+ low bot/circular concentration
+ retained activity after the initial burst
+ canonical creator-fee routing verified.

This is a candidate interaction matrix, not yet a calibrated $100K probability.
