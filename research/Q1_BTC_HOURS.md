# Q1 Bitcoin 21:00-23:00 UTC seasonality

Rules fixed beforehand in research/IDEAS_PLAN.md. Binance 1H, full balance for 2 hours a day. Script: research/q1_btc_hours.py.

| Variant | Cost each side | Period | Trades | Win % | Return | Max DD | PF |
|---|---|---|---|---|---|---|---|
| Q1a every day | 0.1% | 1st half (2018-05 to 2021) | 1341 | 42% | -74.6% | -75.5% | 0.67 |
| Q1a every day | 0.1% | 2nd half (2022-now) | 1734 | 34% | -93.4% | -93.4% | 0.51 |
| Q1a every day | 0.1% | never published (2023-07 to now) | 1188 | 34% | -80.1% | -80.1% | 0.57 |
| Q1a every day | 0.02% | 1st half (2018-05 to 2021) | 1341 | 53% | +116.7% | -27.6% | 1.22 |
| Q1a every day | 0.02% | 2nd half (2022-now) | 1734 | 48% | +5.8% | -32.2% | 1.02 |
| Q1a every day | 0.02% | never published (2023-07 to now) | 1188 | 49% | +33.0% | -15.7% | 1.11 |
| Q1a every day | 0.1% | ETH + XRP pooled, 1st half (2018-05 to 2021) | 2679 | | P/L -1067 USD | worst -65.6% | 0.86 |
| Q1a every day | 0.1% | ETH + XRP pooled, 2nd half (2022-now) | 3438 | | P/L -1880 USD | worst -97.2% | 0.60 |
| Q1b high volatility only | 0.1% | 1st half (2018-05 to 2021) | 588 | 48% | -17.9% | -25.8% | 0.92 |
| Q1b high volatility only | 0.1% | 2nd half (2022-now) | 778 | 36% | -64.0% | -66.4% | 0.65 |
| Q1b high volatility only | 0.1% | never published (2023-07 to now) | 598 | 35% | -60.3% | -60.8% | 0.55 |
| Q1b high volatility only | 0.02% | 1st half (2018-05 to 2021) | 588 | 56% | +110.5% | -10.7% | 1.35 |
| Q1b high volatility only | 0.02% | 2nd half (2022-now) | 778 | 49% | +25.0% | -14.7% | 1.11 |
| Q1b high volatility only | 0.02% | never published (2023-07 to now) | 598 | 48% | +3.4% | -14.7% | 1.02 |
| Q1b high volatility only | 0.1% | ETH + XRP pooled, 1st half (2018-05 to 2021) | 1066 | | P/L -350 USD | worst -39.4% | 0.94 |
| Q1b high volatility only | 0.1% | ETH + XRP pooled, 2nd half (2022-now) | 1460 | | P/L -1331 USD | worst -73.8% | 0.68 |
| Q1c Thu + Fri only | 0.1% | 1st half (2018-05 to 2021) | 384 | 41% | -19.3% | -21.5% | 0.85 |
| Q1c Thu + Fri only | 0.1% | 2nd half (2022-now) | 494 | 33% | -56.3% | -56.4% | 0.47 |
| Q1c Thu + Fri only | 0.1% | never published (2023-07 to now) | 338 | 36% | -33.0% | -33.2% | 0.57 |
| Q1c Thu + Fri only | 0.02% | 1st half (2018-05 to 2021) | 384 | 53% | +49.2% | -10.7% | 1.36 |
| Q1c Thu + Fri only | 0.02% | 2nd half (2022-now) | 494 | 46% | -3.6% | -23.8% | 0.96 |
| Q1c Thu + Fri only | 0.02% | never published (2023-07 to now) | 338 | 47% | +15.1% | -9.1% | 1.24 |
| Q1c Thu + Fri only | 0.1% | ETH + XRP pooled, 1st half (2018-05 to 2021) | 767 | | P/L -132 USD | worst -28.4% | 0.97 |
| Q1c Thu + Fri only | 0.1% | ETH + XRP pooled, 2nd half (2022-now) | 980 | | P/L -1101 USD | worst -60.0% | 0.61 |

- Q1a every day: correlation 0.06, portfolio return/DD 1.84 vs 15.07. fail: loses in 1st half (2018-05 to 2021); DD -75.5% in 1st half (2018-05 to 2021); loses in 2nd half (2022-now); DD -93.4% in 2nd half (2022-now); loses in never published (2023-07 to now); ETH + XRP PF 0.86 in 1st half (2018-05 to 2021); ETH + XRP PF 0.60 in 2nd half (2022-now); portfolio return/DD 1.84 not above 15.07
- Q1b high volatility only: correlation -0.15, portfolio return/DD 5.49 vs 15.07. fail: loses in 1st half (2018-05 to 2021); DD -25.8% in 1st half (2018-05 to 2021); loses in 2nd half (2022-now); DD -66.4% in 2nd half (2022-now); loses in never published (2023-07 to now); ETH + XRP PF 0.94 in 1st half (2018-05 to 2021); ETH + XRP PF 0.68 in 2nd half (2022-now); portfolio return/DD 5.49 not above 15.07
- Q1c Thu + Fri only: correlation 0.00, portfolio return/DD 3.17 vs 15.07. fail: loses in 1st half (2018-05 to 2021); DD -21.5% in 1st half (2018-05 to 2021); loses in 2nd half (2022-now); DD -56.4% in 2nd half (2022-now); loses in never published (2023-07 to now); ETH + XRP PF 0.97 in 1st half (2018-05 to 2021); ETH + XRP PF 0.61 in 2nd half (2022-now); portfolio return/DD 3.17 not above 15.07
