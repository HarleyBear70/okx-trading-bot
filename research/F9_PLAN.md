# F9: Jeff's own Pine Scripts (plan, written before running)

2026-10-06. Jeff uploaded his TradingView scripts to pine/ (made by Chrome Claude). Each testable rule set is ported to Python and tested at the real fee (0.35% per side), 2018-05 to now plus the halves. Research only. Script: research/f9_pine.py. Results: research/F9.md.

- **P-AMD (pine/amd_fvg), long side only (spot):** accumulation = the last 30 candles' high-low range ≤ 3.5 ATR(14). In the next 10 candles: a candle dips below the box bottom (manipulation), then a bullish FVG (low > the high 2 candles back) closes above the box bottom: buy at the close. Stop 1.5 ATR, target 2R (3 ATR). Same state machine as the script, defaults, no session filter. 0.5% risk, max 3 open.
  - AMD-4H: BTC ETH SOL XRP BNB, 4H.
  - AMD-1H: BTC ETH XRP, 1H (Binance 1H data, as B1c/D1).
- **P-V3 (pine/structure pullback (12check) v3):** SP-12 v3 = v4's entry (Tuned score ≥ 2, EMA 8 > 21 > 55, above daily VWAP, swing 7) with the Pine exits: fixed stop, fixed 3R target (2-15%), 120-candle limit, no breakeven or trail. engine.trade_sim on v4's coins, 0.4% risk.
- **P-CC (pine/jeff's command center), tags on Trend Rider buys:** volume profile of the last swing low → swing high (40 rows, 5-candle swings), built when each swing high is confirmed. pb = the lowest low between the swing high and the buy. Same entry and exit as F3's S0 (+145%, DD −10.3%).
  - CC1 take only "POC tap ✓" buys (pb within 1 ATR of the POC)
  - CC2 take only "Heavy volume ✓" buys (breakout candle volume > 1.5 × its 20-candle average)
  - CC3 skip "Low-volume gap ⚠" buys (pb in a profile row with < 25% of the busiest row's volume)
- Multi-TF Delta + HTF Candles: display only (no buy/sell rule), not testable.

Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%. CC1-CC3 must also beat S0 on return/DD in both halves.

## F9b (added after the F9 run, before running this): CC3 robustness
CC3 (skip Trend Rider buys whose pullback low sits in a low-volume gap) beat S0 in both halves. Same rules on never-seen coins (LTC DOGE ADA LINK BCH AVAX XLM XRP LUNA FTT, i.e. e.UNSEEN minus Trend Rider's coins): CC3 must beat S0 on return/DD in both halves there too before it is proposed for Trend Rider.

## F9c (added before running): pine/sp-12 v4 sar, uploaded after F9
v3's entry; after +1R the target is dropped and the stop trails at max(first stop, Parabolic SAR 0.02/0.02/0.2) while SAR is below the close; no breakeven step. Same pass rules.

## F9d (added before running): does Trend Rider's breakeven step hurt at the real fee?
F9c (v4 without breakeven) made +38% vs −2% for bot.py's v4 with it. Trend Rider also moves its stop to breakeven + 0.7% at +1R. Test: Trend Rider as live (bot.py replay, 0.4% risk) with vs without the breakeven step (BE_BUFFER = −1 makes the floor the first stop, so it never applies). Pass: better return/DD in both halves.
