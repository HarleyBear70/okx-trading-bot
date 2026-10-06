# F5: buy the pullback to the 20 EMA in a strong trend (plan, written before running)

2026-10-06. The user asked to test the common pullback entry ("test it"). Research only. Script: research/f5_pullback.py. Results: research/F5.md. Real fee 0.35% per side, 2018-05 to now plus the halves, $1,000 each. Each variant uses the same exit as the bot it is compared with, so only the entry differs.

- P1 (4H, Trend Rider's coins BTC ETH SOL BNB SUI TRX, 0.4% risk, max 3 open). Strong trend: the 4H close is above the 50 EMA, the 20 EMA is above the 50 EMA, and the last daily close is above the daily 50 EMA (Trend Rider's daily filter). Entry: the candle's low touches the 20 EMA and it closes back above it. Stop: the lowest low of the last 10 candles, held between 1 and 3 ATR(14) below the close (as in Trend Rider). Exit: trail at the highest close − 3 ATR(14). Compared with F3's S0 (buy the BOS, same simulator and exit): +145%, DD −10.3%.
- P2 (daily, Donchian's coins BTC ETH SOL XRP BNB, 0.35% risk, max 5 open). Strong trend: the daily close is above the 50 EMA and the 20 EMA is above the 50 EMA. Entry: the day's low touches the 20 EMA and it closes back above it. Stop: 2 ATR(20). Exit: trail at the 10-day low (Donchian's exit). Compared with Donchian (buy the 20-day high): +123%, DD −9.1%.

Pass: better return/DD than its comparison in both halves, PF ≥ 1.3, DD ≤ 10%.
Note: buying exactly at the 20 EMA with a limit order would pay 0.20% instead of 0.35% and fill a little lower. Not modeled; the test buys at the candle's close at the market fee.
