# Freqtrade

Free, open-source bot software. Here it **backtests** Jeff's rules: it replays SP-12 v4, SP-12 v2 and Trend Rider over OKX price history to see how they would have done, without waiting weeks.

- Strategies: `user_data/strategies/jeff_strategies.py`. Entries use the exact rule code in `bot.py`, so it tests the same signals the hourly bots trade.
- Settings: `user_data/config.json` (1,000 USDT practice balance, max 3 trades open, OKX US prices)
- Results: `results/SUMMARY.md` (each strategy with risk step-ups off and on, side by side), plus a full report per strategy in `results/` (`<name>_steps.txt` is the step-ups-on run)
- Runs: every Sunday, or Actions → Freqtrade backtest → Run workflow

Exits copy the live bots, including selling half at +2R. Position size calls `risk_pct()` from `bot.py`, so it uses the same RISK_PCT and RISK_STEPS. Step-ups follow `RISK_STEPS_ON` unless `JEFF_RISK_STEPS=on` or `off` is set (the workflow runs both). Take-profit is checked once per 4H candle, so a target can fill one candle late.

Next step: live practice ("dry-run") needs a computer that is always on, such as a free Oracle Cloud server.
