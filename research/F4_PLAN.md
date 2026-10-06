# F4: volume, RSI and "smart money" at the real fee (plan, written before running)

2026-10-06. The user asked: "what about volume or rsi or smart market money, etc." Research only. Script: research/f4_test.py. Results: research/F4.md. Real fee 0.35% per side, 2018-05 to now plus the halves, $1,000 each.

Already known (no new test needed):
- Smart-money concepts one by one (research/CONCEPTS.md): only "BOS + daily uptrend" has a real edge (that is Trend Rider). Order block retest: no edge. FVG retest, liquidity sweep, market shift, discount zone: mixed (works in one half only). F3 (Oct 6): a discount pullback or a sweep before the BOS makes Trend Rider worse.
- Volume (research/W1_VOLUME.md, at the old 0.1% fee): WV1 (decision candle volume above its 20-candle average) PASSED on SP-12 v4 and halved its trades. It failed on Trend Rider and B1c.
- Volatility filters (VOL.md), BTC mood (H2) and Fear & Greed (S1) mostly failed; only the fear filter on Trend Rider is in use.

New tests (max 3 variants per idea):
- V1: SP-12 v4 + WV1 volume at the real fee (4H, 0.4% risk, live exit rules). Fewer trades means less fee drag: can volume rescue v4?
- V2: Donchian Trend + WV1 (breakout day's volume above its 20-day average), 0.35% risk, max 5 open.
- R1: RSI(2) pullback in an uptrend (Connors), daily, BTC ETH SOL XRP BNB: buy when the close is above the 200-day SMA and RSI(2) < 10; sell when the close is above the 5-day SMA; 3 ATR stop; 0.5% risk, max 5 open.
- R2: RSI(14) momentum, daily, same coins: buy when RSI(14) crosses above 60 with the close above the 200-day SMA; sell when RSI(14) crosses below 40; 2 ATR stop; 0.5% risk, max 5 open.
Pass: positive in both halves, PF ≥ 1.3, DD ≤ 10%. V1 and V2 must also beat their unfiltered bot on return/DD in both halves.

"Smart money" as in following top traders (OKX smart-money signals): no long history to backtest. If the OKX tools give a usable signal history it gets a paper forward test; otherwise it is noted as untestable.

## F4b (added after the F4 run, before running these): R2 robustness
R2 (RSI(14) momentum) made +345% with PF 5.17, positive in both halves, but its drop is −22.7% at 0.5% risk (it gives back open profit before RSI falls below 40). Same rules, no changes:
- R2 at 0.2% and 0.25% risk (does DD drop under 10%?)
- R2 on never-seen coins (LTC DOGE ADA LINK BCH AVAX SUI XLM LUNA FTT) at 0.5% risk: positive in both halves with PF ≥ 1.2.
- Monthly correlation with Trend Rider and Donchian.
