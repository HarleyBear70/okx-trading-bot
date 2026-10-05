# H2 market mood detector

Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider as they trade, $1,000 each; new trades only on 'up' days (BTC's last completed daily candle). Script: research/h2_h5.py.

| Version | Half | Trades | Combined return | Combined max DD | Return/DD | Pass? |
|---|---|---|---|---|---|---|
| all bots always on | 1st half | 528 | +52.6% | -5.1% | 10.25 | - |
| all bots always on | 2nd half | 787 | +42.6% | -7.1% | 5.99 | - |
| M1: BTC above 200-day | 1st half | 374 | +24.9% | -5.8% | 4.29 | fail |
| M1: BTC above 200-day | 2nd half | 552 | +31.7% | -7.3% | 4.34 | fail |
| M2: above + 200-day rising, off in a 20% crash | 1st half | 300 | +16.5% | -6.7% | 2.46 | fail |
| M2: above + 200-day rising, off in a 20% crash | 2nd half | 511 | +34.9% | -7.3% | 4.81 | fail |
| M3: above + ADX >= 20 | 1st half | 335 | +17.5% | -4.4% | 3.99 | fail |
| M3: above + ADX >= 20 | 2nd half | 450 | +16.4% | -7.3% | 2.25 | fail |
