# V4T: Lock in big winners on SP-12 v4

Run 2026-10-11 by the spec runner (research/spec_runner.py) from research/specs/V4T_lock_big_winners.py (written 2026-10-05 by Terminal Claude).

### SP-12 v4 (BTC ETH XRP XLM BNB)

| Version | Half | Trades | Return | Max DD | Return/DD | PF | Avg risk | Never-seen P/L | Never-seen PF |
|---|---|---|---|---|---|---|---|---|---|
| as it trades | 1st half | 282 | +16.1% | -9.9% | 1.63 | 1.19 | 0.50% | -24 | 0.97 |
| as it trades | 2nd half | 477 | -33.8% | -34.6% | -0.98 | 0.71 | 0.50% | -418 | 0.76 |
| VT1: at +10R lock +6R | 1st half | 282 | +16.4% | -9.8% | 1.68 | 1.19 | 0.50% | -49 | 0.95 |
| VT1: at +10R lock +6R | 2nd half | 477 | -33.6% | -34.4% | -0.98 | 0.71 | 0.50% | -415 | 0.76 |
| VT2: at +10R trail 3R under the high | 1st half | 282 | +18.4% | -9.0% | 2.04 | 1.21 | 0.50% | -11 | 0.99 |
| VT2: at +10R trail 3R under the high | 2nd half | 478 | -34.9% | -35.7% | -0.98 | 0.70 | 0.50% | -405 | 0.77 |
| VT3: at +5R lock +3R | 1st half | 282 | +15.0% | -9.7% | 1.55 | 1.18 | 0.50% | -65 | 0.93 |
| VT3: at +5R lock +3R | 2nd half | 477 | -33.7% | -34.6% | -0.98 | 0.71 | 0.50% | -412 | 0.76 |

## Verdicts

- SP-12 v4 / VT1: at +10R lock +6R: fail - never-seen 1st half: P/L -49 vs -24, PF 0.95 vs 0.97; 2nd half: return/DD -0.98 vs -0.98, PF 0.71 vs 0.71, DD -34.4%
- SP-12 v4 / VT2: at +10R trail 3R under the high: fail - 2nd half: return/DD -0.98 vs -0.98, PF 0.70 vs 0.71, DD -35.7%
- SP-12 v4 / VT3: at +5R lock +3R: fail - 1st half: return/DD 1.55 vs 1.63, PF 1.18 vs 1.19, DD -9.7%; never-seen 1st half: P/L -65 vs -24, PF 0.93 vs 0.97; 2nd half: return/DD -0.98 vs -0.98, PF 0.71 vs 0.71, DD -34.6%
