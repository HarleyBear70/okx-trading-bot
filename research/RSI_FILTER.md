# RSI_FILTER (Oct 10 2026)

Jeff's RSI rule as an optional filter: longs only when RSI(14, close) on the last closed 5m candle is above its yellow line (TradingView default SMA 14 of RSI) and above 50; shorts both below. research/rsi_filter.py.


### RSI filter (RSI 14 above/below its yellow SMA-14 line and 50), main coins BTC ETH SOL XRP

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Brad day R3, stop 15m STRONG | 16 | 30% | +3.16R | -1.04R | 1.28 | +0.21R | 13R | 1.16 | 1.42 | 1.25 | 1.31 |
| Brad day R3, stop 15m STRONG, RSI filter | 12 | 29% | +3.12R | -1.04R | 1.22 | +0.17R | 12R | 1.13 | 1.34 | 1.05 | 1.36 |
| Brad day R3, stop 5m sweep | 32 | 20% | +3.96R | -1.04R | 0.94 | -0.05R | 27R | 0.89 | 1.00 | 0.79 | 1.06 |
| Brad day R3, stop 5m sweep, RSI filter | 24 | 19% | +4.00R | -1.06R | 0.90 | -0.08R | 24R | 0.99 | 0.82 | 0.67 | 1.09 |
| Silver Bullet A 3x, near entry | 7 | 45% | +1.61R | -0.93R | 1.42 | +0.22R | 7R | 1.15 | 1.97 | 2.03 | 1.07 |
| Silver Bullet A 3x, near entry, RSI filter | 5 | 44% | +1.76R | -0.89R | 1.55 | +0.27R | 4R | 1.34 | 2.11 | 2.16 | 1.17 |
| Silver Bullet A 3x, 50% entry | 11 | 44% | +1.72R | -1.01R | 1.33 | +0.19R | 9R | 1.24 | 1.47 | 1.69 | 1.12 |
| Silver Bullet A 3x, 50% entry, RSI filter | 7 | 47% | +1.84R | -0.99R | 1.66 | +0.34R | 4R | 1.75 | 1.47 | 2.90 | 1.17 |

### RSI filter (RSI 14 above/below its yellow SMA-14 line and 50), NEVER-SEEN coins BNB ADA DOGE LINK LTC

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Brad day R3, stop 15m STRONG | 23 | 22% | +2.96R | -1.03R | 0.83 | -0.14R | 31R | 1.03 | 0.64 | 1.03 | 0.70 |
| Brad day R3, stop 15m STRONG, RSI filter | 16 | 23% | +2.94R | -1.03R | 0.84 | -0.12R | 28R | 0.88 | 0.80 | 0.91 | 0.80 |
| Brad day R3, stop 5m sweep | 35 | 16% | +4.01R | -1.06R | 0.71 | -0.26R | 72R | 0.77 | 0.63 | 0.85 | 0.59 |
| Brad day R3, stop 5m sweep, RSI filter | 27 | 17% | +4.84R | -1.06R | 0.93 | -0.06R | 34R | 0.74 | 1.17 | 1.17 | 0.74 |
| Silver Bullet A 3x, near entry | 6 | 54% | +1.23R | -0.95R | 1.54 | +0.23R | 5R | 1.17 | 2.13 | 1.49 | 1.59 |
| Silver Bullet A 3x, near entry, RSI filter | 5 | 57% | +1.04R | -1.04R | 1.33 | +0.15R | 4R | 0.97 | 1.96 | 1.53 | 1.14 |
| Silver Bullet A 3x, 50% entry | 9 | 46% | +1.77R | -1.05R | 1.46 | +0.26R | 9R | 1.32 | 1.62 | 1.26 | 1.63 |
| Silver Bullet A 3x, 50% entry, RSI filter | 6 | 37% | +1.26R | -1.04R | 0.72 | -0.18R | 12R | 0.76 | 0.66 | 0.67 | 0.76 |

**Verdict: mostly cuts trades (-25 to -35%), no consistent PF gain.** Main coins: Silver Bullet improves (1.42->1.55, 1.33->1.66), Brad day doesn't (1.28->1.22, 0.94->0.90). Never-seen coins: Silver Bullet gets WORSE (1.54->1.33, 1.46->0.72); Brad sweep-stop improves (0.71->0.93) but still loses. Not a reliable filter.
