# JEFF15: 15m test done Jeff's way (Oct 9 2026) — FAILS

Asked for by Chrome Claude on issue #4. Rules + pass rules written before the run: top of research/jeff15.py.
Daily direction, 4H discount/premium (skip the middle 40-60%), 15m market shift entry, max stop 1.35%,
target at least 2% and 2R, longs AND shorts, 2019-now. Results in R (risk units) per trade.

## Which piece fails
- **Entries:** even with ZERO fees the base is PF 0.89. The entry itself has no edge on 15m.
- **The 1.35% max stop:** the real structure stop is usually wider, so ~9 in 10 setups get skipped (170 trades in
  7 years on 5 coins). Forcing the stop to 1.35% instead (capstop) gives ~5 trades/week but loses (PF 0.85):
  tight stops get hit by normal 15m noise.
- **Trailing exit:** the best piece. Main coins PF 1.06 (1.29 at zero fees), longs 1.34. But on never-seen
  coins it falls to PF 0.50, so it isn't reliable.
- **Shorts:** lose on the main coins in every version (PF 0.61-0.85).
- **Middle filter on/off:** makes little difference (0.77 vs 0.79).
- **30m entries:** too few trades to judge (20 and 1).
- **Every 5 min vs hourly:** about the same (0.77 vs 0.79), so speed isn't the problem.
- **Fees:** at OKX 0.35% everything loses badly (PF 0.36-0.41).

Closest to useful: longs-only + trailing exit + Binance.US fees. That is basically the existing jeff_bot.py
"turnaround" paper account, already running for the Oct 19 review.

## Raw results

### main: BTC ETH SOL XRP BNB (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 170 | 0.4 | 29% | 0.77 | -0.18R | 43R | 0.59 | 0.82 | 1.01 | 0.61 |
| capstop | 1886 | 4.7 | 32% | 0.85 | -0.11R | 227R | 0.85 | 0.84 | 0.87 | 0.83 |
| trail | 183 | 0.5 | 30% | 1.06 | +0.03R | 24R | 0.93 | 1.09 | 1.34 | 0.85 |
| nomiddle | 229 | 0.6 | 30% | 0.79 | -0.16R | 50R | 0.76 | 0.80 | 0.94 | 0.69 |
| 30m | 20 | 0.0 | 20% | 0.44 | -0.49R | 12R | 0.00 | 0.50 | 0.43 | 0.45 |
| hourly | 186 | 0.5 | 31% | 0.79 | -0.17R | 37R | 0.89 | 0.76 | 0.92 | 0.72 |

### main, fee check

| Version | Trades | /wk | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|
| base at zero fees | 170 | 0.4 | 29% | 0.89 | -0.08R | 30R | 0.67 | 0.94 | 1.17 | 0.71 |
| base at OKX 0.35% | 170 | 0.4 | 29% | 0.36 | -0.77R | 132R | 0.29 | 0.37 | 0.47 | 0.29 |
| trail at zero fees | 183 | 0.5 | 31% | 1.29 | +0.13R | 18R | 1.09 | 1.35 | 1.65 | 1.04 |
| trail at OKX 0.35% | 183 | 0.5 | 17% | 0.41 | -0.59R | 113R | 0.41 | 0.41 | 0.54 | 0.32 |

### never-seen: ADA DOGE LINK AVAX LTC DOT (Binance.US 0.05% a side)

| Version | Trades | /wk | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|
| base | 65 | 0.2 | 29% | 0.72 | -0.22R | 18R | 0.87 | 0.67 | 0.47 | 0.85 |
| capstop | 2376 | 5.9 | 33% | 0.87 | -0.10R | 278R | 0.77 | 0.95 | 0.77 | 0.96 |
| trail | 67 | 0.2 | 25% | 0.50 | -0.34R | 23R | 0.81 | 0.37 | 0.13 | 0.66 |
| nomiddle | 94 | 0.2 | 28% | 0.70 | -0.24R | 26R | 0.81 | 0.67 | 0.90 | 0.63 |
| 30m | 1 | 0.0 | 100% | 99.00 | +1.90R | 0R | - | 99.00 | - | 99.00 |
| hourly | 92 | 0.2 | 26% | 0.69 | -0.26R | 25R | 0.83 | 0.64 | 0.81 | 0.61 |
