# New bots N1-N4: plan and pass rules (each section written and committed before that bot is run)

## Common rules (all new bots)

- Spot, long only unless the bot says otherwise, no leverage, 0.5% risk per trade sized from the stop,
  never more than the free cash, 0.1% fee each side, max 3 trades open, one $1,000 balance per test.
- Data: the long-history 4H candles from research/long_history.py (Bitfinex / Binance archive).
- Design coins: BTC, ETH, XRP, traded together on one shared balance (like v4).
  Never-seen coins: SOL, LTC, DOGE, XLM, ADA, BNB, LINK, BCH, AVAX, SUI, LUNA, FTT, each alone, fresh
  $1,000 per job-2b market period, pooled.
- Halves: 1st = 2018-05 to end of 2021, 2nd = 2022 to now (design coins). Never-seen: periods before /
  from 2022.
- Max DD is mark-to-market at every 4H close.
- Comparison set: v4 (BTC ETH XRP) and Trend Rider (BTC ETH SOL BNB SUI) as they trade, 2018-05 to now.

A bot PASSES only if ALL hold:
1. Design coins: PF above 1.0 and profit in BOTH halves.
2. Design coins: max DD not worse than -10% in either half.
3. Never-seen coins: pooled PF above 1.0 in both halves.
4. Diversifies: correlation of its monthly returns with v4 + Trend Rider (50/50) below 0.5, AND a
   1/3 v4 + 1/3 Trend Rider + 1/3 new bot portfolio has a higher return / max DD (2018-05 to now)
   than 1/2 v4 + 1/2 Trend Rider. (A bot that makes the portfolio no better is not worth running.)
If more than one variant passes, take the one with the biggest gain in criterion 4.

## N1. Range bot (4H)

Range = highest high and lowest low of the last N candles (not counting the current one); width W =
(high - low) / low.
"Not trending" = ADX(14) on 4H below 20.
Entry: ADX < 20, W between 4% and 25%, and the candle closes in the bottom 20% of the range.
Stop: range low - 0.5 x ATR(14) (a range break exits). Exit at the target, or after 30 candles.

Variants:
- R1: N = 60 candles (10 days), target = 80% of the way up the range.
- R2: N = 60, target = middle of the range (50%).
- R3: N = 120 candles (20 days), target = 80% of the range.
