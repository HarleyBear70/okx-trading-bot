# Bot Scoreboard

Every bot Jeff tests, on every platform, scored the same way. Numbers live in scoreboard.csv. Claude updates it at each check-in.

## Same starting line

- 1,000 USD practice balance
- 0.5% risk per trade (GitHub bots, since Oct 5 2026)
- Same coins where possible (each bot's coins are in scoreboard.csv)
- No real money until a bot passes the rules below

## What gets measured

- Net profit after fees, in USD and %
- Win rate
- Profit factor: dollars won for every dollar lost. Above 1.3 is decent, above 1.6 is good
- Max drawdown: the biggest drop from a high point
- Trades closed
- Buy and hold: did the bot beat just holding the coin over the same time

## Rules for judging

1. No verdict until about 30 closed trades or 3 weeks
2. No changing a bot in the middle of its test. Changes start a new test
3. Stop any bot that drops 10% from its best balance
4. Cut any bot losing money after 30 trades
5. Profit factor above 1.3, drawdown under 10%, and beats buy and hold: it moves to the shortlist
6. Shortlist bots go live small first, never the whole balance

## Platforms

- GitHub bots: trades.csv in this repo
- HaasOnline: haas_bot_log.csv in this repo, trial ends Oct 11
- 3Commas and Bitsgap: trade history exports
- Freqtrade: backtest on past prices first, then practice mode
- TradingView: charts and alerts, not scored

<!-- equal-terms start -->

## Equal-terms backtest scoreboard (generated 2026-10-05 by research/scoreboard.py)

Every bot on the same footing: $1,000, 0.5% risk per trade, 0.1% fee each side (0.15% on the 1H bots), max 3 open, 2018-05 to now, plus the halves 2018-05 to 2021 and 2022 to now. Sorted by return / max drawdown (higher = more return for each point of pain). Correlation = monthly returns vs 50/50 v4 + Trend Rider. Live demo results are in the Scout's weekly report (reports/).

| Rank | Bot | Status | Coins | Return | Max DD | Return / DD | PF | Trades | Win % | 1st half return / DD | 2nd half return / DD | Corr. with v4+TR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trend Rider | demo, live on OKX (fear filter since Oct 5; row is without it) | BTC ETH SOL BNB SUI | +143% | -8.9% | 16.08 | 1.80 | 580 | 39% | +55% / -5.7% | +57% / -7.0% | 0.88 |
| 2 | SP-12 v4 | demo, live on OKX | BTC ETH XRP XLM BNB | +93% | -10.2% | 9.17 | 1.35 | 735 | 36% | +50% / -6.3% | +28% / -10.2% | 0.84 |
| 3 | N2 M3 rotation (not 0.5% risk: allocation) | research: failed (DD) | top 10 as listed at the time | +287% | -38.8% | 7.39 | 1.54 | 253 | 44% | +118% / -38.8% | +78% / -34.2% | 0.60 |
| 4 | SP-12 v4 (Kraken paper) | paper | BTC ETH XRP | +55% | -9.9% | 5.61 | 1.34 | 493 | 35% | +29% / -5.6% | +20% / -9.9% | 0.81 |
| 5 | B3 P3 pairs | paper forward test | ETH/BTC XRP/BTC, daily | +14% | -5.4% | 2.60 | 1.52 | 105 | 40% | +6% / -4.9% | +8% / -5.1% | 0.40 |
| 6 | B1c breakout retest | paper forward test | BTC ETH XRP, 1H | +15% | -5.8% | 2.55 | 1.26 | 217 | 48% | +8% / -2.3% | +7% / -5.8% | 0.55 |
| 7 | D1 I3 intraday momentum | research: failed | BTC ETH XRP, 1H | +20% | -11.2% | 1.81 | 1.09 | 1389 | 48% | +18% / -7.8% | +2% / -8.9% | 0.21 |
| 8 | N4 X2 short side | research: failed (shorts) | BTC ETH XRP | +20% | -16.7% | 1.21 | 1.27 | 314 | 43% | +22% / -6.8% | -2% / -16.7% | -0.08 |
| 9 | N3 S2 squeeze + daily trend | research: failed | BTC ETH XRP | +6% | -9.9% | 0.58 | 1.15 | 159 | 43% | +12% / -2.1% | -5% / -9.9% | 0.43 |
| 10 | SP-12 v2 | paused | ETH SOL XAUT | +5% | -20.9% | 0.22 | 1.02 | 776 | 31% | -12% / -20.3% | +19% / -9.1% | 0.47 |
| 11 | Trend Rider gold (pivot 3) | paused | XAUT (from 2020) | -1% | -16.3% | -0.08 | 0.97 | 202 | 33% | -3% / -5.6% | +2% / -12.2% | 0.16 |
| 12 | B2c reclaim + daily trend | research: failed | BTC ETH XRP | -7% | -12.9% | -0.58 | 0.81 | 110 | 31% | +3% / -5.9% | -10% / -12.9% | -0.05 |
| 13 | D1 C3 capitulation buy | research: failed | BTC ETH XRP, 1H | -5% | -8.3% | -0.63 | 0.83 | 115 | 43% | -2% / -5.0% | -4% / -6.2% | 0.20 |
| 14 | N1 R3 range bot | research: failed | BTC ETH XRP | -13% | -18.4% | -0.72 | 0.70 | 141 | 33% | -11% / -11.3% | -2% / -8.2% | 0.14 |

Reference: 50/50 v4 + Trend Rider together +99% / -6.6% (return/DD 15.07); buy-and-hold BTC +863% / -77% (return/DD 11.20).
Notes: N2 M3 is an allocation bot (no stops), so its 0.5%-risk footing differs. Trend Rider gold only has data from 2020. B1c / D1 use Binance 1H data; the rest use the long-history 4H data.

<!-- equal-terms end -->
