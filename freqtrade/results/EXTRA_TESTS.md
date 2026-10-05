## Fixed % stop and take profit vs the current exits (8 years, Oct 5 2026)

Jeff asked: what if the stop was 1-1.5% and the take profit 1.5-3%? This is a different test from the Freqtrade runs above. It uses 8 years of prices (May 2018 to Oct 5 2026), each bot's live coins, the same entry signals, $1,000, 0.5% risk per trade, 0.1% fee each side and max 3 open. Made by `python research/fixed_exits_test.py`.

| Bot | Current exits (swing-low stop, trailing) | Best fixed (1.5% stop, 3% TP) | Worst fixed (1% stop, 1.5% TP) |
|---|---|---|---|
| SP-12 v4 | **+93%**, worst drop 10.2%, PF 1.35 | -13%, worst drop 32.0%, PF 0.96 | -72%, worst drop 72.3% |
| Trend Rider | **+195%**, worst drop 8.4%, PF 1.87 | -37%, worst drop 53.4%, PF 0.91 | -87%, worst drop 86.7% |

**Result: all 24 fixed combinations lost money.** Win rate rose to 52% at best, and even that setup lost.

Why:
1. A normal 4H crypto candle moves about 3%, so a 1-1.5% stop gets hit by ordinary noise.
2. Fees (about 0.2% per round trip) take 15-20% of a 1-1.5% stop.
3. A 3% cap cuts off the few big runners (+20% to +150%) that make these bots their money.

Keep the current exits.

<details><summary>Full tables: every stop / take-profit combination, both halves</summary>

### SP-12 v4 (BTC ETH XRP XLM BNB)

Each cell: return / worst drop. Win % and PF are for the full period.

| Exits | Full 2018-now | 2018-2021 | 2022-now | Win % | PF | Trades |
|---|---|---|---|---|---|---|
| **Current exits (swing-low stop, trailing)** | +93% / -10.2% | +50% / -6.3% | +28% / -10.2% | 36% | 1.35 | 735 |
| stop 1%, TP 1.5% | -72% / -72.3% | -33% / -36.9% | -58% / -58.0% | 41% | 0.74 | 1407 |
| stop 1%, TP 2% | -49% / -53.5% | -15% / -22.7% | -40% / -44.5% | 37% | 0.86 | 1282 |
| stop 1%, TP 2.5% | -38% / -47.0% | -1% / -14.1% | -37% / -43.6% | 32% | 0.90 | 1186 |
| stop 1%, TP 3% | -25% / -41.9% | +13% / -12.3% | -34% / -41.5% | 29% | 0.94 | 1131 |
| stop 1.25%, TP 1.5% | -60% / -61.7% | -27% / -30.1% | -45% / -46.9% | 47% | 0.77 | 1441 |
| stop 1.25%, TP 2% | -34% / -43.1% | -6% / -15.8% | -30% / -36.2% | 42% | 0.90 | 1301 |
| stop 1.25%, TP 2.5% | -29% / -42.9% | +3% / -12.6% | -31% / -37.8% | 37% | 0.92 | 1198 |
| stop 1.25%, TP 3% | -21% / -37.9% | +11% / -11.7% | -28% / -35.6% | 33% | 0.95 | 1127 |
| stop 1.5%, TP 1.5% | -51% / -54.4% | -25% / -27.2% | -35% / -39.5% | 52% | 0.80 | 1369 |
| stop 1.5%, TP 2% | -25% / -36.1% | -5% / -15.1% | -21% / -31.4% | 47% | 0.92 | 1228 |
| stop 1.5%, TP 2.5% | -18% / -35.8% | +6% / -12.2% | -23% / -33.6% | 41% | 0.95 | 1122 |
| stop 1.5%, TP 3% | -13% / -32.0% | +11% / -11.8% | -22% / -30.6% | 37% | 0.96 | 1040 |

### Trend Rider (BTC ETH SOL BNB SUI TRX)

Each cell: return / worst drop. Win % and PF are for the full period.

| Exits | Full 2018-now | 2018-2021 | 2022-now | Win % | PF | Trades |
|---|---|---|---|---|---|---|
| **Current exits (swing-low stop, trailing)** | +195% / -8.4% | +59% / -7.4% | +86% / -6.7% | 39% | 1.87 | 684 |
| stop 1%, TP 1.5% | -87% / -86.7% | -76% / -76.0% | -45% / -45.3% | 37% | 0.59 | 1439 |
| stop 1%, TP 2% | -80% / -80.0% | -74% / -74.1% | -23% / -28.5% | 33% | 0.68 | 1407 |
| stop 1%, TP 2.5% | -75% / -77.5% | -68% / -70.7% | -20% / -33.8% | 29% | 0.74 | 1372 |
| stop 1%, TP 3% | -68% / -75.7% | -67% / -70.8% | -4% / -24.2% | 26% | 0.78 | 1335 |
| stop 1.25%, TP 1.5% | -77% / -76.9% | -65% / -65.3% | -34% / -34.3% | 44% | 0.67 | 1509 |
| stop 1.25%, TP 2% | -69% / -68.8% | -62% / -62.4% | -17% / -22.3% | 39% | 0.74 | 1480 |
| stop 1.25%, TP 2.5% | -61% / -65.5% | -56% / -59.0% | -11% / -28.0% | 35% | 0.80 | 1456 |
| stop 1.25%, TP 3% | -52% / -63.3% | -52% / -58.5% | +1% / -20.5% | 32% | 0.85 | 1426 |
| stop 1.5%, TP 1.5% | -67% / -67.6% | -54% / -54.4% | -30% / -30.8% | 49% | 0.73 | 1478 |
| stop 1.5%, TP 2% | -57% / -59.1% | -51% / -51.9% | -14% / -19.3% | 44% | 0.80 | 1448 |
| stop 1.5%, TP 2.5% | -47% / -55.8% | -43% / -48.3% | -8% / -23.6% | 39% | 0.86 | 1421 |
| stop 1.5%, TP 3% | -37% / -53.4% | -35% / -45.7% | -3% / -20.3% | 36% | 0.91 | 1386 |


</details>
