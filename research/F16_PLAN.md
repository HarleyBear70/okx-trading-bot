# F16: bounded adaptation, learning with a safety net (plan, written before running)

2026-10-06. Jeff: "could a bot learn from its mistakes but set a safety net that it can't go over or under" → "yes" (test it). Research only. Script: research/f16_adapt.py. Results: research/F16.md.

Guardrails (the safety net):
1. The bot may only choose between settings that already passed 8-year tests. Nothing new is ever invented.
2. It decides once a quarter (Jan 1, Apr 1, Jul 1, Oct 1), using the last 12 months.
3. Risk per trade, coins and the 10% stop rule never change.
4. The default is kept unless another allowed setting did better over the last 12 months (return ÷ drop), so a setting that stops working is dropped at the next quarter.

How it learns: every allowed setting runs as a shadow (paper) account all the time. Each quarter the live bot follows the setting whose shadow account had the best return/DD over the past 12 months (the first 12 months use the default). Switching mid-trade is approximated by following that shadow account's equity for the quarter.

- A1 Trend Rider: trail 3 ATR (default) or 4 ATR (the F10 T2 variant, good on its own coins, weak on new ones). Engine as F10 (0.4% risk).
- A2 Donchian: plain (default) or with pyramiding (F10 P2). Both at 0.32% risk, as F10.
Own coins and never-seen coins, 2018-05 to now plus the halves (full-history runs, then sliced).
Pass: the adaptive bot beats its default on return/DD in both halves, on both coin sets.
