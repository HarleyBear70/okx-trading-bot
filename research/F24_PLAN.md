# F24: Jeff's two new TradingView strategies (plan, written before running)

2026-10-06. Two scripts were added to pine/:
- **"my strategy" = Trendline Break Pro (TLB).** Draws a falling resistance line through two lower swing highs (5-bar pivots, at least 8 bars apart, line valid for 150 bars). It buys when a close is 0.1 ATR above the line and the smoothed AO momentum is rising. Stop 1.5 ATR(14), take profit at 2R, stop to break-even at +1R, 2 ATR trailing stop from +1.5R. A support-line break (the script's short signal) closes the long.
- **"my strat 2" = Confluence Rank Trend (CRTS).** A 0-100 score built from five parts worth 20 each: trend (EMA 55/233), RSI, efficiency ratio, ATR-percentile "volatility regime" and up-bar volume. It buys when the score crosses up through 85, uses a 3 ATR trailing stop measured from each close, and sells when the score drops below 35.

Code review: neither script repaints (pivots are confirmed and signals use closed bars). Both scripts' TradingView settings are too generous for us. TLB charges 0.04% commission and CRTS 0.05%, but our real fee is 0.35% per side. Both scripts also trade shorts, and OKX US spot can't short. TLB sizes at 20% of equity and CRTS at a fixed 1 coin. Here: long only, risk 0.4% per trade (like Trend Rider), max 5 open, 0.35% fee per side, 2018-05 to now plus both halves, design coins BTC ETH SOL XRP BNB, plus the never-seen coins.

Variants (3 per script):
- A1 TLB as written, daily. A2 TLB as written, 4H. A3 TLB daily, no 2R take profit (trail and support break only, so winners can run).
- B1 CRTS as written, daily. B2 CRTS as written, 4H. B3 CRTS daily, entry score 75.

Pass (all required): PF >= 1.3, DD <= 10%, positive in both halves, positive on never-seen coins, correlation of monthly returns with Donchian < 0.8. If something passes, it goes to paper only, never straight to demo.
Script: research/f24_jeff2.py. Results: research/F24.md.
