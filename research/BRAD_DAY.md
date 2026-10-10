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
