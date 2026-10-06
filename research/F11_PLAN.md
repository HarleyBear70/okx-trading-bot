# F11: Chrome's L1-L3 (plan, written before running)

2026-10-06. From NOTES.md (Chrome, ideas from Jeff's chat). Jeff: "yes ... test". Research only. Script: research/f11_chrome.py. Results: research/F11.md. Real fee 0.35% per side, 2018-05 to now plus the halves, never-seen coins where the rules say so.

## L1: liquidity sweep bot (Brad's material), 1H, long only, BTC ETH XRP (Binance 1H)
Each UTC day, the previous day's low (PDL) and high (PDH). Sweep: a 1H candle trades below the PDL; then, within 24 candles, a 1H candle closes back above the PDL (reclaim). Entry: the first 1H close above the last swing high (3 candles each side) within 24 candles after the reclaim, while price has not traded below the sweep's lowest low. Stop: the lowest low since the sweep began × 0.998. 0.5% risk, max 3 open.
- L1a target the PDH (skip if it is not above the entry)
- L1b target 2R
- L1c no target: trail at the highest close − 3 ATR(14) (Trend Rider's exit)
Comparison: B2 (box reclaim, failed from 2022) and D1 (1H bots, failed). Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%.

## L2: BTC leash (overlay)
New buys on non-BTC coins only when BTC's own trend is up, using each bot's own trend rule on BTC:
- Trend Rider (4H): BTC's 4H close above its 4H 50 EMA and BTC's last daily close above its daily 50 EMA. Run as F3's S0 (engine.trade_sim, 0.4% risk).
- Donchian (daily, as live with pyramiding): BTC's daily close above its daily 50 EMA. bot.py replay.
Each on its own coins and on never-seen coins, vs the same bot without the leash. Pass: better return/DD in both halves on both coin sets.

## L3: crowding filter (overlay), funding only
OI history is not available for 8 years from any source reachable here (Binance and Bybit block the US; OKX keeps about 3 months of funding and no long OI history). BitMEX XBTUSD funding is public back to 2017 (research/bitmex_funding.py), and it ends 2026-09-16; after that the filter is off. Signal: BTC's funding averaged over the last 3 prints (one day) is in the top 10% of the prior 90 days → skip new buys on every coin (crowded longs).
- On Trend Rider (as in L2) and Donchian (as live), own coins and never-seen coins. Pass as L2.
