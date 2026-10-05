# Published ideas: plan and pass rules (each written before its test is run)

## Q1. Bitcoin 21:00-23:00 UTC seasonality (Quantpedia)

Rule as published: buy at the 21:00 UTC open, sell at the 23:00 UTC close (2 hours), every day, full balance
(an allocation rule: no stop, so the 0.5%-risk rule does not apply). Data: Binance 1H (research/hourly.py).
Cost: 0.1% each side (OKX taker); also reported at 0.02% each side (maker-level) for information only.
- Q1a: every day, as published.
- Q1b: only when BTC's 30-day volatility of daily returns is above its 1-year median (published refinement).
- Q1c: Q1a on Thursdays and Fridays only (the strongest days in the article).
Pass (at 0.1% cost): profitable in BOTH halves (2018-05 to 2021, 2022 to now) AND in the never-published
period 2023-07 to now; max DD better than -10% in each half; ETH and XRP (never-seen) profitable pooled in
both halves; and the common portfolio rule (correlation below 0.5 with v4 + TR, and better portfolio return/DD).

## NNFX-style daily system (Chrome / Jeff, research only)

Daily candles. Markets: forex majors EUR/USD, GBP/USD, USD/JPY (FXCM, 2012-now, LONG + SHORT, 0.05% cost each
side) and crypto BTC, ETH, XRP (long-history data, LONG ONLY, 0.1% each side). Shorts stay research until Jeff
confirms Kraken perps access.
Money management (NNFX standard, our risk): stop 1.5 x ATR(14); the trade is two halves; half 1 takes profit at
+1 x ATR, after which half 2's stop moves to breakeven; half 2 leaves on the exit indicator (or its stop).
0.5% risk for the whole trade, no leverage, max 3 open per market group, one $1,000 balance per group.

Built one slot at a time. Every choice is made on the SELECTION period only (crypto 2018-05 to 2021, forex
2012 to 2018), scored by pooled profit factor over all 6 markets; the finished system is then judged ONCE on
the later period (crypto 2022-now, forex 2019-now) and on never-seen markets.
1. C1 confirmation (entry when it flips; exit on the opposite flip). Candidates: Aroon(25) up/down cross,
   Vortex(14) +VI/-VI cross, SSL channel(10) cross. Keep the best.
2. Baseline (only take C1 signals on the baseline's side): Kijun-sen(26), Hull MA(30), KAMA(10, 2, 30).
   Keep the best only if it beats C1 alone; otherwise no baseline.
3. Volume / strength (only enter if true): ADX(14) > 20; ADX(14) rising vs 3 days ago; ATR(14) above its
   50-day average. Keep the best only if it beats step 2.
4. Exit indicator for half 2: opposite C1 flip (default); close crosses back over the baseline (only if a
   baseline was kept); Parabolic SAR (0.02, 0.2) flip. Keep the best.
Pass for the finished system (judged on the later period): PF above 1 and profit for forex pooled AND for crypto
(BTC ETH XRP, long only) separately; group max DD better than -10%; never-seen markets profitable pooled
(crypto: SOL LTC DOGE XLM ADA BNB LINK BCH AVAX SUI, long only; forex: AUD/USD NZD/USD USD/CAD USD/CHF, long +
short); and for the crypto version the common portfolio rule (correlation below 0.5 with v4 + TR, better
portfolio return/DD).
