# Freqtrade backtest results

Updated 2026-10-05 17:21 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee. Exits match the live bots, including selling half at +2R. Risk per trade comes from `risk_pct()` in bot.py: **Step-ups off** risks RISK_PCT every trade; **Step-ups on** raises it by RISK_STEPS as the balance grows (back to RISK_PCT if the balance falls 5% from its best).

## SP12v4: selling half at +2R vs not

| | Sell half at +2R | No half sell |
|---|---|---|
| Trades | 182 / 0.19 | 182 / 0.19 |
| Final balance | 1259.82 USDT | 1566.453 USDT |
| Total profit % | 25.98% | 56.65% |
| CAGR % | 9.30% | 18.86% |
| Win / draw / loss, win % | 75 / 0 / 107, 41.2% | 71 / 0 / 111, 39.0% |
| Profit factor | 1.49 | 1.93 |
| Max % of account underwater | 6.97% | 7.04% |
| Absolute drawdown | 90.524 USDT (6.97%) | 111.991 USDT (7.04%) |
| Best trade | XRP/USDT 82.34% | XRP/USDT 158.33% |
| Worst trade | BTC/USDT -4.19% | BTC/USDT -4.19% |

<details><summary>SP12v4: selling half at +2R vs not: full report, Sell half at +2R</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1259.82 USDT                              │
│ Absolute profit                        │ 259.82 USDT                               │
│ Total profit %                         │ 25.98%                                    │
│ CAGR %                                 │ 9.30%                                     │
│ Sharpe (closed trades)                 │ 0.36                                      │
│ Sortino (closed trades)                │ 2.06                                      │
│ Calmar (closed trades)                 │ 7.52                                      │
│ SQN                                    │ 1.33                                      │
│ Mean profit p-value                    │ 0.1852                                    │
│ Profit factor                          │ 1.49                                      │
│ Expectancy (Ratio)                     │ 1.43 (0.29)                               │
│ Avg. daily profit                      │ 0.274 USDT                                │
│ Avg. stake amount                      │ 223.553 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 93433.912 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 12.23%                           │
│ Worst Pair                             │ BTC/USDT 4.50%                            │
│ Best trade                             │ XRP/USDT 82.34%                           │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 124.633 USDT                              │
│ Worst day                              │ -14.857 USDT                              │
│ Days win/draw/lose                     │ 50 / 815 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 11:31           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:33            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 976.884 USDT / 1299.576 USDT              │
│ Max % of account underwater            │ 6.97%                                     │
│ Absolute drawdown                      │ 90.524 USDT (6.97%)                       │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 299.576 USDT                              │
│ Profit at drawdown end                 │ 209.052 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 975.219 USDT / 1314.693 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2025-10-05 08:00:00 │
│ Max % of account underwater (balance)  │ 8.20%                                     │
│ Absolute drawdown (wallet balance)     │ 107.832 USDT (8.20%)                      │
│ Drawdown duration                      │ 317 days 20:00:00                         │
│ Profit at drawdown start               │ 314.693 USDT                              │
│ Profit at drawdown end                 │ 206.861 USDT                              │
│ Drawdown start                         │ 2025-10-05 08:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.00                                      │
│ Sortino (daily wallet balance)         │ 1.27                                      │
│ Calmar (daily wallet balance)          │ 6.41                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         0.60 │         259.820 │        25.98 │ 2 days, 2:01:00 │   75     0   107  41.2 │ 90.524 USDT  6.97% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴────────────────────┘
```

</details>

<details><summary>SP12v4: selling half at +2R vs not: full report, No half sell</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1566.453 USDT                             │
│ Absolute profit                        │ 566.453 USDT                              │
│ Total profit %                         │ 56.65%                                    │
│ CAGR %                                 │ 18.86%                                    │
│ Sharpe (closed trades)                 │ 0.42                                      │
│ Sortino (closed trades)                │ 3.58                                      │
│ Calmar (closed trades)                 │ 16.21                                     │
│ SQN                                    │ 1.55                                      │
│ Mean profit p-value                    │ 0.122                                     │
│ Profit factor                          │ 1.93                                      │
│ Expectancy (Ratio)                     │ 3.11 (0.56)                               │
│ Avg. daily profit                      │ 0.598 USDT                                │
│ Avg. stake amount                      │ 292.956 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 107416.956 USDT                           │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 31.82%                           │
│ Worst Pair                             │ BTC/USDT 7.59%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 243.623 USDT                              │
│ Worst day                              │ -18.167 USDT                              │
│ Days win/draw/lose                     │ 47 / 815 / 83                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 14:29           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:42            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 975.335 USDT / 1590.768 USDT              │
│ Max % of account underwater            │ 7.04%                                     │
│ Absolute drawdown                      │ 111.991 USDT (7.04%)                      │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 590.42 USDT                               │
│ Profit at drawdown end                 │ 478.429 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 971.359 USDT / 1618.333 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 9.56%                                     │
│ Absolute drawdown (wallet balance)     │ 141.441 USDT (8.75%)                      │
│ Drawdown duration                      │ 155 days 04:00:00                         │
│ Profit at drawdown start               │ 617.191 USDT                              │
│ Profit at drawdown end                 │ 475.749 USDT                              │
│ Drawdown start                         │ 2026-03-17 00:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.34                                      │
│ Sortino (daily wallet balance)         │ 1.95                                      │
│ Calmar (daily wallet balance)          │ 13.08                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃            Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         1.26 │         566.453 │        56.65 │ 2 days, 2:01:00 │   71     0   111  39.0 │ 111.991 USDT  7.04% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴─────────────────────┘
```

