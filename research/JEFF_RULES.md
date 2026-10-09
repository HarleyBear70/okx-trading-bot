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

## Oct 9: trailing exits (Jeff), with/without rules 17 and 19, 15m and 1H

`python3 research/jeff_rules.py trail`. target + trail = as before; trail only = no target, trailing stop is the only exit; trail after 2R = stop stays put until +2R, then trails. Rule 17's 2x is still measured to the nearest swing high (that's the only target the rules give).

### 1H chart, main: BTC ETH SOL XRP BNB (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A, Pivot zones | 36 | 0.1 | 39% | +1.61R | -0.93R | 1.9 | 1.10 | +0.06R | 10R | 0.86 | 1.55 | 0.44 | 2.06 |
| Way B, stop at bottom | 191 | 0.5 | 31% | +1.48R | -1.04R | 2.0 | 0.65 | -0.25R | 62R | 0.76 | 0.57 | 0.65 | 0.64 |
| Way B, stop halfway | 129 | 0.3 | 26% | +2.75R | -1.34R | 2.9 | 0.73 | -0.26R | 37R | 0.81 | 0.68 | 0.86 | 0.64 |
| Range, target + trail | 51 | 0.1 | 27% | +1.13R | -0.95R | 1.6 | 0.45 | -0.38R | 25R | 0.51 | 0.38 | 0.26 | 0.63 |
| Range, target + trail + rule 17 | 17 | 0.0 | 12% | +1.60R | -0.97R | 3.6 | 0.22 | -0.67R | 14R | 0.45 | 0.00 | 0.00 | 0.55 |
| Range, target + trail + rule 19 | 14 | 0.0 | 29% | +0.81R | -0.94R | 1.7 | 0.35 | -0.44R | 6R | 0.43 | 0.22 | 0.47 | 0.26 |
| Range, target + trail + 17 + 19 | 4 | 0.0 | 0% | - | -0.91R | 3.2 | 0.00 | -0.91R | 4R | 0.00 | 0.00 | 0.00 | 0.00 |
| Range, trail only | 51 | 0.1 | 18% | +1.57R | -0.90R | 1.6 | 0.37 | -0.46R | 26R | 0.58 | 0.12 | 0.11 | 0.64 |
| Range, trail only + rule 17 | 17 | 0.0 | 12% | +1.60R | -0.97R | 3.6 | 0.22 | -0.67R | 14R | 0.45 | 0.00 | 0.00 | 0.55 |
| Range, trail only + rule 19 | 14 | 0.0 | 7% | +0.45R | -0.91R | 1.7 | 0.04 | -0.81R | 11R | 0.06 | 0.00 | 0.00 | 0.07 |
| Range, trail only + 17 + 19 | 4 | 0.0 | 0% | - | -0.91R | 3.2 | 0.00 | -0.91R | 4R | 0.00 | 0.00 | 0.00 | 0.00 |
| Range, trail after 2R | 51 | 0.1 | 22% | +1.77R | -1.03R | 1.6 | 0.47 | -0.43R | 29R | 0.72 | 0.18 | 0.18 | 0.75 |
| Range, trail after 2R + rule 17 | 17 | 0.0 | 12% | +1.60R | -1.03R | 3.6 | 0.21 | -0.73R | 14R | 0.42 | 0.00 | 0.00 | 0.49 |
| Range, trail after 2R + rule 19 | 14 | 0.0 | 7% | +0.45R | -1.01R | 1.7 | 0.03 | -0.91R | 13R | 0.05 | 0.00 | 0.00 | 0.06 |
| Range, trail after 2R + 17 + 19 | 4 | 0.0 | 0% | - | -0.91R | 3.2 | 0.00 | -0.91R | 4R | 0.00 | 0.00 | 0.00 | 0.00 |

