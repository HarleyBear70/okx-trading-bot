# Trade lessons

What each closed trade teaches, from the bots' own trades only. Written every hour by tools/trade_lessons.py (read-only). A mistake becomes a **candidate rule** after it shows up on 3+ losers. Claude backtests it, and a bot changes only with Jeff's OK.

## Candidate rules (0)

- none yet (6 closed trades; need a mistake on 3+ losers)

## Mistake tally

| Mistake | On losers | On winners | P/L of those trades |
|---|---|---|---|
| went wrong almost right away (never up even 0.3R) | 1 | 0 | -7.75 |
| was up 1R or more, then ended as a loss | 2 | 0 | -4.16 |
| bought more than 6% above the 50 EMA (chasing) | 1 | 0 | -7.75 |
| stop was more than 8% away | 1 | 0 | -7.75 |
| the 4H Supertrend was still pointing down | 1 | 0 | -7.75 |
| breakout candle had below-average volume | 3 | 2 | -1.71 |
| daily RSI was over 70 (overbought) | 0 | 0 | +0.00 |

## Every closed trade, newest first (6)

### LOSS -12.63 - SP-12 v4 (Kraken paper) ETHUSD (2026-10-04 12:26 -> 2026-10-07 02:25 UTC)
- **Why it bought:** BUY signal. Score 3 (needed 2). Points for: Daily trend up: yesterday's daily close above a rising 20-day EMA; Supertrend is green on this candle; MACD histogram rising (momentum picking up). Stop 1.69% below, target 5.07% above.
- **What happened:** best +1.44% (0.85R), worst -4.07%, held 16 candles, sold by Price fell to the stop-loss, so the bot sold to cap the loss. at 2654.2031 (-2.13%, -1.0R).
- **Lessons:** breakout candle had below-average volume.

### LOSS -7.75 - Trend Rider SUI (2026-10-05 04:28 -> 2026-10-07 01:58 UTC)
- **Why it bought:** BUY signal: broke above the swing high 1.2187 with the daily and 4H trend up. Stop 9.22% below at 1.11702; no fixed target - a trailing stop 3 ATR under the highest close follows the trend.
- **What happened:** best +2.34% (0.26R), worst -9.38%, held 12 candles, sold by trailing stop (exchange; recorded late Oct 7) at 1.1475 (-7.14%, -0.72R).
- **Lessons:** went wrong almost right away (never up even 0.3R); bought more than 6% above the 50 EMA (chasing); stop was more than 8% away; the 4H Supertrend was still pointing down.

### WIN +5.89 - SP-12 v4 BTC (2026-10-04 04:49 -> 2026-10-05 16:27 UTC)
- **Why it bought:** BUY signal. Score 2 (needed 2). Points for: Daily trend up: yesterday's daily close above a rising 20-day EMA; Supertrend is green on this candle; MACD histogram rising (momentum picking up). Points against: Break of structure in the last 20 candles (the tested settings count this AGAINST a buy). Stop 1.23% below, target 3.69% above.
- **What happened:** best +2.56% (2.12R), worst -0.01%, held 10 candles, sold by Price reached +1R, then came back to the entry - the bot got out about even instead of taking a loss. at 84912.662 (-0.25%, 0.09R).
- **Lessons:** breakout candle had below-average volume.

### WIN +9.19 - SP-12 v4 (Kraken paper) XBTUSD (2026-10-04 04:49 -> 2026-10-05 16:27 UTC)
- **Why it bought:** BUY signal. Score 2 (needed 2). Points for: Daily trend up: yesterday's daily close above a rising 20-day EMA; Supertrend is green on this candle; MACD histogram rising (momentum picking up). Points against: Break of structure in the last 20 candles (the tested settings count this AGAINST a buy). Stop 1.24% below, target 3.73% above.
- **What happened:** best +2.52% (2.03R), worst -0.04%, held 10 candles, sold by Price reached +1R, then came back to the entry - the bot got out about even instead of taking a loss. at 85002.666 (-0.00%, 0.16R).
- **Lessons:** breakout candle had below-average volume.

### LOSS -3.32 - SP-12 v2 ETH (2026-10-04 02:47 -> 2026-10-05 05:28 UTC)
- **Why it bought:** BUY signal. Score 2 (needed 2). Points for: Daily trend up: yesterday's daily close above a rising 20-day EMA; Liquidity sweep in the last 10 candles: price dipped under a swing low and closed back above it; Supertrend is green on this candle; MACD histogram rising (momentum picking up). Points against: Break of structure in the last 20 candles (the tested settings count this AGAINST a buy); Price retesting the order block before the last BOS (counted against). Stop 1.45% below, target 3.75% above.
- **What happened:** best +1.77% (1.06R), worst -0.21%, held 8 candles, sold by Price reached +1R, then came back to the entry - the bot got out about even instead of taking a loss. at 2688.2735 (-0.50%, -0.09R).
- **Lessons:** was up 1R or more, then ended as a loss; breakout candle had below-average volume.

### LOSS -0.84 - SP-12 v4 ETH (2026-10-04 21:24 -> 2026-10-05 04:28 UTC)
- **Why it bought:** BUY signal. Score 2 (needed 2). Points for: Daily trend up: yesterday's daily close above a rising 20-day EMA; Supertrend is green on this candle; MACD histogram rising (momentum picking up). Points against: Price dipping into a recent fair value gap (counted against). Stop 1.19% below, target 3.58% above.
- **What happened:** best +1.33% (1.05R), worst -0.33%, held 3 candles, sold by Price reached +1R, then came back to the entry - the bot got out about even instead of taking a loss. at 2701.3521 (-0.45%, -0.08R).
- **Lessons:** was up 1R or more, then ended as a loss; breakout candle had below-average volume.
