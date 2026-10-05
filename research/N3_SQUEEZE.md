# N3 squeeze breakout bot

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. 0.5% risk, 0.1% fee each side. Script: research/n3_squeeze.py.

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| S1: squeeze = 10th pct of 90 days | 1st half | 118 | 48% | +15.7% | -3.7% | 1.69 | 248 | 1.46 | -3.2% |
| S1: squeeze = 10th pct of 90 days | 2nd half | 175 | 37% | -6.8% | -9.1% | 0.84 | 536 | 1.05 | -4.3% |
| S2: S1 + daily trend filter | 1st half | 70 | 50% | +11.8% | -2.1% | 1.87 | 116 | 1.73 | -2.6% |
| S2: S1 + daily trend filter | 2nd half | 89 | 37% | -5.4% | -9.9% | 0.76 | 195 | 1.19 | -3.3% |
| S3: squeeze = lowest of 180 days | 1st half | 16 | 44% | +0.6% | -2.9% | 1.13 | 31 | 0.98 | -1.8% |
| S3: squeeze = lowest of 180 days | 2nd half | 19 | 42% | -0.0% | -3.9% | 1.00 | 72 | 1.56 | -3.1% |

- S1: squeeze = 10th pct of 90 days: correlation with v4+TR 0.48; portfolio return/DD 11.01 (+69% / -6.2%) vs v4+TR 15.07 (+99% / -6.6%); own full period +7.9% / DD -9.4% / PF 1.11
  fail: design 2nd half not profitable (PF 0.84, -6.8%); portfolio return/DD 11.01 not above 15.07
- S2: S1 + daily trend filter: correlation with v4+TR 0.43; portfolio return/DD 11.90 (+68% / -5.7%) vs v4+TR 15.07 (+99% / -6.6%); own full period +5.8% / DD -9.9% / PF 1.15
  fail: design 2nd half not profitable (PF 0.76, -5.4%); portfolio return/DD 11.90 not above 15.07
- S3: squeeze = lowest of 180 days: correlation with v4+TR 0.20; portfolio return/DD 12.53 (+66% / -5.3%) vs v4+TR 15.07 (+99% / -6.6%); own full period +0.6% / DD -5.0% / PF 1.06
  fail: never-seen 1st half PF 0.98; design 2nd half not profitable (PF 1.00, -0.0%); portfolio return/DD 12.53 not above 15.07

Result: no variant passes
