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

## R1. Rejection block (ICT), long only, crypto 4H

Swing low = a confirmed pivot low (strength 3: lower than the 3 candles each side; known only 3 candles later).
Rejection candle = that swing-low candle, if its lower wick (min(open, close) - low) is at least 2 x its body
AND at least 0.5 x ATR(14). Zone = from the wick low up to the body low.
The zone becomes valid only when BOTH the pivot is confirmed and the "strong move" condition has happened
(no look-ahead). It expires 60 candles after the swing low; one entry per zone.
Entry: the first later 4H candle whose low trades into the zone (low <= body low) and that closes above the wick
low; buy at that close. Stop: wick low - 0.25 x ATR. Target: the highest high from the swing low to the moment
the zone became valid (the high of the move); skip if the target isn't above the entry.
- RB1: strong move = a high at least 3 x ATR above the wick low within 6 candles of the swing low.
- RB2: strong move = a break of structure: a close above the last confirmed swing high (strength 3) within 10
  candles of the swing low.
- RB3: RB1 + daily trend filter (last completed daily close above its daily 50 EMA).
Common pass rules (design BTC ETH XRP; never-seen coins; halves; 10% DD; diversification).
Difference from the earlier OB / FVG retests (score test c5 / c6, no edge): those used a candle BODY zone
(order block) or a 3-candle gap; this uses the WICK of a confirmed swing low that was followed by a strong move.

## W1. Wyckoff volume as a filter on existing entries (v4, Trend Rider, B1c)

Only entries are filtered; exits untouched. Volume = the candle's base volume; the "decision candle" is the
signal candle (v4, Trend Rider) or the 4H breakout candle (B1c).
- WV1: decision candle volume above its 20-candle average.
- WV2: effort vs result: WV1 AND the decision candle's range (high - low) above its 20-candle average
  (high volume that doesn't move price = absorption = skip).
- WV3: spring: in the last 10 candles before the decision there was a candle that broke below the lowest low of
  the 20 candles before it, closed back above that low, on volume above its 20-candle average.
Each bot judged as it trades (v4 5 coins, Trend Rider 6 coins with its fear filter, B1c 3 coins, 1H).
A filter passes for a bot only if, in BOTH halves (2018-05 to 2021, 2022-now), that bot's return / max DD is
higher and its PF is not lower than without it.
