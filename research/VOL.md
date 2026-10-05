# Volatility guard for SP-12 v4 (job 2e)

Run 2026-10-05. Variants and rules fixed beforehand in research/VOL_PLAN.md. A = v4 bot as it trades (BTC ETH XRP, shared $1,000, max 3 open); B = 15 coins one at a time per market period, pooled. Gap loss = lost more than 1.5x planned risk. Script: research/vol_test.py.

| Version | Half | A trades | A return | A max DD | A PF | A gaps | B trades | B P/L (USD) | B worst DD | B gaps | Pass? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| current | 1st half | 182 | +29.4% | -5.6% | 1.58 | 0 | 729 | +1346 | -14.6% | 0 | (current) |
| current | 2nd half | 311 | +20.0% | -9.9% | 1.23 | 0 | 1069 | +353 | -13.2% | 0 | (current) |
| G1: skip on hot ATR | 1st half | 180 | +30.1% | -5.6% | 1.59 | 0 | 722 | +1366 | -14.6% | 0 | fail |
| G1: skip on hot ATR | 2nd half | 304 | +20.1% | -11.2% | 1.24 | 0 | 1049 | +367 | -12.7% | 0 | fail |
| G2: half size on hot ATR | 1st half | 182 | +29.0% | -5.6% | 1.57 | 0 | 729 | +1334 | -14.6% | 0 | fail |
| G2: half size on hot ATR | 2nd half | 311 | +19.0% | -10.8% | 1.22 | 0 | 1069 | +344 | -12.9% | 0 | fail |
| G3: skip on hot candle range | 1st half | 182 | +29.5% | -5.6% | 1.58 | 0 | 728 | +1356 | -14.6% | 0 | fail |
| G3: skip on hot candle range | 2nd half | 309 | +20.3% | -9.4% | 1.23 | 0 | 1066 | +362 | -12.7% | 0 | fail |

- G1: skip on hot ATR: 1st half: gap losses not fewer (0 vs 0); 2nd half: DD not better (A -11.2% vs -9.9%, B worst -12.7% vs -13.2%); 2nd half: gap losses not fewer (0 vs 0)
- G2: half size on hot ATR: 1st half: gap losses not fewer (0 vs 0); 2nd half: DD not better (A -10.8% vs -9.9%, B worst -12.9% vs -13.2%); 2nd half: gap losses not fewer (0 vs 0)
- G3: skip on hot candle range: 1st half: DD not better (A -5.6% vs -5.6%, B worst -14.6% vs -14.6%); 1st half: gap losses not fewer (0 vs 0); 2nd half: gap losses not fewer (0 vs 0)
