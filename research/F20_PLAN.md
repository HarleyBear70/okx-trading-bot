# F20: Jeff's half-written breakout script (plan, written before running)

2026-10-06. Jeff shared a screenshot of an article's pseudo-code ("Agno" risk layer, futures): a Donchian channel breakout with a lookback that adapts to recent volatility, stop 1.5 ATR and take-profit 2.0 ATR, long and short, plus a risk layer (pause after a big drawdown, smaller size and more selectivity after a losing streak). Already tested: fixed ATR targets (lost in every test), shorts (N4 failed; no perps on OKX US), drawdown brake (F8), self-adapting settings (F16). New parts tested here, long only, daily, BTC ETH SOL XRP BNB, 0.35% risk, max 5 open, real fee 0.35% per side, 2018-05 to now plus the halves. Research only. Script: research/f20_script.py. Results: research/F20.md.

- X1 the script as written (long side): buy on a close above the prior 20-day high; stop 1.5 ATR(14); target 2.0 ATR.
- X2 adaptive lookback: lookback = 20 × (the coin's median ATR% over the last 100 days ÷ today's ATR%), held between 10 and 40 days (calm market: longer channel; wild market: shorter... see note), with Donchian's live exit (2 ATR stop, trail at the 10-day low).
- X3 = Donchian (20-day, live exit) + the losing-streak layer: after 3 losses in a row, half size until the next win.
Note on X2: the script doesn't say which way the lookback moves; this version shortens the channel when volatility is high relative to its normal level.
Comparison: plain Donchian (+123% / −9.1%). Pass: better return/DD than Donchian in both halves, PF ≥ 1.3, DD ≤ 10%.
