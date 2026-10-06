# F6: popular TradingView trend indicators at the real fee (plan, written before running)

2026-10-06. The user asked: "can u check anything on trading view as ideas or indicators we could use." The TradingView connector only gives current readings (indicator snapshots, screener values such as social sentiment and open interest), so those can't be backtested over 8 years. Its standard indicators are calculated from price, so they can. Research only. Script: research/f6_tv.py. Results: research/F6.md.

Daily candles, Donchian's coins (BTC ETH SOL XRP BNB), 0.35% risk, max 5 open, real fee 0.35% per side, 2018-05 to now plus the halves.

- T1 Donchian + ADX filter: Donchian Trend exactly, but take the breakout only when ADX(14) > 20 (a trend is present). Classic whipsaw filter. Compared with Donchian (+123%, DD −9.1%).
- T2 Supertrend(10, 3) daily: buy when it flips up (green), sell when it flips down (red); first stop 2 ATR(20).
- T3 MACD(12, 26, 9) daily: buy when the MACD line crosses above the signal line with the close above the 200-day SMA; sell when it crosses back below; first stop 2 ATR(20).

Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%. T1 must also beat Donchian on return/DD in both halves. A T2 or T3 that passes is a candidate new bot (correlation with the current bots reported).

## F6b (added after the F6 run, before running this): T3 robustness
T3 (MACD + 200-day SMA) passed. Same rules on never-seen coins (LTC DOGE ADA LINK BCH AVAX SUI XLM LUNA FTT): it must be positive in both halves with PF ≥ 1.2. Also its monthly correlation with Trend Rider, Donchian and NNFX.
