# Freqtrade backtest results

Updated 2026-10-04 22:41 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee, 1% risk per trade.

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
│ Total/Daily Avg Trades                 │ 197 / 0.21                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1326.981 USDT                             │
│ Absolute profit                        │ 326.981 USDT                              │
│ Total profit %                         │ 32.70%                                    │
│ CAGR %                                 │ 11.52%                                    │
│ Sharpe (closed trades)                 │ 0.37                                      │
│ Sortino (closed trades)                │ 1.35                                      │
│ Calmar (closed trades)                 │ 5.37                                      │
│ SQN                                    │ 1.29                                      │
│ Mean profit p-value                    │ 0.2                                       │
│ Profit factor                          │ 1.28                                      │
│ Expectancy (Ratio)                     │ 1.66 (0.16)                               │
│ Avg. daily profit                      │ 0.345 USDT                                │
│ Avg. stake amount                      │ 508.14 USDT                               │
│ Market change                          │ -14.70%                                   │
│ Total trade volume                     │ 200935.594 USDT                           │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 19.89%                           │
│ Worst Pair                             │ SOL/USDT 12.80%                           │
│ Best trade                             │ ETH/USDT 12.64%                           │
│ Worst trade                            │ SOL/USDT -4.19%                           │
│ Best day                               │ 112.652 USDT                              │
│ Worst day                              │ -52.565 USDT                              │
│ Days win/draw/lose                     │ 64 / 800 / 82                             │
│ Min/Max/Avg. Duration Winners          │ 0d 04:00 / 10d 00:00 / 1d 21:49           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 10d 00:00 / 0d 22:41           │
│ Max Consecutive Wins / Loss            │ 6 / 7                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 989.399 USDT / 1328.941 USDT              │
│ Max % of account underwater            │ 12.27%                                    │
│ Absolute drawdown                      │ 148.312 USDT (12.27%)                     │
│ Drawdown duration                      │ 96 days 04:00:00                          │
│ Profit at drawdown start               │ 208.279 USDT                              │
│ Profit at drawdown end                 │ 59.967 USDT                               │
│ Drawdown start                         │ 2025-03-27 16:00:00                       │
│ Drawdown end                           │ 2025-07-01 20:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 986.769 USDT / 1348.932 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-03-03 08:00:00 / 2026-09-27 08:00:00 │
│ Max % of account underwater (balance)  │ 13.79%                                    │
│ Absolute drawdown (wallet balance)     │ 169.551 USDT (13.79%)                     │
│ Drawdown duration                      │ 99 days 12:00:00                          │
│ Profit at drawdown start               │ 229.517 USDT                              │
│ Profit at drawdown end                 │ 59.967 USDT                               │
│ Drawdown start                         │ 2025-03-24 12:00:00                       │
│ Drawdown end                           │ 2025-07-02 00:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.78                                      │
│ Sortino (daily wallet balance)         │ 0.90                                      │
│ Calmar (daily wallet balance)          │ 4.82                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃   Avg Duration ┃  Win  Draw  Loss  Win% ┃             Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │    197 │         0.50 │         326.981 │         32.7 │ 1 day, 8:33:00 │   84     0   113  42.6 │ 148.312 USDT  12.27% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴────────────────┴────────────────────────┴──────────────────────┘
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
