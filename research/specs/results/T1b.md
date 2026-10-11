# T1b: Trend-strength sizing, calibrated on pre-2022 data

Run 2026-10-11 by the spec runner (research/spec_runner.py) from research/specs/T1b_trend_sizing_calibrated.py (written 2026-10-05 by Terminal Claude).

### SP-12 v4 (BTC ETH XRP XLM BNB)

| Version | Half | Trades | Return | Max DD | Return/DD | PF | Avg risk | Never-seen P/L | Never-seen PF |
|---|---|---|---|---|---|---|---|---|---|
| as it trades | 1st half | 282 | +16.1% | -9.9% | 1.63 | 1.19 | 0.50% | -24 | 0.97 |
| as it trades | 2nd half | 477 | -33.8% | -34.6% | -0.98 | 0.71 | 0.50% | -418 | 0.76 |
| TS1b: 4H ADX vs its median | 1st half | 282 | +20.4% | -12.8% | 1.60 | 1.25 | 0.48% | -67 | 0.93 |
| TS1b: 4H ADX vs its median | 2nd half | 476 | -29.9% | -31.8% | -0.94 | 0.74 | 0.52% | -488 | 0.73 |
| TS2b: daily ADX vs its median | 1st half | 282 | +18.2% | -8.9% | 2.05 | 1.21 | 0.50% | +5 | 1.01 |
| TS2b: daily ADX vs its median | 2nd half | 477 | -36.1% | -37.1% | -0.97 | 0.68 | 0.47% | -521 | 0.69 |
| TS3b: EMA50 slope vs its median | 1st half | 282 | +23.4% | -13.0% | 1.80 | 1.25 | 0.53% | -57 | 0.94 |
| TS3b: EMA50 slope vs its median | 2nd half | 476 | -32.8% | -34.5% | -0.95 | 0.72 | 0.55% | -549 | 0.71 |

### Trend Rider (BTC ETH SOL BNB SUI TRX)

| Version | Half | Trades | Return | Max DD | Return/DD | PF | Avg risk | Never-seen P/L | Never-seen PF |
|---|---|---|---|---|---|---|---|---|---|
| as it trades | 1st half | 282 | +43.0% | -9.2% | 4.67 | 1.61 | 0.50% | +476 | 1.46 |
| as it trades | 2nd half | 379 | +41.3% | -9.2% | 4.49 | 1.43 | 0.50% | -23 | 0.98 |
| TS1b: 4H ADX vs its median | 1st half | 282 | +33.9% | -7.8% | 4.33 | 1.55 | 0.45% | +458 | 1.48 |
| TS1b: 4H ADX vs its median | 2nd half | 379 | +30.8% | -7.7% | 4.01 | 1.35 | 0.47% | +92 | 1.08 |
| TS2b: daily ADX vs its median | 1st half | 282 | +46.7% | -9.5% | 4.90 | 1.67 | 0.50% | +545 | 1.52 |
| TS2b: daily ADX vs its median | 2nd half | 379 | +34.3% | -10.0% | 3.44 | 1.38 | 0.48% | -116 | 0.90 |
| TS3b: EMA50 slope vs its median | 1st half | 282 | +25.3% | -8.5% | 2.96 | 1.46 | 0.42% | +368 | 1.42 |
| TS3b: EMA50 slope vs its median | 2nd half | 379 | +20.0% | -9.8% | 2.04 | 1.24 | 0.44% | +36 | 1.03 |

## Verdicts

- SP-12 v4 / TS1b: 4H ADX vs its median: fail - 1st half: return/DD 1.60 vs 1.63, PF 1.25 vs 1.19, DD -12.8%; never-seen 1st half: P/L -67 vs -24, PF 0.93 vs 0.97; 2nd half: return/DD -0.94 vs -0.98, PF 0.74 vs 0.71, DD -31.8%; never-seen 2nd half: P/L -488 vs -418, PF 0.73 vs 0.76
- SP-12 v4 / TS2b: daily ADX vs its median: fail - 2nd half: return/DD -0.97 vs -0.98, PF 0.68 vs 0.71, DD -37.1%; never-seen 2nd half: P/L -521 vs -418, PF 0.69 vs 0.76
- SP-12 v4 / TS3b: EMA50 slope vs its median: fail - 1st half: return/DD 1.80 vs 1.63, PF 1.25 vs 1.19, DD -13.0%; never-seen 1st half: P/L -57 vs -24, PF 0.94 vs 0.97; 2nd half: return/DD -0.95 vs -0.98, PF 0.72 vs 0.71, DD -34.5%; never-seen 2nd half: P/L -549 vs -418, PF 0.71 vs 0.76
- Trend Rider / TS1b: 4H ADX vs its median: fail - 1st half: return/DD 4.33 vs 4.67, PF 1.55 vs 1.61, DD -7.8%; never-seen 1st half: P/L +458 vs +476, PF 1.48 vs 1.46; 2nd half: return/DD 4.01 vs 4.49, PF 1.35 vs 1.43, DD -7.7%
- Trend Rider / TS2b: daily ADX vs its median: fail - 2nd half: return/DD 3.44 vs 4.49, PF 1.38 vs 1.43, DD -10.0%; never-seen 2nd half: P/L -116 vs -23, PF 0.90 vs 0.98
- Trend Rider / TS3b: EMA50 slope vs its median: fail - 1st half: return/DD 2.96 vs 4.67, PF 1.46 vs 1.61, DD -8.5%; never-seen 1st half: P/L +368 vs +476, PF 1.42 vs 1.46; 2nd half: return/DD 2.04 vs 4.49, PF 1.24 vs 1.43, DD -9.8%
