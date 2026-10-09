# Asian range -> London push -> NY reversal: DEAD (Oct 8 2026)

Asked by Chrome Claude on issue #4 (Jeff approved). Rules, variants and pass rules were written first: see the top of research/asian_range.py. 15m candles, 2019-now, real costs (OANDA spread; crypto 0.05%/side).

**Verdict: DEAD.** Fails every pass rule on every market set. Not tweaked further (more tweaking = curve fitting).
- Even with ZERO costs: forex main PF 1.04 (+0.02R), crypto main PF 1.19 (+0.11R). So there is almost no raw edge for fees to eat.
- Only bright spot: crypto main + 4H trend PF 1.12, but the never-seen coins lose badly (PF 0.56), so it does not carry over.

### forex main: EUR GBP gold

| Version | Trades | /wk | Win % | PF | Avg R | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|---|
| A base (Asia 19-24 ET) | 288 | 0.7 | 36% | 0.87 | -0.08 | 44.0R | 0.94 | 0.81 |
| B Asia 00-05 UTC | 282 | 0.7 | 35% | 0.85 | -0.09 | 44.0R | 0.91 | 0.80 |
| C base + 4H trend | 147 | 0.4 | 36% | 0.88 | -0.07 | 32.5R | 0.83 | 0.93 |
| (info) A, no Mon/Fri | 180 | 0.4 | 36% | 0.82 | -0.11 | 25.7R | 0.88 | 0.77 |

A per market (PF): EUR_USD 0.95, GBP_USD 1.07, XAU_USD 0.74

### forex never-seen: AUD NZD CAD CHF JPY

| Version | Trades | /wk | Win % | PF | Avg R | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|---|
| A base (Asia 19-24 ET) | 629 | 1.6 | 32% | 0.63 | -0.26 | 164.5R | 0.51 | 0.76 |
| B Asia 00-05 UTC | 604 | 1.5 | 33% | 0.65 | -0.24 | 147.8R | 0.53 | 0.79 |
| C base + 4H trend | 285 | 0.7 | 28% | 0.54 | -0.34 | 97.1R | 0.46 | 0.63 |
| (info) A, no Mon/Fri | 392 | 1.0 | 30% | 0.61 | -0.29 | 116.9R | 0.45 | 0.78 |

A per market (PF): AUD_USD 0.63, NZD_USD 0.72, USD_CAD 0.60, USD_CHF 0.71, USD_JPY 0.52

### crypto main: BTC ETH SOL

| Version | Trades | /wk | Win % | PF | Avg R | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|---|
| A base (Asia 19-24 ET) | 446 | 1.1 | 38% | 0.96 | -0.03 | 31.0R | 0.89 | 1.00 |
| B Asia 00-05 UTC | 415 | 1.0 | 37% | 0.92 | -0.06 | 41.6R | 0.81 | 0.98 |
| C base + 4H trend | 212 | 0.5 | 44% | 1.12 | +0.07 | 18.7R | 1.34 | 1.03 |
| (info) A, no Mon/Fri | 311 | 0.8 | 37% | 0.90 | -0.07 | 38.9R | 0.97 | 0.86 |

A per market (PF): BTC 0.81, ETH 0.96, SOL 1.09

### crypto never-seen: XRP BNB ADA DOGE

| Version | Trades | /wk | Win % | PF | Avg R | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|---|
| A base (Asia 19-24 ET) | 604 | 1.5 | 33% | 0.69 | -0.21 | 133.3R | 0.80 | 0.62 |
| B Asia 00-05 UTC | 563 | 1.4 | 33% | 0.68 | -0.21 | 132.7R | 0.78 | 0.62 |
| C base + 4H trend | 303 | 0.7 | 29% | 0.56 | -0.32 | 105.4R | 0.65 | 0.52 |
| (info) A, no Mon/Fri | 426 | 1.1 | 31% | 0.68 | -0.22 | 101.9R | 0.72 | 0.66 |

A per market (PF): XRP 0.40, BNB 0.61, ADA 0.99, DOGE 0.70
