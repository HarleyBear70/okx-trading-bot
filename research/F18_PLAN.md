# F18: entries and position sizing (plan, written before running)

2026-10-06. Jeff asked about how many times to enter (single entry, pyramiding, averaging down) and how to size (fixed quantity, fixed % of account, volatility-based). Pyramiding was F10; volatility-based sizing is what every bot already does (risk % ÷ stop distance, ATR stops). Research only. Script: research/f10_exits.py (sizing and averaging-down options added) via research/f18_sizing.py. Results: research/F18.md. Engine and bots as F10: Trend Rider (4H, 0.4% risk, max 3) and Donchian (daily, 0.32% risk, max 5), real fee 0.35% per side, 2018-05 to now plus the halves.

Sizing (single entry):
- Z0 volatility/risk-based (as live): quantity = balance × risk % ÷ (entry − stop).
- Z1 fixed quantity: the same $ amount every trade, never growing: $250 (Trend Rider) / $200 (Donchian), about the bots' typical position size at the start.
- Z2 fixed % of account: each trade buys 25% (Trend Rider) / 20% (Donchian) of the current balance, whatever the stop distance.
Entries:
- AD averaging down: if a trade's close falls halfway to its stop (entry − 0.5R) before reaching +1R, buy a second piece of the same size; the stop doesn't move (so a stop-out loses about twice as much). Once per trade.
Compared with Z0 on return/DD in both halves (Z1 compounds less, so return/DD is the fair yardstick).

## F18b (added after the F18 run, before running these)
Z1/Z2 at the first sizes bet far more than Z0 (25% of the account per trade vs about 7-13%), so their drops (19-44%) aren't comparable. Same rules, scaled so the drop is near the bots' 10%: Trend Rider Z1 $100, Z2 6%; Donchian Z1 $80, Z2 6%. Compared with Z0 on return and DD in both halves.
