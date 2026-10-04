# Bot Scoreboard

Every bot Jeff tests, on every platform, scored the same way. Numbers live in scoreboard.csv. Claude updates it at each check-in.

## Same starting line

- 1,000 USD practice balance
- About 1% risk per trade
- Same coins where possible: BTC, ETH, SOL, XRP
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
