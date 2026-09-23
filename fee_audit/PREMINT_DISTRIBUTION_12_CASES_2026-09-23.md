# Frozen launch cohort: pre-mint distribution probe (2026-09-23)

Purpose: look for an actionable source of independent attention **before** token creation. This is a research probe, not a launch recommendation or a measure of creator income.

## Fixed inputs and source

- The 210-launch baseline was frozen at 2026-09-23 22:12:54 UTC, before subsequent outcomes ([baseline artifact, run 35927052834](https://github.com/arascxe/h40-graac-canary/actions/runs/35927052834)).
- The twelve mints below are the first twelve in lexical mint order, fixed before their first-five-minute trades were read ([matured trade artifact, run 35927416350](https://github.com/arascxe/h40-graac-canary/actions/runs/35927416350)).
- At approximately 22:52 UTC, queried Pump's `GET https://frontend-api-v3.pump.fun/coins-v2/{mint}` for each of the same twelve mints and read `twitter`, `website`, `telegram`, `metadata_uri`, `created_timestamp`, and `creator`. All twelve requests succeeded. The selected fields are preserved in [`premint_distribution_12_metadata_2026-09-23.json`](premint_distribution_12_metadata_2026-09-23.json). These current metadata responses are not a historical snapshot of what the website displayed at launch. A metadata URL can point to mutable content; independently archive/hash content before using it as immutable launch evidence.
- A complete first trade page means only that this API page was complete at query time. It does not prove all addresses are independent people. The one truncated case is `UNKNOWN`, not zero.

| Launch | First 5m gross USD observed | Wallets observed | Linked socials | Pre-mint independent attention status |
| --- | ---: | ---: | --- | --- |
| Ape and Call | 265.68 | 4 | X status; old gorilla news article | X status ID decodes to ~0.5s **after** mint; old news article alone does not prove an active independent audience. Unverified. |
| PIGGWIFHAT | 22.86 | 1 | none | No linked evidence. |
| NOTHING | 2,092.72 | 13 | none | Non-creator addresses traded, but their independence and discovery source are unknown. |
| GRANDPA'S INVESTMENT | 48.22 | 2 | none | No linked evidence. |
| coin market cat | UNKNOWN | UNKNOWN | Instagram post | Trade page truncated; post timing/independence unverified. |
| PluTO$ | 1,245.53 | 7 | none | Discovery source unknown. |
| Last Sheet Regret | 65.50 | 7 | none | Discovery source unknown. |
| PUMP.FUN SHEEP | 109.31 | 2 | none | No linked evidence. |
| The Pill Experiment | 289.12 | 3 | named X account and site | Project-controlled links; prior external attention unverified. |
| Stay Golden | 678.04 | 6 | none | Discovery source unknown. |
| Grand Theft Clout | 9,362.47 | 13 | `gtc_fun` account and `gtc.fun` site | Project-controlled links; $6,660.88 of first-five-minute turnover was directly from the creator address. Remaining wallets' independence unverified. |
| 164 Bucky | 0 | 0 | X status; fat-bear page | X status ID decodes to ~187s **before** mint, but the linked account is named `thedevrrrrrrr`; authorship and independent reach unverified. No observed trades on the complete first page. |

The X status timestamps are derived from the Snowflake IDs (`(status_id >> 22) + 1288834974657` milliseconds). This establishes a platform-generated time for the linked post ID, **not** post content, author identity, engagement, or whether the link was present in mint metadata at creation. X and Instagram page content could not be independently retrieved in this probe.

Three of twelve metadata URLs use `metadata.j7tracker.io`, eight use `ipfs.io`, and one uses `cdn.fomoji.fun`. Hosting/provider identity is not creator identity or a distribution channel. The strongest early gross turnover case is among the three `j7tracker` URLs but is creator dominated; no inference about that provider's effect is warranted.

## Decision now

These twelve cases provide **zero verified pre-mint independent attention-to-buyer transitions**. The presence of social links is not a Demand-Proof gate. Likewise, the absence of a link on Pump does not mean the token had no outside distribution. We should not launch or score a coin as promising on linked socials, name, or gross early volume from this probe.

The 24-hour follow-up can establish the turnover outcome of the 210 frozen mints (where source coverage is complete). It **cannot by itself reconstruct the cause of first independent buyer arrival**. Next investigate a small, same-window outcome contrast using timestamped original posts, independent authors, link appearance before mint, and trade timestamps; if external posts cannot be recovered, mark mechanism `UNKNOWN` rather than fabricate an audience. Separately, verify creator-vault accrual and user-wallet fee receipt for any claimed successful launch.
