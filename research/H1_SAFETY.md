# H1 safety switch and volatility sizing

Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider as they trade, $1,000 each; combined = the sum. Script: research/h1_safety.py.

| Version | Half | Combined return | Combined max DD | Return/DD | v4 return / DD | TR return / DD | Pass? |
|---|---|---|---|---|---|---|---|
| current (no switch) | 1st half | +52.6% | -5.1% | 10.25 | +50.4% / -6.3% | +54.7% / -5.7% | - |
| current (no switch) | 2nd half | +42.6% | -7.1% | 5.99 | +28.4% / -10.2% | +56.9% / -7.0% | - |
| W1: 5%, back halfway | 1st half | +50.5% | -5.1% | 9.85 | +48.2% / -6.0% | +52.8% / -5.7% | fail |
| W1: 5%, back halfway | 2nd half | +21.6% | -6.1% | 3.55 | +7.8% / -9.3% | +35.3% / -6.8% | fail |
| W2: 6%, back to the best | 1st half | +52.6% | -5.1% | 10.25 | +50.4% / -6.3% | +54.7% / -5.7% | fail |
| W2: 6%, back to the best | 2nd half | +22.7% | -7.0% | 3.24 | +17.5% / -10.0% | +27.9% / -6.9% | fail |
| W3: 8%, back to the best | 1st half | +52.6% | -5.1% | 10.25 | +50.4% / -6.3% | +54.7% / -5.7% | fail |
| W3: 8%, back to the best | 2nd half | +42.6% | -7.1% | 5.99 | +28.4% / -10.2% | +56.9% / -7.0% | fail |
| V1: volatility sizing | 1st half | +59.9% | -6.6% | 9.12 | +58.5% / -7.0% | +61.3% / -7.0% | fail |
| V1: volatility sizing | 2nd half | +52.9% | -9.1% | 5.83 | +34.1% / -11.1% | +71.6% / -9.0% | fail |

- W1: 5%, back halfway: fail
- W2: 6%, back to the best: fail
- W3: 8%, back to the best: fail
- V1: volatility sizing: fail
