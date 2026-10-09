# JEFF_RULES: Jeff's own rules (rules/JEFF_RULES_from_Brad.txt), tested exactly (Oct 9 2026)

Script: research/jeff_rules.py (its header lists how each rule is measured; Claude's measuring choices are marked [CHOICE]). OPEN items not used.


### main: BTC ETH SOL XRP BNB (Binance.US 0.05% a side unless noted)

| Version | Trades | /wk | Win % | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A, Pivot zones | 43 | 0.1 | 35% | 1.6 | 0.37 | -0.43R | 19R | 0.25 | 0.47 | 0.66 | 0.10 |
| Way A, Range zones | 117 | 0.3 | 42% | 1.3 | 0.60 | -0.25R | 33R | 0.75 | 0.47 | 0.90 | 0.36 |
| Way B, stop at bottom | 402 | 1.0 | 30% | 2.1 | 0.41 | -0.55R | 221R | 0.44 | 0.39 | 0.45 | 0.39 |
| Way B, stop halfway | 248 | 0.6 | 25% | 3.0 | 0.45 | -0.65R | 163R | 0.29 | 0.58 | 0.42 | 0.47 |
| Way A Pivot, zero fees | 43 | 0.1 | 35% | 1.6 | 0.57 | -0.24R | 14R | 0.40 | 0.72 | 0.94 | 0.21 |
| Way A Range, zero fees | 117 | 0.3 | 44% | 1.3 | 0.87 | -0.07R | 15R | 1.01 | 0.75 | 1.27 | 0.55 |
| Way B bottom, zero fees | 402 | 1.0 | 32% | 2.1 | 0.70 | -0.20R | 80R | 0.65 | 0.74 | 0.75 | 0.66 |
| Way A Pivot, OKX 0.35% | 43 | 0.1 | 12% | 1.6 | 0.04 | -1.60R | 69R | 0.02 | 0.05 | 0.08 | 0.00 |

### never-seen: ADA DOGE LINK AVAX LTC DOT (Binance.US 0.05% a side unless noted)

| Version | Trades | /wk | Win % | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A, Pivot zones | 56 | 0.1 | 45% | 1.2 | 0.75 | -0.14R | 11R | 1.14 | 0.49 | 0.48 | 1.12 |
| Way A, Range zones | 152 | 0.4 | 42% | 1.2 | 0.66 | -0.20R | 32R | 0.74 | 0.60 | 0.58 | 0.75 |
| Way B, stop at bottom | 429 | 1.1 | 38% | 1.8 | 0.64 | -0.29R | 137R | 0.79 | 0.56 | 0.65 | 0.62 |
| Way B, stop halfway | 267 | 0.7 | 30% | 2.5 | 0.57 | -0.43R | 124R | 0.64 | 0.53 | 0.61 | 0.54 |
| Way A Pivot, zero fees | 56 | 0.1 | 45% | 1.2 | 0.99 | -0.01R | 6R | 1.40 | 0.68 | 0.63 | 1.47 |
| Way A Range, zero fees | 152 | 0.4 | 43% | 1.2 | 0.87 | -0.07R | 14R | 0.91 | 0.83 | 0.75 | 0.99 |
| Way B bottom, zero fees | 429 | 1.1 | 38% | 1.8 | 1.00 | -0.00R | 32R | 1.11 | 0.94 | 1.04 | 0.96 |
| Way A Pivot, OKX 0.35% | 56 | 0.1 | 21% | 1.2 | 0.15 | -0.94R | 53R | 0.32 | 0.05 | 0.08 | 0.23 |

## Verdict: FAILS (every version, both coin sets)

Where it loses:
- Way A almost never fires: about 1 trade per coin per year. From BTC's funnel: 3,981 15m sweeps -> 208 inside a 4H discount zone with daily trend agreeing -> 78 market shifts -> 11 pullback + rejection + strong-candle entries. Most shifts run to the nearest swing high or fail before the pullback comes.
- Even with ZERO fees, no version on the main coins gets to PF 1.0. Best: Way A Range zones, longs, zero fees PF 1.27 (but 0.90 at Binance fees). So fees are not the only problem, but they are a big one.
- Fees: on 15m the stop is small, so Binance's 0.05% a side costs about 0.2-0.35R a trade (Way B: -0.20R zero fees -> -0.55R at Binance). OKX's 0.35% wipes everything out (-1.6R a trade).
- Shorts are worse than longs on the main coins.

## Oct 9: OPEN rules 17 and 19 filled with Brad's numbers (Jeff), Way A Range zones

`python3 research/jeff_rules.py open`. Rule 17 = skip if target < 2x risk (measured before fees, at the entry price). Rule 19 = the entry candle opens 2:00-4:59 or 7:00-9:59 AM New York time (daylight saving followed).

### main: BTC ETH SOL XRP BNB (Binance.US 0.05% a side unless noted)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A Range, as before | 117 | 0.3 | 42% | +0.89R | -1.08R | 1.3 | 0.60 | -0.25R | 33R | 0.75 | 0.47 | 0.90 | 0.36 |
| + rule 17 (target 2x risk) | 43 | 0.1 | 14% | +2.54R | -1.11R | 3.2 | 0.37 | -0.60R | 26R | 0.44 | 0.32 | 0.55 | 0.19 |
| + rule 19 (killzones) | 33 | 0.1 | 48% | +0.88R | -0.98R | 1.4 | 0.85 | -0.08R | 7R | 1.31 | 0.52 | 1.19 | 0.45 |
| + rules 17 and 19 | 13 | 0.0 | 15% | +3.01R | -0.98R | 2.6 | 0.56 | -0.36R | 5R | 0.41 | 0.73 | 1.11 | 0.00 |

### never-seen: ADA DOGE LINK AVAX LTC DOT (Binance.US 0.05% a side unless noted)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A Range, as before | 152 | 0.4 | 42% | +0.94R | -1.02R | 1.2 | 0.66 | -0.20R | 32R | 0.74 | 0.60 | 0.58 | 0.75 |
| + rule 17 (target 2x risk) | 46 | 0.1 | 22% | +1.93R | -1.04R | 2.9 | 0.52 | -0.40R | 18R | 0.69 | 0.36 | 0.45 | 0.56 |
| + rule 19 (killzones) | 39 | 0.1 | 41% | +1.05R | -1.03R | 1.2 | 0.71 | -0.17R | 12R | 1.47 | 0.26 | 0.66 | 0.79 |
| + rules 17 and 19 | 9 | 0.0 | 33% | +2.36R | -1.01R | 2.4 | 1.17 | +0.11R | 4R | 1.92 | 0.00 | 2.42 | 0.60 |


Rule 17 makes it worse: win rate falls from 42% to 14-22% because the far targets rarely get hit before the stop.
Rule 19 helps on the main coins (PF 0.60 -> 0.85) but cuts trades to ~33 in 7.8 years; it fails 2023-now (0.52).
Both together: 13 and 9 trades in 7.8 years - too few to judge (never-seen PF 1.17 is 9 trades, 0 trades won since 2023).
Verdict: still FAILS.
