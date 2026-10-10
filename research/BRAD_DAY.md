# BRAD_DAY: Brad's day-trade top-down method (Ep 11 + Ep 18 entry), Oct 10 2026

Jeff: "day trade first, test both zones. Swing size: test 1, 3 and 5 on every timeframe." Rules and every [CHOICE] are in the header of research/brad_day.py. 4H story -> 15m zones (discount/premium, strong/weak fib) -> 5m sweep + body-close shift -> limit at the 5m zone. Stop past the sweep + 0.05%, max 1.35%, target = next 15m swing giving 2:1+. Binance.US costs (0.04% entries/stops). BTC ETH SOL XRP, 2019 - Sep 30 2026. Trades/yr = all 4 coins together.



| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| swing 1, pivot zones | 752 | 23% | +2.94R | -1.27R | 0.68 | -0.32R | 1872R | 0.72 | 0.64 | 0.64 | 0.71 |
| swing 1, range zones | 428 | 24% | +2.83R | -1.23R | 0.71 | -0.27R | 924R | 0.76 | 0.66 | 0.66 | 0.75 |
| swing 3, pivot zones | 453 | 21% | +3.32R | -1.23R | 0.69 | -0.30R | 1070R | 0.75 | 0.65 | 0.71 | 0.67 |
| swing 3, range zones | 177 | 23% | +3.01R | -1.17R | 0.76 | -0.22R | 321R | 0.80 | 0.73 | 0.74 | 0.77 |
| swing 5, pivot zones | 295 | 20% | +3.47R | -1.22R | 0.73 | -0.26R | 608R | 0.71 | 0.74 | 0.71 | 0.74 |
| swing 5, range zones | 100 | 25% | +2.94R | -1.14R | 0.84 | -0.14R | 133R | 0.92 | 0.78 | 0.87 | 0.82 |
| swing 1, pivot zones, ZERO fees | 752 | 23% | +3.07R | -1.00R | 0.90 | -0.08R | 523R | 0.92 | 0.88 | 0.84 | 0.95 |
| swing 1, range zones, ZERO fees | 428 | 24% | +2.94R | -1.00R | 0.90 | -0.07R | 291R | 0.95 | 0.86 | 0.84 | 0.96 |
| swing 3, pivot zones, ZERO fees | 453 | 21% | +3.44R | -1.00R | 0.89 | -0.09R | 338R | 0.92 | 0.85 | 0.91 | 0.87 |
| swing 3, range zones, ZERO fees | 177 | 23% | +3.09R | -1.00R | 0.91 | -0.07R | 138R | 0.93 | 0.89 | 0.89 | 0.94 |
| swing 5, pivot zones, ZERO fees | 295 | 20% | +3.58R | -1.00R | 0.92 | -0.07R | 209R | 0.88 | 0.96 | 0.90 | 0.94 |
| swing 5, range zones, ZERO fees | 100 | 25% | +3.01R | -1.00R | 0.99 | -0.01R | 77R | 1.05 | 0.93 | 1.01 | 0.96 |

**Verdict: fails.** Best = swing 5, range zones: 100 trades/yr, PF 0.84, -0.14R. Even at ZERO fees every version is PF 0.89-0.99, so there is no raw edge. Range zones beat pivot zones at every swing size; bigger swings beat smaller. Fees cost ~0.15-0.3R a trade because 5m stops are small (median ~0.3% on BTC).

Jeff's marks (BTC 15m, Sep 29-30, body way, from the Oct 9 answer-key check): swing 1 matched 5 of 9, swing 2 3, swing 3 2, swing 5 1. The day-trade bot took NO BTC trades in that window at any swing size. Jeff has no 4H or 5m marks yet, so only the 15m can be compared.

## Oct 10 round 2: killzones + maker entry (python3 research/brad_day.py kz)

Jeff approved the 5 choices. Killzone = the limit order can only FILL 2-5 AM / 7-10 AM ET (that detail is a [GUESS], waiting for Jeff).



| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| swing 5, range zones | 100 | 25% | +2.94R | -1.14R | 0.84 | -0.14R | 133R | 0.92 | 0.78 | 0.87 | 0.82 |
| swing 5, range zones, maker entry | 100 | 25% | +3.01R | -1.07R | 0.92 | -0.07R | 99R | 0.99 | 0.86 | 0.95 | 0.90 |
| swing 5, range zones, killzones | 48 | 24% | +3.16R | -1.17R | 0.87 | -0.12R | 67R | 0.97 | 0.78 | 0.94 | 0.81 |
| swing 5, range zones, killzones, maker entry | 48 | 24% | +3.22R | -1.09R | 0.95 | -0.04R | 54R | 1.05 | 0.88 | 1.03 | 0.89 |
| swing 1, range zones | 428 | 24% | +2.83R | -1.23R | 0.71 | -0.27R | 924R | 0.76 | 0.66 | 0.66 | 0.75 |
| swing 1, range zones, maker entry | 428 | 24% | +2.94R | -1.11R | 0.81 | -0.16R | 562R | 0.86 | 0.77 | 0.75 | 0.86 |
| swing 1, range zones, killzones | 147 | 22% | +2.95R | -1.26R | 0.67 | -0.33R | 379R | 0.82 | 0.53 | 0.52 | 0.79 |
| swing 1, range zones, killzones, maker entry | 147 | 22% | +3.07R | -1.13R | 0.77 | -0.20R | 263R | 0.94 | 0.63 | 0.60 | 0.92 |

Maker entry helps every version (+0.08 to +0.10 PF). Killzones help swing 5 a little, hurt swing 1. Best: swing 5 range + killzones + maker = PF 0.95, 48 trades/yr, still losing (2019-22 1.05, 2023-now 0.88). Jeff then asked for every rule tagged [JEFF]/[BRAD]/[GUESS] before any more runs: Claude Files/From Claude/BRAD_BOT_rules_tagged.txt.

## Oct 10 round 3: Jeff's answers to the 43 rules (python3 research/brad_day.py v4)

#7 BOS only past the last HH/LL resets STRONG/WEAK, other breaks = iBOS (RangeStruct, 4H + 15m; the 5m entry trigger is unchanged, rule 25). #33 target = 15m WEAK, min 2:1. #31 stop below 5m sweep vs 15m STRONG (+0.05%). #32 caps 1.35/2/3%/none. #11 no-trade bands. #43 3% daily loss limit = 6R per UTC day at 0.5% risk, all coins one account. Swing 5, range zones, maker entry, killzones (fill time).



| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| stop below 5m sweep, cap 1.35%, no band | 46 | 19% | +3.93R | -1.07R | 0.84 | -0.14R | 60R | 0.67 | 1.00 | 0.77 | 0.90 |
| stop below 5m sweep, cap 1.35%, no trades 0.45-0.55 | 34 | 18% | +4.03R | -1.06R | 0.81 | -0.16R | 55R | 0.60 | 1.00 | 0.62 | 0.95 |
| stop below 5m sweep, cap 1.35%, no trades 0.40-0.60 | 25 | 19% | +3.88R | -1.06R | 0.85 | -0.13R | 32R | 0.72 | 0.96 | 0.57 | 1.06 |
| stop below 5m sweep, cap 2%, no band | 53 | 19% | +4.03R | -1.07R | 0.88 | -0.10R | 59R | 0.74 | 1.02 | 0.89 | 0.87 |
| stop below 5m sweep, cap 2%, no trades 0.45-0.55 | 40 | 18% | +4.23R | -1.05R | 0.85 | -0.13R | 57R | 0.68 | 1.04 | 0.76 | 0.92 |
| stop below 5m sweep, cap 2%, no trades 0.40-0.60 | 29 | 19% | +4.33R | -1.05R | 0.97 | -0.02R | 31R | 0.92 | 1.02 | 0.79 | 1.11 |
| stop below 5m sweep, cap 3%, no band | 57 | 19% | +3.93R | -1.06R | 0.88 | -0.10R | 62R | 0.77 | 0.99 | 0.86 | 0.90 |
| stop below 5m sweep, cap 3%, no trades 0.45-0.55 | 44 | 18% | +4.06R | -1.05R | 0.87 | -0.11R | 56R | 0.73 | 1.03 | 0.76 | 0.96 |
| stop below 5m sweep, cap 3%, no trades 0.40-0.60 | 31 | 20% | +3.99R | -1.05R | 0.92 | -0.06R | 30R | 0.84 | 1.01 | 0.76 | 1.05 |
| stop below 5m sweep, cap no cap, no band | 57 | 19% | +3.91R | -1.06R | 0.89 | -0.09R | 59R | 0.80 | 0.99 | 0.87 | 0.90 |
| stop below 5m sweep, cap no cap, no trades 0.45-0.55 | 44 | 19% | +4.04R | -1.05R | 0.88 | -0.10R | 53R | 0.76 | 1.02 | 0.78 | 0.96 |
| stop below 5m sweep, cap no cap, no trades 0.40-0.60 | 32 | 20% | +3.96R | -1.04R | 0.94 | -0.05R | 27R | 0.89 | 1.00 | 0.79 | 1.06 |
| stop below 15m STRONG, cap 1.35%, no band | 15 | 28% | +2.96R | -1.06R | 1.11 | +0.08R | 13R | 0.99 | 1.22 | 1.13 | 1.10 |
| stop below 15m STRONG, cap 1.35%, no trades 0.45-0.55 | 12 | 23% | +3.22R | -1.06R | 0.89 | -0.09R | 18R | 0.91 | 0.87 | 0.84 | 0.92 |
| stop below 15m STRONG, cap 1.35%, no trades 0.40-0.60 | 7 | 26% | +3.09R | -1.05R | 1.02 | +0.02R | 8R | 1.18 | 0.88 | 0.80 | 1.15 |
| stop below 15m STRONG, cap 2%, no band | 23 | 27% | +3.08R | -1.05R | 1.11 | +0.09R | 19R | 0.89 | 1.34 | 1.27 | 1.03 |
| stop below 15m STRONG, cap 2%, no trades 0.45-0.55 | 18 | 25% | +3.30R | -1.05R | 1.04 | +0.03R | 19R | 0.85 | 1.26 | 1.19 | 0.96 |
| stop below 15m STRONG, cap 2%, no trades 0.40-0.60 | 12 | 27% | +3.33R | -1.04R | 1.20 | +0.15R | 14R | 0.98 | 1.43 | 1.21 | 1.20 |
| stop below 15m STRONG, cap 3%, no band | 26 | 28% | +2.99R | -1.04R | 1.13 | +0.10R | 20R | 1.00 | 1.28 | 1.17 | 1.11 |
| stop below 15m STRONG, cap 3%, no trades 0.45-0.55 | 21 | 26% | +3.19R | -1.04R | 1.06 | +0.05R | 21R | 0.93 | 1.24 | 1.08 | 1.05 |
| stop below 15m STRONG, cap 3%, no trades 0.40-0.60 | 15 | 29% | +3.22R | -1.04R | 1.26 | +0.20R | 13R | 1.10 | 1.46 | 1.11 | 1.37 |
| stop below 15m STRONG, cap no cap, no band | 28 | 29% | +2.96R | -1.04R | 1.17 | +0.13R | 20R | 1.04 | 1.33 | 1.25 | 1.12 |
| stop below 15m STRONG, cap no cap, no trades 0.45-0.55 | 22 | 27% | +3.14R | -1.04R | 1.11 | +0.08R | 21R | 0.97 | 1.30 | 1.19 | 1.07 |
| stop below 15m STRONG, cap no cap, no trades 0.40-0.60 | 16 | 30% | +3.16R | -1.04R | 1.28 | +0.21R | 13R | 1.16 | 1.42 | 1.25 | 1.31 |

**Main coins: stop below the 15m STRONG low turns it positive** (PF 1.02-1.28 in 10 of 12 versions). Best: no cap + no trades 0.40-0.60 = PF 1.28, +0.21R, 16 trades/yr (~124 trades), halves 1.16 / 1.42. Sweep stops all lose (0.81-0.97).

**Never-seen BNB: fails.** STRONG versions PF 0.50-1.07 (5-9 trades/yr), every one < 0.6 since 2023. Sweep versions 0.46-0.76. More never-seen coins (ADA DOGE LINK LTC) being added.

