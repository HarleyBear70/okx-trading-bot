# Freqtrade

Free, open-source bot software. Here it **backtests** Jeff's rules: it replays SP-12 v4, SP-12 v2 and Trend Rider over OKX price history to see how they would have done, without waiting weeks.

- Strategies: `user_data/strategies/jeff_strategies.py`. Entries use the exact rule code in `bot.py`, so it tests the same signals the hourly bots trade.
- Settings: `user_data/config.json` (1,000 USDT practice balance, max 3 trades open, OKX US prices)
- Results: `results/SUMMARY.md`, plus a full report per strategy in `results/`
- Runs: every Sunday, or Actions → Freqtrade backtest → Run workflow

Not copied yet: selling half at +2R and the risk step-ups. Take-profit is checked once per 4H candle, so a target can fill one candle late.

Next step: live practice ("dry-run") needs a computer that is always on, such as a free Oracle Cloud server.
