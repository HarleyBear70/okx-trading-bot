# F22: three indicator filters on Trend Rider and Donchian (plan, written before running)

2026-10-06. Jeff asked about anchored/cumulative indicators and overbought/oversold, then "test the ones you think might help". Tested as entry filters (exits unchanged). Skipped: Stochastic oversold dip-buys (six dip/pullback entries already failed at the real fee; Stochastic measures the same as RSI). Research only. Script: research/f22_filters.py on research/f10_exits.py's engine. Results: research/F22.md. Real fee 0.35% per side, 2018-05 to now plus the halves.

Bots (same engine as F10/F19): Trend Rider 4H (0.4% risk, max 3; base +145% / −10.3%) and Donchian daily as live (BTC leash, one add-on at +1R, 0.32% risk, max 5; base +154% / −9.7%).
- V1 anchored VWAP: buy only if the close is above the VWAP anchored at the last confirmed swing low (lowest low of 5 candles each side).
- V2 OBV confirmation: buy only if on-balance volume is at its highest of the last 20 candles (volume flowing in with the breakout).
- V3 not overbought: skip the buy if RSI(14) is above 80.
Pass: better return/DD than the bot's base in both halves on its own coins AND on never-seen coins, PF ≥ 1.3, DD ≤ 10% (own coins).
