# okx-trading-bot

SP-12 v4 SAR demo trading bot for OKX using the TradingView strategy rules.

**Demo only.** Every OKX order is sent with the demo header, so this bot can't touch real money.

## What it does

GitHub runs `bot.py` every hour (see the **Actions** tab). For BTC, ETH, SOL and XRP (USDT pairs) it:

1. Downloads OKX 4-hour and daily candles.
2. Runs the same checks as the TradingView script "Structure Pullback (12-Check) v4 SAR" with its default settings:
   Tuned score ≥ 2, 4H trend up, EMA 8 > 21 > 55, price above daily VWAP, stop 1–4% away.
3. On a buy signal it buys at market on OKX demo, risking 1% of the bot's own $1,000 practice account.
4. Manages the trade: stop-loss, 3R target, Parabolic SAR trailing stop after +1R, time exit after 120 candles.

It only sells coins it bought itself. Other demo balances aren't touched.

## Files

- `bot.py`: the bot
- `.github/workflows/bot.yml`: the hourly schedule
- `state.json`: the bot's memory (open trades, practice balance), written by the bot
- `trades.csv`: a log of every buy and sell, written by the bot

## Setup

In **Settings → Secrets and variables → Actions**, add these repository secrets from an OKX **demo** API key (Read + Trade, no withdraw):

- `OKX_API_KEY`
- `OKX_API_SECRET`
- `OKX_API_PASSPHRASE`

Optional variable: `OKX_BASE_URL` (default `https://us.okx.com`; use `https://www.okx.com` if your account is on OKX global).

Test it: **Actions → SP-12 v4 demo bot → Run workflow → mode: check**.

## Notes

- Exits are checked once an hour, so a stop can fill a bit past its price. A real exchange stop order would be more exact.
- GitHub's free plan covers this. An hourly run uses roughly 750 of the 2,000 free minutes a month on a private repo.