</details>

Both risk 0.5% per trade (RISK_PCT) with step-ups off. Without the half sell, the whole position runs to the stop, trailing stop, target or time exit.

## SP12v4

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 182 / 0.19 | 181 / 0.19 |
| Final balance | 1259.82 USDT | 1208.872 USDT |
| Total profit % | 25.98% | 20.89% |
| CAGR % | 9.30% | 7.58% |
| Win / draw / loss, win % | 75 / 0 / 107, 41.2% | 74 / 0 / 107, 40.9% |
| Profit factor | 1.49 | 1.32 |
| Max % of account underwater | 6.97% | 11.82% |
| Absolute drawdown | 90.524 USDT (6.97%) | 155.444 USDT (11.82%) |
| Best trade | XRP/USDT 82.34% | XRP/USDT 82.34% |
| Worst trade | BTC/USDT -4.19% | BTC/USDT -4.19% |

<details><summary>SP12v4: full report, Step-ups off</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1259.82 USDT                              │
│ Absolute profit                        │ 259.82 USDT                               │
│ Total profit %                         │ 25.98%                                    │
│ CAGR %                                 │ 9.30%                                     │
│ Sharpe (closed trades)                 │ 0.36                                      │
│ Sortino (closed trades)                │ 2.06                                      │
│ Calmar (closed trades)                 │ 7.52                                      │
│ SQN                                    │ 1.33                                      │
│ Mean profit p-value                    │ 0.1852                                    │
│ Profit factor                          │ 1.49                                      │
│ Expectancy (Ratio)                     │ 1.43 (0.29)                               │
│ Avg. daily profit                      │ 0.274 USDT                                │
│ Avg. stake amount                      │ 223.553 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 93433.912 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 12.23%                           │
│ Worst Pair                             │ BTC/USDT 4.50%                            │
│ Best trade                             │ XRP/USDT 82.34%                           │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 124.633 USDT                              │
│ Worst day                              │ -14.857 USDT                              │
│ Days win/draw/lose                     │ 50 / 815 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 11:31           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:33            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 976.884 USDT / 1299.576 USDT              │
│ Max % of account underwater            │ 6.97%                                     │
│ Absolute drawdown                      │ 90.524 USDT (6.97%)                       │
│ Drawdown duration                      │ 146 days 08:00:00                         │
│ Profit at drawdown start               │ 299.576 USDT                              │
│ Profit at drawdown end                 │ 209.052 USDT                              │
│ Drawdown start                         │ 2026-03-18 08:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 975.219 USDT / 1314.693 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2025-10-05 08:00:00 │
│ Max % of account underwater (balance)  │ 8.20%                                     │
│ Absolute drawdown (wallet balance)     │ 107.832 USDT (8.20%)                      │
│ Drawdown duration                      │ 317 days 20:00:00                         │
│ Profit at drawdown start               │ 314.693 USDT                              │
│ Profit at drawdown end                 │ 206.861 USDT                              │
│ Drawdown start                         │ 2025-10-05 08:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 1.00                                      │
│ Sortino (daily wallet balance)         │ 1.27                                      │
│ Calmar (daily wallet balance)          │ 6.41                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         0.60 │         259.820 │        25.98 │ 2 days, 2:01:00 │   75     0   107  41.2 │ 90.524 USDT  6.97% │
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 181 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1208.872 USDT                             │
│ Absolute profit                        │ 208.872 USDT                              │
│ Total profit %                         │ 20.89%                                    │
│ CAGR %                                 │ 7.58%                                     │
│ Sharpe (closed trades)                 │ 0.27                                      │
│ Sortino (closed trades)                │ 0.87                                      │
│ Calmar (closed trades)                 │ 3.56                                      │
│ SQN                                    │ 1.00                                      │
│ Mean profit p-value                    │ 0.3171                                    │
│ Profit factor                          │ 1.32                                      │
│ Expectancy (Ratio)                     │ 1.15 (0.19)                               │
│ Avg. daily profit                      │ 0.22 USDT                                 │
│ Avg. stake amount                      │ 265.621 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 109266.265 USDT                           │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 8.64%                            │
│ Worst Pair                             │ BTC/USDT 4.28%                            │
│ Best trade                             │ XRP/USDT 82.34%                           │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 139.467 USDT                              │
│ Worst day                              │ -40.007 USDT                              │
│ Days win/draw/lose                     │ 50 / 815 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 12:06           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:33            │
│ Max Consecutive Wins / Loss            │ 6 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 976.884 USDT / 1315.601 USDT              │
│ Max % of account underwater            │ 11.82%                                    │
│ Absolute drawdown                      │ 155.444 USDT (11.82%)                     │
│ Drawdown duration                      │ 310 days 00:00:00                         │
│ Profit at drawdown start               │ 315.601 USDT                              │
│ Profit at drawdown end                 │ 160.157 USDT                              │
│ Drawdown start                         │ 2025-10-05 16:00:00                       │
│ Drawdown end                           │ 2026-08-11 16:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 975.219 USDT / 1342.269 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-05-19 20:00:00 / 2025-10-05 08:00:00 │
│ Max % of account underwater (balance)  │ 13.72%                                    │
│ Absolute drawdown (wallet balance)     │ 184.214 USDT (13.72%)                     │
│ Drawdown duration                      │ 317 days 20:00:00                         │
│ Profit at drawdown start               │ 342.269 USDT                              │
│ Profit at drawdown end                 │ 158.055 USDT                              │
│ Drawdown start                         │ 2025-10-05 08:00:00                       │
│ Drawdown end                           │ 2026-08-19 04:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.74                                      │
│ Sortino (daily wallet balance)         │ 0.80                                      │
│ Calmar (daily wallet balance)          │ 3.08                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                            
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃             Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    181 │         0.59 │         208.872 │        20.89 │ 2 days, 2:05:00 │   74     0   107  40.9 │ 155.444 USDT  11.82% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴──────────────────────┘
```

</details>

## SP12v2

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 197 / 0.21 | 197 / 0.21 |
| Final balance | 1113.057 USDT | 1096 USDT |
| Total profit % | 11.31% | 9.60% |
| CAGR % | 4.21% | 3.59% |
| Win / draw / loss, win % | 90 / 0 / 107, 45.7% | 90 / 0 / 107, 45.7% |
| Profit factor | 1.22 | 1.18 |
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 2                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 197 / 0.21                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1113.057 USDT                             │
│ Absolute profit                        │ 113.057 USDT                              │
│ Total profit %                         │ 11.31%                                    │
│ CAGR %                                 │ 4.21%                                     │
│ Sharpe (closed trades)                 │ 0.31                                      │
│ Sortino (closed trades)                │ 1.07                                      │
│ Calmar (closed trades)                 │ 3.85                                      │
│ SQN                                    │ 1.10                                      │
│ Mean profit p-value                    │ 0.2723                                    │
│ Profit factor                          │ 1.22                                      │
│ Expectancy (Ratio)                     │ 0.57 (0.12)                               │
│ Avg. daily profit                      │ 0.119 USDT                                │
│ Avg. stake amount                      │ 199.735 USDT                              │
│ Market change                          │ -15.43%                                   │
│ Total trade volume                     │ 91931.417 USDT                            │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 8.05%                            │
│ Worst Pair                             │ SOL/USDT 3.25%                            │
│ Best trade                             │ ETH/USDT 9.96%                            │
│ Worst trade                            │ SOL/USDT -4.19%                           │
│ Best day                               │ 38.531 USDT                               │
│ Worst day                              │ -23.384 USDT                              │
│ Days win/draw/lose                     │ 67 / 801 / 79                             │
│ Min/Max/Avg. Duration Winners          │ 0d 00:00 / 10d 00:00 / 1d 22:27           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 10d 00:00 / 0d 21:14           │
│ Max Consecutive Wins / Loss            │ 6 / 7                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 994.646 USDT / 1113.057 USDT              │
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
│ Sharpe (daily wallet balance)          │ 0.64                                      │
│ Sortino (daily wallet balance)         │ 0.66                                      │
│ Calmar (daily wallet balance)          │ 3.63                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃   Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │    197 │         0.38 │         113.057 │        11.31 │ 1 day, 8:45:00 │   90     0   107  45.7 │ 63.323 USDT  5.92% │
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 2                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 197 / 0.21                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1096 USDT                                 │
│ Absolute profit                        │ 96 USDT                                   │
│ Total profit %                         │ 9.60%                                     │
│ CAGR %                                 │ 3.59%                                     │
│ Sharpe (closed trades)                 │ 0.26                                      │
│ Sortino (closed trades)                │ 0.77                                      │
│ Calmar (closed trades)                 │ 3.11                                      │
│ SQN                                    │ 0.92                                      │
│ Mean profit p-value                    │ 0.359                                     │
│ Profit factor                          │ 1.18                                      │
│ Expectancy (Ratio)                     │ 0.49 (0.10)                               │
│ Avg. daily profit                      │ 0.101 USDT                                │
│ Avg. stake amount                      │ 206.248 USDT                              │
│ Market change                          │ -15.43%                                   │
│ Total trade volume                     │ 94462.564 USDT                            │
│                                        │                                           │
│ Best Pair                              │ ETH/USDT 7.17%                            │
│ Worst Pair                             │ SOL/USDT 2.43%                            │
│ Best trade                             │ ETH/USDT 9.96%                            │
│ Worst trade                            │ SOL/USDT -4.19%                           │
│ Best day                               │ 38.531 USDT                               │
│ Worst day                              │ -23.193 USDT                              │
│ Days win/draw/lose                     │ 67 / 801 / 79                             │
│ Min/Max/Avg. Duration Winners          │ 0d 00:00 / 10d 00:00 / 1d 22:27           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 10d 00:00 / 0d 21:14           │
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
│ Sharpe (daily wallet balance)          │ 0.54                                      │
│ Sortino (daily wallet balance)         │ 0.54                                      │
│ Calmar (daily wallet balance)          │ 2.58                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃   Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v2 │    197 │         0.38 │          96.000 │          9.6 │ 1 day, 8:45:00 │   90     0   107  45.7 │ 68.949 USDT  6.22% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴────────────────┴────────────────────────┴────────────────────┘
```

