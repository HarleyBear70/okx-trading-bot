# Job 2d plan: more coins for SP-12 v4 (written before any test was run)

Candidates: the never-seen coins from job 2b: LTC, DOGE, XLM, ADA, BNB, LINK, BCH, AVAX, SUI, LUNA, FTT.

Engine: research/long_history.py (bot.py as it is now: 0.5% risk, 0.1% fee each side), v4 settings unchanged.

Step 1, pick (data up to 2021-12-31 only). One continuous run per coin, own $1,000, from its first
candle to the end of 2021. A coin is picked if ALL hold:
- at least 30 trades
- PF at least 1.30 (the median PF of v4 on its own coins in job 2b)
- return above 0
- max drawdown not worse than -10%
Coins with no data before 2022 (SUI) cannot be picked.

Step 2, check (2022-01-01 to now, never looked at for picking). Same run on 2022-now. A picked coin passes if:
- PF above 1.0, return above 0, max drawdown not worse than -10%
(a coin that died, e.g. LUNA / FTT, is judged on whatever data it has)

Step 3, portfolio. The v4 bot as it trades: one $1,000 balance shared by all its coins, max 3 open,
bot.py's own functions. Compare BTC+ETH+XRP alone vs BTC+ETH+XRP + the coins that passed both steps,
on 2022-now (the out-of-sample part) and on the full common period: trades, return, max DD, PF.
Only coins that pass both steps get recommended. No change to bot.py without Jeff's OK.
