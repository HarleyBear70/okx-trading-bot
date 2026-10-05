# Job 2e plan: volatility guard for SP-12 v4 (written before any test was run)

Problem: in wild markets (DOGE 2021) 4H candles move 20%+, stops fill far below their level, and DD jumps.

"Hot" = measured on the signal candle, compared with the previous 90 days (540 4H candles) of the same coin:
- ATR14 as % of price above its 95th percentile, or (G3) the candle's own range (high-low)/close above its
  95th percentile.

Variants (max 3, fixed now):
- G1: skip the entry when ATR% is hot.
- G2: enter at half size (0.25% risk instead of 0.5%) when ATR% is hot.
- G3: skip the entry when the signal candle's range is hot.

Test sets (bot.py as it is now otherwise: 0.5% risk, 0.1% fee, v4 settings):
- A. The v4 bot as it trades: BTC+ETH+XRP, one shared $1,000, max 3 open. Halves: 2018-05 to 2021, 2022 to now.
- B. Every long-history coin on its own (the 16 coins of job 2b, XAUT excluded), fresh $1,000 per market
  period, pooled. Halves: periods before 2022 / from 2022.

Gap loss = a trade that lost more than 1.5x its planned risk (stop filled far below its level).

Pass rules (all must hold, in BOTH halves):
1. Max DD better (less negative) on A, or the worst coin-period DD better on B, and neither gets worse.
2. Gap losses fewer on A + B combined.
3. Return / pooled P/L at least 90% of the current version's on A and on B.
If more than one passes, take the one with the best combined return. Only a pass gets recommended.
