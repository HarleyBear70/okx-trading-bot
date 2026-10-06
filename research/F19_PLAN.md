# F19: three untested ways to improve Trend Rider (plan, written before running)

2026-10-06. Jeff: "trend rider is my best bot so anything we can do to make him better never hurts." Research only. Script: research/f19_tr.py (uses research/f10_exits.py's engine: Trend Rider entry and first stop, trail at highest close − 3 ATR, 0.4% risk, max 3 open; base = +145% / −10.3%). Results: research/F19.md. Real fee 0.35% per side, 2018-05 to now plus the halves; never-seen coins where it applies.

- E1 limit-order entry with a realistic fill: at the signal candle's close, place a limit buy at that close. It fills only if the NEXT 4H candle trades down to it (low ≤ the limit), at the limit, with the maker fee (0.20%); otherwise the signal is dropped. Exits stay market (0.35%). (F1's "M" assumed every limit buy filled.)
- E2 more coins: Trend Rider's 6 coins + XRP, DOGE, ADA, LINK (10 coins), same rules, max 3 open.
- E3 slower candles: the same rules on 8H and on 12H candles (built from the 4H data; pivot 5, EMA50, ATR14 on that timeframe; daily filter unchanged).
Pass: better return/DD than the base in both halves (E1 and E3 also on never-seen coins), PF ≥ 1.3, DD ≤ 10%.

## F19b (added after the F19 run, before running this)
E2 (10 coins) beat the base on return/DD in both halves but its drop was 12.8% at 0.4% risk. Same rules at 0.31% risk (drop scales about linearly). Pass: DD ≤ 10% and better return/DD than the base in both halves.
