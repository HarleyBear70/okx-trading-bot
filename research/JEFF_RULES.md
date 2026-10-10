# JEFF_RULES.md — Jeff's day-trade method, ONLY rules Jeff stated

Status: **v3 (Oct 10 2026), built from Jeff's answers on issue #4 (16:52, 17:01, 17:25, 17:26, 18:05 UTC).**
Code: research/jeff_setup.py. Lines marked [NOT JEFF] are the only places Claude turned Jeff's words into numbers.

## Jeff's rules

| # | Rule | Source |
|---|---|---|
| 1 | Higher timeframe is king. 4H = direction (Daily/Weekly above it). Only trade the 4H direction. | 17:25 (1), 18:05 |
| 2 | 15m = working + entry chart (5m optional, 1m avoid). Process: 4H direction -> 15m premium/discount -> wait for price there -> 15m sweep + small MS -> enter. | 18:05 |
| 3 | Swings: Jeff marks by eye -> TEST 1, 2 and 3 candles each side. | 16:52 (5) |
| 4 | Newest-leg fib: STRONG (fib 1) = the low that led to the newest high, WEAK (fib 0) = that high. Redraw on every BOS. WEAK is set once the pullback starts. | 10:09, Brad Ep5 |
| 5 | BOS = a candle BODY closes past the last high (wick doesn't count). | 06:38, Brad Ep5 |
| 6 | MS = a candle BODY closes past STRONG's WICK. A wick past = sweep. | 11:33 |
| 7 | Long only in the 15m discount, short only in the 15m premium, never the middle. | 17:25 (2) |
| 8 | Sweep = a wick into the nearest liquidity pool with the body closing back inside (the fuel grab). | 17:25 (8) |
| 9 | Entry after the turn is confirmed: TEST A = at the confirming candle's close, B = limit at the retest of the broken level. No OB/FVG entries. | 17:25 (4, 5) |
| 10 | Stop below the STRONG wick / beyond the liquidity pool, never right at the wick. TEST a few gap sizes. | 17:25 (6, 8) |
| 11 | Target: TEST -27% extension of the 15m leg (min 2:1 to it) vs fixed 2R vs fixed 3R. | 17:25 (3), 18:05 |
| 12 | Cancel an unfilled order when the setup is invalid: an MS against it, or price reaches the target first. | 17:01 (8) |
| 13 | One trade at a time per coin, no daily limit, no killzones, trade any time. | 17:01 (10), 16:52 (12) |
| 14 | Fees: limit entries 0%, stop-outs 0.02% taker + TEST slippage 0 / 0.02% / 0.05% (must pass at the worst). | 16:52 (11), 17:25 (7) |
| 15 | Small losses are fine; judge on total profit over many trades. No extra filters. | 17:26 |
| 16 | Longs and shorts. BTC ETH SOL XRP + never-seen coins. Paper only. | earlier notes |

## How the code reads Jeff's words [NOT JEFF where marked]

- "Nearest liquidity pool" = the last 15m swing low (N candles each side). Equal lows / W lows aren't detected separately. [NOT JEFF]
- "Small MS" = a 15m body close above the last 15m swing high after the sweep; entry B = that swing high (the retest). [NOT JEFF]
- Discount = the sweep wick is below the 0.5 of the 15m leg as it stood before that candle.
- Stop gap sizes 0.05% / 0.15% / 0.30% below the level. [NOT JEFF: Jeff said "test a few"]
- Stop + target inside the same 5m candle = counted as the stop. [NOT JEFF, the safe way]
- Stall management (take profit / trail) = optional, not in this test.
