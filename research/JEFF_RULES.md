# JEFF_RULES.md — Jeff's day-trade method, ONLY rules Jeff stated

Status: **DRAFT, waiting for Jeff's approval. No test runs until Jeff approves this file.**
Sources = Jeff's notes on GitHub issue #4 (times are UTC, Oct 10 2026), or Jeff's words relayed by Chrome Claude.
Anything Jeff did not state is in the MISSING list at the bottom. Nothing gets filled in by Claude.

## A. Rules Jeff stated

| # | Rule | Where Jeff said it |
|---|---|---|
| 1 | Trade WITH the trend only. | #4 14:01 (via Chrome Claude) |
| 2 | Timeframes 4H -> 15m -> 5m. | #4 14:01; day trade first #4 05:13 |
| 3 | No killzones / time rules for crypto. | #4 14:01 (via Chrome Claude). Note: #4 05:35 asked to ADD killzones 2-5 / 7-10 AM ET. 14:01 replaces it? |
| 4 | Fib on the NEWEST leg: up leg = the low that led to the newest high (STRONG, fib 1) to that high (WEAK, fib 0). Down leg = mirror. | #4 10:09; screenshot BTC 5m 82,770.7 -> 82,950; Smoke v22 checked live #4 12:41 |
| 5 | My BOS rule and my fib are the same thing: every new HH moves STRONG up to the newest pullback low, WEAK = the new high. Redraw after every BOS. | #4 10:09 |
| 6 | BOS = a candle BODY closes past the last HH (uptrend) / LL (downtrend). Breaks inside the range = iBOS, warning only, no reset. | #4 06:38 (#7) |
| 7 | Market shift (MS) = a candle BODY closes past STRONG's WICK. A wick past it = sweep. A body close between STRONG's body and its wick = NOT an MS. | #4 11:33 |
| 8 | Fib only 0 / 0.5 / 1. Long only in discount (below 0.5), short only in premium (above 0.5). Never the middle. | #4 05:13 |
| 9 | Stop past STRONG + "my cushion". | #4 05:13, #4 10:09 |
| 10 | Target = -27% fib extension (TP1 = the 0% line). | #4 10:37; #4 14:01 |
| 11 | At least 2:1, measured to the target used. | #4 05:13, #4 10:37 |
| 12 | Longs and shorts, shorts are the mirror. | Jeff "both directions" |
| 13 | Entry = limit order -> maker fee (0%); stop exits pay taker. | #4 05:35 |
| 14 | Coins BTC ETH SOL XRP; check on never-seen coins too. | #4 07:44, #4 10:09 |
| 15 | 3% daily loss limit. | #4 06:38 (#43) |
| 16 | Trailing stop = an optional add-on to TEST, not Jeff's rule. | #4 14:01 |
| 17 | Paper / research only. | every note |

## B. MISSING — Claude needs Jeff's answer (nothing filled in)

1. **Entry trigger:** what has to happen before you enter? (e.g. a 5m sweep then a 5m MS? price touching a zone? or just price in discount?)
2. **Entry price:** limit at what level? (the zone of the shift, the 0.5, the close of the shift candle, ...)
3. **Zones:** are zones (order blocks) part of your setup at all? If yes, which candle(s)?
4. **What each timeframe does:** what must the 4H show, what must the 15m show, what does the 5m do?
5. **Swing size:** how many candles each side make a swing high/low (for the newest leg)? Smoke v22 uses 2 on your chart.
6. **Cushion size:** how much is "my cushion"? (0.05% was used before; Chrome Claude says you never approved it.)
7. **Stop:** past STRONG (#4 10:09) or past the sweep candle (your own BTC short, #4 10:29)? Or test both?
8. **Order cancel:** when does an unfilled order get cancelled? (price hits target first? an MS against it? never?)
9. **-27% rule:** go straight for -27%, or TP1 at 0% then TP2 at -27% only after a new HH/LL (#4 10:37)? Part closes at TP1?
10. **One trade per coin at a time?** Max trades per day?
11. **Fees / slippage numbers** for stop exits (0.02% taker + 0.02% slippage was used before).
12. **Killzones:** confirm none for crypto (rule 3 above).

## C. Your requests I have NOT done yet (queued until this file is approved)

- #4 10:29 test YOUR BTC 5m short setup (stop past the sweep candle, target 0%) + re-check Smoke v22 SH/SL/MUST HOLD/TARGET/box.
- #4 10:31 Silver Bullet with your fib filter.
- #4 10:37 TP1 0% / -27% / -27% + trailing comparison.
- #4 11:33 MS-rule check of the code. Answer now: the code does NOT match. It flips the leg on a body close past the
  newest swing's BODY, not past STRONG's wick. All past tests did it that way. Will be fixed in the next test.
- #4 12:41 + 12:46 Smoke Detector v23 (color on/off, remove GOOD/SKIP and 1.35%/2%, purple only on your MS rule, new color key).