### 1H chart, never-seen: ADA DOGE LINK AVAX LTC DOT (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Way A, Pivot zones | 30 | 0.1 | 50% | +0.93R | -0.93R | 1.2 | 1.00 | +0.00R | 5R | 0.53 | 1.84 | 0.92 | 1.21 |
| Way B, stop at bottom | 218 | 0.5 | 39% | +1.45R | -1.04R | 2.3 | 0.89 | -0.07R | 42R | 0.51 | 1.25 | 0.74 | 1.17 |
| Way B, stop halfway | 135 | 0.3 | 31% | +1.76R | -1.23R | 2.5 | 0.65 | -0.30R | 44R | 0.62 | 0.66 | 0.63 | 0.67 |
| Range, target + trail | 58 | 0.1 | 40% | +1.13R | -0.90R | 2.0 | 0.82 | -0.10R | 12R | 0.40 | 1.22 | 0.73 | 0.91 |
| Range, target + trail + rule 17 | 27 | 0.1 | 33% | +1.51R | -0.83R | 3.4 | 0.91 | -0.05R | 8R | 0.28 | 1.94 | 0.98 | 0.87 |
| Range, target + trail + rule 19 | 17 | 0.0 | 41% | +1.37R | -0.98R | 2.6 | 0.98 | -0.01R | 6R | 0.15 | 1.91 | 2.36 | 0.67 |
| Range, target + trail + 17 + 19 | 10 | 0.0 | 30% | +2.20R | -0.99R | 3.5 | 0.95 | -0.03R | 4R | 0.00 | 2.33 | 4.37 | 0.55 |
| Range, trail only | 58 | 0.1 | 29% | +3.31R | -0.89R | 2.0 | 1.55 | +0.34R | 15R | 1.45 | 1.64 | 1.53 | 1.57 |
| Range, trail only + rule 17 | 27 | 0.1 | 33% | +3.90R | -0.83R | 3.4 | 2.35 | +0.75R | 8R | 2.28 | 2.47 | 4.35 | 1.02 |
| Range, trail only + rule 19 | 17 | 0.0 | 35% | +3.26R | -0.99R | 2.6 | 1.80 | +0.51R | 6R | 0.22 | 3.25 | 2.07 | 1.71 |
| Range, trail only + 17 + 19 | 10 | 0.0 | 30% | +2.75R | -0.99R | 3.5 | 1.19 | +0.13R | 4R | 0.00 | 2.91 | 6.65 | 0.55 |
| Range, trail after 2R | 58 | 0.1 | 36% | +3.46R | -1.03R | 2.0 | 1.90 | +0.59R | 17R | 1.29 | 2.48 | 1.89 | 1.91 |
| Range, trail after 2R + rule 17 | 27 | 0.1 | 41% | +4.16R | -0.99R | 3.4 | 2.90 | +1.11R | 9R | 2.02 | 4.63 | 5.02 | 1.48 |
| Range, trail after 2R + rule 19 | 17 | 0.0 | 41% | +3.25R | -1.05R | 2.6 | 2.18 | +0.72R | 6R | 0.21 | 4.11 | 1.88 | 2.30 |
| Range, trail after 2R + 17 + 19 | 10 | 0.0 | 30% | +2.75R | -1.04R | 3.5 | 1.14 | +0.10R | 4R | 0.00 | 2.63 | 4.70 | 0.55 |

### 15m chart, main: BTC ETH SOL XRP BNB (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Range, target + trail | 117 | 0.3 | 42% | +0.89R | -1.08R | 1.3 | 0.60 | -0.25R | 33R | 0.75 | 0.47 | 0.90 | 0.36 |
| Range, target + trail + rule 17 | 43 | 0.1 | 14% | +2.54R | -1.11R | 3.2 | 0.37 | -0.60R | 26R | 0.44 | 0.32 | 0.55 | 0.19 |
| Range, target + trail + rule 19 | 33 | 0.1 | 48% | +0.88R | -0.98R | 1.4 | 0.85 | -0.08R | 7R | 1.31 | 0.52 | 1.19 | 0.45 |
| Range, target + trail + 17 + 19 | 13 | 0.0 | 15% | +3.01R | -0.98R | 2.6 | 0.56 | -0.36R | 5R | 0.41 | 0.73 | 1.11 | 0.00 |
| Range, trail only | 117 | 0.3 | 26% | +2.36R | -1.07R | 1.3 | 0.76 | -0.19R | 23R | 0.79 | 0.73 | 0.80 | 0.72 |
| Range, trail only + rule 17 | 43 | 0.1 | 9% | +2.36R | -1.09R | 3.2 | 0.22 | -0.77R | 33R | 0.48 | 0.04 | 0.35 | 0.10 |
| Range, trail only + rule 19 | 33 | 0.1 | 36% | +1.11R | -1.04R | 1.4 | 0.61 | -0.26R | 10R | 0.65 | 0.55 | 0.71 | 0.49 |
| Range, trail only + 17 + 19 | 13 | 0.0 | 15% | +1.52R | -0.98R | 2.6 | 0.28 | -0.59R | 8R | 0.34 | 0.21 | 0.56 | 0.00 |
| Range, trail after 2R | 117 | 0.3 | 23% | +2.91R | -1.16R | 1.3 | 0.75 | -0.22R | 26R | 0.76 | 0.74 | 0.66 | 0.84 |
| Range, trail after 2R + rule 17 | 43 | 0.1 | 12% | +2.71R | -1.17R | 3.2 | 0.30 | -0.72R | 31R | 0.71 | 0.04 | 0.33 | 0.28 |
| Range, trail after 2R + rule 19 | 33 | 0.1 | 33% | +1.49R | -1.10R | 1.4 | 0.67 | -0.24R | 9R | 0.86 | 0.45 | 0.56 | 0.82 |
| Range, trail after 2R + 17 + 19 | 13 | 0.0 | 23% | +2.39R | -1.06R | 2.6 | 0.68 | -0.26R | 4R | 1.13 | 0.20 | 0.52 | 0.87 |

