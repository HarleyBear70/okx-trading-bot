# Candle pattern test: do the popular candle signals work?

OKX 4H candles, BTC, ETH, SOL, XRP, DOGE, SUI, BNB, AVAX, ADA. Edge = average % move 2 days after the candle minus the average move after any candle. **Real** = positive in both halves (Mar 2024 - Jun 2025 and Jul 2025 - now) and passed the shift test (p under 0.005: the same candles slid to random times did as well less than 0.5% of the time).

| Candle | Times seen | Edge 1st half | Edge 2nd half | Edge +4 days (all) | Up % | Verdict |
|---|---|---|---|---|---|---|
| Big breakout candle | 2554 | +0.81% | -0.02% | +0.43% | 49% | Mixed (works only part of the time) (p=0.00) |
| Big breakout candle + daily uptrend | 1190 | +0.84% | +0.49% | +0.86% | 48% | **Real** (p=0.00) |
| Bullish engulfing | 3527 | -0.06% | -0.07% | +0.03% | 47% | No edge (p=0.79) |
| Bullish engulfing + daily uptrend | 1519 | -0.05% | +0.62% | +0.49% | 48% | Mixed (works only part of the time) (p=0.07) |
| CRT confirmed (candle 3) | 2713 | -0.06% | -0.17% | -0.05% | 47% | No edge (p=0.85) |
| CRT confirmed (candle 3) + daily uptrend | 1164 | -0.29% | -0.06% | +0.02% | 44% | No edge (p=0.76) |
| CRT sweep (candle 2) | 10606 | -0.23% | -0.25% | -0.23% | 47% | No edge (p=1.00) |
| CRT sweep (candle 2) + daily uptrend | 4477 | -0.15% | +0.01% | -0.14% | 46% | Mixed (works only part of the time) (p=0.56) |
| Hammer | 800 | -0.82% | -0.29% | -0.35% | 47% | No edge (p=0.99) |
| Hammer + daily uptrend | 309 | +0.00% | -1.03% | -0.96% | 46% | Mixed (works only part of the time) (p=0.80) |
| Inside bar breakout | 1519 | +0.48% | +0.71% | +0.52% | 49% | **Real** (p=0.00) |
| Inside bar breakout + daily uptrend | 681 | +1.04% | +0.66% | +0.97% | 48% | **Real** (p=0.00) |
| Morning star | 478 | +0.50% | -0.73% | +0.06% | 45% | Mixed (works only part of the time) (p=0.71) |
| Morning star + daily uptrend | 190 | +0.48% | -0.62% | +0.47% | 42% | Mixed (works only part of the time) (p=0.50) |
| Three white soldiers | 1604 | +1.37% | +0.69% | +1.07% | 52% | **Real** (p=0.00) |
| Three white soldiers + daily uptrend | 738 | +1.69% | +0.72% | +1.61% | 51% | **Real** (p=0.00) |

Baseline (any candle, 2-day move): first half +0.29%, second half -0.03%
