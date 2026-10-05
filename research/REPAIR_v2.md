# Repair test: SP-12 v2 and Trend Rider gold

Run 2026-10-05. Variants and pass rules fixed beforehand in research/REPAIR_PLAN.md. P/L in USD summed over coin-periods (fresh $1,000 each); PF pooled over all trades. Halves: 1st = periods starting before 2022, 2nd = 2022 and 2023-now. Script: research/repair_test.py.

## SP-12 v2 (traded: ETH, SOL, XAUT; never-seen: the 11 out-of-sample coins from job 2b)

| Version | 1st half P/L | 1st half PF | 2nd half P/L | 2nd half PF | Never-seen P/L | Never-seen PF | Worst DD | Pass? |
|---|---|---|---|---|---|---|---|---|
| v2 now | -150 | 0.82 | +190 | 1.14 | -884 | 0.89 | -20.1% | (current) |
| v2 A: v4 trend filter | -13 | 0.96 | +175 | 1.25 | +192 | 1.07 | -12.6% | fail |
| v2 B: A + daily uptrend | -37 | 0.89 | +195 | 1.30 | +137 | 1.05 | -12.6% | fail |
| v2 C: A + v4 exits | -2 | 0.99 | +176 | 1.25 | +1095 | 1.40 | -14.6% | fail |

- v2 A: v4 trend filter: PF 0.96 on 1st half (needs > 1); doesn't beat now on 2nd half; DD > 10%: LTC 2023-now -12.6%
- v2 B: A + daily uptrend: PF 0.89 on 1st half (needs > 1); DD > 10%: LTC 2023-now -12.6%
- v2 C: A + v4 exits: PF 0.99 on 1st half (needs > 1); doesn't beat now on 2nd half; DD > 10%: LTC 2023-now -12.2%, DOGE 2019-21 bull -14.6%

