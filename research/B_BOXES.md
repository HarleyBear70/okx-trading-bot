# Box bots B1 and B2

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Binance archive 1H candles (4H built from them). Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. 0.5% risk, 0.1% fee each side. Script: research/b_boxes.py.

## B1 breakout retest

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| B1a: retest, target 2R | 1st half | 216 | 48% | +23.5% | -5.9% | 1.38 | 349 | 1.19 | -6.3% |
| B1a: retest, target 2R | 2nd half | 387 | 41% | -5.3% | -16.2% | 0.95 | 968 | 1.06 | -9.5% |
| B1b: retest, target 3R | 1st half | 210 | 45% | +44.5% | -5.6% | 1.63 | 336 | 1.32 | -6.0% |
| B1b: retest, target 3R | 2nd half | 366 | 39% | +1.5% | -14.2% | 1.01 | 921 | 1.16 | -13.1% |
| B1c: retest, target 2R, 60-candle box | 1st half | 66 | 52% | +7.7% | -2.3% | 1.51 | 67 | 1.13 | -3.3% |
| B1c: retest, target 2R, 60-candle box | 2nd half | 151 | 46% | +6.5% | -5.8% | 1.17 | 244 | 1.06 | -5.7% |

- B1a: retest, target 2R: correlation with v4+TR 0.58; portfolio return/DD 9.10 (+72% / -7.9%) vs v4+TR 15.07 (+99% / -6.6%); own full period +17.0% / DD -16.2% / PF 1.08
  fail: design 2nd half not profitable (PF 0.95, -5.3%); design 2nd half DD -16.2%; correlation 0.58; portfolio return/DD 9.10 not above 15.07
- B1b: retest, target 3R: correlation with v4+TR 0.57; portfolio return/DD 10.86 (+82% / -7.5%) vs v4+TR 15.07 (+99% / -6.6%); own full period +46.7% / DD -14.5% / PF 1.20
  fail: design 2nd half DD -14.2%; correlation 0.57; portfolio return/DD 10.86 not above 15.07
- B1c: retest, target 2R, 60-candle box: correlation with v4+TR 0.55; portfolio return/DD 13.42 (+71% / -5.3%) vs v4+TR 15.07 (+99% / -6.6%); own full period +14.7% / DD -5.8% / PF 1.26
  fail: correlation 0.55; portfolio return/DD 13.42 not above 15.07

Result: no variant passes

## B2 failed-breakdown reclaim

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| B2a: reclaim within 3 | 1st half | 85 | 34% | +5.8% | -8.3% | 1.19 | 180 | 1.26 | -4.0% |
| B2a: reclaim within 3 | 2nd half | 256 | 30% | -20.3% | -24.8% | 0.77 | 628 | 0.83 | -13.4% |
| B2b: reclaim within 6 | 1st half | 100 | 34% | +3.0% | -10.0% | 1.09 | 221 | 1.31 | -5.0% |
| B2b: reclaim within 6 | 2nd half | 310 | 32% | -22.5% | -27.5% | 0.78 | 759 | 0.88 | -13.3% |
| B2c: reclaim within 3 + daily trend | 1st half | 32 | 38% | +3.1% | -5.9% | 1.30 | 49 | 2.09 | -2.8% |
| B2c: reclaim within 3 + daily trend | 2nd half | 78 | 28% | -10.3% | -12.9% | 0.64 | 163 | 0.82 | -7.5% |

- B2a: reclaim within 3: correlation with v4+TR 0.17; portfolio return/DD 7.84 (+61% / -7.8%) vs v4+TR 15.07 (+99% / -6.6%); own full period -15.3% / DD -24.8% / PF 0.87
  fail: design 2nd half not profitable (PF 0.77, -20.3%); design 2nd half DD -24.8%; never-seen 2nd half PF 0.83; portfolio return/DD 7.84 not above 15.07
- B2b: reclaim within 6: correlation with v4+TR 0.12; portfolio return/DD 6.91 (+59% / -8.6%) vs v4+TR 15.07 (+99% / -6.6%); own full period -19.9% / DD -27.5% / PF 0.86
  fail: design 1st half DD -10.0%; design 2nd half not profitable (PF 0.78, -22.5%); design 2nd half DD -27.5%; never-seen 2nd half PF 0.88; portfolio return/DD 6.91 not above 15.07
- B2c: reclaim within 3 + daily trend: correlation with v4+TR -0.05; portfolio return/DD 11.65 (+64% / -5.5%) vs v4+TR 15.07 (+99% / -6.6%); own full period -7.5% / DD -12.9% / PF 0.81
  fail: design 2nd half not profitable (PF 0.64, -10.3%); design 2nd half DD -12.9%; never-seen 2nd half PF 0.82; portfolio return/DD 11.65 not above 15.07

Result: no variant passes

