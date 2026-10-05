# Helper bots H1, H2, H3, H5: plan and pass rules (each section written before that test is run)
(H4, the smart buyer, was covered by research/HOLD_PLAN.md.)

Common setup: the two demo trading bots as they trade now, each with its own $1,000 and bot.py's own
functions: SP-12 v4 (BTC ETH XRP XLM BNB) and Trend Rider (BTC ETH SOL BNB SUI), 0.5% risk, 0.1% fee,
long-history data (research/long_history.py). "Combined" = the sum of both bots' mark-to-market balances.
Halves: 2018-05 to end of 2021, and 2022 to now, each started fresh.

## H1. Safety switch + volatility sizing

Switch: when the combined balance is X% below its best, every new trade risks half (0.25%) until the
combined balance recovers to the level R, then back to 0.5%. Max 3 variants:
- W1: X = 5%, R = halfway back to the best.
- W2: X = 6%, R = the best.
- W3: X = 8%, R = the best.
Volatility sizing (one variant, judged by the same rule):
- V1: each new trade's risk = 0.5% x (the coin's median 4H ATR% over the previous 540 candles / its ATR%
  now), clamped to 0.25%-0.75%.
Pass (each variant separately): in BOTH halves, the combined max drawdown is smaller AND the combined
return is at least 90% of the current setup's.
