# FEE100K Crypto-Native Crossover — Prospective Pilot 20 (research-only)

Activated 2026-09-23 16:11:40 UTC. First live check: 2026-09-23 16:26 UTC.
Purpose: field-test Success Matrix V1 without suppressing weaker candidates or pretending there is a calibrated $100K probability.

## What is running
- Public, bounded crypto-discussion observation: GitHub Actions every 15 minutes (scheduler jitter possible). Sources: public Reddit RSS, low-confidence public Mastodon tags and an 18-second Bluesky Jetstream window.
- Freshness rule: prospective sensor includes only observable public posts published in the preceding 120 minutes. Feed failures are retained as coverage gaps.
- GitHub publishes ONLY a small public crypto-observation snapshot; Supabase consumes it with rate-guarded pg_net GET ~every 16 minutes.
- Supabase cron job: `fee100k-crypto-crossover-shadow-q2m` processes inbound responses every 2 minutes. No minting, spending, promotion or transaction automation.
- Two evidence lanes: (1) exact URL crossover citations, excluding the object's own social envelope and excluding stale/retrospectively discovered posts; (2) shadow semantic suggestions requiring >=2 distinctive tokens, explicitly MANUAL_REVIEW_ONLY.
- Actor hashes are namespaced and de-duplicated. Reddit community membership / crypto-keyword mention is NOT a verified buyer signal.
- Keep all existing Demand-Proof and production thresholds unchanged.

## Immutable initial observational cohort
Frozen at 2026-09-23 16:11:40 UTC from then-visible object features:
- 10 evidence-enriched observational objects.
- 10 deterministic same-period, same dominant-source matched controls.
- Per-group source mix: 4 Bluesky Jetstream / 4 Mastodon public / 1 Reddit RSS / 1 YouTube fresh search.
- The evidence-enriched group had four objects with >=2 actors, four with >=1 creative actor, two with >=2 adapters at enrollment. This is NOT a prospective success rate.
- Matrix monitoring lanes at first check: 8 evidence-enriched NEAR_MISS_TRACK, 2 EARLY_TRACK, plus 10 continued controls.
- 0 met the original full Demand-Proof gate, 0 verified pre-mint-eligibility audits, 0 verified crypto crossover links, 0 Y100 outcomes.
- Tokenization status at enrollment is UNVERIFIED. No row is labeled true pre-mint merely because we detected its social object.
- The research score used to assemble the cohort is NOT a probability of earning $100K.

## Source reality — transparent limitations
First ingestion accepted 25 Reddit:r/solana RSS posts, many of which were old. A freshness audit found they must NOT be treated as newly emerging crypto-native attention.
After enforcing the <=120min publishing window, a sample produced 8–9 fresh Reddit:r/solana posts per run and a single fresh crypto-keyword Bluesky Jetstream post in one observed 18-second window.
The other three Reddit RSS feeds and the Bluesky search endpoint reported HTTP errors. Mastodon tags returned success but no timely posts in the sample. These are genuine coverage gaps; zero observations are not interpreted as evidence that no crossover occurred.
At the 16:26 UTC check the independent bridge returned HTTP 200; 27 crypto-source posts were persisted across the initial test and fresh cycle; 0 exact cross-object matches and 0 semantic review hints had emerged. All 18 active FEE100K cron jobs had successful/running last statuses. Storage ~354MB.

## False-negative-safe decision
The full strict gate controls only LIVE-LAUNCH-REVIEW eligibility. The discovery and prospective research lanes DO NOT discard weak objects for failing the full gate:
- NEAR_MISS_TRACK: preserve objects with >=2 actors, >=1 creative actor or later clean exact cross citations.
- EARLY_TRACK: preserve lower-evidence signals for comparison.
- MATCHED_CONTROL: preserve negative denominators, not hindsight-selected successes.
- Low-confidence text/crypto-tag evidence can trigger review but never be counted as verified genuine buyer demand.

## Pre-registered next checks (not yet results)
At 24h: source freshness/coverage, exact crossover evidence, manual precision/false-negative audit, progression of each of the 20 objects, timestamp verified mint checks.
At 7d: verified original-family tokenization links and where available actual canonical fee recipient receipts, with data gaps labeled UNKNOWN.
Do NOT train or promote any score as P(Y100) using the first 20. Expand PIT controls and obtain independent later-period positive outcomes before calibration.
