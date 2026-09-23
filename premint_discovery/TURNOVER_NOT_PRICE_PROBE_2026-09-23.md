# FEE100K — turnover without lasting price appreciation

UTC snapshot: 2026-09-23 21:28–21:33. Research only; no mint, trading, production change or user receipt.

## Question and bounded observations

Can a coin show material trading turnover while its price collapses? Yes. A read-only query of the **already monitored, selected** `public.fee100k_right_tail_econ_v1` mints with a latest observation in the prior six hours found 264 distinct mints; 37 had reported rolling 24-hour volume >=$1m, 23 of those had negative reported 24-hour price change, and 15 were down at least 80%. This is not the fraction among all launches, is not a fee count, and does not establish independent buyers.

Two high-volume, falling-price examples were frozen from the 20:00–21:00 UTC observation window. Free DEX Screener and GeckoTerminal pool calls at ~21:32 UTC yielded:

| Mint / name | PumpSwap pool created UTC | Reported 24h turnover | 24h price change | Current liquidity | 24h trades | Unique buyers / sellers (aggregator) |
|---|---|---:|---:|---:|---:|---:|
| `2ekqDh2VNP5mfMUh7fngof1APUBmkAsJJATmDZBapump` / EPEP | 16:45:12 | $4.631m | -91.819% | $4,279 | 10,793 buys / 10,262 sells | 2,520 / 2,433 |
| `Mt35YvgRr7Skc1f1ihAztT8MfzE3C3JvS6z6qAVpump` / WSOS | 01:09:12 | $1.968m | -99.678% | $2,529 | 46,533 buys / 816 sells | 1,967 / 54 |

These are distinct patterns. A high count of unique addresses does not establish distinct beneficial owners or independent economic risk. WSOS's very asymmetric buy/sell and buyer/seller counts deserve transaction-level diagnosis. EPEP's current website and X link cannot establish that either existed *before* its pool or brought real users. Present-day liquidity is not historical liquidity. Neither case has a mint-specific creator-fee total, a proven recipient, or a creator claim in this probe. It is therefore wrong to multiply the reported turnover by a fee tier and call it our attainable income.

Reproducible public pool references: [EPEP DEX Screener](https://api.dexscreener.com/latest/dex/tokens/2ekqDh2VNP5mfMUh7fngof1APUBmkAsJJATmDZBapump), [EPEP GeckoTerminal](https://api.geckoterminal.com/api/v2/networks/solana/pools/5XiD2kYEGd1MRrdRem7AjMVaNsej1zqdtAC2W6YHiDZ8), [WSOS DEX Screener](https://api.dexscreener.com/latest/dex/tokens/Mt35YvgRr7Skc1f1ihAztT8MfzE3C3JvS6z6qAVpump), [WSOS GeckoTerminal](https://api.geckoterminal.com/api/v2/networks/solana/pools/DYpc59VS1gBunH6RsAjrM18D3fLV5frhbZ21qAiS3Wcz). Values will move as the rolling window ages. The 264-mint query used `DISTINCT ON (mint)` ordered by latest `observed_at` in the previous six hours, followed by `volume_h24_usd >= 1000000` and `price_change_h24_pct <= -80` filters.

The previously frozen low-fee access-probe coins `7WRX...` and `ACtf...` were also checked. Their pools were created in **April**, months before the September examples. They cannot serve as same-launch-period controls. For `7WRX...`, the current DEX Screener PumpSwap pool also differs from the pool in the historical economics row, demonstrating why pool identity must be reconciled on-chain before fee attribution.

## Result for the economic strategy

Price survival is not the selection endpoint. The gating sequence for this lane is:

1. Freeze **new launches in the same time window**, including quiet failures, before seeing outcomes. Do not sample only the existing right-tail watchlist.
2. For each, measure 5m/2h/24h canonical turnover, independent makers and related-wallet concentration. Record buy/sell asymmetry and repeated maker patterns as review flags, not proof of wash trading.
3. On a small high-versus-low same-age sample, reconstruct *pre-mint* object/distribution evidence from timestamped posts and original links. Current metadata is insufficient.
4. Use `fee_audit/pool_fee_flow_v1.py` on actual eligible trades, identify recipient/share configuration, then reconcile a creator claim. Disaggregate each mint's vault contribution before calculating income.
5. Test whether genuinely independent, high-turnover cases have an observable prelaunch signature that our no-audience, zero-cost workflow can reproduce. If they are mostly inaccessible social networks or related-wallet churn, change the acquisition mechanism rather than tuning the same selector.

The new `fee_audit/turnover_quality_probe_v1.py` makes two read-only aggregator calls per mint, limits a run to four mints, and prints source time, pool candidate, turnover, transaction and unique-address aggregates with explicit UNKNOWN fields for independence, fee and pre-mint distribution. It is a triage tool, not a wash-trading detector or income calculator. A four-mint real-source smoke succeeded. Its `pumpswap` label is only an aggregator pool candidate; canonical status and program ownership require on-chain proof.

Production health cross-check at 21:28 UTC: last five minutes of cron had 47 successes, one running and zero recorded failures; the 20-member primary cohort remained 20, exact crossover matches 0, actual fee ledger rows 0. The most recent crypto bridge response was HTTP 200 but rejected as `STALE_OR_FUTURE_SNAPSHOT`, with zero valid items. Thus the earlier cron timeout episode eased, while prospective crypto coverage remained incomplete. No full seven-day result or launch-ready object is inferred.

Decision: **FIX / continue bounded shadow research**, with the independent-turnover source and pre-mint distribution as the highest-value missing evidence. No revenue or $100k probability is claimed.
