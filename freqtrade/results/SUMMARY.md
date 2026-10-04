# Freqtrade backtest results

Updated 2026-10-04 22:14 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee, 1% risk per trade.

## SP12v4

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-04 16:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 225 / 0.24                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1573.222 USDT                             │
│ Absolute profit                        │ 573.222 USDT                              │
│ Total profit %                         │ 57.32%                                    │
│ CAGR %                                 │ 19.08%                                    │
│ Sharpe (closed trades)                 │ 0.31                                      │
│ Sortino (closed trades)                │ 1.89                                      │
│ Calmar (closed trades)                 │ 7.36                                      │
│ SQN                                    │ 1.03                                      │
│ Mean profit p-value                    │ 0.3049                                    │
│ Profit factor                          │ 1.41                                      │
│ Expectancy (Ratio)                     │ 2.55 (0.25)                               │
│ Avg. daily profit                      │ 0.605 USDT                                │
│ Avg. stake amount                      │ 501.308 USDT                              │
│ Market change                          │ 41.29%                                    │
│ Total trade volume                     │ 226614.407 USDT                           │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 44.35%                           │
│ Worst Pair                             │ SOL/USDT -14.75%                          │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 464.619 USDT                              │
│ Worst day                              │ -35.998 USDT                              │
│ Days win/draw/lose                     │ 59 / 796 / 91                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 06:37           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 00:14            │
│ Max Consecutive Wins / Loss            │ 6 / 7                                     │
│ Rejected Entry signals                 │ 16                                        │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 877.853 USDT / 1635.857 USDT              │
│ Max % of account underwater            │ 15.71%                                    │
│ Absolute drawdown                      │ 253.462 USDT (15.71%)                     │
│ Drawdown duration                      │ 331 days 04:00:00                         │
│ Profit at drawdown start               │ 613.673 USDT                              │
│ Profit at drawdown end                 │ 360.211 USDT                              │
│ Drawdown start                         │ 2025-09-14 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 874.257 USDT / 1715.659 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-10-13 16:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 18.75%                                    │
│ Absolute drawdown (wallet balance)     │ 312.38 USDT (18.74%)                      │
│ Drawdown duration                      │ 397 days 00:00:00                         │
│ Profit at drawdown start               │ 666.735 USDT                              │
│ Profit at drawdown end                 │ 354.355 USDT                              │
│ Drawdown start                         │ 2025-07-18 04:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.87                                      │
│ Sortino (daily wallet balance)         │ 1.16                                      │
│ Calmar (daily wallet balance)          │ 6.20                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                            
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃             Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    225 │         0.94 │         573.222 │        57.32 │ 1 day, 21:59:00 │   90     0   135  40.0 │ 253.462 USDT  15.71% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴──────────────────────┘
```

## SP12v2

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-04 16:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 2                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 96 / 0.1                                  │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 953.298 USDT                              │
│ Absolute profit                        │ -46.702 USDT                              │
│ Total profit %                         │ -4.67%                                    │
│ CAGR %                                 │ -1.83%                                    │
│ Sharpe (closed trades)                 │ -0.04                                     │
│ Sortino (closed trades)                │ -0.26                                     │
│ Calmar (closed trades)                 │ -0.24                                     │
│ SQN                                    │ -0.18                                     │
│ Mean profit p-value                    │ 0.8604                                    │
│ Profit factor                          │ 0.88                                      │
│ Expectancy (Ratio)                     │ -0.49 (-0.07)                             │
│ Avg. daily profit                      │ -0.049 USDT                               │
│ Avg. stake amount                      │ 342.48 USDT                               │
│ Market change                          │ -14.70%                                   │
│ Total trade volume                     │ 65841.098 USDT                            │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 12.03%                           │
│ Worst Pair                             │ SOL/USDT -16.70%                          │
│ Best trade                             │ SOL/USDT 57.18%                           │
│ Worst trade                            │ SOL/USDT -4.13%                           │
│ Best day                               │ 342.569 USDT                              │
│ Worst day                              │ -27.988 USDT                              │
│ Days win/draw/lose                     │ 27 / 871 / 48                             │
│ Min/Max/Avg. Duration Winners          │ 0d 04:00 / 274d 04:00 / 18d 17:22         │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 59d 20:00 / 3d 06:17           │
│ Max Consecutive Wins / Loss            │ 6 / 8                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 610.729 USDT / 989.399 USDT               │
│ Max % of account underwater            │ 38.93%                                    │
│ Absolute drawdown                      │ 389.271 USDT (38.93%)                     │
│ Drawdown duration                      │ 876 days 20:00:00                         │
│ Profit at drawdown start               │ 0 USDT                                    │
│ Profit at drawdown end                 │ -389.271 USDT                             │
│ Drawdown start                         │ 2024-03-03 04:00:00                       │
│ Drawdown end                           │ 2026-07-28 00:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 623.726 USDT / 1213.499 USDT              │
│ Min/Max balance dates (wallet balance) │ 2026-07-08 16:00:00 / 2025-09-13 04:00:00 │
│ Max % of account underwater (balance)  │ 48.60%                                    │
│ Absolute drawdown (wallet balance)     │ 589.773 USDT (48.60%)                     │
│ Drawdown duration                      │ 298 days 12:00:00                         │
│ Profit at drawdown start               │ 213.499 USDT                              │
│ Profit at drawdown end                 │ -376.274 USDT                             │
│ Drawdown start                         │ 2025-09-13 04:00:00                       │
│ Drawdown end                           │ 2026-07-08 16:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.13                                      │
│ Sortino (daily wallet balance)         │ 0.16                                      │
│ Calmar (daily wallet balance)          │ -0.19                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                            
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃             Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │     96 │        -0.13 │         -46.702 │        -4.67 │ 9 days, 9:10:00 │   38     0    58  39.6 │ 389.271 USDT  38.93% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴──────────────────────┘
```

