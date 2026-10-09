# LEG_TEST: new Smoke Detector market-shift rule in the bots (Oct 9 2026) — KEEP THE OLD RULE IN THE BOTS

Script: research/leg_test.py. New rule = jeff_topdown.structure(leg=1), same as pine commit 520c390. Default stays off, so the bots are unchanged.

| Test | Trades | Win % | PF | R/trade | Worst drop | 2019-22 PF | 2023-now PF | Long PF |
|---|---|---|---|---|---|---|---|---|
| jeff_bot 15m A old rule | 3557 | 37% | 1.11 | +0.05R | -8.6% | 1.20 | 1.05 | 1.27 |
| jeff_bot 15m BC old rule | 558 | 40% | 0.97 | -0.01R | -3.6% | 1.02 | 0.94 | 1.14 |
| jeff_bot 15m A NEW leg rule | 10662 | 33% | 0.95 | -0.02R | -36.6% | 1.03 | 0.87 | 0.95 |
| jeff_bot 15m BC NEW leg rule | 1399 | 33% | 0.89 | -0.04R | -9.8% | 1.01 | 0.80 | 0.83 |
| brad_bot 1H main 12 old rule | 285 | 29% | 1.16 | +0.12R | -1.1% | 1.38 | 1.04 | 1.25 |
| brad_bot 1H main 12 NEW leg rule | 677 | 25% | 0.95 | -0.04R | -3.2% | 1.02 | 0.88 | 0.95 |
| brad_bot 1H never-seen 11 old rule | 249 | 33% | 1.41 | +0.29R | -0.7% | 1.47 | 1.37 | 1.60 |
| brad_bot 1H never-seen 11 NEW leg rule | 575 | 23% | 0.85 | -0.12R | -4.3% | 0.82 | 0.86 | 0.77 |

Verdict: the leg rule fires 2-3x more shifts and loses in every test (PF 0.85-0.95 vs 0.97-1.41). It shows the turn early on the chart (good for reading), but as a bot trigger it is too jumpy. The bots keep the 5-candle swing rule.
