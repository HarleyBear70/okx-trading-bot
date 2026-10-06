# F25: Jeff's "my strat 3" = Trend Analysis Strategy (plan, written before running)

2026-10-06. The script's default trades:
- **Tracker:** an ATR trailing line, WMA(true range, 14) × 2.2 from the high/low, which flips bull/bear when the close crosses it.
- **Entry:** buy on a bull flip, or within 10 bars of it, if the 6-part trend score is ≥ 50%. The six parts: tracker direction; close vs the "equilibrium" HMA(linreg 55, 9); equilibrium slope; RSI vs 50; RSI vs its 14-bar average; +DI vs −DI.
- **Exits:** initial stop at the tracker line. Three take-profits: 33% at 1.5R, 33% at 2.5R, the rest at 3.5R. The stop moves to break-even after TP1. A bear flip closes the trade. The trailing stop is off by default.
- **Defaults that don't count here:** the other filters (ADX, RSI, volume, MTF, zones) are off by default, and the consolidation zones are drawn only.

Code review: no repainting. The MTF table uses closed higher-timeframe bars with the correct lookahead pattern, and its filter is off anyway. TradingView commission is set to 0.05%; ours is 0.35%. The script also shorts by default, which we can't do on OKX US spot.

Test: long only, 0.4% risk, max 5 coins, 0.35% fee per side, 2018-05 to now plus both halves, BTC ETH SOL XRP BNB and the never-seen coins. The three take-profits are simulated as three one-third pieces.
- C1 as written, daily.
- C2 daily, no take-profits: the stop trails at the tracker line and the trade exits on the flip (let winners run).
- C3 as written, 4H.

Pass: PF ≥ 1.3, DD ≤ 10%, positive in both halves and on never-seen coins, corr. with Donchian < 0.8, and it must improve Donchian's return/DD in both halves when added (as F24's follow-up did).
Script: research/f25_tas.py. Results: research/F25.md.