</details>

## TrendRider

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 134 / 0.14 | 134 / 0.14 |
| Final balance | 1096.838 USDT | 1072.989 USDT |
| Total profit % | 9.68% | 7.30% |
| CAGR % | 3.62% | 2.75% |
| Win / draw / loss, win % | 52 / 0 / 82, 38.8% | 52 / 0 / 82, 38.8% |
| Profit factor | 1.37 | 1.25 |
| Max % of account underwater | 4.26% | 4.26% |
| Absolute drawdown | 46.645 USDT (4.26%) | 46.645 USDT (4.26%) |
| Best trade | SOL/USDT 26.24% | SOL/USDT 26.24% |
| Worst trade | SOL/USDT -8.92% | SOL/USDT -8.92% |

<details><summary>TrendRider: full report, Step-ups off</summary>

```
                                   SUMMARY METRICS                                    
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Metric                                 ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Backtesting from                       │ 2024-03-01 00:00:00                       │
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 134 / 0.14                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1096.838 USDT                             │
│ Absolute profit                        │ 96.838 USDT                               │
│ Total profit %                         │ 9.68%                                     │
│ CAGR %                                 │ 3.62%                                     │
│ Sharpe (closed trades)                 │ 0.28                                      │
│ Sortino (closed trades)                │ 1.05                                      │
│ Calmar (closed trades)                 │ 4.58                                      │
│ SQN                                    │ 1.21                                      │
│ Mean profit p-value                    │ 0.23                                      │
│ Profit factor                          │ 1.37                                      │
│ Expectancy (Ratio)                     │ 0.72 (0.22)                               │
│ Avg. daily profit                      │ 0.102 USDT                                │
│ Avg. stake amount                      │ 108.01 USDT                               │
│ Market change                          │ 2.89%                                     │
│ Total trade volume                     │ 32891.027 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 7.02%                            │
│ Worst Pair                             │ ETH/USDT -0.35%                           │
│ Best trade                             │ SOL/USDT 26.24%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 37.239 USDT                               │
│ Worst day                              │ -10.762 USDT                              │
│ Days win/draw/lose                     │ 35 / 852 / 58                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:01            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 988.653 USDT / 1114.111 USDT              │
│ Max % of account underwater            │ 4.26%                                     │
│ Absolute drawdown                      │ 46.645 USDT (4.26%)                       │
│ Drawdown duration                      │ 308 days 00:00:00                         │
│ Profit at drawdown start               │ 94.696 USDT                               │
│ Profit at drawdown end                 │ 48.051 USDT                               │
│ Drawdown start                         │ 2025-10-07 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 986.676 USDT / 1130.471 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-09-18 16:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 4.85%                                     │
│ Absolute drawdown (wallet balance)     │ 53.377 USDT (4.85%)                       │
│ Drawdown duration                      │ 316 days 12:00:00                         │
│ Profit at drawdown start               │ 101.294 USDT                              │
│ Profit at drawdown end                 │ 47.917 USDT                               │
│ Drawdown start                         │ 2025-10-06 20:00:00                       │
│ Drawdown end                           │ 2026-08-19 08:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.65                                      │
│ Sortino (daily wallet balance)         │ 0.69                                      │
│ Calmar (daily wallet balance)          │ 4.05                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.48 │          96.838 │         9.68 │ 3 days, 19:42:00 │   52     0    82  38.8 │ 46.645 USDT  4.26% │
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 134 / 0.14                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1072.989 USDT                             │
│ Absolute profit                        │ 72.989 USDT                               │
│ Total profit %                         │ 7.30%                                     │
│ CAGR %                                 │ 2.75%                                     │
│ Sharpe (closed trades)                 │ 0.21                                      │
│ Sortino (closed trades)                │ 0.56                                      │
│ Calmar (closed trades)                 │ 3.45                                      │
│ SQN                                    │ 0.88                                      │
│ Mean profit p-value                    │ 0.3821                                    │
│ Profit factor                          │ 1.25                                      │
│ Expectancy (Ratio)                     │ 0.54 (0.15)                               │
│ Avg. daily profit                      │ 0.077 USDT                                │
│ Avg. stake amount                      │ 113.393 USDT                              │
│ Market change                          │ 2.89%                                     │
│ Total trade volume                     │ 34309.567 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 5.35%                            │
│ Worst Pair                             │ ETH/USDT -0.34%                           │
│ Best trade                             │ SOL/USDT 26.24%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 37.239 USDT                               │
│ Worst day                              │ -14.946 USDT                              │
│ Days win/draw/lose                     │ 35 / 852 / 58                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:01            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 988.653 USDT / 1114.111 USDT              │
│ Max % of account underwater            │ 4.26%                                     │
│ Absolute drawdown                      │ 46.645 USDT (4.26%)                       │
│ Drawdown duration                      │ 308 days 00:00:00                         │
│ Profit at drawdown start               │ 94.696 USDT                               │
│ Profit at drawdown end                 │ 48.051 USDT                               │
│ Drawdown start                         │ 2025-10-07 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 986.676 USDT / 1130.471 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-09-18 16:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 5.59%                                     │
│ Absolute drawdown (wallet balance)     │ 63.2 USDT (5.59%)                         │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 130.471 USDT                              │
│ Profit at drawdown end                 │ 67.271 USDT                               │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.50                                      │
│ Sortino (daily wallet balance)         │ 0.51                                      │
│ Calmar (daily wallet balance)          │ 2.65                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.48 │          72.989 │          7.3 │ 3 days, 19:42:00 │   52     0    82  38.8 │ 46.645 USDT  4.26% │
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
