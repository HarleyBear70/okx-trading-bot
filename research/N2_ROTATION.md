# N2 rotation bot

Variants and rules fixed beforehand in research/NEWBOTS_PLAN.md. Universe = CoinMarketCap top 10 (or ranks 11-20) as listed at the time, stablecoins removed. Weekly, 0.1% fee. Script: research/n2_rotation.py.

| Variant | Universe | Half | Holdings | Win % | Return | Max DD | PF |
|---|---|---|---|---|---|---|---|
| M1: top 3, 28-day momentum | top 10 | 1st half | 121 | 42% | +198.0% | -68.5% | 1.28 |
| M1: top 3, 28-day momentum | top 10 | 2nd half | 132 | 46% | +70.8% | -56.1% | 1.17 |
| M1: top 3, 28-day momentum | ranks 11-20 | 1st half | 104 | 46% | +40.1% | -60.7% | 1.09 |
| M1: top 3, 28-day momentum | ranks 11-20 | 2nd half | 110 | 37% | -15.9% | -74.9% | 0.96 |
| M2: top 3, 90-day momentum | top 10 | 1st half | 68 | 49% | +277.2% | -58.7% | 1.70 |
| M2: top 3, 90-day momentum | top 10 | 2nd half | 84 | 43% | +111.3% | -55.0% | 1.35 |
| M2: top 3, 90-day momentum | ranks 11-20 | 1st half | 75 | 41% | +202.3% | -58.3% | 1.28 |
| M2: top 3, 90-day momentum | ranks 11-20 | 2nd half | 84 | 37% | -0.9% | -49.5% | 1.00 |
| M3: top 3, 28-day, volatility-scaled | top 10 | 1st half | 121 | 42% | +118.0% | -38.8% | 1.82 |
| M3: top 3, 28-day, volatility-scaled | top 10 | 2nd half | 132 | 46% | +77.7% | -34.2% | 1.44 |
| M3: top 3, 28-day, volatility-scaled | ranks 11-20 | 1st half | 104 | 48% | +48.9% | -27.5% | 1.40 |
| M3: top 3, 28-day, volatility-scaled | ranks 11-20 | 2nd half | 110 | 39% | +30.5% | -36.7% | 1.20 |

- M1: top 3, 28-day momentum: own 2018-05 to now +403% / DD -72.8%; correlation with v4+TR 0.56; portfolio return/DD 3.68 (+201% / -54.6%) vs v4+TR 15.07 (+99% / -6.6%); top-10 coins skipped for no data: 72 of 2280
  fail: top-10 1st half DD -68.5%; top-10 2nd half DD -56.1%; ranks 11-20 2nd half PF 0.96; correlation 0.56; portfolio return/DD 3.68 not above 15.07
- M2: top 3, 90-day momentum: own 2018-05 to now +690% / DD -58.7%; correlation with v4+TR 0.61; portfolio return/DD 6.61 (+296% / -44.8%) vs v4+TR 15.07 (+99% / -6.6%); top-10 coins skipped for no data: 85 of 2280
  fail: top-10 1st half DD -58.7%; top-10 2nd half DD -55.0%; ranks 11-20 2nd half PF 1.00; correlation 0.61; portfolio return/DD 6.61 not above 15.07
- M3: top 3, 28-day, volatility-scaled: own 2018-05 to now +286% / DD -38.8%; correlation with v4+TR 0.60; portfolio return/DD 8.40 (+162% / -19.2%) vs v4+TR 15.07 (+99% / -6.6%); top-10 coins skipped for no data: 72 of 2280
  fail: top-10 1st half DD -38.8%; top-10 2nd half DD -34.2%; correlation 0.60; portfolio return/DD 8.40 not above 15.07

Result: no variant passes
