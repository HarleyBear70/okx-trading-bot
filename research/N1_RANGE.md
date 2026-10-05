# N1 range bot

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. 0.5% risk, 0.1% fee each side. Script: research/n1_range.py.

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| R1: 60 candles, target 80% | 1st half | 133 | 25% | -4.3% | -11.6% | 0.92 | 334 | 0.61 | -14.6% |
| R1: 60 candles, target 80% | 2nd half | 194 | 30% | -9.2% | -16.3% | 0.87 | 767 | 0.78 | -17.4% |
| R2: 60 candles, target 50% | 1st half | 133 | 26% | -16.4% | -18.1% | 0.66 | 351 | 0.56 | -13.4% |
| R2: 60 candles, target 50% | 2nd half | 204 | 35% | -18.2% | -21.6% | 0.72 | 814 | 0.70 | -15.2% |
| R3: 120 candles, target 80% | 1st half | 38 | 18% | -11.3% | -11.3% | 0.25 | 85 | 0.82 | -3.7% |
| R3: 120 candles, target 80% | 2nd half | 103 | 38% | -2.2% | -8.2% | 0.93 | 262 | 0.80 | -8.1% |

- R1: 60 candles, target 80%: correlation with v4+TR 0.28; portfolio return/DD 8.59 (+62% / -7.2%) vs v4+TR 15.07 (+99% / -6.6%); own full period -13.1% / DD -16.4% / PF 0.89
  fail: design 1st half not profitable (PF 0.92, -4.3%); design 1st half DD -11.6%; never-seen 1st half PF 0.61; design 2nd half not profitable (PF 0.87, -9.2%); design 2nd half DD -16.3%; never-seen 2nd half PF 0.78; portfolio return/DD 8.59 not above 15.07
- R2: 60 candles, target 50%: correlation with v4+TR 0.30; portfolio return/DD 7.72 (+55% / -7.2%) vs v4+TR 15.07 (+99% / -6.6%); own full period -31.6% / DD -34.7% / PF 0.69
  fail: design 1st half not profitable (PF 0.66, -16.4%); design 1st half DD -18.1%; never-seen 1st half PF 0.56; design 2nd half not profitable (PF 0.72, -18.2%); design 2nd half DD -21.6%; never-seen 2nd half PF 0.70; portfolio return/DD 7.72 not above 15.07
- R3: 120 candles, target 80%: correlation with v4+TR 0.14; portfolio return/DD 9.64 (+62% / -6.4%) vs v4+TR 15.07 (+99% / -6.6%); own full period -13.3% / DD -18.4% / PF 0.70
  fail: design 1st half not profitable (PF 0.25, -11.3%); design 1st half DD -11.3%; never-seen 1st half PF 0.82; design 2nd half not profitable (PF 0.93, -2.2%); never-seen 2nd half PF 0.80; portfolio return/DD 9.64 not above 15.07

Result: no variant passes
