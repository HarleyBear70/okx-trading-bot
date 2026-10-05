# okx-trading-bot

Jeff's demo trading bots. GitHub runs them every hour for free, so they don't use any Claude usage.

**Nothing here can touch real money.** "Demo" bots trade on the OKX demo account, and every order carries OKX's demo header. "Paper" bots place no orders at all. They only write pretend trades to `trades.csv`.

## The bots

| Bot | Where | Coins | Rules |
|---|---|---|---|
| SP-12 v4 | OKX demo | BTC, ETH, XRP, XLM, BNB | 12-check score ≥ 2, EMA 8>21>55, above daily VWAP, 3R target, SAR trail after +1R, 120-candle limit. Risks 0.5% of a $1,000 practice balance |
| SP-12 v4 (Kraken paper) | Kraken prices | BTC, ETH, XRP | Same as above, paper only |
| SP-12 v2 (PAUSED Oct 5 2026, no edge in long-history test) | OKX demo | ETH, SOL | 12-check score ≥ 2, stop 1.5–4%, target 2.5R (3–10%), 60-candle limit, risks 0.5% of a $1,000 practice balance |
| SP-12 v2 (gold paper, PAUSED Oct 5 2026) | OKX live gold price | XAUT | Same as above, paper only (OKX demo gold is frozen) |
| Trend Rider | OKX demo | BTC, ETH, SOL, BNB, SUI, TRX | Daily close > daily 50 EMA, 4H break of structure above 4H 50 EMA, stop under swing low (1–3 ATR), trails at highest close − 3 ATR, risks 0.5% of a $1,000 practice balance. No new buys when the Crypto Fear & Greed Index was 25 or lower the day before (since Oct 5 2026) |
| Trend Rider (gold paper, PAUSED Oct 5 2026) | OKX live gold price | XAUT | Same as above with swing strength 3, paper only |
| B1c breakout retest (paper forward test) | OKX live prices, no orders | BTC, ETH, XRP | 1H: after a 4H close above a 60-candle box (3-12% tall), buy the first 1H dip back to the old box top that closes above it; stop 25% back inside the box, target 2R, 48-hour limit, no half-profit step. Paper only since Oct 5 2026 to collect forward data (research/B_BOXES.md) |
| B3 pairs (paper forward test) | OKX live prices, no orders | ETH/BTC, XRP/BTC (daily) | Holds the lagging coin when the coin/BTC spread is 2.5 standard deviations from its 60-day normal; exits when the spread is back within 0.5, after 30 days, or at a 2 x daily ATR stop. Paper since Oct 5 2026 (research/B3_PAIRS.md) |
| Hold pile (paper) | OKX live prices, no orders | BTC, XRP | Weekly dip-DCA buyer: $10 a week 50/50 (setting DCA in bot.py), double when a coin is 20%+ below its 200-day average. Buys logged in hold_pile.csv. Profit sweeper (25% of wins to the hold pile) is built but switched off |

All of them run on 4-hour candles. Every bot: stop moves to breakeven once a trade is up 1R, half is sold at +2R, stops only move up, max 3 trades open. Risk is 0.5% of the current balance per trade (cut from 1% on Oct 5 2026 to keep drawdown under 10%, see research/drawdown_test.py). Stepping risk up as the balance grows (1.25% / 1.5% / 2% at +10% / 25% / 50%) is built in but switched off for now (RISK_STEPS_ON in bot.py). Each bot only sells coins it bought itself. SOL was dropped from SP-12 v4 after it lost money in backtests, and XLM and BNB were added to it on Oct 5 after passing a pick + out-of-sample check (the Kraken paper copy stays on BTC, ETH, XRP); BNB and SUI were added to Trend Rider on Oct 5 after passing a backtest, and TRX on Oct 5 after passing a pick + out-of-sample check (research/TRX.md).

## Where to look

- **trades.csv**: every buy and sell, with profit or loss and each bot's practice balance
- **state.json**: the bots' memory (open trades and stops)
- **Actions tab**: a log for every hourly run

## Setup

The repository secrets `OKX_API_KEY`, `OKX_API_SECRET` and `OKX_API_PASSPHRASE` come from an OKX **demo** API key with Read + Trade permissions. The optional variable `OKX_BASE_URL` defaults to `https://us.okx.com`.

To test: **Actions → SP-12 v4 demo bot → Run workflow → check**.

## Notes

- Stops and targets are checked once an hour, so a demo fill can land a little past the stop price.
- Kraken has no demo mode, which is why the Kraken bot is paper only for now.
