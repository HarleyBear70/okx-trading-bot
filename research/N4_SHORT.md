# N4 short side (mirrored Trend Rider), backtest only

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Shorts, no leverage, 0.5% risk, 0.1% fee each side, funding ignored. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. Script: research/n4_short.py.

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| X1: pivot 5 | 1st half | 185 | 42% | +24.8% | -9.9% | 1.62 | 547 | 1.24 | -9.1% |
| X1: pivot 5 | 2nd half | 289 | 41% | -3.0% | -17.5% | 0.95 | 1125 | 1.06 | -8.8% |
| X2: pivot 5, BTC below 200-day | 1st half | 129 | 43% | +22.5% | -6.8% | 1.82 | 290 | 1.49 | -4.7% |
| X2: pivot 5, BTC below 200-day | 2nd half | 186 | 42% | -2.1% | -16.7% | 0.95 | 691 | 0.97 | -4.9% |
| X3: pivot 3 | 1st half | 203 | 45% | +34.8% | -11.6% | 1.69 | 633 | 1.15 | -9.9% |
| X3: pivot 3 | 2nd half | 354 | 41% | -6.5% | -24.0% | 0.92 | 1341 | 1.01 | -10.2% |

- X1: pivot 5: correlation with v4+TR -0.15; portfolio return/DD 12.42 (+73% / -5.9%) vs v4+TR 15.07 (+99% / -6.6%); own full period +20.8% / DD -17.5% / PF 1.18
  fail: design 2nd half not profitable (PF 0.95, -3.0%); design 2nd half DD -17.5%; portfolio return/DD 12.42 not above 15.07
- X2: pivot 5, BTC below 200-day: correlation with v4+TR -0.08; portfolio return/DD 12.44 (+73% / -5.8%) vs v4+TR 15.07 (+99% / -6.6%); own full period +20.2% / DD -16.7% / PF 1.27
  fail: design 2nd half not profitable (PF 0.95, -2.1%); design 2nd half DD -16.7%; never-seen 2nd half PF 0.97; portfolio return/DD 12.44 not above 15.07
- X3: pivot 3: correlation with v4+TR -0.17; portfolio return/DD 10.76 (+74% / -6.9%) vs v4+TR 15.07 (+99% / -6.6%); own full period +24.7% / DD -24.0% / PF 1.16
  fail: design 1st half DD -11.6%; design 2nd half not profitable (PF 0.92, -6.5%); design 2nd half DD -24.0%; portfolio return/DD 10.76 not above 15.07

Result: no variant passes