### Never-seen coins, 5m (BNB ADA DOGE LINK LTC), STRONG-stop versions

| Version (5 never-seen coins: BNB ADA DOGE LINK LTC) | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| stop below 15m STRONG, cap 1.35%, no band | 18 | 25% | +3.24R | -1.06R | 1.03 | +0.02R | 30R | 1.52 | 0.76 | 1.12 | 0.96 |
| stop below 15m STRONG, cap 1.35%, no trades 0.40-0.60 | 9 | 22% | +3.19R | -1.06R | 0.84 | -0.13R | 33R | 2.08 | 0.27 | 1.17 | 0.65 |
| stop below 15m STRONG, cap 2%, no band | 27 | 23% | +3.25R | -1.05R | 0.93 | -0.06R | 39R | 1.22 | 0.73 | 0.86 | 0.99 |
| stop below 15m STRONG, cap 2%, no trades 0.40-0.60 | 14 | 22% | +3.10R | -1.05R | 0.82 | -0.15R | 30R | 1.30 | 0.51 | 0.99 | 0.71 |
| stop below 15m STRONG, cap 3%, no band | 34 | 22% | +3.17R | -1.04R | 0.85 | -0.12R | 49R | 1.10 | 0.67 | 0.82 | 0.88 |
| stop below 15m STRONG, cap 3%, no trades 0.40-0.60 | 19 | 22% | +3.02R | -1.04R | 0.80 | -0.17R | 39R | 1.22 | 0.48 | 0.94 | 0.71 |
| stop below 15m STRONG, cap no cap, no band | 40 | 23% | +3.04R | -1.04R | 0.87 | -0.10R | 42R | 1.00 | 0.75 | 0.84 | 0.90 |
| stop below 15m STRONG, cap no cap, no trades 0.40-0.60 | 23 | 22% | +2.96R | -1.03R | 0.83 | -0.14R | 31R | 1.03 | 0.64 | 1.03 | 0.70 |

**Verdict: the main-coin win does not carry over.** Best main-coin version (no cap, 0.40-0.60 band) = PF 0.83 here; all 8 versions 0.80-1.03, every one losing since 2023 (0.27-0.76). The PF 1.28 on BTC/ETH/SOL/XRP is most likely luck from picking the best of 24. Not a pass.

## Oct 10 round 4: Jeff's NEWEST leg for premium/discount, STRONG stop and WEAK target (python3 research/brad_day.py v5)

