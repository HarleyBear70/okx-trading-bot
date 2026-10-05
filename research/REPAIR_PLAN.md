# Repair plan: SP-12 v2 and Trend Rider gold (written before any test was run)

Jeff's rule (NOTES, 2026-10-05): one fair repair attempt each, at most 3 variants per bot, chosen before
looking at results. If none pass, pause the bot (switch off, keep the code). Demo only.

Same engine as research/long_history.py: bot.py as it is now (0.5% risk, 0.1% fee each side), one coin
at a time, fresh $1,000 per period.

## SP-12 v2 variants

Now: pivot 5, no trend filters, stop 1.5-4%, target 2.5R (3-10%), 60-candle limit, no SAR trail.

- A. v4's 4H trend filter: EMA 8 > 21 > 55 and close above daily VWAP (`filters: True`).
- B. A + daily uptrend required (c1: daily close above a rising daily EMA20).
- C. A + v4's exits: 3R target, SAR trail after +1R, 120-candle limit.

## Trend Rider gold variants

Now: pivot 3, daily close > daily EMA50, stop 1-3 ATR under the swing low, trail at highest close - 3 ATR.

- A. Pivot 5 (same as the main Trend Rider).
- B. Longer trend filter: daily close > daily EMA100 (pivot 3).
- C. Wider trail: highest close - 4 ATR (pivot 3).

## Pass rules (all must hold)

Halves: 1st = start to end of 2021, 2nd = 2022 to now.

1. Beats the current version in BOTH halves on the coins the bot trades (v2: ETH, SOL, XAUT; gold: XAUT):
   higher total P/L and higher pooled PF (all trades on those coins together).
2. Beats the current version on never-seen markets, full period, pooled P/L and pooled PF:
   - v2: the out-of-sample coins from job 2b (LTC, DOGE, XLM, ADA, BNB, LINK, BCH, AVAX, SUI, LUNA, FTT).
   - gold: spot gold XAU/USD 2003-2019 and silver XAG/USD 2003-now (Dukascopy), which the gold bot never saw.
3. Makes money: pooled PF above 1.0 in both halves and on the never-seen markets. Beating a losing
   version while still losing is not a repair.
4. No coin-period breaks the 10% max drawdown.

If more than one variant passes, take the one with the higher never-seen pooled PF. If none pass, pause the bot.
