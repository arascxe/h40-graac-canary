# MDRTF future-only runtime

This directory is isolated from the historical H40 GRAAC canary. It does not
reuse CSR signals, raw CTO rules, prior outcomes, or trading authority.

The workflow runs one prospective cut every 90 seconds for 210 cuts, restores
the latest successful state artifact, and writes one compressed rolling state
artifact per six-hour job. Artifacts expire after seven days. No Telegram or
other notification is emitted.

Capital remains locked. `ROUTED_QUOTE_PASS` means only that a public Jupiter
(Solana) or Kyber (Ethereum/Base/Arbitrum/BSC) route existed for a simulated
`$50` stablecoin buy and immediate reverse sell inside the declared cost bounds.
Robinhood Chain and Monad cannot pass execution until an admitted public
round-trip router exists. A route result is not a signed transaction,
contract-safety proof, or permission to trade.

`MDRTF_AFT_CAPITAL_ENGINE_V1.md` is the canonical AFT contract.
`MDRTF_FAMILY_OPTIONALITY_SHADOW_V1.md` defines the isolated paper-only early
family basket and evidence-gated leader rotation. The shadow lane cannot alter
canonical AFT decisions or unlock capital.
