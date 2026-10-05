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

## N2. Rotation bot (weekly)

Universe, as it was at the time (no survivorship): CoinMarketCap's historical snapshot for the first Sunday
of each month (coinmarketcap.com/historical/), top 10 by market cap after removing stablecoins and
wrapped coins (USDT, USDC, BUSD, DAI, TUSD, UST, USDe, USD1, WBTC). A coin with no free price data at that
date (e.g. CRO, HYPE, LEO before Bitfinex listing, glitch entries like TAGZ5) is skipped for that month;
how often this happens is reported.
Prices: Binance archive daily closes built from 4H (renamed tickers spliced: BCC->BCHABC->BCH,
VEN->VET, MATIC->POL), Bitfinex where Binance has nothing (BSV, LEO).

Every Monday 00:00 UTC: rank the universe by momentum, hold the top K at equal weight, sell the rest.
Cash when BTC's daily close is below its 200-day average. Only coins with positive momentum are held
(fewer than K if needed). 0.1% fee on every buy and sell. No stops; it is an allocation bot, so the
0.5%-risk rule is replaced by the position weights below.

Variants:
- M1: K = 3, momentum = 28-day return, equal weight (1/3 each, fully invested when on).
- M2: K = 3, momentum = 90-day return, equal weight.
- M3: as M1, but each weight is cut to 1/3 x min(1, 2% / the coin's 20-day daily volatility), so wild coins
  get less money (volatility-scaled; the rest stays in cash).

Pass rules: the common rules, adapted:
- "Design coins" = the historical top-10 universe; halves 2018-05 to 2021 / 2022 to now.
- "Never-seen coins" = the historical ranks 11-20 universe (same rules, its own run), halves as above.
- PF is over closed holdings (each buy-to-sell of a coin counts as one trade).

## N3. Squeeze breakout bot (4H, long only)

Bollinger width = (upper - lower) / middle of 20-candle, 2-standard-deviation bands.
Squeeze = width at or below its 10th percentile of the previous 540 candles (90 days).
Entry: within 6 candles after a squeeze candle, the candle closes above the upper band.
Stop: lowest low of the 20 candles before the breakout candle (the squeeze base); skip if that is more
than 10% below the close. Target: 2R. Time exit: 30 candles.

Variants:
- S1: as above.
- S2: S1 + daily trend filter (last completed daily close above its daily 50 EMA).
- S3: S1 with a stricter squeeze: width at its lowest of the previous 1080 candles (180 days).
Pass rules: the common rules.

## Box bots (B1, B2): shared definitions

Data: Binance archive 1H candles (one source per coin), with 4H candles built from them, for the design
and never-seen coins (coins with no Binance history are skipped). Common pass rules apply.
Box = highest high and lowest low of the 30 4H candles (5 days) before the candle being judged, height
between 3% and 12% of the box low. The box is frozen at the moment of the break.

## B1. Breakout retest (4H box, 1H entry)

Breakout: a 4H candle closes above the box high. Then, within the next 12 4H candles (48 hours), a 1H
candle's low comes back to within 0.2% of the old box high (or below it) and that 1H candle closes above
the box high: buy at that 1H close. Stop: back inside the box, at box high - 25% of the box height.
Exit: target or 48 1H candles. One retest entry per breakout.

Variants:
- B1a: target 2R.
- B1b: target 3R.
- B1c: target 2R, box of 60 4H candles (10 days).

## B2. Failed-breakdown reclaim (4H)

Break: a 4H candle closes below the box low. Reclaim: within N candles after that close, a 4H candle closes
back above the box low: buy at that close. Stop: lowest low since the break - 0.1%. Target: the box high.
Time exit: 30 candles. One entry per break.

Variants:
- B2a: N = 3.
- B2b: N = 6.
- B2c: N = 3 + daily trend filter (last completed daily close above its daily 50 EMA).
