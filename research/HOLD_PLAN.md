# Hold pile test: M3 rotation vs buy-and-hold vs DCA vs dip-buying DCA (covers job H4)
(written before any test was run)

Data: daily closes (research/universe.py: Binance archive, BTC and XRP; M3 uses the historical top-10
universe as in N2). Every buy and sell pays 0.1%. Trades happen at the Monday 00:00 UTC price (Sunday close).
Periods: 2018-05 to now, and the halves 2018-05 to end of 2021 / 2022 to now, each started fresh.

Contenders:
- Lump sums ($1,000 on day one): (1) buy-and-hold BTC, (2) buy-and-hold 50/50 BTC + XRP, (3) M3 rotation
  (top 3 of the top 10 by 28-day momentum, volatility-scaled, cash when BTC is below its 200-day average).
- Weekly ($10 every Monday): (4) plain DCA, $5 BTC + $5 XRP; (5) dip DCA (H4): as (4), but a coin gets
  double ($10) in a week when its close is 20% or more below its 200-day average; (6) M3 with the $10
  added each week as cash before the rebalance.

Measured on a time-weighted unit value (so weekly deposits don't count as gains): return, max drawdown,
worst calendar year, share of days below a previous peak, and the longest stretch below a previous peak.
For the weekly ones also: total paid in, final value, value / paid in, and (4, 5) the average price paid
per BTC and per XRP.

Decision rules:
- M3 is recommended for the hold pile only if, in BOTH halves, it has a smaller max drawdown than
  buy-and-hold BTC AND a higher return / max drawdown.
- Dip DCA is recommended over plain DCA only if, in BOTH halves, it buys both coins at a lower average
  price AND its value / paid in is not lower.
