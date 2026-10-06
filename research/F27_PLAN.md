# F27: Jeff's "my strat 5" = TRADLEWARE DCA + Trend (plan, written before running)

2026-10-06. This is a long-term buying plan for US stock ETFs (MGK, QQQ, VOO), not a trading bot. Defaults:
- Buy $300 on the first day of every month, always, including in bear markets.
- Regime: bull when the close is more than 2% above the 200-day SMA, bear when it is more than 2% below (2% hysteresis).
- When the regime flips to bear, sell the whole stack.
- After a crash exit, a "dip ladder" spends 95% of the sale value in three equal pieces as price falls 15%, 20% and 30% below the all-time high. Any piece that hasn't bought by the time the regime turns bull again buys then.
- Fills at the next day's open. TradingView commission is set to 0%; ours is 0.35%.

Question: does it beat what the Hold pile (bot.py run_dca) already does on crypto? The Hold pile buys weekly, never sells, and doubles the buy when price is 20%+ under the 200-day average.

Test: BTC and XRP (the Hold pile coins), plus ETH, each on its own, daily, 0.35% fee per buy and sell, $300 a month of new money. Periods: 2018-05 to now, plus both halves, each starting from zero.
Compared against: plain monthly DCA (never sells) and the Hold pile rule (same money spread weekly, double on deep dips).
- E1 as written (ladder at 15/20/30% below the high).
- E2 ladder set for crypto's deeper bear markets (40/55/70%).
- E3 ladder off (95% of the sale buys back when the regime turns bull).

Measures: total put in, final value, value ÷ money put in, and the worst drop of the account (time-weighted, so new deposits don't hide losses).
Pass: higher value ÷ money put in than the Hold pile on all three coins and in both halves, without a worse drop.
Script: research/f27_dca.py. Results: research/F27.md.
