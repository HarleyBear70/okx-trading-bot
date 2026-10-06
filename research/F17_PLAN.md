# F17: a risk-manager ("supervisor") over all bots, the 3-5-7 idea (plan, written before running)

2026-10-06. Jeff asked whether a bot could send signals to the other bots to enforce the 3-5-7 rule; "yes" to testing. The supervisor never trades; it only says go / no-go before a bot buys. Research only. Script: research/f17_supervisor.py. Results: research/F17.md.

One combined simulation of the three demo bots as live (each with its own $1,000, own sizing, real fee 0.35% per side), on one 4H timeline (daily bots act at the close of each day's last 4H candle):
- Trend Rider: 4H BOS entry, first stop, breakeven at +1R (entry + 0.7%), trail at the highest close − 3 ATR, 0.4% risk, max 3 open (no fear filter, as in the research runs).
- Donchian: daily 20-day breakout with the BTC leash, 2 ATR stop, 10-day-low trail, one add-on at +1R (stop then ≥ entry), 0.32% risk, max 5 open.
- NNFX: daily Aroon flip, 1.5 ATR stop, half sold at +1 ATR then breakeven, rest exits on the Aroon flip down, 0.5% risk, max 3 open.
Open risk of a position = what it loses if every piece is stopped out now (0 once the stop is at/above entry).

- S0: no supervisor (the comparison).
- S1: block a new buy if total open risk across all bots would go over 5% of the combined balance (the "5" rule; the "3" rule is already met).
- S2: block a new buy if 2 bots already hold that coin.
- S3: S1 and S2 together.
2018-05 to now plus the halves. Pass: better return/DD than S0 in both halves (a supervisor that only cuts profit is not worth it).
