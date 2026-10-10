# BRAD_FX: best Brad day version on forex (Oct 10 2026)

Jeff's issue #4 note. Round-3 best version (BIGGER-swing STRONG/WEAK per Jeff's answer #7), real OANDA practice spreads, M5 2019-now. Sessions London 2-5 / NY 7-10 ET (no Asia); DXY (built from the ICE formula) and CFTC COT filters on/off. Rules + guesses: header of research/brad_fx.py.

**Verdict: fails.** Base London+NY PF 0.74 (12 trades/yr on 5 pairs); NY only 0.90, London only 0.60. DXY filter makes every version worse. COT filter lifts the main pairs to PF 1.47-1.95 but only 1-4 trades/yr (~10-30 trades in 7.75 yrs, far under 100) and fails on never-seen AUDUSD (0.46-0.59). Too few trades to trust.

### Brad day best version on forex, EURUSD GBPUSD GBPJPY USDJPY XAUUSD, real OANDA spreads

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| London only | 9 | 19% | +2.69R | -1.07R | 0.60 | -0.34R | 23R | 0.37 | 0.77 | 1.17 | 0.37 |
| London only, COT filter | 2 | 37% | +2.67R | -1.06R | 1.47 | +0.31R | 4R | 0.60 | 1.91 | 2.48 | 0.43 |
| London only, DXY filter | 5 | 17% | +2.74R | -1.07R | 0.51 | -0.44R | 17R | 0.29 | 0.68 | 1.01 | 0.26 |
| London only, DXY filter, COT filter | 1 | 38% | +3.19R | -1.07R | 1.79 | +0.53R | 2R | 0.00 | 3.05 | 1.60 | 2.60 |
| NY only | 8 | 25% | +2.90R | -1.07R | 0.90 | -0.08R | 11R | 0.75 | 0.99 | 1.03 | 0.84 |
| NY only, COT filter | 3 | 43% | +2.71R | -1.07R | 1.95 | +0.57R | 3R | 1.83 | 2.00 | 1.55 | 3.25 |
| NY only, DXY filter | 4 | 21% | +3.19R | -1.07R | 0.78 | -0.18R | 15R | 0.59 | 0.89 | 0.37 | 0.92 |
| NY only, DXY filter, COT filter | 1 | 33% | +2.57R | -1.08R | 1.19 | +0.14R | 2R | 0.00 | 1.80 | 0.44 | 4.61 |
| London + NY | 12 | 23% | +2.73R | -1.07R | 0.74 | -0.21R | 20R | 0.61 | 0.84 | 0.97 | 0.62 |
| London + NY, COT filter | 4 | 40% | +2.84R | -1.06R | 1.78 | +0.50R | 5R | 1.04 | 2.26 | 1.79 | 1.75 |
| London + NY, DXY filter | 6 | 19% | +2.73R | -1.07R | 0.60 | -0.34R | 17R | 0.53 | 0.66 | 0.78 | 0.51 |
| London + NY, DXY filter, COT filter | 2 | 33% | +3.17R | -1.07R | 1.49 | +0.35R | 4R | 0.00 | 3.04 | 0.91 | 5.61 |

### Brad day best version on forex, NEVER-SEEN AUDUSD, real OANDA spreads

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| London only | 1 | 18% | +2.54R | -1.07R | 0.53 | -0.41R | 7R | 0.95 | 0.40 | 0.79 | 0.00 |
| London only, COT filter | 1 | 0% | - | -1.06R | 0.00 | -1.06R | 6R | 0.00 | 0.00 | 0.00 | 0.00 |
| London only, DXY filter | 1 | 0% | - | -1.06R | 0.00 | -1.06R | 4R | - | 0.00 | 0.00 | 0.00 |
| London only, DXY filter, COT filter | 0 | 0% | - | -1.05R | 0.00 | -1.05R | 2R | - | 0.00 | - | 0.00 |
| NY only | 2 | 27% | +2.74R | -1.09R | 0.91 | -0.07R | 11R | 0.64 | 1.16 | 1.20 | 0.68 |
| NY only, COT filter | 1 | 22% | +2.23R | -1.08R | 0.59 | -0.35R | 6R | 0.00 | 1.05 | 0.00 | 0.82 |
| NY only, DXY filter | 1 | 0% | - | -1.09R | 0.00 | -1.09R | 7R | 0.00 | 0.00 | 0.00 | 0.00 |
| NY only, DXY filter, COT filter | 1 | 0% | - | -1.09R | 0.00 | -1.09R | 4R | 0.00 | 0.00 | - | 0.00 |
| London + NY | 2 | 22% | +2.39R | -1.09R | 0.63 | -0.31R | 13R | 0.31 | 0.87 | 0.68 | 0.58 |
| London + NY, COT filter | 1 | 18% | +2.23R | -1.08R | 0.46 | -0.48R | 8R | 0.00 | 0.85 | 0.00 | 0.68 |
| London + NY, DXY filter | 1 | 0% | - | -1.09R | 0.00 | -1.09R | 8R | 0.00 | 0.00 | 0.00 | 0.00 |
| London + NY, DXY filter, COT filter | 1 | 0% | - | -1.09R | 0.00 | -1.09R | 4R | 0.00 | 0.00 | - | 0.00 |
