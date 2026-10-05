# W1 Wyckoff volume as a filter

Variants and rules fixed beforehand in research/IDEAS_PLAN.md. Each bot as it trades; only entries are filtered. Script: research/w1_volume.py.

| Bot | Version | Half | Trades | Return | Max DD | Return/DD | PF | Pass? |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 | no filter | 1st half | 274 | +50.4% | -6.3% | 8.06 | 1.62 | - |
| SP-12 v4 | no filter | 2nd half | 461 | +28.4% | -10.2% | 2.80 | 1.23 | - |
| SP-12 v4 | WV1 | 1st half | 139 | +37.8% | -4.6% | 8.17 | 1.97 | PASS |
| SP-12 v4 | WV1 | 2nd half | 279 | +31.2% | -6.8% | 4.55 | 1.44 | PASS |
| SP-12 v4 | WV2 | 1st half | 96 | +32.3% | -5.7% | 5.66 | 2.22 | fail |
| SP-12 v4 | WV2 | 2nd half | 227 | +27.8% | -7.2% | 3.85 | 1.46 | fail |
| SP-12 v4 | WV3 | 1st half | 19 | -0.8% | -3.5% | -0.23 | 0.85 | fail |
| SP-12 v4 | WV3 | 2nd half | 45 | +7.5% | -3.2% | 2.37 | 1.83 | fail |
| Trend Rider (with fear filter) | no filter | 1st half | 280 | +59.7% | -7.5% | 7.96 | 1.89 | - |
| Trend Rider (with fear filter) | no filter | 2nd half | 368 | +84.2% | -7.4% | 11.31 | 1.94 | - |
| Trend Rider (with fear filter) | WV1 | 1st half | 257 | +57.4% | -6.1% | 9.43 | 1.97 | fail |
| Trend Rider (with fear filter) | WV1 | 2nd half | 326 | +58.9% | -8.4% | 6.97 | 1.77 | fail |
| Trend Rider (with fear filter) | WV2 | 1st half | 243 | +61.2% | -6.1% | 10.05 | 2.09 | fail |
| Trend Rider (with fear filter) | WV2 | 2nd half | 316 | +51.5% | -8.7% | 5.92 | 1.71 | fail |
| Trend Rider (with fear filter) | WV3 | 1st half | 33 | +10.2% | -1.7% | 6.12 | 3.21 | fail |
| Trend Rider (with fear filter) | WV3 | 2nd half | 85 | +25.5% | -2.5% | 10.40 | 2.95 | fail |
| B1c | no filter | 1st half | 66 | +7.7% | -2.3% | 3.35 | 1.51 | - |
| B1c | no filter | 2nd half | 151 | +6.5% | -5.8% | 1.14 | 1.17 | - |
| B1c | WV1 | 1st half | 66 | +7.4% | -2.4% | 3.13 | 1.48 | fail |
| B1c | WV1 | 2nd half | 147 | +8.9% | -5.3% | 1.68 | 1.25 | fail |
| B1c | WV2 | 1st half | 64 | +7.0% | -2.4% | 2.95 | 1.47 | fail |
| B1c | WV2 | 2nd half | 145 | +7.7% | -5.2% | 1.46 | 1.21 | fail |
| B1c | WV3 | 1st half | 7 | -0.7% | -1.6% | -0.43 | 0.64 | fail |
| B1c | WV3 | 2nd half | 21 | -2.4% | -2.7% | -0.89 | 0.67 | fail |

- SP-12 v4, WV1: PASS
- SP-12 v4, WV2: fail
- SP-12 v4, WV3: fail
- Trend Rider (with fear filter), WV1: fail
- Trend Rider (with fear filter), WV2: fail
- Trend Rider (with fear filter), WV3: fail
- B1c, WV1: fail
- B1c, WV2: fail
- B1c, WV3: fail
