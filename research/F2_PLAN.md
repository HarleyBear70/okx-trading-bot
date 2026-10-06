# F2: new ideas that fit the real fees (plan, written before running)

2026-10-06. The user asked: "test whatever you think would work and search the internet for more ideas." Research only, no bot.py changes. Script: research/f2_test.py. Results: research/F2.md.

All tests use the real OKX fee (0.35% per buy and per sell, market orders), daily candles, and 2018-05 to now plus the halves (2018-05 to 2021, 2022 to now), each starting with a fresh $1,000.

## Idea A: daily Donchian trend (the "Turtle" family)
Source: the web search. Studies of crypto trend-following that count transaction costs find that time-series momentum survives costs and cross-sectional momentum does not (Han, Kang & Ryu 2023), and that an ensemble of Donchian channels with several lookbacks, plus volatility sizing, works net of fees (Zarattini, Pagani & Barbon, "Catching Crypto Trends"). Long only.
Coins: BTC ETH SOL XRP BNB (the coins the live bots know). Risk 0.5% per trade, max 5 open, stop sized by ATR.
- A1 Turtle 55/20: buy on a close above the prior 55-day high; stop 2 ATR(20) under entry, then trail at the 20-day low.
- A2 Fast 20/10: 20-day breakout, 2 ATR stop, trail at the 10-day low.
- A3 Ensemble: buy when the close is above the prior N-day high for the majority of N in (20, 40, 80, 160); exit when it is above that high for none of them (trail at the 20-day low); 2 ATR initial stop.
Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%. Also reported: monthly correlation with Trend Rider at 0.4% (F1b).

## Idea B: protected BTC hold (for the BTC coming from Coinbase)
All-in BTC while the daily close is above its moving average, all in cash (USDC) below. 0.35% per switch. No interest on cash in the base test (Idea C covers that).
- B1 200-day SMA
- B2 200-day SMA with a 3% band (buy above +3%, sell below −3%) to cut whipsaw trades
- B3 100-day SMA
Pass (a hold, not a bot, so the 10% DD rule doesn't apply): higher return/DD than buy-and-hold BTC in both halves, and a max DD no worse than half of buy-and-hold's.

## Idea C: interest on idle cash
OKX's flexible USDC lending rate is about 2.75% a year now (earn_get_lending_rate_history, Oct 6 2026). Estimate what it adds to Trend Rider + NNFX, given how much of their balance sits in cash (measured from the backtest). Arithmetic, not a pass/fail test. US availability and how fast cash comes back must be confirmed before use.

## Idea D: SP-12 v4 on daily candles (its last chance)
v4's own rules on daily candles (the trend check uses the previous daily close), 0.4% risk. One variant only. Same pass rules as A.

Funding carry (spot + perpetual short) is not tested: OKX's perpetuals are offered only where it is licensed, and US access is not confirmed.

## F2b (added after the first F2 run, before running these): robustness for Idea A
A1-A3 pass on profit but their drop is 12.7-13.9% at 0.5% risk, and the 2018-21 PFs (5-16) are high enough to look lucky. Same rules, no changes:
- A1, A2, A3 at 0.35% risk (does DD drop under 10%?)
- A1, A2, A3 on never-seen coins (e.UNSEEN without the 5 design coins: LTC DOGE ADA LINK BCH AVAX SUI XLM, plus delisted LUNA FTT), 0.5% risk, max 5 open. They must be positive in both halves with PF ≥ 1.2.
- Monthly correlation with Trend Rider at 0.4% (F1b), and the combined curves TR + A and TR + NNFX + A.
