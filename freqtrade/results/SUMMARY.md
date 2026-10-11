# Freqtrade backtest results

Updated 2026-10-11 13:36 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee. Exits and risk follow each bot's live settings in bot.py: no half sell at +2R on SP-12 v4 and Trend Rider (since Oct 5 2026), risk 0.4% on SP-12 v4 and 0.5% on the rest. **Step-ups off** risks that every trade; **Step-ups on** raises it by RISK_STEPS as the balance grows (back to base if the balance falls 5% from its best).

## SP12v4: old half sell at +2R vs live rules (no half sell)

| | Old: sell half at +2R | Live: no half sell |
|---|---|---|
| Trades | 182 / 0.19 | 182 / 0.19 |
| Final balance | 1196.79 USDT | 1435.46 USDT |
| Total profit % | 19.68% | 43.55% |
| CAGR % | 7.11% | 14.83% |
| Win / draw / loss, win % | 74 / 0 / 108, 40.7% | 70 / 0 / 112, 38.5% |
| Profit factor | 1.46 | 1.91 |
| Max % of account underwater | 5.61% | 5.67% |
| Absolute drawdown | 69.4 USDT (5.61%) | 83.073 USDT (5.67%) |
| Best trade | XRP/USDT 82.34% | XRP/USDT 158.33% |
| Worst trade | BTC/USDT -4.19% | BTC/USDT -4.19% |

<details><summary>SP12v4: old half sell at +2R vs live rules (no half sell): full report, Old: sell half at +2R</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1196.79 USDT                              │
│ Absolute profit                        │ 196.79 USDT                               │
│ Total profit %                         │ 19.68%                                    │
│ CAGR %                                 │ 7.11%                                     │
│ Sharpe (closed trades)                 │ 0.34                                      │
│ Sortino (closed trades)                │ 2.04                                      │
│ Calmar (closed trades)                 │ 7.03                                      │
│ SQN                                    │ 1.27                                      │
│ Mean profit p-value                    │ 0.2055                                    │
│ Profit factor                          │ 1.46                                      │
│ Expectancy (Ratio)                     │ 1.08 (0.27)                               │
│ Avg. daily profit                      │ 0.206 USDT                                │
│ Avg. stake amount                      │ 174.218 USDT                              │
│ Market change                          │ 48.76%                                    │
│ Total trade volume                     │ 72843.993 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 9.88%                            │
│ Worst Pair                             │ BTC/USDT 3.16%                            │
│ Best trade                             │ XRP/USDT 82.34%                           │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 99.89 USDT                                │
│ Worst day                              │ -11.33 USDT                               │
│ Days win/draw/lose                     │ 49 / 817 / 81                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 12:16           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 03:20            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 981.672 USDT / 1237.668 USDT              │
│ Max % of account underwater            │ 5.61%                                     │
│ Absolute drawdown                      │ 69.4 USDT (5.61%)                         │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 237.668 USDT                              │
│ Profit at drawdown end                 │ 168.268 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 980.173 USDT / 1248.996 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2025-10-05 08:00:00 │
│ Max % of account underwater (balance)  │ 6.60%                                     │
│ Absolute drawdown (wallet balance)     │ 82.421 USDT (6.60%)                       │
│ Drawdown duration                      │ 317 days 20:00:00                         │
│ Profit at drawdown start               │ 248.996 USDT                              │
│ Profit at drawdown end                 │ 166.574 USDT                              │
│ Drawdown start                         │ 2025-10-05 08:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.95                                      │
│ Sortino (daily wallet balance)         │ 1.21                                      │
│ Calmar (daily wallet balance)          │ 5.97                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                         STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃         Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         0.57 │         196.790 │        19.68 │ 2 days, 2:29:00 │   74     0   108  40.7 │ 69.4 USDT  5.61% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴──────────────────┘
```

</details>

<details><summary>SP12v4: old half sell at +2R vs live rules (no half sell): full report, Live: no half sell</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1435.46 USDT                              │
│ Absolute profit                        │ 435.46 USDT                               │
│ Total profit %                         │ 43.55%                                    │
│ CAGR %                                 │ 14.83%                                    │
│ Sharpe (closed trades)                 │ 0.41                                      │
│ Sortino (closed trades)                │ 3.71                                      │
│ Calmar (closed trades)                 │ 15.38                                     │
│ SQN                                    │ 1.52                                      │
│ Mean profit p-value                    │ 0.1294                                    │
│ Profit factor                          │ 1.91                                      │
│ Expectancy (Ratio)                     │ 2.39 (0.56)                               │
│ Avg. daily profit                      │ 0.456 USDT                                │
│ Avg. stake amount                      │ 223.372 USDT                              │
│ Market change                          │ 48.76%                                    │
│ Total trade volume                     │ 81906.491 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 25.35%                           │
│ Worst Pair                             │ BTC/USDT 5.69%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 194.651 USDT                              │
│ Worst day                              │ -13.406 USDT                              │
│ Days win/draw/lose                     │ 46 / 817 / 84                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 15:19           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 03:28            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 980.253 USDT / 1466.323 USDT              │
│ Max % of account underwater            │ 5.67%                                     │
│ Absolute drawdown                      │ 83.073 USDT (5.67%)                       │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 465.394 USDT                              │
│ Profit at drawdown end                 │ 382.321 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 977.06 USDT / 1486.968 USDT               │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 7.82%                                     │
│ Absolute drawdown (wallet balance)     │ 104.939 USDT (7.07%)                      │
│ Drawdown duration                      │ 155 days 04:00:00                         │
│ Profit at drawdown start               │ 485.256 USDT                              │
│ Profit at drawdown end                 │ 380.316 USDT                              │
│ Drawdown start                         │ 2026-03-17 00:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.31                                      │
│ Sortino (daily wallet balance)         │ 1.90                                      │
│ Calmar (daily wallet balance)          │ 12.34                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         1.23 │         435.460 │        43.55 │ 2 days, 2:29:00 │   70     0   112  38.5 │ 83.073 USDT  5.67% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴────────────────────┘
```

