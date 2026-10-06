# F13: the classic TradingView strategy families, tested fairly (plan, written before running)

2026-10-06. Jeff: "test everything under the sun online if u can see it." TradeSearcher (about 29,000 TradingView backtests) is login/paywall-locked; its public BTCUSDT page shows 6 strategies with ROI and PF but no drawdown and TradingView's default fees, mostly all-in on BTC (buy-and-hold BTC made about +850% over the same years with a −77% drop). Most community scripts are variations of a dozen classic indicators, so the classics are tested with their textbook settings (no tuning), as long-only trend systems. Research only. Script: research/f13_classics.py. Results: research/F13.md.

Common rules: daily candles, BTC ETH SOL XRP BNB, long only, buy at the close of the signal day, first stop 2 ATR(14), then exit on the strategy's own exit signal (or the stop), 0.35% risk, max 5 open, real fee 0.35% per side, 2018-05 to now plus the halves.

1. EMA cross 20/50 (as "test ema cross script"): buy when EMA20 crosses above EMA50; exit on the cross back down.
2. Golden cross: SMA50 crosses above SMA200; exit on the death cross.
3. Ichimoku (9/26/52): buy when the close is above the cloud (both spans, displaced 26), Tenkan > Kijun and the close is above the close 26 days ago (Chikou); exit when Tenkan crosses below Kijun or the close falls into/below the cloud.
4. UT Bot (key 1, ATR 10): ATR trailing line; buy when the close crosses above it, exit when it crosses below.
5. Follow Line (as "Strategy Follow Line"): Bollinger(21, 1) + ATR(5) line; buy when the line turns up, exit when it turns down.
6. Keltner breakout: close above EMA20 + 2 × ATR(10); exit on a close below EMA20.
7. Hull MA (55): buy when the HMA turns up (above its value 2 days ago), exit when it turns down.
8. Parabolic SAR (0.02/0.02/0.2): buy when SAR flips below price, exit when it flips above.
9. Heikin Ashi: buy on the first green HA candle after a red one with the close above SMA50; exit on the first red HA candle.
10. Kaufman adaptive MA (10, 2, 30): buy when the close crosses above a rising KAMA; exit on a close below KAMA.
11. Traders Dynamic Index (as the TDI script): RSI(13), price line = SMA2 of RSI, signal = SMA7; buy when the price line crosses above the signal with both above 50; exit when it crosses below.
12. Vortex (14): buy when VI+ crosses above VI−, exit when it crosses below.

Because 12 systems are tested, the bar is higher: pass = positive in both halves, PF ≥ 1.3, DD ≤ 10%, AND positive in both halves on never-seen coins (LTC DOGE ADA LINK BCH AVAX SUI XLM LUNA FTT), AND a monthly correlation below 0.8 with Donchian (otherwise it's a copy of a bot already running).

## F13b (added after the F13 run, before running these)
- Jeff asked for the triple RSI mean-reversion strategy (Quantified Strategies' published rules): #13 = buy at the close when RSI(5) < 30, RSI(5) has fallen 3 days in a row, RSI(5) 3 days ago was < 60, and the close is above the 200-day SMA; exit when RSI(5) > 50; first stop 2 ATR. Same pass rules.
- Systems that beat the rules on profit but went just over the 10% drop (Follow Line 11.1%, Hull MA 12.7%, Vortex 11.3%) are re-run at a lower risk (0.3%, 0.27%, 0.3%) to see if they fit; same rules otherwise.
- Vortex never-seen run fixed (zero true range on flat days) and re-run.

## F13c (added before running): Follow Line exactly as the original TradingView script
F13's #5 resets the line on the first bullish day, so it can flip up sooner than the original. #14 follows the original "Follow Line" logic: BBSignal = +1 when the close is above BB(21, 1) upper, −1 below the lower band, else 0; +1: line = low − ATR(5), but never below the previous line; −1: line = high + ATR(5), but never above the previous line; 0: line unchanged. Trend = +1 when the line rises, −1 when it falls, else unchanged. Buy on the flip to +1, exit on the flip to −1. Tested at 0.3% risk, own and never-seen coins, same pass rules.
