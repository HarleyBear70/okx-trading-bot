# QuantConnect Strategy Library vs Jeff's markets (Oct 8 2026)

83 strategies in the free library (quantconnect.com/learning/articles/investment-strategy-library); ~60 are stock-only, none crypto. Already covered here: time-series momentum (F38), coin rotation (F32, N2), forex trend/momentum (F38: fails on forex since 2019). New tests below; plan + pass rules at the top of research/qc_library.py. Their own pages: Dual Thrust on SPY Sharpe -0.17; Dynamic Breakout II EURUSD +2.3%/yr, GBPUSD negative.


### crypto main (BTC ETH SOL XRP BNB), long only

| Strategy | Trades | Win % | PF | Avg trade | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|
| Dual Thrust | 1289 | 35% | 1.82 | +2.01% | 1.98 | 1.62 |
| Dynamic Breakout II | 158 | 46% | 4.90 | +20.11% | 7.08 | 2.90 |
| Turn of the Month | 440 | 52% | 1.51 | +1.04% | 2.19 | 0.94 |

### crypto never-seen (18 coins), long only

| Strategy | Trades | Win % | PF | Avg trade | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|
| Dual Thrust | 4298 | 31% | 1.46 | +1.56% | 1.59 | 1.33 |
| Dynamic Breakout II | 509 | 36% | 3.31 | +15.72% | 4.03 | 2.52 |
| Turn of the Month | 1451 | 53% | 1.63 | +1.54% | 2.20 | 1.27 |

### forex main (EUR GBP gold), long+short

| Strategy | Trades | Win % | PF | Avg trade | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|
| Dual Thrust | 1518 | 34% | 1.08 | +0.03% | 0.97 | 1.20 |
| Dynamic Breakout II | 168 | 39% | 1.12 | +0.10% | 0.85 | 1.54 |

### forex never-seen (AUD NZD CAD CHF JPY), long+short

| Strategy | Trades | Win % | PF | Avg trade | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|
| Dual Thrust | 2585 | 34% | 0.98 | -0.01% | 1.00 | 0.94 |
| Dynamic Breakout II | 269 | 33% | 0.83 | -0.14% | 1.21 | 0.56 |

main 5: median per coin, 1x full size, 2019-now
| Strategy | Median growth | Median worst drop | Trades/coin |
|---|---|---|---|
| Dual Thrust | 27.3x | -52% | 264 |
| Dynamic Breakout II | 17.5x | -38% | 33 |
| Turtle 55/20 (your bot's rules, 1x) | 12.3x | -43% | 18 |
| Buy and hold | 22.7x | -79% | 1 |

never-seen 18: median per coin, 1x full size, 2019-now
| Strategy | Median growth | Median worst drop | Trades/coin |
|---|---|---|---|
| Dual Thrust | 1.8x | -81% | 251 |
| Dynamic Breakout II | 5.4x | -54% | 28 |
| Turtle 55/20 (your bot's rules, 1x) | 3.4x | -55% | 14 |
| Buy and hold | 2.2x | -94% | 1 |

## Verdict
- **Dynamic Breakout II (crypto, long only): PROMISING.** Passes every rule (PF 4.90 main / 3.31 never-seen, both halves). At the same 1x size it beat the live Turtle 55/20 rules on both coin sets (17.5x vs 12.3x, 5.4x vs 3.4x median per coin) with a similar worst drop. It's a close cousin of Turtle (volatility-adjusted 20-60 day breakout + Bollinger, exit at the average), so expect them to trade together. Next step if Jeff OKs: paper bot next to turtle-bnus, 0.5% risk sizing like Turtle, compare at a review.
- **Dual Thrust (crypto): FRAGILE.** PF passes, but always-in with no stop: worst drops -52% (main) / -81% (never-seen), and on never-seen coins it grew less than buy and hold. ~35 trades a coin a year. Not worth it.
- **Turn of the Month (crypto): FAIL.** Stopped working on the main coins since 2023 (PF 0.94).
- **Forex (both): FAIL.** Near break-even on EUR/GBP/gold, losing on the other pairs. Same story as F38: simple trend systems died on forex.