</details>

Both at SP-12 v4's live risk (0.4%) with step-ups off. Without the half sell, the whole position runs to the stop, trailing stop, target or time exit.

## SP12v4

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 182 / 0.19 | 179 / 0.19 |
| Final balance | 1435.46 USDT | 1346.503 USDT |
| Total profit % | 43.55% | 34.65% |
| CAGR % | 14.83% | 12.06% |
| Win / draw / loss, win % | 70 / 0 / 112, 38.5% | 70 / 0 / 109, 39.1% |
| Profit factor | 1.91 | 1.53 |
| Max % of account underwater | 5.67% | 9.83% |
| Absolute drawdown | 83.073 USDT (5.67%) | 142.692 USDT (9.83%) |
| Best trade | XRP/USDT 158.33% | XRP/USDT 158.33% |
| Worst trade | BTC/USDT -4.19% | BTC/USDT -4.19% |

<details><summary>SP12v4: full report, Step-ups off</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1435.46 USDT                              │
│ Absolute profit                        │ 435.46 USDT                               │
│ Total profit %                         │ 43.55%                                    │
│ CAGR %                                 │ 14.83%                                    │
│ Sharpe (closed trades)                 │ 0.41                                      │
│ Sortino (closed trades)                │ 3.71                                      │
│ Calmar (closed trades)                 │ 15.38                                     │
│ SQN                                    │ 1.52                                      │
│ Mean profit p-value                    │ 0.1294                                    │
│ Profit factor                          │ 1.91                                      │
│ Expectancy (Ratio)                     │ 2.39 (0.56)                               │
│ Avg. daily profit                      │ 0.456 USDT                                │
│ Avg. stake amount                      │ 223.372 USDT                              │
│ Market change                          │ 48.76%                                    │
│ Total trade volume                     │ 81906.491 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 25.35%                           │
│ Worst Pair                             │ BTC/USDT 5.69%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 194.651 USDT                              │
│ Worst day                              │ -13.406 USDT                              │
│ Days win/draw/lose                     │ 46 / 817 / 84                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 15:19           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 03:28            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 980.253 USDT / 1466.323 USDT              │
│ Max % of account underwater            │ 5.67%                                     │
│ Absolute drawdown                      │ 83.073 USDT (5.67%)                       │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 465.394 USDT                              │
│ Profit at drawdown end                 │ 382.321 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 977.06 USDT / 1486.968 USDT               │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 7.82%                                     │
│ Absolute drawdown (wallet balance)     │ 104.939 USDT (7.07%)                      │
│ Drawdown duration                      │ 155 days 04:00:00                         │
│ Profit at drawdown start               │ 485.256 USDT                              │
│ Profit at drawdown end                 │ 380.316 USDT                              │
│ Drawdown start                         │ 2026-03-17 00:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.31                                      │
│ Sortino (daily wallet balance)         │ 1.90                                      │
│ Calmar (daily wallet balance)          │ 12.34                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         1.23 │         435.460 │        43.55 │ 2 days, 2:29:00 │   70     0   112  38.5 │ 83.073 USDT  5.67% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴────────────────────┘
```

</details>

<details><summary>SP12v4: full report, Step-ups on</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 179 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1346.503 USDT                             │
│ Absolute profit                        │ 346.503 USDT                              │
│ Total profit %                         │ 34.65%                                    │
│ CAGR %                                 │ 12.06%                                    │
│ Sharpe (closed trades)                 │ 0.31                                      │
│ Sortino (closed trades)                │ 1.16                                      │
│ Calmar (closed trades)                 │ 7.06                                      │
│ SQN                                    │ 1.16                                      │
│ Mean profit p-value                    │ 0.2489                                    │
│ Profit factor                          │ 1.53                                      │
│ Expectancy (Ratio)                     │ 1.94 (0.32)                               │
│ Avg. daily profit                      │ 0.363 USDT                                │
│ Avg. stake amount                      │ 324.58 USDT                               │
│ Market change                          │ 48.76%                                    │
│ Total trade volume                     │ 116779.38 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 21.74%                           │
│ Worst Pair                             │ BTC/USDT 2.30%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 219.041 USDT                              │
│ Worst day                              │ -45.125 USDT                              │
│ Days win/draw/lose                     │ 47 / 818 / 82                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 15:02           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 03:14            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 980.253 USDT / 1451.463 USDT              │
│ Max % of account underwater            │ 9.83%                                     │
│ Absolute drawdown                      │ 142.692 USDT (9.83%)                      │
│ Drawdown duration                      │ 308 days 16:00:00                         │
│ Profit at drawdown start               │ 451.463 USDT                              │
│ Profit at drawdown end                 │ 308.771 USDT                              │
│ Drawdown start                         │ 2025-10-07 00:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 977.06 USDT / 1483.321 USDT               │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2025-10-05 08:00:00 │
│ Max % of account underwater (balance)  │ 11.90%                                    │
│ Absolute drawdown (wallet balance)     │ 176.448 USDT (11.90%)                     │
│ Drawdown duration                      │ 317 days 20:00:00                         │
│ Profit at drawdown start               │ 483.321 USDT                              │
│ Profit at drawdown end                 │ 306.873 USDT                              │
│ Drawdown start                         │ 2025-10-05 08:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.95                                      │
│ Sortino (daily wallet balance)         │ 1.02                                      │
│ Calmar (daily wallet balance)          │ 5.83                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃            Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    179 │         1.27 │         346.503 │        34.65 │ 2 days, 2:37:00 │   70     0   109  39.1 │ 142.692 USDT  9.83% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴─────────────────────┘
```

