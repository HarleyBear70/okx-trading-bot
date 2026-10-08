# BRAD: Brad Goh's sweep + FVG model, backtested (Oct 8 2026)

Script: research/brad_rules.py (rules in its header). Source: Jeff's notes in Claude Files/To Claude.

| Market | Chart | Version | 2019-now (return / drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|
| crypto | 1H | 2R | +2% / -1% / PF 2.02 | +0% / -0% / PF 1.57 | +1% / -1% / PF 2.32 | 52% | 0.1 | 1.97 | 2.05 |
| crypto | 1H | 3R | +2% / -1% / PF 1.98 | +0% / -0% / PF 1.07 | +2% / -1% / PF 2.59 | 41% | 0.1 | 2.92 | 1.50 |
| crypto | 1H | 2R + daily | +1% / -0% / PF 2.19 | +0% / -0% / PF 1.91 | +1% / -0% / PF 2.36 | 53% | 0.0 | 2.85 | 1.84 |
| crypto | 1H | 2R + NY time | +1% / -0% / PF 4.76 | -0% / -0% / PF 0.96 | +1% / -0% / PF 99.00 | 71% | 0.0 | 3.85 | 5.64 |
| crypto | 1H | 3R + NY time | +1% / -0% / PF 4.72 | +0% / -0% / PF 1.45 | +1% / -0% / PF 10.93 | 62% | 0.0 | 5.84 | 4.19 |
| crypto | 15m | 2R | -3% / -3% / PF 0.75 | -1% / -1% / PF 0.77 | -2% / -2% / PF 0.73 | 30% | 0.4 | 0.76 | 0.74 |
| crypto | 15m | 3R | -2% / -3% / PF 0.85 | -0% / -1% / PF 0.96 | -2% / -3% / PF 0.76 | 24% | 0.4 | 0.93 | 0.78 |
| crypto | 15m | 2R + daily | -3% / -3% / PF 0.59 | -1% / -1% / PF 0.69 | -2% / -2% / PF 0.52 | 25% | 0.2 | 0.65 | 0.51 |
| crypto | 15m | 2R + NY time | -1% / -2% / PF 0.58 | -1% / -1% / PF 0.45 | -1% / -1% / PF 0.68 | 26% | 0.1 | 0.62 | 0.55 |
| crypto | 15m | 3R + NY time | -0% / -2% / PF 0.91 | +0% / -1% / PF 1.14 | -0% / -1% / PF 0.79 | 26% | 0.1 | 0.79 | 1.04 |
| forex | 1H | 2R | +0% / -0% / PF 1.43 | +0% / -0% / PF 1.24 | +0% / -0% / PF 1.87 | 43% | 0.1 | 1.86 | 1.07 |
| forex | 1H | 3R | +1% / -0% / PF 1.58 | +0% / -0% / PF 1.68 | +0% / -0% / PF 1.40 | 36% | 0.1 | 1.55 | 1.61 |
| forex | 1H | 2R + daily | +0% / -0% / PF 1.88 | +0% / -0% / PF 1.41 | +0% / -0% / PF 2.82 | 50% | 0.0 | 1.40 | 2.83 |
| forex | 1H | 2R + NY time | +0% / -0% / PF 1.83 | -0% / -0% / PF 0.92 | +0% / -0% / PF 99.00 | 50% | 0.0 | 1.83 | 1.84 |
| forex | 1H | 3R + NY time | +0% / -0% / PF 1.39 | +0% / -0% / PF 1.11 | +0% / -0% / PF 2.82 | 33% | 0.0 | 0.70 | 2.76 |
| forex | 15m | 2R | -2% / -2% / PF 0.81 | -1% / -1% / PF 0.85 | -1% / -1% / PF 0.76 | 33% | 0.5 | 0.82 | 0.80 |
| forex | 15m | 3R | -3% / -4% / PF 0.73 | -1% / -2% / PF 0.87 | -3% / -3% / PF 0.61 | 23% | 0.6 | 0.77 | 0.71 |
| forex | 15m | 2R + daily | -1% / -1% / PF 0.89 | +0% / -1% / PF 1.11 | -1% / -1% / PF 0.66 | 35% | 0.3 | 0.87 | 0.90 |
| forex | 15m | 2R + NY time | -0% / -1% / PF 0.98 | +0% / -0% / PF 1.13 | -0% / -1% / PF 0.86 | 36% | 0.1 | 1.21 | 0.83 |
| forex | 15m | 3R + NY time | -0% / -1% / PF 0.85 | +0% / -1% / PF 1.04 | -1% / -1% / PF 0.71 | 24% | 0.1 | 1.12 | 0.68 |

## Verdict
- 1H works on paper (crypto PF ~2.0, forex PF ~1.4-1.9) but trades are rare: ~0.1/week across 5 coins (~40 trades since 2019). Too few to trust yet.
- 15m loses on both crypto and forex (PF 0.6-0.9).
- NY time window: high PF but almost no trades.
- Next: run 1H 2R as a paper bot alongside jeff_bot, or loosen the sweep window for more trades.

## More trades (research/brad_more.py: 23 coins / 8 forex, looser sweep window, discount on/off)

| Market | Chart | Sweep window | Discount rule | Target | Trades/wk | Win % | PF | R/trade | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|---|---|---|
| crypto (23) | 1H | 12 candles | on | 2R | 0.3 | 40% | 1.27 | +0.17 | 1.01 | 1.43 |
| crypto (23) | 1H | 12 candles | on | 3R | 0.3 | 28% | 1.11 | +0.08 | 1.01 | 1.16 |
| crypto (23) | 1H | 12 candles | off | 2R | 0.9 | 37% | 1.10 | +0.07 | 1.24 | 1.02 |
| crypto (23) | 1H | 12 candles | off | 3R | 0.9 | 27% | 1.06 | +0.05 | 1.28 | 0.93 |
| crypto (23) | 1H | 24 candles | on | 2R | 0.8 | 39% | 1.19 | +0.12 | 1.29 | 1.13 |
| crypto (23) | 1H | 24 candles | on | 3R | 0.8 | 30% | 1.20 | +0.15 | 1.27 | 1.16 |
| crypto (23) | 1H | 24 candles | off | 2R | 2.0 | 38% | 1.16 | +0.10 | 1.27 | 1.09 |
| crypto (23) | 1H | 24 candles | off | 3R | 2.1 | 29% | 1.15 | +0.11 | 1.32 | 1.05 |
| crypto (23) | 1H | 48 candles | on | 2R | 1.3 | 39% | 1.21 | +0.14 | 1.32 | 1.14 |
| crypto (23) | 1H | 48 candles | on | 3R | 1.3 | 31% | 1.27 | +0.20 | 1.42 | 1.18 |
| crypto (23) | 1H | 48 candles | off | 2R | 3.7 | 37% | 1.13 | +0.09 | 1.18 | 1.10 |
| crypto (23) | 1H | 48 candles | off | 3R | 3.7 | 29% | 1.17 | +0.13 | 1.28 | 1.09 |
| crypto (5) | 15m | 12 candles | on | 2R | 0.4 | 30% | 0.75 | -0.18 | 0.77 | 0.73 |
| crypto (5) | 15m | 12 candles | on | 3R | 0.4 | 24% | 0.85 | -0.12 | 0.96 | 0.76 |
| crypto (5) | 15m | 12 candles | off | 2R | 1.1 | 35% | 0.92 | -0.06 | 1.00 | 0.85 |
| crypto (5) | 15m | 12 candles | off | 3R | 1.2 | 29% | 1.10 | +0.08 | 1.29 | 0.96 |
| crypto (5) | 15m | 24 candles | on | 2R | 0.8 | 32% | 0.84 | -0.11 | 0.91 | 0.79 |
| crypto (5) | 15m | 24 candles | on | 3R | 0.9 | 26% | 0.94 | -0.05 | 0.97 | 0.91 |
| crypto (5) | 15m | 24 candles | off | 2R | 2.6 | 34% | 0.90 | -0.07 | 0.99 | 0.83 |
| crypto (5) | 15m | 24 candles | off | 3R | 2.8 | 27% | 1.00 | -0.00 | 1.08 | 0.93 |
| crypto (5) | 15m | 48 candles | on | 2R | 1.6 | 33% | 0.88 | -0.08 | 0.86 | 0.90 |
| crypto (5) | 15m | 48 candles | on | 3R | 1.6 | 26% | 0.96 | -0.03 | 0.94 | 0.98 |
| crypto (5) | 15m | 48 candles | off | 2R | 4.8 | 34% | 0.91 | -0.06 | 0.95 | 0.87 |
| crypto (5) | 15m | 48 candles | off | 3R | 4.9 | 26% | 0.94 | -0.04 | 0.96 | 0.92 |
| forex (8) | 1H | 12 candles | on | 2R | 0.1 | 43% | 1.43 | +0.26 | 1.24 | 1.87 |
| forex (8) | 1H | 12 candles | on | 3R | 0.1 | 36% | 1.58 | +0.39 | 1.68 | 1.40 |
| forex (8) | 1H | 12 candles | off | 2R | 0.2 | 36% | 1.06 | +0.04 | 0.85 | 1.33 |
| forex (8) | 1H | 12 candles | off | 3R | 0.3 | 33% | 1.38 | +0.27 | 1.17 | 1.60 |
| forex (8) | 1H | 24 candles | on | 2R | 0.1 | 39% | 1.18 | +0.11 | 1.20 | 1.15 |
| forex (8) | 1H | 24 candles | on | 3R | 0.1 | 31% | 1.28 | +0.20 | 1.71 | 0.83 |
| forex (8) | 1H | 24 candles | off | 2R | 0.6 | 32% | 0.88 | -0.09 | 0.80 | 0.97 |
| forex (8) | 1H | 24 candles | off | 3R | 0.6 | 25% | 0.92 | -0.06 | 0.91 | 0.93 |
| forex (8) | 1H | 48 candles | on | 2R | 0.2 | 39% | 1.20 | +0.13 | 1.32 | 1.05 |
| forex (8) | 1H | 48 candles | on | 3R | 0.2 | 29% | 1.15 | +0.11 | 1.41 | 0.85 |
| forex (8) | 1H | 48 candles | off | 2R | 1.1 | 33% | 0.91 | -0.06 | 0.87 | 0.95 |
| forex (8) | 1H | 48 candles | off | 3R | 1.1 | 25% | 0.93 | -0.05 | 0.89 | 0.98 |
| forex (8) | 15m | 12 candles | on | 2R | 0.5 | 33% | 0.81 | -0.14 | 0.85 | 0.76 |
| forex (8) | 15m | 12 candles | on | 3R | 0.6 | 23% | 0.73 | -0.23 | 0.87 | 0.61 |
| forex (8) | 15m | 12 candles | off | 2R | 1.8 | 35% | 0.90 | -0.08 | 0.96 | 0.83 |
| forex (8) | 15m | 12 candles | off | 3R | 2.0 | 25% | 0.84 | -0.13 | 0.90 | 0.78 |
| forex (8) | 15m | 24 candles | on | 2R | 1.1 | 31% | 0.75 | -0.18 | 0.64 | 0.91 |
| forex (8) | 15m | 24 candles | on | 3R | 1.2 | 22% | 0.74 | -0.22 | 0.68 | 0.81 |
| forex (8) | 15m | 24 candles | off | 2R | 3.8 | 34% | 0.89 | -0.07 | 0.87 | 0.92 |
| forex (8) | 15m | 24 candles | off | 3R | 4.1 | 25% | 0.86 | -0.11 | 0.80 | 0.93 |
| forex (8) | 15m | 48 candles | on | 2R | 1.8 | 31% | 0.76 | -0.17 | 0.71 | 0.83 |
| forex (8) | 15m | 48 candles | on | 3R | 2.0 | 22% | 0.75 | -0.21 | 0.75 | 0.76 |
| forex (8) | 15m | 48 candles | off | 2R | 6.3 | 34% | 0.91 | -0.06 | 0.93 | 0.88 |
| forex (8) | 15m | 48 candles | off | 3R | 6.5 | 25% | 0.90 | -0.08 | 0.90 | 0.89 |

- Best busy version: crypto 1H, 23 coins, 48-candle sweep window, no discount rule, 3R: 3.7 trades/wk, PF 1.17, +0.13R/trade, profitable in both halves.
- Best quality: same with discount on: 1.3/wk, PF 1.27, +0.20R/trade.
- 15m loses on crypto and forex at every setting; forex 1H only works at very low frequency.
- Costs here are 0.05%/side; at OKX taker 0.35% these thin edges would vanish. Binance.US-level fees or maker (limit) fills needed.
