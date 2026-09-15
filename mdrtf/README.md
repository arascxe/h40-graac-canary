# MDRTF future-only runtime

This directory is isolated from the historical H40 GRAAC canary. It does not
reuse CSR signals, raw CTO rules, prior outcomes, or trading authority.

The workflow runs one prospective cut every 90 seconds for 38 cuts, restores
the latest successful state artifact, and writes one compressed rolling state
artifact per hourly job. Artifacts expire after seven days. No Telegram or
other notification is emitted.

Capital remains locked. `ROUTED_QUOTE_PASS` means only that a public Jupiter
route existed for a simulated `$50` USDC buy and immediate reverse sell inside
the declared cost and price-impact bounds. It is not a signed transaction,
contract-safety proof, or permission to trade.
