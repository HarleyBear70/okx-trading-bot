# F10: managing trades like trend-following pros (plan, written before running)

2026-10-06. The user asked for pro-style trade management ("moving my SL and TP to get profit") and said yes to: pyramiding, trail width, volatility sizing. Volatility sizing is not tested: every bot already sizes each trade so the stop risks a fixed % of the balance, with ATR-based stops, so a volatile coin already gets a smaller position. Research only. Script: research/f10_exits.py (its own small simulator so a coin can hold 2 pieces). Results: research/F10.md. Real fee 0.35% per side, 2018-05 to now plus the halves. Every variant and its comparison run in the same simulator.

- Base TR: Trend Rider's entry and first stop, trail at the highest close − 3 ATR(14), 0.4% risk, max 3 coins open (as F3 S0).
- Base DC: Donchian Trend (20-day high, 2 ATR first stop, trail at the 10-day low), 0.35% risk, max 5 coins open.
- P1 TR + pyramid / P2 DC + pyramid (Turtle style, one add-on): when a position's close reaches entry + 1R (R = entry − first stop), buy a second piece sized to risk the same % of the balance down to the current stop (capped by free cash). From then on the shared stop is at least the first entry price (so the first piece can't lose). Both pieces exit together on the trailing stop. One add-on per trade.
- T1 TR trail 2.5 ATR / T2 TR trail 4 ATR (no pyramid).

Pass: better return/DD than its base in both halves, PF ≥ 1.3, DD ≤ 10%.

## F10b (added after the F10 run, before running these): robustness
P1 (TR + pyramid), P2 (DC + pyramid) and T2 (TR trail 4 ATR) beat their bases on return/DD in both halves, but their DD is over 10% at the bots' current risk. Same rules, no changes:
- Lower risk so the drop fits: P1 at 0.27%, P2 at 0.32%, T2 at 0.34% (DD scales about linearly with risk). Pass: DD ≤ 10% and return above its base.
- Never-seen coins (e.UNSEEN minus each bot's coins), current risk: each of P1, P2, T2 must beat its own base on the same coins on return/DD in both halves.