LegStruct = the Smoke Detector v22 logic (matched Jeff's BTC 5m fib). Everything else = round-3 best (swing 5 range zones, 5m sweep + shift entry, maker, killzones, no cap, 2:1 min, 3% day limit).


### Brad DAY TRADE round 4 (NEWEST leg for premium/discount, STRONG stop, WEAK target), BTC ETH SOL XRP

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| newest leg, leg swing 1, no band | 0 |
| newest leg, leg swing 1, no trades 0.40-0.60 | 0 |
| newest leg, leg swing 2, no band | 0 | 0% | - | -1.10R | 0.00 | -1.10R | 3R | 0.00 | - | 0.00 | 0.00 |
| newest leg, leg swing 2, no trades 0.40-0.60 | 0 | 0% | - | -1.05R | 0.00 | -1.05R | 1R | 0.00 | - | - | 0.00 |
| newest leg, leg swing 3, no band | 1 | 50% | +3.01R | -1.15R | 2.61 | +0.93R | 1R | 99.00 | 1.38 | 0.00 | 99.00 |
| newest leg, leg swing 3, no trades 0.40-0.60 | 0 | 33% | +2.83R | -1.15R | 1.23 | +0.17R | 2R | 99.00 | 0.00 | 0.00 | 99.00 |
| newest leg, leg swing 5, no band | 2 | 20% | +2.28R | -1.06R | 0.53 | -0.40R | 7R | 0.36 | 0.78 | 1.12 | 0.25 |
| newest leg, leg swing 5, no trades 0.40-0.60 | 1 | 38% | +2.28R | -1.07R | 1.28 | +0.19R | 4R | 0.64 | 3.62 | 1.49 | 0.98 |

### Brad DAY TRADE round 4 (NEWEST leg for premium/discount, STRONG stop, WEAK target), BNB ADA DOGE LINK LTC

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| newest leg, leg swing 1, no band | 0 |
| newest leg, leg swing 1, no trades 0.40-0.60 | 0 |
| newest leg, leg swing 2, no band | 0 | 100% | +3.15R | - | 99.00 | +3.15R | 0R | - | 99.00 | 99.00 | - |
| newest leg, leg swing 2, no trades 0.40-0.60 | 0 | 100% | +2.63R | - | 99.00 | +2.63R | 0R | - | 99.00 | 99.00 | - |
| newest leg, leg swing 3, no band | 1 | 38% | +2.54R | -1.09R | 1.40 | +0.27R | 3R | 0.58 | 4.92 | 2.11 | 1.20 |
| newest leg, leg swing 3, no trades 0.40-0.60 | 1 | 25% | +2.55R | -1.09R | 0.78 | -0.18R | 2R | 0.78 | - | 2.11 | 0.00 |
| newest leg, leg swing 5, no band | 3 | 50% | +2.96R | -1.06R | 2.80 | +0.95R | 4R | 2.96 | 2.54 | 5.45 | 1.64 |
| newest leg, leg swing 5, no trades 0.40-0.60 | 2 | 46% | +3.46R | -1.05R | 2.81 | +1.03R | 3R | 2.78 | 3.01 | 5.55 | 0.75 |

**Verdict: almost no trades (0-3 a year on 4 coins, 0-23 in 7.75 yrs).** With the stop past STRONG and the target at WEAK on the SAME small leg, 2:1 is only possible when the entry is in the bottom third of the leg (below 0.33), and small legs flip bearish often, which cancels setups (BTC leg 2: 291 setups -> 0 trades). Too few trades to judge either way.

## Oct 10 round 5: newest leg + target = -27% fib extension (2:1 measured to it) + what blocks setups (python3 research/brad_day.py v6)


### Brad DAY round 5 (NEWEST leg, STRONG stop, target -27% fib extension), BTC ETH SOL XRP

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| newest leg, leg swing 1, target -27% ext | 0 |
| newest leg, leg swing 2, target -27% ext | 1 | 27% | +2.11R | -1.06R | 0.75 | -0.19R | 5R | 0.00 | 2.04 | 0.00 | 1.21 |
| newest leg, leg swing 3, target -27% ext | 3 | 22% | +2.19R | -1.07R | 0.58 | -0.35R | 11R | 0.41 | 0.77 | 0.55 | 0.60 |
| newest leg, leg swing 5, target -27% ext | 6 | 32% | +2.69R | -1.05R | 1.20 | +0.14R | 7R | 1.20 | 1.19 | 1.69 | 0.87 |

### Brad DAY round 5 (NEWEST leg, STRONG stop, target -27% fib extension), BNB ADA DOGE LINK LTC

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| newest leg, leg swing 1, target -27% ext | 0 | 100% | +2.65R | - | 99.00 | +2.65R | 0R | 99.00 | - | - | 99.00 |
| newest leg, leg swing 2, target -27% ext | 1 | 50% | +2.73R | -1.04R | 2.62 | +0.85R | 2R | 1.68 | 5.42 | 1.94 | 4.67 |
| newest leg, leg swing 3, target -27% ext | 3 | 28% | +2.80R | -1.06R | 1.03 | +0.02R | 6R | 0.56 | 1.62 | 0.84 | 1.22 |
| newest leg, leg swing 5, target -27% ext | 9 | 35% | +3.12R | -1.05R | 1.62 | +0.42R | 8R | 2.02 | 1.15 | 2.57 | 1.02 |

### What blocks setups: newest leg, leg swing 1, target -27% ext (main coins, longs + shorts, 2019-now)

- a 5m candle touched a 15m demand zone: 178017
- touch blocked: zone not in the 15m discount: 170104
- touch blocked: price not in the 4H discount: 4769
- setup started (zone OK, 15m + 4H discount OK): 3144
- setup ended: 15m turned bearish: 3135
- liquidity swept (5m wick under the last 5m swing low): 1759
- 5m market shift after the sweep: 168
- shift blocked: target under 2:1: 91
- shift blocked: entry zone is above price: 75
- setup ended: switched to a deeper zone: 7
- order placed: 2
- setup ended: 15m turned bearish (order was waiting): 2

### What blocks setups: newest leg, leg swing 2, target -27% ext (main coins, longs + shorts, 2019-now)

- a 5m candle touched a 15m demand zone: 100306
- touch blocked: zone not in the 15m discount: 94607
- touch blocked: price not in the 4H discount: 3332
- setup started (zone OK, 15m + 4H discount OK): 2367
- setup ended: 15m turned bearish: 2334
- liquidity swept (5m wick under the last 5m swing low): 1895
- 5m market shift after the sweep: 660
- shift blocked: target under 2:1: 391
- shift blocked: entry zone is above price: 242
- order placed: 27
- setup ended: 15m turned bearish (order was waiting): 11
- FILLED (trade taken): 11
- setup ended: FILLED: 11
- setup ended: switched to a deeper zone: 6
- order missed: price hit the target before the fill: 5
- setup ended: order missed: 5

### What blocks setups: newest leg, leg swing 3, target -27% ext (main coins, longs + shorts, 2019-now)

- a 5m candle touched a 15m demand zone: 68525
- touch blocked: zone not in the 15m discount: 63214
- touch blocked: price not in the 4H discount: 2991
- setup started (zone OK, 15m + 4H discount OK): 2320
- setup ended: 15m turned bearish: 2249
- liquidity swept (5m wick under the last 5m swing low): 2084
- 5m market shift after the sweep: 1310
- shift blocked: target under 2:1: 784
- shift blocked: entry zone is above price: 463
- order placed: 63
- setup ended: 15m turned bearish (order was waiting): 29
- FILLED (trade taken): 27
- setup ended: FILLED: 27
- setup ended: switched to a deeper zone: 7
- order missed: price hit the target before the fill: 7
- setup ended: order missed: 7
- setup ended: 15m candle closed below the zone: 1

### What blocks setups: newest leg, leg swing 5, target -27% ext (main coins, longs + shorts, 2019-now)

- a 5m candle touched a 15m demand zone: 40822
- touch blocked: zone not in the 15m discount: 35492
- touch blocked: price not in the 4H discount: 2896
- 5m market shift after the sweep: 2527
- setup started (zone OK, 15m + 4H discount OK): 2434
- liquidity swept (5m wick under the last 5m swing low): 2354
- setup ended: 15m turned bearish: 2279
- shift blocked: target under 2:1: 1497
- shift blocked: entry zone is above price: 896
- order placed: 134
- setup ended: 15m turned bearish (order was waiting): 61
- FILLED (trade taken): 47
- setup ended: FILLED: 47
- order missed: price hit the target before the fill: 26
- setup ended: order missed: 26
- setup ended: 15m candle closed below the zone: 12
- setup ended: switched to a deeper zone: 9

**Verdict:** leg swing 5 is the only one with trades: main PF 1.20 (6/yr, halves 1.20/1.19), never-seen 1.62 (9/yr). Only ~47 trades on the main coins in 7.75 yrs. Biggest blockers: (1) the zone isn't in the 15m discount when price first touches it (87% of touches; the zone is then used up), (2) the 15m newest leg turns bearish before the entry (94% of setups end that way), (3) target under 2:1 (59% of shifts).

## Round 6 (Oct 10): counter-trend longs in discount while the 15m leg is DOWN (shorts = mirror)

Jeff: "could go for a long [in discount] and then when the time is right go for a short." Counter-trend setup = 15m leg DOWN, 5m wick in the 15m + 4H discount, then the same 5m sweep + shift + limit entry, stop below the sweep low, target the top of the 15m down leg or its 0.5 (2:1 min). Note: with one trade per coin, the counter-trend setups crowd out most with-trend ones, so "+ counter-trend" ~ "counter-trend ONLY".
### Brad DAY + COUNTER-TREND longs in discount / shorts in premium, BTC ETH SOL XRP

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3 with-trend only | 16 | 30% | +3.16R | -1.04R | 1.28 | +0.21R | 13R | 1.16 | 1.42 | 1.25 | 1.31 |
| R3 + counter-trend, target top of leg | 34 | 15% | +3.11R | -1.04R | 0.54 | -0.40R | 108R | 0.53 | 0.57 | 0.23 | 0.56 |
| R3 + counter-trend, target 0.5 | 3 | 11% | +2.53R | -1.01R | 0.31 | -0.61R | 18R | 0.10 | 1.12 | 2.03 | 0.24 |
| R3 counter-trend ONLY, target top of leg | 33 | 15% | +3.14R | -1.04R | 0.53 | -0.42R | 108R | 0.51 | 0.57 | 0.23 | 0.55 |
| R3 counter-trend ONLY, target 0.5 | 3 | 11% | +2.53R | -1.01R | 0.31 | -0.61R | 18R | 0.10 | 1.12 | 2.03 | 0.24 |
| R5 with-trend only | 6 | 32% | +2.69R | -1.05R | 1.20 | +0.14R | 7R | 1.20 | 1.19 | 1.69 | 0.87 |
| R5 + counter-trend, target top of leg | 43 | 12% | +4.28R | -1.03R | 0.55 | -0.41R | 164R | 0.49 | 0.88 | 0.46 | 0.57 |
| R5 + counter-trend, target 0.5 | 4 | 10% | +2.09R | -1.01R | 0.22 | -0.71R | 24R | 0.16 | 0.80 | 0.71 | 0.16 |
| R5 counter-trend ONLY, target top of leg | 43 | 12% | +4.28R | -1.03R | 0.55 | -0.41R | 164R | 0.49 | 0.88 | 0.46 | 0.57 |
| R5 counter-trend ONLY, target 0.5 | 4 | 10% | +2.09R | -1.01R | 0.22 | -0.71R | 24R | 0.16 | 0.80 | 0.71 | 0.16 |

### Brad DAY + COUNTER-TREND longs in discount / shorts in premium, BNB ADA DOGE LINK LTC

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R3 with-trend only | 23 | 22% | +2.96R | -1.03R | 0.83 | -0.14R | 31R | 1.03 | 0.64 | 1.03 | 0.70 |
| R3 + counter-trend, target top of leg | 34 | 15% | +3.44R | -1.08R | 0.58 | -0.39R | 117R | 0.59 | 0.22 | 0.54 | 0.59 |
| R3 + counter-trend, target 0.5 | 2 | 32% | +2.42R | -1.05R | 1.06 | +0.05R | 6R | 1.06 | - | 1.50 | 0.80 |
| R3 counter-trend ONLY, target top of leg | 34 | 16% | +3.44R | -1.09R | 0.59 | -0.38R | 113R | 0.60 | 0.22 | 0.54 | 0.60 |
| R3 counter-trend ONLY, target 0.5 | 2 | 32% | +2.42R | -1.05R | 1.06 | +0.05R | 6R | 1.06 | - | 1.50 | 0.80 |
| R5 with-trend only | 9 | 35% | +3.12R | -1.05R | 1.62 | +0.42R | 8R | 2.02 | 1.15 | 2.57 | 1.02 |
| R5 + counter-trend, target top of leg | 39 | 16% | +3.15R | -1.02R | 0.59 | -0.35R | 108R | 0.60 | 0.50 | 0.70 | 0.57 |
| R5 + counter-trend, target 0.5 | 3 | 15% | +1.38R | -1.02R | 0.24 | -0.66R | 13R | 0.29 | 0.00 | 0.00 | 0.29 |
| R5 counter-trend ONLY, target top of leg | 39 | 16% | +3.15R | -1.02R | 0.59 | -0.35R | 108R | 0.60 | 0.50 | 0.70 | 0.57 |
| R5 counter-trend ONLY, target 0.5 | 3 | 15% | +1.38R | -1.02R | 0.24 | -0.66R | 13R | 0.29 | 0.00 | 0.00 | 0.29 |

Verdict: counter-trend trades lose (PF 0.53-0.59 at the top-of-leg target, 0.2-0.3 at the 0.5). Keep trading with the leg.
