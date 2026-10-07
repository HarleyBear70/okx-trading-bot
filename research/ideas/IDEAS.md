# Idea log

| Idea | Status | Where |
|---|---|---|
| Funding carry (long spot + short perp when funding is high) | blocked: needs perps / shorting access (Jeff to check Kraken); no spec until then | NOTES idea list #4 |
| Volatility-managed sizing (Moreira & Muir) | FAILED on TR + Donchian: drops past 10%, same return per drop (F34) | research/F34.md |
| N4 short side (mirrored Trend Rider) | research only; paper run if Jeff gets Kraken perps | research/N4_SHORT.md |
| B3 P3 pairs (60 days, z 2.5) as a paper forward test | candidate, Jeff's call | research/B3_PAIRS.md |
| Trend Rider + skip entries in extreme fear (F&G <= 25) | passed S1, Jeff's call | research/S1_SENTIMENT.md |
| M3 rotation for the hold pile | failed the both-halves rule; judgment call | research/HOLD.md |
| Tighten v4's trail after +10R (cut give-back on huge winners) | queued for the Scout as spec V4T | research/specs/V4T_lock_big_winners.py |
| Relative-strength filter (buy only coins beating BTC over 30 days) | FAILED: cuts a third of profit (F34) | research/F34.md |
| Altcoin-season switch for a top-3 rotation (on only when alts beat BTC) | queued for the Saturday research scout | research/F32.md (idea from F32b) |
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
| Rejection block (ICT), long only | Jeff / ICT | wick zone of a swing low before a strong move | tested on crypto 4H | FAILED: all 3 variants lose (research/R1_REJECTION.md) |
| Wyckoff volume filter (volume above average, effort vs result, spring) | Jeff / Wyckoff | better entries | tested on v4, Trend Rider, B1c | only v4 + volume-above-average passed, and it got worse on never-seen coins; not recommended (research/W1_VOLUME.md) |

## Scout queue

The weekly Scout (research/scout.py, Sundays) runs the next 2-3 rows marked "queued", using research/spec_runner.py.
Each row points to a spec file written BEFORE it runs (rules + max 3 variants); the Scout never invents or tunes
anything. Results go in research/specs/results/ and every tested variant is counted in research/specs/LEDGER.md.
A pass only makes a PAPER candidate, and only with Jeff's OK. To add an idea: write a spec file in research/specs/
(copy T1_trend_sizing.py) and add a row here with status "queued".

| Order | Spec | Status | Result |
|---|---|---|---|
| 1 | research/specs/T1_trend_sizing.py | fail | research/specs/results/T1.md |
| 2 | research/specs/T1b_trend_sizing_calibrated.py | queued | - |
| 3 | research/specs/V4T_lock_big_winners.py | queued | - |
