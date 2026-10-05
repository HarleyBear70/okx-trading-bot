# Look-ahead audit

T1 = decision at a past candle recomputed with only the data that existed then, vs the full-history backtest (any mismatch = look-ahead). T2 = recomputed with exactly the history the live bot downloads (mismatch = signal flips or stop / target more than 0.1% off: a warm-up difference). Script: research/audit_lookahead.py.

| Bot / coin | T1 cuts | T1 mismatches | T2 random cuts mismatched | T2 signal candles | T2 signals lost / changed (120 daily candles, before the fix) |
|---|---|---|---|---|---|
| v4 BTC | 40 | 0 | 0 | 60 | 0 |
| Trend Rider BTC | 40 | 0 | 0 | 60 | 0 |
| B1c BTC | 40 | 0 | 0 | 60 | 0 |
| v4 ETH | 40 | 0 | 0 | 60 | 0 |
| Trend Rider ETH | 40 | 0 | 0 | 60 | 0 |
| B1c ETH | 40 | 0 | 0 | 17 | 0 |
| v4 XRP | 40 | 0 | 0 | 60 | 0 |
| Trend Rider XRP | 40 | 0 | 0 | 57 | 1 |
| B1c XRP | 40 | 0 | 0 | 31 | 0 |
| B3 pairs ETH | 40 | 0 | 0 | 60 | 0 |
| B3 pairs XRP | 40 | 0 | 0 | 60 | 0 |
| B3 pairs BTC | 40 | 0 | 0 | 60 | 0 |

## Fix made

- Live daily history for the 4H bots: 120 -> 400 daily candles (bot.py get_data). With 120, Trend Rider's daily 50 EMA
  hadn't fully settled, and 1 of 57 Trend Rider signals on XRP (in the last 2.7 years) would have been missed live.
  With 400: 0 of 232 signals differ on BTC/ETH/XRP. Backtests already used full history, so no backtest number
  changes; live now matches them.

## Code review (things the tests above can't see)

| Item | Live | Backtest | Verdict |
|---|---|---|---|
| Daily inputs to 4H bots (v4 daily EMA20 uptrend, Trend Rider daily EMA50) | previous UTC day's CLOSED daily candle (daily_lookup = day - 1; only confirmed candles kept) | same function | PASS |
| VWAP (v4) | built from the current UTC day's closed 4H candles up to the signal candle | same | PASS |
| Swing points (pivots) | value appears only on the candle that confirms it (L candles later) | same | PASS |
| 4H boxes inside B1c | 4H candles built only from complete groups of 4 closed 1H candles; the retest must come after the breakout candle has closed | same function | PASS |
| B3 spread z-score | closed daily candles; mean / sd from the 60 days BEFORE the decision day | same (identical signals verified) | PASS |
| Fear & Greed (Trend Rider filter) | value stamped the PREVIOUS UTC day (alternative.me publishes each day's value at 00:00 UTC, so it is always known); missing = no trade | same | PASS (conservative by a day) |
| Dip-DCA | last CLOSED daily candle and the 200 closed days before it; buys once per ISO week | Monday trade at the Sunday close | PASS |
| Candle boundaries | OKX 4H (UTC-aligned) and 1Dutc; Kraken 240 / 1440 (UTC); forming candle dropped | Bitfinex / Binance UTC candles; daily built from complete UTC days | PASS |
| Indicator warm-up | 500 4H, 400 daily (was 120), 400 1H, 220 daily for B3 | full history | PASS after the fix (T2 above) |
| Entry price | market order a few minutes after the signal candle closes (runner at :07) | signal candle's close | PASS: crypto trades 24/7, so the next price is the close plus a few minutes of drift; no gap to exploit. Demo bots record real fills |
| Stops / targets | checked on later candles (and the forming candle, intrabar) | only from the candle AFTER entry; gaps fill at the open; if stop and target are in the same candle, the stop wins | PASS (conservative) |
| Research-only simulators (engine trade_sim, NNFX, rotation, hold pile, Q1, D1, news guard) | - | entries at the decision close or a known open, inputs only from earlier data, scheduled event times only | PASS |
