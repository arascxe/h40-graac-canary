# H40 GRAAC Cloudflare canary

[![Deploy to Cloudflare](https://deploy.workers.cloudflare.com/button)](https://deploy.workers.cloudflare.com/?url=https://github.com/arascxe/h40-graac-canary)

Status: engineering-only source-coverage probe. No H40 promotion and no trading authority.

The Worker runs once per minute and records coverage/recall for:
- GeckoTerminal global new pools (COLD),
- Pump.fun / PumpSwap / Raydium LaunchLab aggregate Solana program recall (WARM),
- Base Uniswap V2 factory pool births (WARM EVM canary).

## Zero-cost write discipline
COLD/WARM Solana does not persist raw signatures. It stores one aggregate recall window + coverage + checkpoint per poll.

New-pool identities are preserved as append-only **raw JSON batches per poll**, not one D1 row per pool. This is deliberate because Cloudflare D1 counts index writes too; event-per-row storage would create unnecessary write amplification.

The Worker accumulates D1 query metadata (`rows_read`, `rows_written`) and stores the measured usage in each `canary_runs` result (excluding only the final canary-run row itself). The canary therefore measures rather than guesses whether it fits the strict free envelope.

Raw transaction/trader decode is intentionally absent and belongs only to HOT anomaly promotion.

## Current EVM canary
The Base factory address is the Uniswap V2 factory deployment for chain 8453 from the current Uniswap deployment table. Base's official public RPC supports `eth_getLogs`; it is used only as an engineering source-canary path, not as a preferred chain thesis.

## Deployment package
The repository is self-contained:
- `src/index.js`
- `wrangler.jsonc`
- `migrations/0001_init.sql`
- `schema.sql`
- `package.json`

`npm run deploy` applies the remote D1 migration through the `DB` binding and deploys the Worker. Cloudflare's supported deploy flow can automatically provision D1 for a suitable repository/template.

This repository contains no Cloudflare API token or secret and no private research state.

## Zero-cost rule
Use Cloudflare Free only. If the deployment flow offers a paid upgrade, decline it; this canary is designed to remain inside the free envelope and measures its own D1 usage.

## Evaluation
Judge only by the preregistered H40 GRAAC source-coverage criteria: latency, deterministic watermark recovery, burst overflow, provider errors/429, duplicate behavior, cross-source disagreement, actual D1/Worker free-budget use, and eligible coverage. Do not inspect or tune against later winner outcomes.
