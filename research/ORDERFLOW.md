# Order flow as a filter on the Brad bot: NOTHING PASSES (Oct 8 2026)

Asked by Chrome Claude on issue #4 (Jeff approved). Plan and pass rules written first: top of research/orderflow.py. Signal = Binance global taker-buy share per 1H candle (data.binance.vision, 2019-now); trades costed at Binance.US. 23 coins split: main 12 / never-seen 11.

| Coins | Filter | Trades/wk | Trades | Win % | PF | R/trade | 2019-22 PF | 2023-now PF | Long PF |
|---|---|---|---|---|---|---|---|---|---|
| main 12 | base | 0.7 | 285 | 29% | 1.16 | +0.12 | 1.38 | 1.04 | 1.25 |
| main 12 | delta | 0.6 | 236 | 29% | 1.16 | +0.12 | 1.23 | 1.12 | 1.23 |
| main 12 | absorb | 0.2 | 71 | 35% | 1.56 | +0.37 | 1.52 | 1.59 | 1.91 |
| main 12 | cvd | 0.5 | 214 | 30% | 1.22 | +0.16 | 1.23 | 1.22 | 1.48 |
| never-seen 11 | base | 0.6 | 249 | 33% | 1.41 | +0.29 | 1.47 | 1.37 | 1.60 |
| never-seen 11 | delta | 0.5 | 200 | 30% | 1.23 | +0.17 | 1.37 | 1.15 | 1.44 |
| never-seen 11 | absorb | 0.1 | 56 | 30% | 1.26 | +0.18 | 1.87 | 0.92 | 1.50 |
| never-seen 11 | cvd | 0.5 | 182 | 31% | 1.31 | +0.22 | 1.25 | 1.36 | 1.49 |

**Verdict: no filter is worth adding.**
- delta (shift candle won by buyers): no better on main, worse on never-seen (1.23 vs 1.41). FAIL.
- cvd (buyers out-traded sellers from sweep to shift): a bit better on main (1.22 vs 1.16), worse on never-seen (1.31 vs 1.41). FAIL.
- absorb (big sell volume on the sweep candle but it closes in its top half): best-looking on main (PF 1.56, +0.37R) but only 71 trades in 7 years, and on never-seen coins it is WORSE than base and loses since 2023 (0.92). FAIL. The most interesting one: worth re-checking in a year, not trading now.
- Crowding (funding + open interest): not tested; Binance OI history starts only late 2021.
