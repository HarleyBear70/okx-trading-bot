# R1 rejection block (ICT), long only, crypto 4H

Variants and pass rules fixed beforehand in research/IDEAS_PLAN.md. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. 0.5% risk, 0.1% fee each side. Script: research/r1_rejection.py.

## Results

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| RB1: +3 ATR move within 6 | 1st half | 113 | 45% | -8.3% | -9.3% | 0.74 | 274 | 0.90 | -6.7% |
| RB1: +3 ATR move within 6 | 2nd half | 144 | 44% | -2.4% | -11.2% | 0.95 | 458 | 0.73 | -10.1% |
| RB2: break of structure within 10 | 1st half | 134 | 38% | -17.6% | -17.6% | 0.58 | 321 | 0.98 | -6.0% |
| RB2: break of structure within 10 | 2nd half | 189 | 40% | -14.4% | -22.0% | 0.74 | 528 | 0.61 | -11.3% |
| RB3: RB1 + daily trend | 1st half | 59 | 46% | -4.2% | -8.6% | 0.76 | 157 | 0.96 | -7.5% |
| RB3: RB1 + daily trend | 2nd half | 83 | 43% | -3.0% | -7.7% | 0.88 | 203 | 0.65 | -8.5% |

- RB1: +3 ATR move within 6: correlation with v4+TR 0.30; portfolio return/DD 12.13 (+63% / -5.2%) vs v4+TR 15.07 (+99% / -6.6%); own full period -10.4% / DD -14.5% / PF 0.86
  fail: design 1st half not profitable (PF 0.74, -8.3%); never-seen 1st half PF 0.90; design 2nd half not profitable (PF 0.95, -2.4%); design 2nd half DD -11.2%; never-seen 2nd half PF 0.73; portfolio return/DD 12.13 not above 15.07
- RB2: break of structure within 10: correlation with v4+TR 0.28; portfolio return/DD 7.95 (+56% / -7.1%) vs v4+TR 15.07 (+99% / -6.6%); own full period -29.5% / DD -33.2% / PF 0.67
  fail: design 1st half not profitable (PF 0.58, -17.6%); design 1st half DD -17.6%; never-seen 1st half PF 0.98; design 2nd half not profitable (PF 0.74, -14.4%); design 2nd half DD -22.0%; never-seen 2nd half PF 0.61; portfolio return/DD 7.95 not above 15.07
- RB3: RB1 + daily trend: correlation with v4+TR 0.19; portfolio return/DD 12.01 (+64% / -5.3%) vs v4+TR 15.07 (+99% / -6.6%); own full period -7.1% / DD -13.5% / PF 0.83
  fail: design 1st half not profitable (PF 0.76, -4.2%); never-seen 1st half PF 0.96; design 2nd half not profitable (PF 0.88, -3.0%); never-seen 2nd half PF 0.65; portfolio return/DD 12.01 not above 15.07

Result: no variant passes

