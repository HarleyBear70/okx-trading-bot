# JEFF_RULES.md — Jeff's day-trade method, ONLY rules Jeff stated

Status: **v2, waiting for Jeff's FINAL OK. No test runs until Jeff approves this file.**
Sources = Jeff's notes on GitHub issue #4 (UTC times, Oct 10 2026), some relayed by Chrome Claude.
Nothing here is filled in by Claude. Open questions are in section C.

## A. Jeff's rules

| # | Rule | Source |
|---|---|---|
| 1 | Trade WITH the higher-timeframe trend only. | #4 14:01, 16:52 (1) |
| 2 | Mark everything on every timeframe before moving down. Nothing marked = no trade. | #4 16:52 (0) |
| 3 | Timeframes: start high (Daily or 4H), 1H optional, 15m = working chart, 5m = entry (1m sometimes). | #4 16:52 (4) |
| 4 | Swings: Jeff marks by eye. TEST 1, 2 and 3 candles each side. | #4 16:52 (5) |
| 5 | Fib on the NEWEST leg: up leg = the low that led to the newest high (STRONG, fib 1) to that high (WEAK, fib 0). Down leg = mirror. Redraw on every BOS. | #4 10:09 |
| 6 | BOS = a candle BODY closes past the last HH (up) / LL (down). New HH -> STRONG moves up to the newest pullback low, WEAK = the new high. Breaks inside the range = iBOS, warning only. | #4 06:38, 10:09 |
| 7 | Market shift (MS) = a candle BODY closes past STRONG's WICK. A wick past it = sweep. A body close between STRONG's body and wick = NOT an MS. | #4 11:33 |
| 8 | Fib 0 / 0.5 / 1 only. Long only in discount, short only in premium, never the middle. | #4 05:13, 16:52 (3) |
| 9 | Entry: with the HTF trend, in the right zone, a 5m liquidity sweep, then a 5m MS. | #4 16:52 (1) |
| 10 | Limit orders, 1x mindset, sized in dollars. Limit price: TEST A = shift candle close, B = shift candle level, C = fib 50% or a box. | #4 16:52 (2) |
| 11 | Stop past STRONG's wick, beyond the liquidity, far enough that price must make an MS to hit it. Cushion: TEST none / small / one wick. | #4 16:52 (6-7) |
| 12 | Target = -27% fib extension, at least 2:1 measured to it. Compare with TP at the 0% line. | #4 10:37, 16:52 (9) |
| 13 | Trailing / taking profit when it stalls = optional TEST only, not the base rule. | #4 14:01, 16:52 (9) |
| 14 | Cancel an unfilled order when the setup is no longer valid: an MS against it, or price reaches the target without filling. | #4 17:01 (8) |
| 15 | One trade at a time PER COIN. NO daily limit. Trade any time a clean setup appears. | #4 17:01 (10) |
| 16 | No killzones for crypto, trade any time. | #4 16:52 (12) |
| 17 | Fees: Binance.US maker 0% (limit entries), taker 0.02% (stop exits), plus small standard slippage on stop-outs. | #4 16:52 (11) |
| 18 | Longs and shorts (shorts = mirror). Coins BTC ETH SOL XRP, plus never-seen coins as a check. | #4 07:44, 10:09 |
| 19 | Paper / research only. | every note |

Removed (not Jeff's): killzones on crypto, the 3% daily loss limit, 1.35% max stop, 0.40-0.60 band, counter-trend, fixed 0.05% cushion.

## B. Before the test

- Fix the MS code to rule 7 first (now it flips on a body close past the swing's BODY, not STRONG's wick).

## C. Still unclear — need Jeff's answer (Claude will NOT pick)

1. **HTF trend:** Daily or 4H? Or test both?
2. **"Right zone":** discount/premium of which leg: the 15m, the HTF (4H/Daily), or both?
3. **-27% extension:** of which leg: the 15m leg or the 5m leg?
4. **Limit B "shift candle level":** which price is that? (the STRONG wick it broke? the open of the shift candle?)
5. **Limit C "a box":** which box? (the order block that caused the shift? the FVG?)
6. **Cushion "small":** how much? (e.g. 0.05%, 0.1%?) "One wick" = the size of the STRONG candle's wick?
7. **Slippage "small standard":** how much? (e.g. 0.02%?)
8. **The 5m sweep:** a wick past the last 5m swing low (longs)? Any 5m swing, or a particular one?
