# Concept test: do Brad's concepts work on your coins?

OKX 4H candles, BTC, ETH, SOL, XRP, DOGE, SUI, BNB, AVAX, ADA. Bullish (buy) side only. Edge = average % move after the concept minus the average % move after any candle. **Real** means the 2-day edge was positive in both halves (Mar 2024 - Jun 2025 and Jul 2025 - now) AND passed the shift test: the same signals slid to random times did as well less than 0.5% of the time (p under 0.005).

## Summary (2-day move)

| Concept | Times seen | Edge 1st half | Edge 2nd half | Up % (all) | Verdict |
|---|---|---|---|---|---|
| BOS + daily uptrend | 687 | +0.56% | +0.79% | 49% | **Real** (p=0.00) |
| Break of structure | 1477 | +0.56% | +0.17% | 48% | Weak (could be luck) (p=0.02) |
| Discount zone (uptrend) | 1125 | -0.61% | +0.47% | 50% | Mixed (works only part of the time) (p=0.67) |
| FVG retest | 3273 | +0.11% | -0.32% | 46% | Mixed (works only part of the time) (p=0.84) |
| Liquidity sweep | 2458 | +0.46% | -0.22% | 53% | Mixed (works only part of the time) (p=0.28) |
| Market shift | 408 | +1.19% | -0.19% | 49% | Mixed (works only part of the time) (p=0.07) |
| Order block retest | 1050 | -0.14% | -0.15% | 46% | No edge (p=0.74) |

## Detail by time after the signal

| Concept | Half | +1 day edge | +2 day edge | +4 day edge | Up % at +2 days | Count |
|---|---|---|---|---|---|---|
| BOS + daily uptrend | first half | +0.40% | +0.56% | +0.85% | 48% | 405 |
| BOS + daily uptrend | second half | +0.43% | +0.79% | +0.97% | 51% | 282 |
| Break of structure | first half | +0.27% | +0.56% | +0.63% | 49% | 788 |
| Break of structure | second half | +0.09% | +0.17% | +0.08% | 46% | 689 |
| Discount zone (uptrend) | first half | -0.20% | -0.61% | -0.60% | 49% | 636 |
| Discount zone (uptrend) | second half | +0.11% | +0.47% | +0.41% | 52% | 489 |
| FVG retest | first half | +0.12% | +0.11% | -0.16% | 49% | 1661 |
| FVG retest | second half | -0.08% | -0.32% | -0.62% | 43% | 1612 |
| Liquidity sweep | first half | +0.23% | +0.46% | +0.70% | 56% | 1235 |
| Liquidity sweep | second half | -0.38% | -0.22% | -0.29% | 51% | 1223 |
| Market shift | first half | +0.94% | +1.19% | +1.79% | 56% | 216 |
| Market shift | second half | +0.41% | -0.19% | +0.14% | 42% | 192 |
| Order block retest | first half | -0.04% | -0.14% | +0.20% | 45% | 562 |
| Order block retest | second half | -0.24% | -0.15% | -0.34% | 47% | 488 |
| *Any candle (baseline)* | first half | | +0.29% avg | | 49% | 26298 |
| *Any candle (baseline)* | second half | | -0.05% avg | | 48% | 25137 |

## By coin (average 2-day move after the concept, full period)

| Concept | BTC | ETH | SOL | XRP | DOGE | SUI | BNB | AVAX | ADA |
|---|---|---|---|---|---|---|---|---|---|
| BOS + daily uptrend | +0.6% | +0.2% | +0.6% | +1.0% | +1.8% | +1.7% | +0.7% | -0.0% | +1.0% |
| Break of structure | +0.4% | +0.3% | +0.2% | +0.9% | +0.8% | +1.1% | +0.3% | +0.3% | +0.5% |
| Discount zone (uptrend) | +0.1% | +0.3% | -0.4% | -0.4% | -1.4% | +0.8% | +0.2% | +0.2% | +0.5% |
| FVG retest | +0.0% | -0.0% | +0.3% | +0.1% | -0.1% | +0.4% | +0.0% | -0.8% | +0.2% |
| Liquidity sweep | +0.2% | +0.5% | +0.4% | +0.0% | +0.3% | -0.7% | +0.2% | +1.0% | +0.0% |
| Market shift | +0.3% | +0.8% | +0.3% | +0.3% | +0.5% | +0.9% | +0.9% | +1.7% | +0.7% |
| Order block retest | +0.4% | +0.1% | +0.2% | +0.3% | -0.4% | +0.5% | +0.2% | -1.0% | -0.7% |

## How to read this

- A positive edge means price tended to rise more than usual after the concept appeared.
- **Real** = positive in both halves and passed the shift test (p under 0.005). p = chance that luck alone did this well. **Mixed** = worked in one half only, which usually means luck or a change in the market.
- This tests each concept on its own. A concept with no edge alone can still help as a filter together with others (that is what the bots do).
