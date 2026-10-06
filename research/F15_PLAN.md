# F15: spot grid bot: price range, grid count, maker vs taker (plan, written before running)

2026-10-06. Jeff asked about grid bots (OKX's built-in spot grid): the price range (upper/lower limits), grid step/count and order type (maker vs taker). No grid bot was ever tested in this repo. Research only. Script: research/f15_grid.py. Results: research/F15.md.

Simulation (1H candles, BTC ETH XRP, $1,000 per coin, 2018-05 to now plus the halves):
- Range: on the 1st of every month, the lower/upper limits = the lowest low / highest high of the previous 30 days (at least ±5% around the price). Geometric grid with N lines; each grid slot holds an equal share of the $1,000.
- Start: slots above the price are filled at once (buy coin at market, taker fee), so they have something to sell; slots below wait with a buy order.
- Each hour, price moves open → low → high → close (or open → high → low → close on a red candle). Going down through a line fills that slot's buy; going up through the next line fills its sell. The profit per round trip is one grid step minus two fees.
- Monthly reset: whatever coin the grid holds is sold at market (taker) and a new range is set. Below the range the grid is full of coin (losing with the price); above it the grid is all cash (missing the rally).
- G1: 20 grids, limit orders (maker 0.20%). G2: 50 grids (smaller step), maker 0.20%. G3: 20 grids, market orders (taker 0.35%), to show the order-type effect.
Reported against buy-and-hold of the same coins. Pass: positive in both halves, PF-equivalent not used; DD ≤ 10% is applied as for every bot, and the result must beat holding on return/DD.
