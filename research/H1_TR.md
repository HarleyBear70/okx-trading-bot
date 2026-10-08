# H1-TR: Trend Rider on 1H vs 4H at the Binance.US cost (Oct 7 2026)

Script: research/h1_tr.py. Same rules, stop, 3 ATR trail, 0.4% risk, max 3 open, $1,000. 2018-now. Cost 0.07%/side (0.02% fee + 0.05% slip).

| Chart | Coins | Trades/week | Return 2018-now | Worst drop | PF | 2022-now |
|---|---|---|---|---|---|---|
| 4H (live) | design | 1.3 | +182% | -7.5% | 2.13 | +68% / -6.4% |
| 1H, daily trend | design | 4.7 | +211% | -22.7% | 1.27 | +37% / -22.7% |
| 1H, 4H trend | design | 5.8 | +177% | -18.1% | 1.21 | +44% / -18.1% |
| 4H (live) | never-seen | 1.3 | +98% | -13.9% | 1.62 | +13% / -10.5% |
| 1H, daily trend | never-seen | 4.7 | +34% | -38.1% | 1.07 | -24% / -34.7% |
| 1H, 4H trend | never-seen | 6.2 | +81% | -29.5% | 1.11 | +2% / -29.0% |

At 0.15%/side (the old test cost) both 1H versions lose since 2022.

Verdict: 1H gives ~4x more trades but about the same profit with 2.5-3x deeper drops, and loses on never-seen coins since 2022. Per unit of pain, 4H is ~3x better: 4H at higher risk beats 1H at the same drop. Faster action = more trades, not more money. Better way to get more trades: same 4H rules on more coins.
