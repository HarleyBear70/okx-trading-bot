# Freqtrade backtest results

Updated 2026-10-04 23:58 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee, 1% risk per trade.

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
│ Total/Daily Avg Trades                 │ 180 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1806.026 USDT                             │
│ Absolute profit                        │ 806.026 USDT                              │
│ Total profit %                         │ 80.60%                                    │
│ CAGR %                                 │ 25.59%                                    │
│ Sharpe (closed trades)                 │ 0.36                                      │
│ Sortino (closed trades)                │ 2.23                                      │
│ Calmar (closed trades)                 │ 13.06                                     │
│ SQN                                    │ 1.31                                      │
│ Mean profit p-value                    │ 0.1904                                    │
│ Profit factor                          │ 1.65                                      │
│ Expectancy (Ratio)                     │ 4.48 (0.40)                               │
│ Avg. daily profit                      │ 0.851 USDT                                │
│ Avg. stake amount                      │ 600.174 USDT                              │
│ Market change                          │ 58.26%                                    │
│ Total trade volume                     │ 217302.94 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 41.37%                           │
│ Worst Pair                             │ BTC/USDT 5.67%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 478.287 USDT                              │
│ Worst day                              │ -42.139 USDT                              │
│ Days win/draw/lose                     │ 45 / 815 / 84                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 15:08           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 01:57            │
│ Max Consecutive Wins / Loss            │ 5 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 951.342 USDT / 1887.514 USDT              │
│ Max % of account underwater            │ 12.71%                                    │
│ Absolute drawdown                      │ 233.194 USDT (12.45%)                     │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 873.53 USDT                               │
│ Profit at drawdown end                 │ 640.336 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 943.622 USDT / 1947.684 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 16.85%                                    │
│ Absolute drawdown (wallet balance)     │ 279.663 USDT (14.61%)                     │
│ Drawdown duration                      │ 155 days 04:00:00                         │
│ Profit at drawdown start               │ 914.113 USDT                              │
│ Profit at drawdown end                 │ 634.45 USDT                               │
│ Drawdown start                         │ 2026-03-17 00:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.16                                      │
│ Sortino (daily wallet balance)         │ 1.60                                      │
│ Calmar (daily wallet balance)          │ 11.17                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                            
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃             Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    180 │         1.26 │         806.026 │         80.6 │ 2 days, 1:24:00 │   69     0   111  38.3 │ 233.194 USDT  12.45% │
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
