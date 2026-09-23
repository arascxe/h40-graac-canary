# FEE100K SUCCESS MATRIX V1 — evidence-weighted, prospective
Date: 2026-09-23
Status: RESEARCH SPEC. No production selector threshold or auto-launch behavior is changed by this document.

## Primary target
Y100 = verified cumulative creator-fee distributions attributable to the canonical coin >= USD 100,000.
Use actual distribution receipts where possible. Payout timestamps are not assumed to equal fee-generation timestamps.

Secondary labels:
Y10 = verified creator fees >= USD 10,000
Y1 = verified creator fees >= USD 1,000
YG = verified graduation
YS = survival / continued genuine turnover after graduation

Never train the pre-mint selector on post-mint variables.

## Matrix architecture
Hard gates are conjunctive. Evidence scores do not compensate for a failed hard gate.

### PRE-MINT HARD GATES (available before token creation)
A. EXACT OBJECT / COHERENCE
- one identifiable object, not generic topic/hashtag/news category
- entity resolution supported by object-level URL/image/text evidence

B. INDEPENDENT TRANSFORMED REPLICATION — current frozen R&D gate
- actor_count >= 3
- creative_actor_count >= 2
- actor_dominance <= 0.67
CROSS_SURFACE_PROVEN additionally requires:
- source_adapter_count >= 2
- actor_dominance <= 0.60
- members_5m >= 2
These are frozen hypotheses, NOT calibrated probabilities.

C. VACANCY / FIRST-MOVER
- exact existing representation count = 0
- no established canonical token leader for the object
- current semantic proxy: token refs in prior 24h = 0 preferred; <=3 is low competition
- family-level variants must be checked, not just exact URL/name

D. INDEPENDENCE / MANIPULATION VETO
- creator-owned/related posts are excluded from external demand evidence
- no bot/syndication cluster may satisfy actor or transformation count
- no fabricated volume/engagement

E. CRYPTO-NATIVE CROSSOVER — new factor to estimate prospectively
Freeze at T-1:
- number of independent crypto-native actors referencing the object
- number of distinct crypto-native communities/surfaces
- first crossover latency after external object birth
- transformed vs simple-link crossover
Do not impose an optimized threshold until held-out data supports one.

F. ATTENTION ACCELERATION — estimate prospectively
Freeze:
- actors_5m, actors_15m, actors_30m
- unique transformations 5m/15m/30m
- adapter/surface expansion
- low-base acceleration relative to the same source/time-of-day baseline
Raw follower/view count is contextual, not a hard gate.

### EXECUTION / PACKAGING GATE
- original/right-safe 32px recognizable icon
- name/ticker maps unambiguously to object
- one-line concept intelligible without price promises
- social/contract provenance and fee-recipient disclosure
- no false official affiliation
Measure blind recognition/recall; do not equate synthetic ratings with market demand.

### POST-MINT CONFIRMATION (never leaks into T-1 selection)
At 30s / 2m / 5m checkpoints:
- bonding-curve state / vSOL
- real SOL accumulation speed
- number of trades needed to reach each fixed curve state
- unique makers and buyer concentration
- organic/manual vs bot-like participation
- creator/related-wallet sell behavior
- competing copycat count and arrival order
- actual canonical-pool turnover and creator-fee receipts

Literature prior: current curve state is the baseline predictor of graduation; faster liquidity accumulation with fewer trades is the strongest additional predictor reported by Marino et al. (2026). Bot-dominated activity is adverse beyond intermediate curve states. Successful-trader presence is only modest/non-monotonic.

## Evidence tiers
TIER A (statistically supported, but target often graduation not Y100)
1. FIRST-MOVER WITH COPYCAT DEMAND: CCS'26 reports originals in copycat groups graduated 9.20% vs 0.86% for copycats and 1.02% baseline; 17.7% of graduated tokens were nevertheless copycats. Treat arrival order as strong competition feature, not guarantee.
2. FAST CURVE PROGRESSION / FEW TRADES: strongest additional graduation predictor in Marino et al. 2026.
3. CURRENT BONDING-CURVE STATE: monotonic baseline predictor.
4. LOW BOT DOMINANCE: bot-heavy markets have lower graduation probabilities after intermediate stages.

TIER B (strongly plausible / external evidence, not yet calibrated to Y100)
5. INDEPENDENT EXTERNAL ATTENTION -> RETAIL CROSSOVER: causal social-attention literature supports attention increasing retail participation, but not a Pump-specific Y100 threshold.
6. TRANSFORMED MULTI-ACTOR REPLICATION.
7. CROSS-SURFACE SPREAD.
8. SEMANTIC VACANCY / no recognized leader.
9. OBJECT LEGIBILITY / memeability.

TIER C (association only / unstable / easy to manipulate)
10. Social-link presence (Telegram/X/website). Large lift was reported in a short-window Pump collector study, but later measurement/generalization audits require caution.
11. Creator self-buy / initial mcap above default. Association reported, not accepted as causal or recommended.
12. Influencer/follower count. Track, but no hard audience-size threshold is currently defensible.
13. Historically successful traders / “smart money”. Marino et al. finds only modest/non-monotonic effect.

HARD NEGATIVE / VETO
- recognized existing canonical leader
- broad generic topic rather than exact object
- sports/news/SEO contamination when no meme transformation exists
- single-actor dominance
- fake/bought engagement, wash trading, related-wallet maker inflation
- copycat impersonation / misleading official claim
- creator-fee route not verified

## Statistical design to discover the maximizing combination
Prospectively freeze all T-1 features before mint/token reference.
Use matched same-time/same-source controls.
Outcomes at 1h, 24h, 7d, 30d: graduation, genuine canonical turnover, Y1/Y10/Y100 receipts.
Models:
1. regularized logistic / discrete-time hazard for YG, Y1, Y10
2. hurdle / survival model for turnover
3. Y100 treated as extreme-tail label; do not fit probability until enough positives
Validation:
- rolling temporal holdout, never random-only split
- calibration slope/intercept + precision at top-k
- bootstrap by calendar day/event family
- ablation per feature family
- report base-rate-adjusted lift and confidence intervals
- freeze thresholds before each validation window
No threshold is promoted to production merely because it fits development data.

## Operational decision rule for now
Do NOT produce a numeric “P(Y100)” yet.
An object may enter PILOT_REVIEW only when A-D hard gates pass.
E-F are measured and frozen for learning.
Post-mint metrics are confirmation/outcome variables, not retroactive proof of pre-mint quality.
