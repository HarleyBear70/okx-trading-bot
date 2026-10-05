# Idea log

| Idea | Status | Where |
|---|---|---|
| Funding carry (long spot + short perp when funding is high) | waiting: Jeff to confirm perps / shorting access | NOTES idea list #4 |
| Volatility-managed sizing (Moreira & Muir) | queued as part of H1 | NOTES idea list #2 |
| N4 short side (mirrored Trend Rider) | research only; paper run if Jeff gets Kraken perps | research/N4_SHORT.md |
| B3 P3 pairs (60 days, z 2.5) as a paper forward test | candidate, Jeff's call | research/B3_PAIRS.md |
| Trend Rider + skip entries in extreme fear (F&G <= 25) | passed S1, Jeff's call | research/S1_SENTIMENT.md |
| M3 rotation for the hold pile | failed the both-halves rule; judgment call | research/HOLD.md |
| Tighten v4's trail after +10R (cut give-back on huge winners) | untested; trades some upside for DD | NOTES job 2e |
| Dip DCA for the hold pile (2x when 20% below 200-day) | passed; Jeff to set it up (job 4) | research/HOLD.md |

## From published sources (Quantpedia free articles, Google Scholar / SSRN). Free content only.

| Idea | Source | Claimed edge | Crypto-tested? | Status |
|---|---|---|---|---|
| Bitcoin 21:00-23:00 UTC seasonality (buy 21:00, sell 23:00 daily) | Quantpedia own research, "Are There Seasonal Intraday or Overnight Anomalies in Bitcoin?" and "The Seasonality of Bitcoin" (Gemini hourly 2015-10 to 2023-06) | 33-41% a year, max DD about -22%; fees not included | yes (BTC) | FAILED after fees (research/Q1_BTC_HOURS.md): -75% to -93% at 0.1% fees; tiny edge since 2022 even at maker fees |
| Same, only when 30-day volatility is above its 1-year median | Quantpedia, "The Seasonality of Bitcoin" | 37% a year, DD -19% | yes (BTC) | FAILED after fees (Q1b) |
| Price overreactions: trade the day after an abnormal daily move | Caporale & Plastun (2018, SSRN), via Quantpedia | none: results "not significantly different from random" | yes (BTC LTC XRP DASH) | skip: authors found no edge, and our D1 capitulation buy failed |
| Crypto momentum fades and needs long-only + cost-aware testing | "Cryptocurrency anomalies and economic constraints" (2024, open.icm.edu.pl) | momentum works in large coins, mostly in bull markets, fading over time; most alpha from shorts | yes | insight only: matches our "2018-21 only" finding; supports judging on recent years |
| 20+ stock anomalies on daily crypto data | "Behavioral Anomalies in Cryptocurrency Markets" (2023, SSRN / UZH) | price momentum strong after market and size controls | yes | covered by v4 / Trend Rider / N2 |
| NNFX daily system (No Nonsense Forex method) | NNFX community method (Chrome / Jeff) | trend system built from C1 + baseline + volume + exit | built and tested on both | forex FAILED out of sample; crypto long-only Aroon(25) version strong (2022-now PF 2.20) but 0.75 correlated with v4+TR (research/NNFX.md); paper candidate if Jeff wants |
| TRX for Trend Rider | Scout flag | passed pick + check; TR + TRX better on every measure | yes | awaiting Jeff's OK (research/TRX.md) |
