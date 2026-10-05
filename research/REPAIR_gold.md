# Repair test: SP-12 v2 and Trend Rider gold

Run 2026-10-05. Variants and pass rules fixed beforehand in research/REPAIR_PLAN.md. P/L in USD summed over coin-periods (fresh $1,000 each); PF pooled over all trades. Halves: 1st = periods starting before 2022, 2nd = 2022 and 2023-now. Script: research/repair_test.py.

## Trend Rider gold (traded: XAUT; never-seen: AUD/USD, NZD/USD, USD/CAD, USD/CHF 2012-now, 0.01% cost)

| Version | 1st half P/L | 1st half PF | 2nd half P/L | 2nd half PF | Never-seen P/L | Never-seen PF | Worst DD | Pass? |
|---|---|---|---|---|---|---|---|---|
| gold now (pivot 3) | -30 | 0.73 | +19 | 1.05 | -188 | 0.90 | -10.8% | (current) |
| gold A: pivot 5 | +20 | 1.32 | +25 | 1.08 | -162 | 0.89 | -8.6% | fail |
| gold B: daily EMA100 | -22 | 0.80 | -65 | 0.86 | -128 | 0.93 | -16.6% | fail |
| gold C: 4 ATR trail | -15 | 0.84 | +102 | 1.30 | -272 | 0.85 | -9.0% | fail |

- gold A: pivot 5: doesn't beat now on never-seen; PF 0.89 on never-seen (needs > 1)
- gold B: daily EMA100: PF 0.80 on 1st half (needs > 1); doesn't beat now on 2nd half; PF 0.86 on 2nd half (needs > 1); PF 0.93 on never-seen (needs > 1); DD > 10%: XAUT 2023-now -16.6%
- gold C: 4 ATR trail: PF 0.84 on 1st half (needs > 1); doesn't beat now on never-seen; PF 0.85 on never-seen (needs > 1)

