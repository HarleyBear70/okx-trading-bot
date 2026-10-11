# Candle pattern test: do the popular candle signals work?

OKX 4H candles, BTC, ETH, SOL, XRP, DOGE, SUI, BNB, AVAX, ADA. Edge = average % move 2 days after the candle minus the average move after any candle. **Real** = positive in both halves (Mar 2024 - Jun 2025 and Jul 2025 - now) and passed the shift test (p under 0.005: the same candles slid to random times did as well less than 0.5% of the time).

| Candle | Times seen | Edge 1st half | Edge 2nd half | Edge +4 days (all) | Up % | Verdict |
|---|---|---|---|---|---|---|
| Big breakout candle | 2566 | +0.81% | -0.03% | +0.41% | 48% | Mixed (works only part of the time) (p=0.00) |
| Big breakout candle + daily uptrend | 1202 | +0.84% | +0.42% | +0.80% | 48% | **Real** (p=0.00) |
| Bullish engulfing | 3547 | -0.06% | -0.06% | +0.02% | 47% | No edge (p=0.76) |
| Bullish engulfing + daily uptrend | 1539 | -0.05% | +0.59% | +0.43% | 47% | Mixed (works only part of the time) (p=0.07) |
| CRT confirmed (candle 3) | 2734 | -0.06% | -0.20% | -0.07% | 47% | No edge (p=0.88) |
| CRT confirmed (candle 3) + daily uptrend | 1185 | -0.29% | -0.18% | -0.08% | 44% | No edge (p=0.83) |
| CRT sweep (candle 2) | 10681 | -0.23% | -0.25% | -0.23% | 47% | No edge (p=1.00) |
| CRT sweep (candle 2) + daily uptrend | 4550 | -0.15% | -0.04% | -0.17% | 46% | No edge (p=0.63) |
| Hammer | 809 | -0.82% | -0.28% | -0.33% | 47% | No edge (p=0.99) |
| Hammer + daily uptrend | 318 | +0.00% | -0.97% | -0.93% | 45% | Mixed (works only part of the time) (p=0.81) |
| Inside bar breakout | 1527 | +0.48% | +0.72% | +0.52% | 49% | **Real** (p=0.00) |
| Inside bar breakout + daily uptrend | 689 | +1.04% | +0.65% | +0.94% | 48% | **Real** (p=0.00) |
| Morning star | 482 | +0.50% | -0.77% | +0.03% | 44% | Mixed (works only part of the time) (p=0.75) |
| Morning star + daily uptrend | 194 | +0.48% | -0.78% | +0.33% | 41% | Mixed (works only part of the time) (p=0.58) |
| Three white soldiers | 1618 | +1.37% | +0.65% | +1.04% | 52% | **Real** (p=0.00) |
| Three white soldiers + daily uptrend | 748 | +1.69% | +0.62% | +1.51% | 51% | **Real** (p=0.00) |

Baseline (any candle, 2-day move): first half +0.29%, second half -0.05%
