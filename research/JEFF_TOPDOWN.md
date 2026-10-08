# JEFF_TOPDOWN: Jeff's top-down SMC process as a bot (Oct 8 2026)

Script: research/jeff_topdown.py (rules in its header), Smoke Detector engine. Costs as research/battery.py.
Each instrument its own $1,000 at 0.5% risk; portfolio = equal mix (so returns look small: x number of coins for one shared account).

## Both directions, crypto 5 coins + forex 8
| Market | Chart | Version | 2019-now (return / drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|
| crypto | 1H | A | +13% / -4% / PF 1.41 | +8% / -3% / PF 1.58 | +5% / -2% / PF 1.29 | 35% | 1.8 | 1.81 | 0.95 |
| crypto | 1H | A + max stop 1.35% | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | 0% | 0.0 | 0.00 | 0.00 |
| crypto | 1H | B | +8% / -2% / PF 1.48 | +8% / -1% / PF 2.33 | -0% / -2% / PF 0.99 | 35% | 0.9 | 1.97 | 0.96 |
| crypto | 1H | B + max stop 1.35% | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | 0% | 0.0 | 0.00 | 0.00 |
| crypto | 1H | C | +2% / -2% / PF 1.21 | +1% / -1% / PF 1.31 | +1% / -1% / PF 1.13 | 37% | 0.5 | 1.65 | 0.77 |
| crypto | 1H | C + max stop 1.35% | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | -0% / -0% / PF 0.00 | 0% | 0.0 | 0.00 | 0.00 |
| crypto | 15m | A | +17% / -9% / PF 1.11 | +13% / -6% / PF 1.20 | +4% / -9% / PF 1.05 | 37% | 8.8 | 1.27 | 0.93 |
| crypto | 15m | A + max stop 1.35% | +1% / -3% / PF 1.05 | +0% / -1% / PF 1.00 | +1% / -3% / PF 1.06 | 29% | 0.8 | 1.22 | 0.93 |
| crypto | 15m | B | +10% / -5% / PF 1.14 | +8% / -4% / PF 1.27 | +2% / -3% / PF 1.04 | 38% | 4.3 | 1.30 | 0.97 |
| crypto | 15m | B + max stop 1.35% | +1% / -2% / PF 1.14 | +0% / -1% / PF 1.42 | +1% / -2% / PF 1.10 | 34% | 0.5 | 0.94 | 1.26 |
| crypto | 15m | C | -0% / -5% / PF 0.99 | -3% / -4% / PF 0.84 | +3% / -4% / PF 1.11 | 36% | 2.7 | 1.13 | 0.85 |
| crypto | 15m | C + max stop 1.35% | +2% / -1% / PF 1.27 | -0% / -1% / PF 0.79 | +2% / -1% / PF 1.41 | 32% | 0.3 | 1.97 | 0.83 |
| forex | 1H | A | -1% / -3% / PF 0.94 | -2% / -2% / PF 0.85 | +1% / -1% / PF 1.07 | 39% | 2.2 | 1.11 | 0.77 |
| forex | 1H | B | +0% / -1% / PF 1.04 | +0% / -1% / PF 1.01 | +0% / -1% / PF 1.07 | 39% | 1.1 | 1.19 | 0.86 |
| forex | 1H | C | -1% / -2% / PF 0.75 | -2% / -2% / PF 0.44 | +0% / -1% / PF 1.29 | 35% | 0.4 | 0.89 | 0.60 |
| forex | 15m | A | -8% / -10% / PF 0.94 | -6% / -7% / PF 0.90 | -2% / -5% / PF 0.97 | 36% | 11.5 | 1.01 | 0.86 |
| forex | 15m | B | -6% / -7% / PF 0.91 | -4% / -5% / PF 0.88 | -2% / -4% / PF 0.93 | 35% | 5.9 | 0.96 | 0.85 |
| forex | 15m | C | -1% / -3% / PF 0.97 | -3% / -3% / PF 0.84 | +2% / -2% / PF 1.13 | 36% | 2.9 | 1.10 | 0.85 |

## Buys only
| Chart | Coins | Version | 2019-now | 2019-22 | 2023-now | Win % | Trades/wk |
| 1H | 23 | A longs | +5% / -1% / PF 1.41 | +4% / -1% / PF 1.85 | +1% / -1% / PF 1.15 | 36% | 3.8 |
| 1H | 23 | B longs | +2% / -1% / PF 1.37 | +2% / -0% / PF 2.04 | +0% / -1% / PF 1.02 | 34% | 1.8 |
| 15m | 5 | A longs | +23% / -7% / PF 1.26 | +16% / -3% / PF 1.54 | +6% / -7% / PF 1.12 | 38% | 4.9 |
| 15m | 5 | B longs | +11% / -4% / PF 1.30 | +10% / -1% / PF 1.86 | +1% / -4% / PF 1.05 | 40% | 2.3 |
| 1H | 23 | C longs | +1% / -1% / PF 1.13 | +0% / -0% / PF 1.18 | +0% / -1% / PF 1.09 | 35% | 1.2 |
| 1H | 23 | BC longs | +0% / -1% / PF 1.06 | -0% / -0% / PF 0.95 | +0% / -0% / PF 1.13 | 33% | 0.6 |
| 15m | 5 | C longs | +3% / -4% / PF 1.13 | +0% / -2% / PF 1.03 | +3% / -4% / PF 1.19 | 36% | 1.4 |
| 15m | 5 | BC longs | +1% / -2% / PF 1.14 | +2% / -1% / PF 1.61 | -0% / -2% / PF 0.95 | 41% | 0.7 |

## Verdict
- Version A buys (daily + 4H trend agree, then a market shift on the entry chart) make money in both halves on crypto: 15m PF 1.26 (~5 trades/week on 5 coins), 1H PF 1.41 (~4/week on 23 coins). Weaker since 2023 (PF 1.12-1.15). Weaker than Trend Rider 4H (PF 2.3), but much faster.
- Shorts lose on crypto; forex is flat to losing on 15m and 1H.
- Jeff's 1.35% max stop blocks nearly every trade (the swing stop is usually farther).
- Adding the 4H discount and a liquidity sweep (BC, Brad Guan style) cuts trades to ~0.7/week and is about break-even; definitions asked from Chrome Claude (issue #4) to make sure they match.
- Paper bot: jeff_bot.py, 15m, accounts "turnaround" (A) and "full-recipe" (BC), every 15 minutes (.github/workflows/jeff-bot.yml).