### 15m chart, never-seen: ADA DOGE LINK AVAX LTC DOT (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Range, target + trail | 152 | 0.4 | 42% | +0.94R | -1.02R | 1.2 | 0.66 | -0.20R | 32R | 0.74 | 0.60 | 0.58 | 0.75 |
| Range, target + trail + rule 17 | 46 | 0.1 | 22% | +1.93R | -1.04R | 2.9 | 0.52 | -0.40R | 18R | 0.69 | 0.36 | 0.45 | 0.56 |
| Range, target + trail + rule 19 | 39 | 0.1 | 41% | +1.05R | -1.03R | 1.2 | 0.71 | -0.17R | 12R | 1.47 | 0.26 | 0.66 | 0.79 |
| Range, target + trail + 17 + 19 | 9 | 0.0 | 33% | +2.36R | -1.01R | 2.4 | 1.17 | +0.11R | 4R | 1.92 | 0.00 | 2.42 | 0.60 |
| Range, trail only | 152 | 0.4 | 24% | +2.32R | -0.98R | 1.2 | 0.76 | -0.18R | 31R | 0.55 | 0.94 | 0.53 | 1.00 |
| Range, trail only + rule 17 | 46 | 0.1 | 20% | +2.34R | -1.05R | 2.9 | 0.54 | -0.38R | 18R | 0.56 | 0.53 | 0.53 | 0.56 |
| Range, trail only + rule 19 | 39 | 0.1 | 26% | +3.12R | -1.08R | 1.2 | 1.00 | -0.00R | 10R | 1.50 | 0.63 | 0.61 | 1.52 |
| Range, trail only + 17 + 19 | 9 | 0.0 | 33% | +2.52R | -1.01R | 2.4 | 1.25 | +0.17R | 4R | 2.05 | 0.00 | 1.75 | 1.02 |
| Range, trail after 2R | 151 | 0.4 | 26% | +2.44R | -1.10R | 1.2 | 0.80 | -0.16R | 33R | 0.64 | 0.94 | 0.55 | 1.06 |
| Range, trail after 2R + rule 17 | 46 | 0.1 | 20% | +2.34R | -1.14R | 2.9 | 0.50 | -0.46R | 21R | 0.49 | 0.50 | 0.48 | 0.51 |
| Range, trail after 2R + rule 19 | 39 | 0.1 | 26% | +3.12R | -1.13R | 1.2 | 0.95 | -0.04R | 11R | 1.38 | 0.62 | 0.57 | 1.48 |
| Range, trail after 2R + 17 + 19 | 9 | 0.0 | 33% | +2.52R | -1.10R | 2.4 | 1.15 | +0.11R | 5R | 1.79 | 0.00 | 1.60 | 0.94 |


Verdict: FAILS. Main coins lose in every 1H and 15m version except 1H Way A Pivot (PF 1.10, 36 trades).
The 1H never-seen coins look great with trailing (trail after 2R PF 1.90, + rule 17 PF 2.90) but the SAME rules on the
main coins are PF 0.47 / 0.21 - when the two coin sets disagree that much on 17-58 trades it's luck, not an edge.
