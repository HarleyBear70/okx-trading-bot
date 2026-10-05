# H3 news guard

Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider as they trade, $1,000 each. Events: research/events_us.json (FOMC, CPI, NFP since 2018). Script: research/h3_news.py.

| Version | Half | Trades | Combined return | Combined max DD | Return/DD | Pass? |
|---|---|---|---|---|---|---|
| no guard | 1st half | 528 | +52.6% | -5.1% | 10.25 | - |
| no guard | 2nd half | 787 | +42.6% | -7.1% | 5.99 | - |
| G1: 4h before to 4h after | 1st half | 523 | +53.9% | -5.1% | 10.51 | PASS |
| G1: 4h before to 4h after | 2nd half | 772 | +44.7% | -7.3% | 6.16 | PASS |
| G2: 12h before to 12h after | 1st half | 505 | +50.1% | -5.0% | 10.09 | fail |
| G2: 12h before to 12h after | 2nd half | 742 | +43.2% | -7.9% | 5.44 | fail |
| G3: 24h before to 4h after | 1st half | 496 | +52.7% | -4.7% | 11.12 | PASS |
| G3: 24h before to 4h after | 2nd half | 751 | +43.9% | -7.3% | 6.04 | PASS |
