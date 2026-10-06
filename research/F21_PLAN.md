# F21: Quantpedia's MAX strategy for Bitcoin (plan, written before running)

2026-10-06. From Quantpedia's "Revisiting Trend-following and Mean-reversion Strategies in Bitcoin": hold BTC on the day after its close is the highest of the previous X days (MAX); they report X = 10 as best and that MAX kept working out of sample (Feb 2022-Aug 2024), with no fees and no numbers given. Their hourly seasonality (21:00-23:00 UTC) was already tested as Q1 and failed after fees. Research only. Script: research/f21_max.py. Results: research/F21.md.

Rules (daily closes, BTC, all-in / all-cash like the paper, real fee 0.35% per buy and per sell), 2018-05 to now plus the halves:
- M1 MAX10: if today's close is the highest close of the last 10 days, hold BTC tomorrow; otherwise hold cash. (Consecutive signal days keep the position, no extra fees.)
- M2 MAX20: the same with 20 days.
- M3 MAX10 with an exit lag: once in, stay in until the close falls below the 10-day low (fewer switches, fewer fees).
Compared with buy-and-hold BTC and the BTC Protected Hold (100-day average, +1893% / −41%). Pass (as a hold, like F2 B): better return/DD than buy-and-hold in both halves; to replace the Protected Hold it must also beat it on return/DD in both halves. Also on ETH as a never-seen check.
