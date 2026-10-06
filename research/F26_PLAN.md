# F26: Jeff's "my strat 4" = ATR Breakout Trend Strategy (plan, written before running)

2026-10-06. Rules: buy when the close crosses above the prior 20-bar high **and** is above the 200-bar SMA. Initial stop 2 × ATR, where ATR is an SMA of true range over 20 bars. Exit on a close below the prior 20-bar low (at that close). The ATR trailing stop (2 ATR under the bar's high) is off by default. Sizing: 1% risk, capped at 100% of equity. Shorts are on by default; we can't short on OKX US spot.

This is nearly the live Donchian bot. Donchian enters on any close above the 20-day high, uses a 2 ATR stop, and trails at the 10-day low. The new parts are the 200-day SMA filter, the cross-only entry, the 20-day exit and the optional trailing stop. So it is judged as a **replacement or upgrade for Donchian**, not as an add-on.

Code review: no repainting (the channels use [1], and entries require a confirmed bar). TradingView commission is 0.06% vs our real 0.35%. `process_orders_on_close=true` fills at the signal close, which is how our simulator works too.

Test: long only, 0.35% risk (same as the Donchian comparison), max 5 coins, 0.35% fee per side, 2018-05 to now plus both halves, BTC ETH SOL XRP BNB and the never-seen coins.
- D1 as written, daily.
- D2 as written with the ATR trailing stop on, daily.
- D3 live Donchian rules + only the 200-day SMA filter (does the filter alone improve Donchian?).

Pass: beat plain Donchian (+122.8% / −9.1%, F24) on return/DD in both halves and on never-seen coins, with PF ≥ 1.3 and DD ≤ 10%.
Script: research/f26_atrbo.py. Results: research/F26.md.
