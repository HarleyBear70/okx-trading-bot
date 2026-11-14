# Research team

How new trading ideas get tested before any bot trades them. Claude runs it; Jeff brings ideas.

## The three jobs

1. **Rule writer**: turns an idea (a Brad Goh video, a book, a chart pattern Jeff noticed) into exact rules a computer can test. No vague "looks strong".
2. **Tester**: backtests the rules on OKX prices with Freqtrade (1,000 USDT start, 0.1% fee, 1% risk per trade).
3. **Skeptic**: tries to prove the idea is luck or a bug.
   - Splits the test in two halves (Mar 2024 - Jun 2025, Jul 2025 - now). Must make money in both.
   - Checks the result is not one lucky trade.
   - Checks the numbers make sense (a surprising result gets checked before it is believed).
   - The concept test was run on fake random prices first and found nothing, which shows it is not fooled by noise.

## Rules

- Test a few ideas at a time, only ideas that make sense. Testing hundreds and keeping the best is how people fool themselves.
- An idea passes if: profit factor above 1.3, worst drop under 10%, beats buy and hold, and works in both halves.
- Passing ideas go to practice trading for a few weeks before real money.
- Ideas that fail are written down with the reason, so they are not retried by accident.

## Weekly (every Sunday, automatic)

- `freqtrade/results/SUMMARY.md`: full backtest of each strategy
- `freqtrade/results/SKEPTIC.md`: first half vs second half
- `freqtrade/results/COINSCAN.md`: which coins each strategy works on
- `research/CONCEPTS.md`: which of Brad's concepts actually move price

## Idea log

| Date | Idea | Source | Result |
|---|---|---|---|
| 2026-10-04 | Brad's concepts one by one (BOS, market shift, sweep, FVG, order block, discount zone) | Brad Goh videos | see CONCEPTS.md |
| 2026-10-04 | New coins DOGE, SUI, BNB, AVAX, ADA | Jeff's watchlist | BNB and SUI positive on both strategies; AVAX and DOGE negative |
| 2026-10-04 | Gold with Trend Rider and SP-12 v2 | gold paper bots | about +33% on both |
| 2026-10-05 | Trend Rider + BNB + SUI | coin scan | +62%, PF 1.71, both halves up, worst drop 11.6% - Watch (next to try in practice) |
| 2026-10-05 | Trend Rider on 1H chart | Jeff prefers 1H | Fail: -35%, worst drop 49% - too much noise and fees |
| 2026-10-05 | Fixed 1% stop / 2.5% target on Trend Rider entries | Jeff manual style | Fail: -15% - tight fixed stops cut winners short |
| 2026-10-05 | SP-12 v4 + BNB + SUI | coin scan | Fail: lost money in first half - keep BTC ETH XRP |
| 2026-10-05 | DCA bot (3Commas style) | 3Commas/Bitsgap/Haas | Fail: +1% vs +42% just holding, worst drop 24% |
| 2026-10-05 | Flash crash dip buyer | HaasOnline | Fail: -24% |
| 2026-10-05 | Candle patterns (engulfing, hammer, morning star, soldiers, inside bar, big breakout) | investment club pitch | Real: inside bar breakout, big breakout candle in daily uptrend. No edge: engulfing, hammer, morning star - see CANDLES.md |
| 2026-10-05 | Candle Range Theory (CRT 3-candle model) - closest public match to the club pitch | Mechanix Framework talk | No edge: slightly worse than a random candle |
| 2026-10-05 | Stricter skeptic (shift test, checked on fake random prices) | process fix | BOS alone downgraded to could-be-luck; BOS + daily uptrend still Real |
| 2026-10-05 | Fixed 1-1.5% stop / 1.5-3% take profit on v4 and Trend Rider entries, 8 years (fixed_exits_test.py) | Jeff | Fail: all 24 combos lose (best v4 -13%, TR -37% vs +93% / +195% now) - stops inside normal 4H noise, fees, winners capped |
| 2026-10-10 | Month-end USD flow (forex short) and Bollinger-stretch fade (forex+crypto) | bank desk notes, quant theses | NOT RUN: data hosts blocked in sandbox; rules saved in F43.md |
| 2026-10-17 | Weekly scout run | scheduled | NOT RUN: data hosts blocked again (only OKX reachable); see F44.md |
| 2026-10-24 | Turn of month (long, crypto) | bank desk notes, F43 | Fail: 2nd half -2.3%, PF 0.52 - F45.md |
| 2026-10-24 | Bollinger stretch fade (crypto long) | quant thesis, F43 | Fail: PF 1.03 at 0.35%, 1.18 at 0.02% - F45.md |
| 2026-10-24 | Bandwidth squeeze breakout (crypto) | TradingView-style write-ups | Fail/too few trades - F45.md. Forex ideas still NOT RUN (FX data hosts blocked) |
| 2026-10-31 | Dip in uptrend (3 down days, -8%, above SMA100) crypto long | own variant, arXiv 2602.11708 context | Fail: first half flat, PF 1.00 - F46.md |
| 2026-10-31 | Gated fast breakout (10-day high, above SMA200, SMA50>SMA200, 5-day low exit) crypto long | own variant | Candidate: PF 2.9/2.1 both halves at 0.35%; overlap with Donchian untested - F46.md. Forex still NOT run (data blocked) |
| 2026-11-07 | Month-end dollar flow (EUR/USD, GBP/USD short, plus long mirror), daily closes only | bank desk notes, Melvin & Prins 2013, HSBC Donnelly | Fail: short flat/negative, mirror flips sign between halves - F47.md |
| 2026-11-07 | Bollinger stretch fade (EUR/USD, GBP/USD both ways), daily closes only | quant thesis, F43 | Fail: PF 0.83-1.16, EUR first half -4.6% - F47.md. Only close data (no FXCM) |
| 2026-11-14 | NR4 + volatility-contraction breakout in uptrend (crypto long) | Street Smarts / cryptodatadownload | Fail: 2nd half negative, PF 0.92 at 0.35%, too few trades - F48.md |
| 2026-11-14 | 3-day streak fade (EUR/USD, GBP/USD both ways), closes only | tastyfx, short-term reversal papers | Fail: PF 0.92-1.06 - F48.md |
| 2026-11-14 | Trend pullback vs SMA200 (EUR/USD, GBP/USD both ways), closes only | own variant | Fail: EUR +7% pre-2019 then -6%, GBP negative - F48.md |
