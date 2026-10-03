# okx-trading-bot

Jeff's demo trading bots. GitHub runs them every hour for free, so they don't use any Claude usage.

**Nothing here can touch real money.** "Demo" bots trade on the OKX demo account, and every order carries OKX's demo header. "Paper" bots place no orders at all. They only write pretend trades to `trades.csv`.

## The bots

| Bot | Where | Coins | Rules |
|---|---|---|---|
| SP-12 v4 | OKX demo | BTC, ETH, SOL, XRP | 12-check score ≥ 2, EMA 8>21>55, above daily VWAP, 3R target, SAR trail after +1R, 120-candle limit. Risks 1% of a $1,000 practice balance |
| SP-12 v4 (Kraken paper) | Kraken prices | BTC, ETH, SOL, XRP | Same as above, paper only |
| SP-12 v2 | OKX demo | ETH, SOL | 12-check score ≥ 2, stop 1.5–4%, target 2.5R (3–10%), 60-candle limit, $50 risk |
| SP-12 v2 (gold paper) | OKX live gold price | XAUT | Same as above, paper only (OKX demo gold is frozen) |
| Trend Rider | OKX demo | BTC, ETH, SOL | Daily close > daily 50 EMA, 4H break of structure above 4H 50 EMA, stop under swing low (1–3 ATR), trails at highest close − 3 ATR, $50 risk |
| Trend Rider (gold paper) | OKX live gold price | XAUT | Same as above with swing strength 3, paper only |

All of them run on 4-hour candles. Each bot only sells coins it bought itself.

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
