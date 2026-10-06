# F23: TrendSpider Sidekick's 15-minute TQQQ mean-reversion bot, on crypto (plan, written before running)

2026-10-06. Jeff shared TrendSpider's blog on its "Sidekick" AI strategy builder. Its TQQQ (stocks, ~free trading) example: entry when the close is below the lower Bollinger Band (20, 2) AND RSI(14) < 40 AND volume > its 20-bar average; exit when the close is back above SMA(20), or a 1.5 ATR stop (the end-of-day exit doesn't apply to 24/7 crypto). Reported +196% in 18.7 months, DD −12.5%. Research only. Script: research/f23_bbrsi.py. Results: research/F23.md.

Same rules on crypto at the real fee 0.35% per side, 0.5% risk, max 3 open, 2018-05 to now plus the halves:
- T1 on 1H candles, BTC ETH XRP (Binance 1H, as B1c/D1/L1).
- T2 on 4H candles, BTC ETH SOL XRP BNB.
- T3 on daily candles, BTC ETH SOL XRP BNB.
Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%.
