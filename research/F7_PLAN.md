# F7: weekly trend filter (multi-timeframe) and the fib golden pocket (plan, written before running)

2026-10-06. The user asked about multi-timeframe analysis and Fibonacci; standing request: "if u suggest something then lets try it." Research only. Script: research/f7_mtf.py. Results: research/F7.md. Real fee 0.35% per side, 2018-05 to now plus the halves.

Weekly trend = the last COMPLETED week's close is above its 20-week EMA (weeks built from daily candles, Monday-Sunday UTC; a week counts only after it has closed, so there is no look-ahead).

- W1 Trend Rider + weekly filter: F3's S0 (Trend Rider's BOS entry and exit in engine.trade_sim, 0.4% risk, max 3 open), taking a BOS only when the weekly trend is up. Compared with S0 (+145%, DD −10.3%).
- W2 Donchian + weekly filter: Donchian Trend exactly (bot.py replay), taking a breakout only when that coin's weekly trend is up. Compared with Donchian (+123%, DD −9.1%).
- G1 Fib golden pocket on Trend Rider: after a BOS, wait up to 12 candles for price to retrace to the 61.8% level of the move from the stop (swing low) to the BOS close. Buy at that candle's close if it is still above the stop. Same stop and exit as S0.

Pass: better return/DD than its comparison in both halves, PF ≥ 1.3, DD ≤ 10%.
