# B3 spot-only pairs (daily)

Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Design pairs ETH/BTC and XRP/BTC on one shared $1,000; never-seen coins vs BTC, alone, pooled. 0.5% risk, 0.1% fee each side. Script: research/b3_s1.py.

## Results

| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | Never-seen worst DD |
|---|---|---|---|---|---|---|---|---|---|
| P1: 60 days, z 2 | 1st half | 55 | 40% | +3.0% | -6.0% | 1.22 | 318 | 1.92 | -5.7% |
| P1: 60 days, z 2 | 2nd half | 92 | 46% | +6.7% | -6.8% | 1.31 | 515 | 1.66 | -6.4% |
| P2: 30 days, z 2 | 1st half | 93 | 52% | +11.2% | -4.5% | 1.56 | 488 | 1.52 | -11.7% |
| P2: 30 days, z 2 | 2nd half | 137 | 46% | +5.3% | -5.5% | 1.17 | 812 | 1.38 | -7.7% |
| P3: 60 days, z 2.5 | 1st half | 43 | 35% | +5.9% | -4.9% | 1.51 | 206 | 1.92 | -4.5% |
| P3: 60 days, z 2.5 | 2nd half | 62 | 44% | +7.7% | -5.1% | 1.52 | 340 | 1.61 | -4.8% |

- P1: 60 days, z 2: correlation with v4+TR 0.49; portfolio return/DD 12.53 (+69% / -5.5%) vs v4+TR 15.07 (+99% / -6.6%); own full period +9.9% / DD -6.8% / PF 1.28
  fail: portfolio return/DD 12.53 not above 15.07
- P2: 30 days, z 2: correlation with v4+TR 0.50; portfolio return/DD 11.46 (+72% / -6.3%) vs v4+TR 15.07 (+99% / -6.6%); own full period +17.1% / DD -6.2% / PF 1.31
  fail: correlation 0.50; portfolio return/DD 11.46 not above 15.07
- P3: 60 days, z 2.5: correlation with v4+TR 0.40; portfolio return/DD 13.11 (+71% / -5.4%) vs v4+TR 15.07 (+99% / -6.6%); own full period +14.1% / DD -5.4% / PF 1.52
  fail: portfolio return/DD 13.11 not above 15.07

Result: no variant passes

