# F12: range trading on the daily chart (plan, written before running)

2026-10-06. Jeff found this advice online: "mark the range, avoid the middle, trade the edges, wait for the retest, control risk." Earlier range tests were on 4H/1H and failed (N1 range bot −13%, B1c breakout retest −9% at the real fee, B2 reclaim −7%). This tests the same ideas on daily candles, where the trend bots work. Long only (spot). Research only. Script: research/f12_range.py. Results: research/F12.md. Real fee 0.35% per side, Donchian's coins BTC ETH SOL XRP BNB, 0.35% risk, max 5 open, 2018-05 to now plus the halves, never-seen coins if a variant passes.

The range = the highest high and lowest low of the prior 30 days, counted as a range only if it is 8-40% tall and each edge was touched at least twice (a candle within 10% of the range height of that edge on 2+ separate days, at least 5 days apart).
- R1 trade the bottom edge: the day's low reaches the bottom 20% of the range and the close is back above the range low (a rejection, not a break). Stop: range low − 1 ATR(14). Target: the top 20% line (range low + 80% of the height). No trades in the middle.
- R2 breakout and retest of the top edge: a daily close above the range high; then within 10 days a candle's low comes back to within 1% of the old range high and the day closes above it: buy. Stop: old range high − 1.5 ATR(14). Exit: trail at the 10-day low (Donchian's exit).
- R3 = R2 with the stop at the range middle (a wider, "structure" stop).
Comparison: Donchian (buys the breakout without waiting, +123% plain / +154% live). Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%.

## F12b (added after the F12 run, before running this): never-seen coins for R1 and R2 (both technically passed but are small), same rules.
