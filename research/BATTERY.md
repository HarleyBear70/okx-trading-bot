# BATTERY: every bot type on 15m and 1H, crypto and forex (Oct 8 2026)

Jeff: "dca, grid, scalping, shorts, longs, buy and hold, 15 min, 1 hr, test them". Script: research/battery.py (rules in its header).
Crypto BTC ETH SOL XRP BNB (Binance, 0.05%/side); forex 7 majors + gold (OANDA Practice candles, real spread). 2019-now; entries at the next candle's open.
Directional bots 0.5% risk a trade; DCA/GRID use the whole $1,000 per instrument (forex 5x).

| Market | Chart | Strategy | 2019-now (return / worst drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|
| crypto | 1H | TR | +47% / -8% / PF 1.17 | +31% / -4% / PF 1.26 | +12% / -8% / PF 1.10 | 34% | 12.0 | 1.28 | 1.06 |
| crypto | 1H | DON | +54% / -16% / PF 1.07 | +41% / -11% / PF 1.12 | +9% / -13% / PF 1.03 | 31% | 22.7 | 1.20 | 0.93 |
| crypto | 1H | SCALP | -28% / -29% / PF 0.91 | -7% / -9% / PF 0.95 | -22% / -23% / PF 0.86 | 51% | 17.6 | 0.88 | 0.94 |
| crypto | 1H | RSI2 | -11% / -12% / PF 0.90 | -4% / -6% / PF 0.93 | -7% / -8% / PF 0.86 | 63% | 17.0 | 1.00 | 0.80 |
| crypto | 1H | HOLD | +4162% / -77% / PF 99.00 | +1068% / -77% / PF 99.00 | +267% / -61% / PF 99.00 | 100% | 0.0 | 99.00 | - |
| crypto | 1H | GRID | +63% / -61% / PF 1.07 | -10% / -61% / PF 1.02 | +81% / -29% / PF 1.24 | 87% | 160.9 | 1.07 | - |
| crypto | 15m | TR | -65% / -68% / PF 0.91 | -31% / -35% / PF 0.93 | -50% / -55% / PF 0.87 | 31% | 51.4 | 0.95 | 0.85 |
| crypto | 15m | DON | -96% / -96% / PF 0.88 | -75% / -77% / PF 0.88 | -84% / -85% / PF 0.87 | 27% | 98.3 | 0.95 | 0.80 |
| crypto | 15m | SCALP | -96% / -96% / PF 0.77 | -73% / -73% / PF 0.78 | -84% / -84% / PF 0.76 | 49% | 74.3 | 0.73 | 0.82 |
| crypto | 15m | RSI2 | -72% / -72% / PF 0.74 | -34% / -34% / PF 0.80 | -58% / -58% / PF 0.64 | 58% | 67.9 | 0.77 | 0.70 |
| crypto | 15m | HOLD | +4194% / -78% / PF 99.00 | +1068% / -78% / PF 99.00 | +268% / -60% / PF 99.00 | 100% | 0.0 | 99.00 | - |
| crypto | 15m | GRID | +111% / -58% / PF 1.08 | +31% / -58% / PF 1.05 | +62% / -35% / PF 1.16 | 87% | 181.0 | 1.08 | - |
| forex | 1H | TR | -6% / -9% / PF 0.96 | -3% / -5% / PF 0.96 | -2% / -6% / PF 0.97 | 35% | 14.9 | 1.04 | 0.88 |
| forex | 1H | DON | -27% / -29% / PF 0.93 | -11% / -12% / PF 0.95 | -18% / -20% / PF 0.90 | 31% | 30.8 | 0.98 | 0.88 |
| forex | 1H | SCALP | -39% / -39% / PF 0.82 | -22% / -22% / PF 0.82 | -22% / -23% / PF 0.82 | 49% | 20.6 | 0.82 | 0.82 |
| forex | 1H | RSI2 | -14% / -15% / PF 0.85 | -10% / -10% / PF 0.81 | -5% / -6% / PF 0.90 | 60% | 22.9 | 0.89 | 0.82 |
| forex | 1H | GRID | -56% / -56% / PF 0.89 | -49% / -50% / PF 0.85 | -13% / -19% / PF 0.98 | 84% | 198.4 | 0.89 | - |
| forex | 15m | TR | -77% / -78% / PF 0.78 | -57% / -57% / PF 0.77 | -47% / -48% / PF 0.82 | 32% | 63.6 | 0.82 | 0.75 |
| forex | 15m | DON | -98% / -98% / PF 0.71 | -95% / -95% / PF 0.70 | -71% / -71% / PF 0.85 | 27% | 126.1 | 0.72 | 0.70 |
| forex | 15m | SCALP | -99% / -99% / PF 0.59 | -92% / -92% / PF 0.59 | -88% / -88% / PF 0.65 | 47% | 86.8 | 0.61 | 0.58 |
| forex | 15m | RSI2 | -80% / -80% / PF 0.62 | -57% / -57% / PF 0.61 | -54% / -54% / PF 0.64 | 52% | 88.1 | 0.64 | 0.59 |
| forex | 15m | GRID | -57% / -58% / PF 0.90 | -49% / -51% / PF 0.87 | -16% / -22% / PF 0.98 | 84% | 217.9 | 0.90 | - |
| crypto | 1H | DCA (fixed) | +1363% / -73% / PF 2.32 | +230% / -73% | +345% / -59% / PF 1.12 | | | | |
| crypto | 15m | DCA (fixed) | +1835% / -82% / PF 2.47 | +201% / -82% | +544% / -61% / PF 1.08 | | | | |
| forex | 1H | DCA (fixed) | -32% / -66% / PF 0.75 (6 of 8 pairs wiped out) | -57% / -61% | +59% / -42% | | | | |
| forex | 15m | DCA (fixed) | -36% / -70% / PF 0.72 (6 of 8 pairs wiped out) | -61% / -65% | +67% / -41% | | | | |

DCA rows: first run let a candle fill the dip buys and the take-profit in the same candle (too kind); fixed to walk each candle low->high or high->low.

## Verdict
- **15m: every strategy loses, on crypto and forex** (scalping -96% / -99%). Costs and noise eat everything.
- **Forex 1H: everything loses** (best TR PF 0.96). Forex stays daily (RSI(2), forex_bot.py, now on the OANDA Practice account).
- **Crypto 1H: only Trend Rider's long side holds up** (long PF 1.28, shorts 1.06) - already on paper as tr1h-bnus.
- **Crypto DCA / GRID make money but with -60% to -80% drops, and less than plain buy-and-hold** (+4,162% / -77%): they are leveraged holding, not an edge. Forex DCA wipes out 6 of 8 pairs.