## TrendRider

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-04 16:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 134 / 0.14                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1251.237 USDT                             │
│ Absolute profit                        │ 251.237 USDT                              │
│ Total profit %                         │ 25.12%                                    │
│ CAGR %                                 │ 9.02%                                     │
│ Sharpe (closed trades)                 │ 0.27                                      │
│ Sortino (closed trades)                │ 1.33                                      │
│ Calmar (closed trades)                 │ 6.68                                      │
│ SQN                                    │ 1.16                                      │
│ Mean profit p-value                    │ 0.2481                                    │
│ Profit factor                          │ 1.46                                      │
│ Expectancy (Ratio)                     │ 1.87 (0.28)                               │
│ Avg. daily profit                      │ 0.265 USDT                                │
│ Avg. stake amount                      │ 249.237 USDT                              │
│ Market change                          │ 3.47%                                     │
│ Total trade volume                     │ 67181.049 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 19.00%                           │
│ Worst Pair                             │ ETH/USDT -0.06%                           │
│ Best trade                             │ BTC/USDT 37.16%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 108.74 USDT                               │
│ Worst day                              │ -21.854 USDT                              │
│ Days win/draw/lose                     │ 33 / 851 / 60                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 12:32            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 949.494 USDT / 1303.951 USDT              │
│ Max % of account underwater            │ 7.99%                                     │
│ Absolute drawdown                      │ 91.267 USDT (7.58%)                       │
│ Drawdown duration                      │ 308 days 00:00:00                         │
│ Profit at drawdown start               │ 203.519 USDT                              │
│ Profit at drawdown end                 │ 112.252 USDT                              │
│ Drawdown start                         │ 2025-10-07 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 949.462 USDT / 1367.446 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-11-05 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 9.78%                                     │
│ Absolute drawdown (wallet balance)     │ 122.837 USDT (8.98%)                      │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 367.446 USDT                              │
│ Profit at drawdown end                 │ 244.608 USDT                              │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.71                                      │
│ Sortino (daily wallet balance)         │ 0.77                                      │
│ Calmar (daily wallet balance)          │ 5.67                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.58 │         251.237 │        25.12 │ 3 days, 19:24:00 │   52     0    82  38.8 │ 91.267 USDT  7.58% │
└────────────┴────────┴──────────────┴─────────────────┴──────────────┴──────────────────┴────────────────────────┴────────────────────┘
```
