# EMT / Exhaustion Mean Theory (VWAP snap-back) — DEAD

Asked for by Chrome Claude on issue #4 (Oct 9 2026), from a YouTube short. Rules and pass rules written before
the run: see the top of research/emt.py. 2019-now, long + short, crypto 0.05% a side, forex OANDA spread.

**Verdict: DEAD on every market, timeframe and version.** Real-cost PF 0.47-0.67 (pass needs 1.3), both halves
fail, never-seen markets fail, the 4H-trend skip doesn't help. Even with ZERO fees it is only PF 1.05 (5m) /
0.92 (15m): no raw edge. At OKX's 0.35% it loses about 5R a trade on 5m. Win rate is 24-31%; the video showed
only winners. Forex had only 15m history on file (no 5m), so forex was tested on 15m.

### crypto main: BTC ETH SOL

| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|
| A 5m as stated | 37391 | 24% | 0.47 | -0.70R | 26299R | 0.63 | 0.39 |
| B 5m + skip 4H trend | 18488 | 24% | 0.47 | -0.71R | 13078R | 0.63 | 0.39 |
| A 5m at zero fees | 37391 | 25% | 1.05 | +0.04R | 372R | 1.00 | 1.10 |
| A 5m at OKX 0.35% | 37391 | 13% | 0.04 | -5.17R | 193217R | 0.10 | 0.02 |
| C 15m as stated | 8624 | 30% | 0.63 | -0.31R | 2658R | 0.69 | 0.58 |
| B 15m + skip 4H trend | 4209 | 31% | 0.63 | -0.30R | 1269R | 0.71 | 0.58 |
| C 15m at zero fees | 8624 | 32% | 0.92 | -0.05R | 520R | 0.91 | 0.92 |
| C 15m at OKX 0.35% | 8624 | 19% | 0.11 | -1.82R | 15717R | 0.18 | 0.07 |

### crypto never-seen: XRP BNB (+ ADA DOGE on 15m)

| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|
| A 5m as stated | 28157 | 24% | 0.55 | -0.54R | 15124R | 0.66 | 0.48 |
| B 5m + skip 4H trend | 13948 | 23% | 0.53 | -0.57R | 7921R | 0.65 | 0.45 |

### crypto never-seen 15m: XRP BNB ADA DOGE

| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|
| C 15m as stated | 12285 | 30% | 0.67 | -0.28R | 3430R | 0.74 | 0.61 |
| B 15m + skip 4H trend | 6123 | 31% | 0.66 | -0.28R | 1756R | 0.73 | 0.61 |

### forex main: EUR/USD gold (15m only)

| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|
| C 15m as stated | 4617 | 29% | 0.65 | -0.29R | 1363R | 0.62 | 0.68 |
| B 15m + skip 4H trend | 2267 | 29% | 0.65 | -0.29R | 662R | 0.61 | 0.69 |

### forex never-seen: GBP AUD JPY (15m only)

| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |
|---|---|---|---|---|---|---|---|
| C 15m as stated | 7738 | 28% | 0.65 | -0.31R | 2363R | 0.63 | 0.67 |
| B 15m + skip 4H trend | 3708 | 29% | 0.66 | -0.29R | 1068R | 0.62 | 0.72 |
