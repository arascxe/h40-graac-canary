# FEE100K same-window launch shadow — 2026-09-23

Status: research only; no launch, trading, user receipt or production selector change.

## Source and failures

The previously published MDRTF census artifact from run `35851840827` was 564,205,426 compressed bytes. The GitHub connector rejected direct download above its 512 MiB limit. A bounded GitHub runner could restore it, but a read-only SQLite query returned `database disk image is malformed` ([run 35926876675](https://github.com/arascxe/h40-graac-canary/actions/runs/35926876675)). Do not use that artifact as a denominator or silently interpret unreadable trades as zero. Investigate backup consistency separately; this shadow did not modify the collector or its state.

The alternate first-party Pump recent-coins snapshot succeeded in [run 35927052834](https://github.com/arascxe/h40-graac-canary/actions/runs/35927052834). At **2026-09-23 22:12:54 UTC**, three 70-row pages yielded **210 unique Pump launches**, created over roughly 7.5 minutes. The complete list and creator addresses are frozen in the seven-day `matched-launch-shadow` artifact. This is a **baseline snapshot**, not proof of continuous coverage or all launches in that interval: overlap with the previous cut was not established. No high-volume outcome influenced inclusion.

## First five minutes

Twelve mints were selected by lexical mint order before fetching subsequent trades. The [matured-window run 35927416350](https://github.com/arascxe/h40-graac-canary/actions/runs/35927416350) queried first-party trade pages only after each coin was older than five minutes. Eleven had a complete first page; one was truncated and its displayed zero early trades must be **UNKNOWN**. Among the eleven complete observations, first-five-minute gross trade amounts ranged from $0 to $9,362.47. A single returned page marked complete is source pagination completeness at query time; it does not certify identity or economic independence.

Four cases were then deliberately chosen after seeing the twelve early amounts, solely to investigate the mechanism. This **retrospective 4-case probe** is not prospective predictive performance. [Run 35927736130](https://github.com/arascxe/h40-graac-canary/actions/runs/35927736130) returned:

| Mint/name | First 5m gross USD | Trades | Addresses | Direct creator-address gross USD | Largest wallet share |
| --- | ---: | ---: | ---: | ---: | ---: |
| `39yyKzPL...` Grand Theft Clout | 9,362.47 | 26 | 13 | 6,660.88 | 71.14% |
| `2Di2EFr...` NOTHING | 2,092.72 | 24 | 13 | 8.81 | 23.27% |
| `2E3wgKG...` GRANDPA'S INVESTMENT | 48.22 | 17 | 2 | 23.41 | 51.45% |
| `3Lit1s5Z...` 164 Bucky | 0 | 0 | 0 | 0 | n/a |

Grand Theft Clout's largest wallet was the creator address in this direct-address comparison: $6,660.88 / $9,362.47 = 71.14%. The remaining $2,701.59 is **not proven independent**: funding links, beneficial ownership and coordinated wallets were not tested. NOTHING has a wider direct-address distribution, but 13 addresses do not establish 13 people or lasting demand. The early five-minute gross amounts are not eligible canonical 24-hour turnover, creator fees, cash receipts or net profit. No mint here has a verified fee claim to the user's wallet.

## Next decision, frozen before 24h outcomes

At or after **2026-09-24 22:13 UTC** (September 25 01:13 Türkiye time), follow the **same 210 frozen mint IDs**. Record 24-hour canonical turnover where source coverage permits, pool identity, source gaps, direct creator participation, and fee-owner/recipient configuration. Report missing pairs and missing trade history as UNKNOWN. Do not call 164 Bucky a 24-hour failure from its first five minutes alone. Compare same-age high and low outcomes only after all eligible IDs and gaps are counted; inspect pre-mint independent distribution with timestamped original links. For a small high-outcome sample, separately reconcile mint-specific creator-vault fee flows and actual claims. Exclude direct creator turnover and flag concentration, then assess whether any feasible no-audience mechanism remains. If none emerges, report `NO_VALIDATED_ROUTE` rather than tune a score around one winner.

Immediate engineering issue: the large SQLite artifact was unreadable in a clean read-only runner. Its archive is not evidence of a healthy persisted future-only ledger. Diagnose how artifact snapshots are produced while the collector writes, without overwriting frozen evidence or disrupting production. The independent compact 210-launch snapshot is the usable baseline for this experiment.
