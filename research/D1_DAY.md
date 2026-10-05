# D1 1H day bots

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Binance archive 1H candles. Cost 0.15% each side (0.1% taker + 0.05% slippage). Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. Script: research/d1_day.py.

## D1-C capitulation buy

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| C1: drop > 3 sigma | 1st half | 101 | 42% | -5.4% | -9.1% | 0.80 | 217 | 0.94 | -3.8% |
| C1: drop > 3 sigma | 2nd half | 128 | 40% | -10.5% | -15.3% | 0.74 | 391 | 0.77 | -5.9% |
| C2: drop > 2.5 sigma | 1st half | 155 | 35% | -13.6% | -16.9% | 0.68 | 372 | 0.92 | -6.4% |
| C2: drop > 2.5 sigma | 2nd half | 220 | 41% | -13.7% | -15.3% | 0.79 | 698 | 0.95 | -7.9% |
| C3: drop > 3 sigma, BTC above 200-day | 1st half | 59 | 42% | -1.5% | -5.0% | 0.90 | 140 | 1.10 | -3.0% |
| C3: drop > 3 sigma, BTC above 200-day | 2nd half | 56 | 45% | -3.8% | -6.2% | 0.75 | 175 | 1.13 | -3.9% |

- C1: drop > 3 sigma: correlation with v4+TR 0.19; portfolio return/DD 9.42 (+61% / -6.5%) vs v4+TR 15.07 (+99% / -6.6%); own full period -15.3% / DD -16.4% / PF 0.77
  fail: design 1st half not profitable (PF 0.80, -5.4%); never-seen 1st half PF 0.94; design 2nd half not profitable (PF 0.74, -10.5%); design 2nd half DD -15.3%; never-seen 2nd half PF 0.77; portfolio return/DD 9.42 not above 15.07
- C2: drop > 2.5 sigma: correlation with v4+TR 0.22; portfolio return/DD 9.54 (+58% / -6.0%) vs v4+TR 15.07 (+99% / -6.6%); own full period -25.5% / DD -26.1% / PF 0.74
  fail: design 1st half not profitable (PF 0.68, -13.6%); design 1st half DD -16.9%; never-seen 1st half PF 0.92; design 2nd half not profitable (PF 0.79, -13.7%); design 2nd half DD -15.3%; never-seen 2nd half PF 0.95; portfolio return/DD 9.54 not above 15.07
- C3: drop > 3 sigma, BTC above 200-day: correlation with v4+TR 0.20; portfolio return/DD 12.20 (+64% / -5.3%) vs v4+TR 15.07 (+99% / -6.6%); own full period -5.3% / DD -8.3% / PF 0.83
  fail: design 1st half not profitable (PF 0.90, -1.5%); design 2nd half not profitable (PF 0.75, -3.8%); portfolio return/DD 12.20 not above 15.07

Result: no variant passes

## D1-I intraday momentum

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| I1: up > 1% by 14:00 UTC | 1st half | 1245 | 49% | +22.3% | -9.0% | 1.12 | 4073 | 1.02 | -12.4% |
| I1: up > 1% by 14:00 UTC | 2nd half | 1253 | 43% | -20.3% | -24.7% | 0.89 | 5688 | 0.78 | -24.7% |
| I2: up > 2% by 14:00 UTC | 1st half | 752 | 54% | +38.3% | -4.6% | 1.45 | 2930 | 1.14 | -10.3% |
| I2: up > 2% by 14:00 UTC | 2nd half | 674 | 44% | -9.8% | -13.1% | 0.89 | 3499 | 0.82 | -16.1% |
| I3: up > 1%, BTC above 200-day | 1st half | 730 | 52% | +18.2% | -7.8% | 1.17 | 2509 | 0.95 | -12.7% |
| I3: up > 1%, BTC above 200-day | 2nd half | 659 | 44% | +1.8% | -8.9% | 1.02 | 2992 | 0.77 | -20.3% |

- I1: up > 1% by 14:00 UTC: correlation with v4+TR 0.24; portfolio return/DD 5.45 (+65% / -12.0%) vs v4+TR 15.07 (+99% / -6.6%); own full period -2.5% / DD -31.0% / PF 0.99
  fail: design 2nd half not profitable (PF 0.89, -20.3%); design 2nd half DD -24.7%; never-seen 2nd half PF 0.78; portfolio return/DD 5.45 not above 15.07
- I2: up > 2% by 14:00 UTC: correlation with v4+TR 0.16; portfolio return/DD 9.31 (+74% / -8.0%) vs v4+TR 15.07 (+99% / -6.6%); own full period +24.7% / DD -13.8% / PF 1.12
  fail: design 2nd half not profitable (PF 0.89, -9.8%); design 2nd half DD -13.1%; never-seen 2nd half PF 0.82; portfolio return/DD 9.31 not above 15.07
- I3: up > 1%, BTC above 200-day: correlation with v4+TR 0.21; portfolio return/DD 11.46 (+73% / -6.4%) vs v4+TR 15.07 (+99% / -6.6%); own full period +20.4% / DD -11.2% / PF 1.09
  fail: never-seen 1st half PF 0.95; never-seen 2nd half PF 0.77; portfolio return/DD 11.46 not above 15.07

Result: no variant passes

