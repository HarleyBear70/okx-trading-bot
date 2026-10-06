# F28: Jeff's "my strat8" (Triple Supertrend) and "my strat9" (BTC Trend-Momentum) (plan, written before running)

2026-10-06. (my strat6 and my strat7 are byte-for-byte copies of my strat 5, which F27 already tested.)

**Strat 8, Triple Supertrend.**
- Rules: three Supertrends on hl2: (10, 1.5), (14, 2.5) and (20, 3). Buy when the close is above all three, ADX(14) > 25 and +DI > −DI. Sell when the close drops below the fast Supertrend; the stop trails at the slow Supertrend line. Sizing: 1% risk to the slow line, with the stop at least 0.5 ATR away.
- Defaults: the volume and higher-timeframe filters are off. Commission is set to 0.05%; ours is 0.35%.
- Test: long only, 0.4% risk, max 5 coins, BTC ETH SOL XRP BNB plus the never-seen coins, 2018-05 to now plus both halves.
- Variants: G1 as written, daily. G2 as written, 4H. G3 daily, with no fast-line exit (only the slow-line trail closes the trade).
- Pass: PF ≥ 1.3, DD ≤ 10%, positive in both halves and on never-seen coins, and it must improve Donchian's return/DD in both halves when added (like F24).

**Strat 9, BTC Trend-Momentum.**
- Rules: buy all-in when Chaikin Money Flow(20) > 0, Stoch RSI %K(14, 14, 3) crosses up through 20, ATR(14) > its 20-bar average, and the close is above EMA 200. The short signal (CMF < 0, %K crossing down through 80, ATR filter) closes the long. No stop loss. 100% of equity per trade; commission set to 0.075%.
- Test: an all-in single-coin plan, so it's judged against BTC Protected Hold (hold-paper) and buy & hold. BTC, plus ETH as the never-seen coin, 0.35% fee.
- Variants: H1 daily. H2 4H.
- Pass: beats Protected Hold on return/DD in both halves on BTC, and makes money on ETH.

Script: research/f28_st_btc.py. Results: research/F28.md.
