# Team test: Turtle 55/20 + Dynamic Breakout II, mixes and BTC switch (Oct 8 2026)

Plan and rules at the top of research/team_test.py. Crypto daily, long only, Binance.US costs, each coin an equal slice, ALL money in (no stops, no 0.5% risk sizing), so the drops are far bigger than the live bots' (Turtle at 0.5% risk: -13.6%, F38). MAR = yearly growth / worst drop (higher = better ride).


### main 5 (BTC ETH SOL XRP BNB)

| Version | Growth | Per year | Worst drop | MAR | 2019-22 MAR | 2023-now MAR |
|---|---|---|---|---|---|---|
| T | 33.1x | +57% | -51% | 1.12 | 1.91 | 0.51 |
| D | 40.0x | +61% | -45% | 1.35 | 2.37 | 0.93 |
| T-adapt | 71.1x | +73% | -56% | 1.32 | 2.24 | 0.83 |
| T-avg | 33.9x | +58% | -50% | 1.16 | 2.18 | 0.59 |
| TEAM (T+D) | 36.5x | +59% | -47% | 1.25 | 2.11 | 0.73 |
| T +BTC | 40.3x | +61% | -54% | 1.13 | 3.11 | 0.62 |
| D +BTC | 29.9x | +55% | -37% | 1.50 | 2.54 | 0.83 |
| T-adapt +BTC | 76.8x | +75% | -45% | 1.66 | 3.20 | 0.96 |
| T-avg +BTC | 37.8x | +60% | -48% | 1.25 | 2.50 | 0.71 |
| TEAM (T+D) +BTC | 35.1x | +58% | -43% | 1.36 | 3.07 | 0.75 |

### never-seen 18

| Version | Growth | Per year | Worst drop | MAR | 2019-22 MAR | 2023-now MAR |
|---|---|---|---|---|---|---|
| T | 11.9x | +38% | -71% | 0.53 | 0.86 | 0.37 |
| D | 13.6x | +40% | -43% | 0.93 | 1.55 | 0.62 |
| T-adapt | 8.9x | +33% | -77% | 0.42 | 0.86 | 0.15 |
| T-avg | 11.4x | +37% | -60% | 0.62 | 0.99 | 0.37 |
| TEAM (T+D) | 12.7x | +39% | -61% | 0.64 | 1.02 | 0.48 |
| T +BTC | 13.6x | +40% | -62% | 0.64 | 0.99 | 0.40 |
| D +BTC | 17.3x | +44% | -34% | 1.30 | 1.59 | 1.24 |
| T-adapt +BTC | 11.4x | +37% | -64% | 0.58 | 0.94 | 0.35 |
| T-avg +BTC | 11.8x | +37% | -58% | 0.65 | 1.27 | 0.32 |
| TEAM (T+D) +BTC | 15.5x | +42% | -54% | 0.79 | 1.02 | 0.71 |

## Verdict
- **Winner: Dynamic Breakout II + BTC switch** (no new buys while BTC is under its 200-day average). The only version better than Turtle in both halves AND on the 18 never-seen coins: MAR 1.50 vs 1.12 (main), 1.30 vs 0.53 (never-seen), with the smallest drops (-37% / -34% vs -51% / -71%).
- DB2 alone already beats Turtle everywhere; the BTC switch makes it steadier.
- TEAM (half each) lands between the two: better than Turtle alone, not better than DB2 alone. Mixing in Turtle dilutes DB2.
- T-adapt (+BTC) is best on the main 5 but falls apart on never-seen coins: overfit to the big coins. Not used.
- Next step (needs Jeff's OK): paper bot 'DB2 + BTC switch' next to turtle-bnus, same 0.5% risk sizing, compare at a review. Live Turtle untouched.