</details>

## SP12v2

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 197 / 0.21 | 197 / 0.21 |
| Final balance | 1100.451 USDT | 1073.896 USDT |
| Total profit % | 10.05% | 7.39% |
| CAGR % | 3.73% | 2.77% |
| Win / draw / loss, win % | 88 / 0 / 109, 44.7% | 88 / 0 / 109, 44.7% |
| Profit factor | 1.19 | 1.14 |
| Max % of account underwater | 5.92% | 6.22% |
| Absolute drawdown | 63.323 USDT (5.92%) | 68.949 USDT (6.22%) |
| Best trade | ETH/USDT 9.96% | ETH/USDT 9.96% |
| Worst trade | SOL/USDT -4.19% | SOL/USDT -4.19% |

<details><summary>SP12v2: full report, Step-ups off</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 2                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 197 / 0.21                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1100.451 USDT                             │
│ Absolute profit                        │ 100.451 USDT                              │
│ Total profit %                         │ 10.05%                                    │
│ CAGR %                                 │ 3.73%                                     │
│ Sharpe (closed trades)                 │ 0.28                                      │
│ Sortino (closed trades)                │ 0.93                                      │
│ Calmar (closed trades)                 │ 3.40                                      │
│ SQN                                    │ 0.98                                      │
│ Mean profit p-value                    │ 0.3295                                    │
│ Profit factor                          │ 1.19                                      │
│ Expectancy (Ratio)                     │ 0.51 (0.11)                               │
│ Avg. daily profit                      │ 0.105 USDT                                │
│ Avg. stake amount                      │ 199.735 USDT                              │
│ Market change                          │ -21.89%                                   │
│ Total trade volume                     │ 91918.785 USDT                            │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 7.44%                            │
│ Worst Pair                             │ SOL/USDT 2.60%                            │
│ Best trade                             │ ETH/USDT 9.96%                            │
│ Worst trade                            │ SOL/USDT -4.19%                           │
│ Best day                               │ 38.531 USDT                               │
│ Worst day                              │ -23.384 USDT                              │
│ Days win/draw/lose                     │ 66 / 803 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 00:00 / 10d 00:00 / 1d 21:08           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 10d 00:00 / 0d 23:31           │
│ Max Consecutive Wins / Loss            │ 6 / 7                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 994.646 USDT / 1112.273 USDT              │
│ Max % of account underwater            │ 5.92%                                     │
│ Absolute drawdown                      │ 63.323 USDT (5.92%)                       │
│ Drawdown duration                      │ 96 days 04:00:00                          │
│ Profit at drawdown start               │ 70.249 USDT                               │
│ Profit at drawdown end                 │ 6.926 USDT                                │
│ Drawdown start                         │ 2025-03-27 16:00:00                       │
│ Drawdown end                           │ 2025-07-01 20:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 993.318 USDT / 1120.723 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-03-03 08:00:00 / 2026-09-27 08:00:00 │
│ Max % of account underwater (balance)  │ 6.34%                                     │
│ Absolute drawdown (wallet balance)     │ 68.117 USDT (6.34%)                       │
│ Drawdown duration                      │ 400 days 08:00:00                         │
│ Profit at drawdown start               │ 75.043 USDT                               │
│ Profit at drawdown end                 │ 6.926 USDT                                │
│ Drawdown start                         │ 2024-05-27 16:00:00                       │
│ Drawdown end                           │ 2025-07-02 00:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.57                                      │
│ Sortino (daily wallet balance)         │ 0.58                                      │
│ Calmar (daily wallet balance)          │ 3.17                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃   Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │    197 │         0.35 │         100.451 │        10.05 │ 1 day, 9:11:00 │   88     0   109  44.7 │ 63.323 USDT  5.92% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴────────────────┴────────────────────────┴────────────────────┘
```

</details>

<details><summary>SP12v2: full report, Step-ups on</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 2                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 197 / 0.21                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1073.896 USDT                             │
│ Absolute profit                        │ 73.896 USDT                               │
│ Total profit %                         │ 7.39%                                     │
│ CAGR %                                 │ 2.77%                                     │
│ Sharpe (closed trades)                 │ 0.20                                      │
│ Sortino (closed trades)                │ 0.55                                      │
│ Calmar (closed trades)                 │ 2.38                                      │
│ SQN                                    │ 0.70                                      │
│ Mean profit p-value                    │ 0.4838                                    │
│ Profit factor                          │ 1.14                                      │
│ Expectancy (Ratio)                     │ 0.38 (0.07)                               │
│ Avg. daily profit                      │ 0.077 USDT                                │
│ Avg. stake amount                      │ 206.248 USDT                              │
│ Market change                          │ -21.89%                                   │
│ Total trade volume                     │ 94440.417 USDT                            │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 6.57%                            │
│ Worst Pair                             │ SOL/USDT 0.82%                            │
│ Best trade                             │ ETH/USDT 9.96%                            │
│ Worst trade                            │ SOL/USDT -4.19%                           │
│ Best day                               │ 38.531 USDT                               │
│ Worst day                              │ -23.193 USDT                              │
│ Days win/draw/lose                     │ 66 / 803 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 00:00 / 10d 00:00 / 1d 21:08           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 10d 00:00 / 0d 23:31           │
│ Max Consecutive Wins / Loss            │ 6 / 7                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 994.646 USDT / 1109.214 USDT              │
│ Max % of account underwater            │ 6.22%                                     │
│ Absolute drawdown                      │ 68.949 USDT (6.22%)                       │
│ Drawdown duration                      │ 82 days 00:00:00                          │
│ Profit at drawdown start               │ 109.214 USDT                              │
│ Profit at drawdown end                 │ 40.265 USDT                               │
│ Drawdown start                         │ 2026-04-17 12:00:00                       │
│ Drawdown end                           │ 2026-07-08 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 993.318 USDT / 1125.934 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-03-03 08:00:00 / 2026-04-17 16:00:00 │
│ Max % of account underwater (balance)  │ 7.61%                                     │
│ Absolute drawdown (wallet balance)     │ 85.669 USDT (7.61%)                       │
│ Drawdown duration                      │ 82 days 00:00:00                          │
│ Profit at drawdown start               │ 125.934 USDT                              │
│ Profit at drawdown end                 │ 40.265 USDT                               │
│ Drawdown start                         │ 2026-04-17 16:00:00                       │
│ Drawdown end                           │ 2026-07-08 16:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.42                                      │
│ Sortino (daily wallet balance)         │ 0.41                                      │
│ Calmar (daily wallet balance)          │ 1.94                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃   Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │    197 │         0.35 │          73.896 │         7.39 │ 1 day, 9:11:00 │   88     0   109  44.7 │ 68.949 USDT  6.22% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴────────────────┴────────────────────────┴────────────────────┘
```

