# S1 Fear & Greed filter on v4 and Trend Rider

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Index: alternative.me, last completed day. Bots as they trade (shared $1,000, max 3 open). Script: research/b3_s1.py.

| Bot | Version | Half | Trades | Return | Max DD | Return/DD | PF | Pass? |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 | no filter | 1st half | 274 | +50.4% | -6.3% | 8.06 | 1.62 | - |
| SP-12 v4 | no filter | 2nd half | 461 | +28.4% | -10.2% | 2.80 | 1.23 | - |
| SP-12 v4 | F1: skip when >= 75 | 1st half | 227 | +40.0% | -6.6% | 6.02 | 1.62 | fail |
| SP-12 v4 | F1: skip when >= 75 | 2nd half | 425 | +12.5% | -9.5% | 1.33 | 1.12 | fail |
| SP-12 v4 | F2: skip when <= 25 | 1st half | 252 | +41.9% | -6.3% | 6.71 | 1.58 | fail |
| SP-12 v4 | F2: skip when <= 25 | 2nd half | 430 | +20.0% | -11.2% | 1.79 | 1.17 | fail |
| SP-12 v4 | F3: both | 1st half | 205 | +32.1% | -6.6% | 4.83 | 1.58 | fail |
| SP-12 v4 | F3: both | 2nd half | 394 | +5.6% | -11.2% | 0.50 | 1.06 | fail |
| Trend Rider | no filter | 1st half | 254 | +54.7% | -5.7% | 9.60 | 1.88 | - |
| Trend Rider | no filter | 2nd half | 326 | +56.9% | -7.0% | 8.14 | 1.75 | - |
| Trend Rider | F1: skip when >= 75 | 1st half | 199 | +35.9% | -5.7% | 6.31 | 1.74 | fail |
| Trend Rider | F1: skip when >= 75 | 2nd half | 293 | +57.6% | -7.0% | 8.24 | 1.88 | fail |
| Trend Rider | F2: skip when <= 25 | 1st half | 244 | +55.4% | -5.5% | 10.08 | 1.94 | PASS |
| Trend Rider | F2: skip when <= 25 | 2nd half | 311 | +60.1% | -5.3% | 11.30 | 1.84 | PASS |
| Trend Rider | F3: both | 1st half | 189 | +36.5% | -5.5% | 6.65 | 1.80 | fail |
| Trend Rider | F3: both | 2nd half | 278 | +60.8% | -5.3% | 11.43 | 1.99 | fail |

- SP-12 v4, F1: skip when >= 75: fail
- SP-12 v4, F2: skip when <= 25: fail
- SP-12 v4, F3: both: fail
- Trend Rider, F1: skip when >= 75: fail
- Trend Rider, F2: skip when <= 25: PASS
- Trend Rider, F3: both: fail
