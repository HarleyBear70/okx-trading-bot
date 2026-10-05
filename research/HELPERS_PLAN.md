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

## H2. Market mood detector

One label per day from BTC's last completed daily candle; v4 and Trend Rider may open new trades only on
"up" days (exits untouched). No range bot passed, so sideways and crash both mean "no new trades".
- M1: up = BTC above its 200-day average.
- M2: up = BTC above its 200-day average AND that average higher than 20 days earlier; crash (no trades) =
  BTC down 20% or more over the last 30 days, overriding up.
- M3: up = BTC above its 200-day average AND daily ADX(14) at least 20 (trending, not sideways).
Pass: in BOTH halves, the combined return / max DD beats "all bots always on".

## H3. News guard

US high-impact events: FOMC rate decisions (federalreserve.gov calendars, 19:00 UTC used for the 2pm ET
statement unless the page gives otherwise... standard ET time converted with daylight saving), CPI and
Non-Farm Payrolls release times (TradingView economic calendar, exact UTC times). No new trades whose
4H decision candle closes inside the window around an event.
- G1: from 4 hours before to 4 hours after.
- G2: from 12 hours before to 12 hours after.
- G3: from 24 hours before to 4 hours after.
Pass: in BOTH halves, combined return / max DD higher and combined return at least 90% of no guard.

## H5. Profit sweeper

After every winning trade (including the half sold at +2R), a share of the profit leaves the trading bot's
balance and buys BTC + XRP 50/50 for the hold pile at that moment's price (0.1% fee), held to the end.
Combined = trading balances + hold pile value.
- K1: 25% of each win.
- K2: 50% of each win.
No pass rule (Chrome asked for the effect): report combined return, max DD and return / DD per half,
vs no sweeping, plus how big the hold pile gets.