</details>

## TrendRider

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 134 / 0.14 | 134 / 0.14 |
| Final balance | 1106.283 USDT | 1079.084 USDT |
| Total profit % | 10.63% | 7.91% |
| CAGR % | 3.94% | 2.95% |
| Win / draw / loss, win % | 52 / 0 / 82, 38.8% | 52 / 0 / 82, 38.8% |
| Profit factor | 1.49 | 1.33 |
| Max % of account underwater | 3.42% | 4.24% |
| Absolute drawdown | 37.035 USDT (3.42%) | 47.726 USDT (4.24%) |
| Best trade | BTC/USDT 37.16% | BTC/USDT 37.16% |
| Worst trade | SOL/USDT -8.92% | SOL/USDT -8.92% |

<details><summary>TrendRider: full report, Step-ups off</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 134 / 0.14                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1106.283 USDT                             │
│ Absolute profit                        │ 106.283 USDT                              │
│ Total profit %                         │ 10.63%                                    │
│ CAGR %                                 │ 3.94%                                     │
│ Sharpe (closed trades)                 │ 0.29                                      │
│ Sortino (closed trades)                │ 1.48                                      │
│ Calmar (closed trades)                 │ 6.22                                      │
│ SQN                                    │ 1.23                                      │
│ Mean profit p-value                    │ 0.2225                                    │
│ Profit factor                          │ 1.49                                      │
│ Expectancy (Ratio)                     │ 0.79 (0.30)                               │
│ Avg. daily profit                      │ 0.111 USDT                                │
│ Avg. stake amount                      │ 97.206 USDT                               │
│ Market change                          │ -2.57%                                    │
│ Total trade volume                     │ 26209.99 USDT                             │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 7.65%                            │
│ Worst Pair                             │ ETH/USDT 0.77%                            │
│ Best trade                             │ BTC/USDT 37.16%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 43.986 USDT                               │
│ Worst day                              │ -8.534 USDT                               │
│ Days win/draw/lose                     │ 33 / 854 / 60                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:54            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 979.594 USDT / 1126.81 USDT               │
│ Max % of account underwater            │ 3.42%                                     │
│ Absolute drawdown                      │ 37.035 USDT (3.42%)                       │
│ Drawdown duration                      │ 308 days 00:00:00                         │
│ Profit at drawdown start               │ 82.756 USDT                               │
│ Profit at drawdown end                 │ 45.721 USDT                               │
│ Drawdown start                         │ 2025-10-07 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 979.576 USDT / 1152.887 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-11-05 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 4.13%                                     │
│ Absolute drawdown (wallet balance)     │ 46.992 USDT (4.08%)                       │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 152.887 USDT                              │
│ Profit at drawdown end                 │ 105.896 USDT                              │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.71                                      │
│ Sortino (daily wallet balance)         │ 0.78                                      │
│ Calmar (daily wallet balance)          │ 5.22                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.57 │         106.283 │        10.63 │ 3 days, 20:14:00 │   52     0    82  38.8 │ 37.035 USDT  3.42% │
└────────────┴────────┴──────────────┴─────────────────┴──────────────┴──────────────────┴────────────────────────┴────────────────────┘
```

</details>

<details><summary>TrendRider: full report, Step-ups on</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-11 08:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 134 / 0.14                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1079.084 USDT                             │
│ Absolute profit                        │ 79.084 USDT                               │
│ Total profit %                         │ 7.91%                                     │
│ CAGR %                                 │ 2.95%                                     │
│ Sharpe (closed trades)                 │ 0.21                                      │
│ Sortino (closed trades)                │ 0.64                                      │
│ Calmar (closed trades)                 │ 3.74                                      │
│ SQN                                    │ 0.88                                      │
│ Mean profit p-value                    │ 0.3797                                    │
│ Profit factor                          │ 1.33                                      │
│ Expectancy (Ratio)                     │ 0.59 (0.20)                               │
│ Avg. daily profit                      │ 0.083 USDT                                │
│ Avg. stake amount                      │ 103.404 USDT                              │
│ Market change                          │ -2.57%                                    │
│ Total trade volume                     │ 27847.019 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 5.76%                            │
│ Worst Pair                             │ ETH/USDT 0.78%                            │
│ Best trade                             │ BTC/USDT 37.16%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 43.986 USDT                               │
│ Worst day                              │ -15.117 USDT                              │
│ Days win/draw/lose                     │ 33 / 854 / 60                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:54            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 979.594 USDT / 1126.81 USDT               │
│ Max % of account underwater            │ 4.24%                                     │
│ Absolute drawdown                      │ 47.726 USDT (4.24%)                       │
│ Drawdown duration                      │ 37 days 04:00:00                          │
│ Profit at drawdown start               │ 126.81 USDT                               │
│ Profit at drawdown end                 │ 79.084 USDT                               │
│ Drawdown start                         │ 2026-08-30 20:00:00                       │
│ Drawdown end                           │ 2026-10-07 00:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 979.576 USDT / 1152.887 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-11-05 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 6.43%                                     │
│ Absolute drawdown (wallet balance)     │ 74.181 USDT (6.43%)                       │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 152.887 USDT                              │
│ Profit at drawdown end                 │ 78.706 USDT                               │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.53                                      │
│ Sortino (daily wallet balance)         │ 0.56                                      │
│ Calmar (daily wallet balance)          │ 2.46                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.57 │          79.084 │         7.91 │ 3 days, 20:14:00 │   52     0    82  38.8 │ 47.726 USDT  4.24% │
└────────────┴────────┴──────────────┴─────────────────┴──────────────┴──────────────────┴────────────────────────┴────────────────────┘
```

</details>

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
