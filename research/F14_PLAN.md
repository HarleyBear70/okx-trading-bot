# F14: candlestick patterns and chart patterns (plan, written before running)

2026-10-06. Jeff asked about candlestick trading and price patterns; the only earlier test was inside SP-12's checklist (a bullish candle counted against a buy). Research only. Script: research/f14_patterns.py. Results: research/F14.md.

Common rules: daily candles, BTC ETH SOL XRP BNB, long only, buy at the close of the pattern day, 0.35% risk, max 5 open, real fee 0.35% per side, 2018-05 to now plus the halves. Exit for every pattern: trail at the 10-day low (Donchian's exit, since fixed targets failed in every earlier test). Stop: below the pattern's low × 0.998, held between 1 and 3 ATR(14) below the close.

Candlesticks (in an uptrend: close above the 50-day SMA):
- C1 bullish engulfing: yesterday red, today green, today's body covers yesterday's body.
- C2 hammer after a down day: lower wick ≥ 2 × body, upper wick ≤ body, yesterday closed lower than the day before.
- C3 morning star: day 1 red with a body ≥ 0.6 ATR; day 2 body ≤ 30% of day 1's; day 3 green closing above the middle of day 1's body.
Chart patterns:
- P1 double bottom: two lows within 3% of each other, 10-60 days apart, with a peak between them at least 5% above the higher low (the neckline); buy on the first close above the neckline within 20 days of the second low. Stop below the lower of the two lows.
- P2 ascending triangle: in the last 30 days, a flat top (2+ separate highs within 1.5% of the 30-day high) and rising lows (the lowest low of the last 10 days ≥ 2% above the lowest low of days 11-30); buy on a close above the flat top. Stop below the last 10 days' low.

Pass (strict, as F13): positive in both halves, PF ≥ 1.3, DD ≤ 10%, positive in both halves on never-seen coins, monthly correlation with Donchian < 0.8.

## F14b (added after the F14 run, before running these)
P1 (double bottom) and P2 (ascending triangle) passed every strict rule, with drops of only 2.7% / 3.7% at 0.35% risk. Same rules at 1% risk (do they stay under 10%?), on the design coins and on never-seen coins.
