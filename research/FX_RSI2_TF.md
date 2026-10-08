# Forex RSI(2): daily vs 4H, 2 vs 7 pairs (Oct 8 2026)

Script: research/fx_rsi2_tf.py (f39_both rules, long+short, ~1 pip cost, 0.5% risk, FXCM 2012-now).

| Chart | Pairs | RSI | 2012-now | 2019-now | Trades/yr |
|---|---|---|---|---|---|
| Daily | EUR+GBP | 5/95 | +3% / -1.3% / PF 1.35 / win 68% | PF 1.67 | 10 |
| **Daily** | **7 majors** | **5/95** | **+6% / -2.8% / PF 1.16 / win 67%** | **PF 1.33 / win 70%** | **35** |
| 4H | EUR+GBP | 5/95 | +3% / -6.5% / PF 1.03 | PF 1.11 | 76 |
| 4H | 7 majors | 5/95 | -16% / -24.0% / PF 0.95 | PF 0.93 | 257 |

Verdict: 4H is break-even to losing; daily 7 majors 5/95 chosen for the forex paper bot (forex_bot.py): most trades among the ones that make money, win ~70%. Small edge.
