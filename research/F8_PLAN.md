# F8: bots that learn without hurting themselves (plan, written before running)

2026-10-06. The user: "i want it to learn but not really change itself to lose money." Two kinds of learning, each tested on 8 years at the real fee before anything goes live. Research only. Script: research/f8_learn.py. Results: research/F8.md.

## L1: drawdown brake (protects money, never changes the strategy)
When a bot's balance is more than X% below its best balance, it risks half its normal amount per trade until it gets back above that line. bot.py replay, live settings, real fee, 2018-05 to now plus the halves.
- L1a X = 5%, L1b X = 8%; on Trend Rider, Donchian Trend and NNFX.
Pass: better return/DD than the same bot without the brake in both halves (a brake that only lowers profit is not worth it).

## L2: AI trade filter that learns from past trades (walk-forward, no peeking)
Trend Rider's entries (F3 S0 setup: engine.trade_sim, 0.4% risk, max 3 open, trailing exit). For every entry, record 8 facts known at that moment: stop distance %, ATR % of price, distance from the 4H 50 EMA %, RSI(14), 20-candle return %, volume vs its 20-candle average, daily close vs daily 50 EMA %, BTC's daily close vs its 200-day SMA %. The label is whether the trade made money.
A logistic regression (plain Python, L2 penalty) is trained each January 1st on all trades that closed before that date (from 2018-05), then judges that year's new entries. It never sees the future. 2018-2019 are training only.
- L2a: skip the entries the model scores in the bottom 30% (cut-off from the training trades).
- L2b: skip the bottom 50%.
Compared with Trend Rider's unfiltered entries over the same test years (2020-now), split 2020-2021 and 2022-now.
Pass: better return/DD than unfiltered in both splits, PF ≥ 1.3, DD ≤ 10%.

If neither passes, the bots keep learning the safe way: the journal, watcher, weekly Scout report and reviews, with every change tested before it goes live.
