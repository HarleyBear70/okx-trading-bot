# Freqtrade backtest results

Updated 2026-10-05 18:16 UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee. Exits and risk follow each bot's live settings in bot.py: no half sell at +2R on SP-12 v4 and Trend Rider (since Oct 5 2026), risk 0.4% on SP-12 v4 and 0.5% on the rest. **Step-ups off** risks that every trade; **Step-ups on** raises it by RISK_STEPS as the balance grows (back to base if the balance falls 5% from its best).

## SP12v4: old half sell at +2R vs live rules (no half sell)

| | Old: sell half at +2R | Live: no half sell |
|---|---|---|
| Trades | 182 / 0.19 | 182 / 0.19 |
| Final balance | 1207.649 USDT | 1448.485 USDT |
| Total profit % | 20.76% | 44.85% |
| CAGR % | 7.53% | 15.33% |
| Win / draw / loss, win % | 75 / 0 / 107, 41.2% | 71 / 0 / 111, 39.0% |
| Profit factor | 1.50 | 1.96 |
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1207.649 USDT                             │
│ Absolute profit                        │ 207.649 USDT                              │
│ Total profit %                         │ 20.76%                                    │
│ CAGR %                                 │ 7.53%                                     │
│ Sharpe (closed trades)                 │ 0.37                                      │
│ Sortino (closed trades)                │ 2.13                                      │
│ Calmar (closed trades)                 │ 7.46                                      │
│ SQN                                    │ 1.34                                      │
│ Mean profit p-value                    │ 0.181                                     │
│ Profit factor                          │ 1.50                                      │
│ Expectancy (Ratio)                     │ 1.14 (0.29)                               │
│ Avg. daily profit                      │ 0.219 USDT                                │
│ Avg. stake amount                      │ 174.218 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 72854.873 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 9.88%                            │
│ Worst Pair                             │ BTC/USDT 3.66%                            │
│ Best trade                             │ XRP/USDT 82.34%                           │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 99.89 USDT                                │
│ Worst day                              │ -11.33 USDT                               │
│ Days win/draw/lose                     │ 50 / 815 / 80                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 11:31           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:33            │
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
│ Sharpe (daily wallet balance)          │ 1.00                                      │
│ Sortino (daily wallet balance)         │ 1.28                                      │
│ Calmar (daily wallet balance)          │ 6.36                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                         STRATEGY SUMMARY                                                          
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃         Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         0.60 │         207.649 │        20.76 │ 2 days, 2:01:00 │   75     0   107  41.2 │ 69.4 USDT  5.61% │
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1448.485 USDT                             │
│ Absolute profit                        │ 448.485 USDT                              │
│ Total profit %                         │ 44.85%                                    │
│ CAGR %                                 │ 15.33%                                    │
│ Sharpe (closed trades)                 │ 0.43                                      │
│ Sortino (closed trades)                │ 3.80                                      │
│ Calmar (closed trades)                 │ 15.94                                     │
│ SQN                                    │ 1.57                                      │
│ Mean profit p-value                    │ 0.1181                                    │
│ Profit factor                          │ 1.96                                      │
│ Expectancy (Ratio)                     │ 2.46 (0.59)                               │
│ Avg. daily profit                      │ 0.473 USDT                                │
│ Avg. stake amount                      │ 223.372 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 81919.542 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 25.35%                           │
│ Worst Pair                             │ BTC/USDT 6.29%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 194.651 USDT                              │
│ Worst day                              │ -13.406 USDT                              │
│ Days win/draw/lose                     │ 47 / 815 / 83                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 14:29           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:42            │
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
│ Sharpe (daily wallet balance)          │ 1.35                                      │
│ Sortino (daily wallet balance)         │ 1.96                                      │
│ Calmar (daily wallet balance)          │ 12.82                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         1.26 │         448.485 │        44.85 │ 2 days, 2:01:00 │   71     0   111  39.0 │ 83.073 USDT  5.67% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴────────────────────┘
```

</details>

Both at SP-12 v4's live risk (0.4%) with step-ups off. Without the half sell, the whole position runs to the stop, trailing stop, target or time exit.

## SP12v4

| | Step-ups off | Step-ups on |
|---|---|---|
| Trades | 182 / 0.19 | 179 / 0.19 |
| Final balance | 1448.485 USDT | 1358.721 USDT |
| Total profit % | 44.85% | 35.87% |
| CAGR % | 15.33% | 12.53% |
| Win / draw / loss, win % | 71 / 0 / 111, 39.0% | 71 / 0 / 108, 39.7% |
| Profit factor | 1.96 | 1.56 |
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
│ Backtesting to                         │ 2026-10-05 12:00:00                       │
│ Trading Mode                           │ Spot                                      │
│ Max open trades                        │ 3                                         │
│                                        │                                           │
│ Total/Daily Avg Trades                 │ 182 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1448.485 USDT                             │
│ Absolute profit                        │ 448.485 USDT                              │
│ Total profit %                         │ 44.85%                                    │
│ CAGR %                                 │ 15.33%                                    │
│ Sharpe (closed trades)                 │ 0.43                                      │
│ Sortino (closed trades)                │ 3.80                                      │
│ Calmar (closed trades)                 │ 15.94                                     │
│ SQN                                    │ 1.57                                      │
│ Mean profit p-value                    │ 0.1181                                    │
│ Profit factor                          │ 1.96                                      │
│ Expectancy (Ratio)                     │ 2.46 (0.59)                               │
│ Avg. daily profit                      │ 0.473 USDT                                │
│ Avg. stake amount                      │ 223.372 USDT                              │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 81919.542 USDT                            │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 25.35%                           │
│ Worst Pair                             │ BTC/USDT 6.29%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 194.651 USDT                              │
│ Worst day                              │ -13.406 USDT                              │
│ Days win/draw/lose                     │ 47 / 815 / 83                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 14:29           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:42            │
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
│ Sharpe (daily wallet balance)          │ 1.35                                      │
│ Sortino (daily wallet balance)         │ 1.96                                      │
│ Calmar (daily wallet balance)          │ 12.82                                     │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                          STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    182 │         1.26 │         448.485 │        44.85 │ 2 days, 2:01:00 │   71     0   111  39.0 │ 83.073 USDT  5.67% │
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
│ Total/Daily Avg Trades                 │ 179 / 0.19                                │
│ Starting balance                       │ 1000 USDT                                 │
│ Final balance                          │ 1358.721 USDT                             │
│ Absolute profit                        │ 358.721 USDT                              │
│ Total profit %                         │ 35.87%                                    │
│ CAGR %                                 │ 12.53%                                    │
│ Sharpe (closed trades)                 │ 0.32                                      │
│ Sortino (closed trades)                │ 1.20                                      │
│ Calmar (closed trades)                 │ 7.35                                      │
│ SQN                                    │ 1.20                                      │
│ Mean profit p-value                    │ 0.2323                                    │
│ Profit factor                          │ 1.56                                      │
│ Expectancy (Ratio)                     │ 2.00 (0.34)                               │
│ Avg. daily profit                      │ 0.378 USDT                                │
│ Avg. stake amount                      │ 324.58 USDT                               │
│ Market change                          │ 57.34%                                    │
│ Total trade volume                     │ 116791.622 USDT                           │
│                                        │                                           │
│ Best Pair                              │ XRP/USDT 21.74%                           │
│ Worst Pair                             │ BTC/USDT 2.86%                            │
│ Best trade                             │ XRP/USDT 158.33%                          │
│ Worst trade                            │ BTC/USDT -4.19%                           │
│ Best day                               │ 219.041 USDT                              │
│ Worst day                              │ -45.125 USDT                              │
│ Days win/draw/lose                     │ 48 / 816 / 81                             │
│ Min/Max/Avg. Duration Winners          │ 0d 08:00 / 13d 16:00 / 3d 14:12           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 5d 20:00 / 1d 02:27            │
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
│ Sharpe (daily wallet balance)          │ 0.98                                      │
│ Sortino (daily wallet balance)         │ 1.06                                      │
│ Calmar (daily wallet balance)          │ 6.09                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                           STRATEGY SUMMARY                                                           
┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃    Avg Duration ┃  Win  Draw  Loss  Win% ┃            Drawdown ┃
┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│   SP12v4 │    179 │         1.30 │         358.721 │        35.87 │ 2 days, 2:09:00 │   71     0   108  39.7 │ 142.692 USDT  9.83% │
└──────────┴────────┴──────────────┴─────────────────┴──────────────┴─────────────────┴────────────────────────┴─────────────────────┘
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
| Final balance | 1137.98 USDT | 1093.505 USDT |
| Total profit % | 13.80% | 9.35% |
| CAGR % | 5.10% | 3.50% |
| Win / draw / loss, win % | 52 / 0 / 82, 38.8% | 52 / 0 / 82, 38.8% |
| Profit factor | 1.52 | 1.30 |
| Max % of account underwater | 4.26% | 4.87% |
| Absolute drawdown | 47.005 USDT (4.26%) | 55.052 USDT (4.79%) |
| Best trade | BTC/USDT 37.16% | BTC/USDT 37.16% |
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
│ Final balance                          │ 1137.98 USDT                              │
│ Absolute profit                        │ 137.98 USDT                               │
│ Total profit %                         │ 13.80%                                    │
│ CAGR %                                 │ 5.10%                                     │
│ Sharpe (closed trades)                 │ 0.30                                      │
│ Sortino (closed trades)                │ 1.49                                      │
│ Calmar (closed trades)                 │ 6.53                                      │
│ SQN                                    │ 1.27                                      │
│ Mean profit p-value                    │ 0.2066                                    │
│ Profit factor                          │ 1.52                                      │
│ Expectancy (Ratio)                     │ 1.03 (0.32)                               │
│ Avg. daily profit                      │ 0.146 USDT                                │
│ Avg. stake amount                      │ 122.553 USDT                              │
│ Market change                          │ 2.89%                                     │
│ Total trade volume                     │ 33048.267 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 9.87%                            │
│ Worst Pair                             │ ETH/USDT 1.18%                            │
│ Best trade                             │ BTC/USDT 37.16%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 54.712 USDT                               │
│ Worst day                              │ -10.735 USDT                              │
│ Days win/draw/lose                     │ 33 / 852 / 60                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:01            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 974.49 USDT / 1158.755 USDT               │
│ Max % of account underwater            │ 4.26%                                     │
│ Absolute drawdown                      │ 47.005 USDT (4.26%)                       │
│ Drawdown duration                      │ 308 days 00:00:00                         │
│ Profit at drawdown start               │ 103.367 USDT                              │
│ Profit at drawdown end                 │ 56.363 USDT                               │
│ Drawdown start                         │ 2025-10-07 12:00:00                       │
│ Drawdown end                           │ 2026-08-11 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 974.469 USDT / 1191.684 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-11-05 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 5.14%                                     │
│ Absolute drawdown (wallet balance)     │ 59.769 USDT (5.02%)                       │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 191.684 USDT                              │
│ Profit at drawdown end                 │ 131.915 USDT                              │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.74                                      │
│ Sortino (daily wallet balance)         │ 0.81                                      │
│ Calmar (daily wallet balance)          │ 5.57                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.59 │         137.980 │         13.8 │ 3 days, 19:42:00 │   52     0    82  38.8 │ 47.005 USDT  4.26% │
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
│ Final balance                          │ 1093.505 USDT                             │
│ Absolute profit                        │ 93.505 USDT                               │
│ Total profit %                         │ 9.35%                                     │
│ CAGR %                                 │ 3.50%                                     │
│ Sharpe (closed trades)                 │ 0.20                                      │
│ Sortino (closed trades)                │ 0.65                                      │
│ Calmar (closed trades)                 │ 3.93                                      │
│ SQN                                    │ 0.84                                      │
│ Mean profit p-value                    │ 0.405                                     │
│ Profit factor                          │ 1.30                                      │
│ Expectancy (Ratio)                     │ 0.70 (0.19)                               │
│ Avg. daily profit                      │ 0.099 USDT                                │
│ Avg. stake amount                      │ 133.727 USDT                              │
│ Market change                          │ 2.89%                                     │
│ Total trade volume                     │ 36004.271 USDT                            │
│                                        │                                           │
│ Best Pair                              │ BTC/USDT 7.61%                            │
│ Worst Pair                             │ ETH/USDT 0.61%                            │
│ Best trade                             │ BTC/USDT 37.16%                           │
│ Worst trade                            │ SOL/USDT -8.92%                           │
│ Best day                               │ 54.712 USDT                               │
│ Worst day                              │ -16.051 USDT                              │
│ Days win/draw/lose                     │ 33 / 852 / 60                             │
│ Min/Max/Avg. Duration Winners          │ 1d 12:00 / 19d 20:00 / 5d 20:05           │
│ Min/Max/Avg. Duration Losers           │ 0d 00:00 / 9d 04:00 / 2d 13:01            │
│ Max Consecutive Wins / Loss            │ 4 / 9                                     │
│ Rejected Entry signals                 │ 0                                         │
│ Entry/Exit Timeouts                    │ 0 / 0                                     │
│                                        │                                           │
│ Min/Max balance (closed trades)        │ 974.49 USDT / 1148.557 USDT               │
│ Max % of account underwater            │ 4.87%                                     │
│ Absolute drawdown                      │ 55.052 USDT (4.79%)                       │
│ Drawdown duration                      │ 35 days 16:00:00                          │
│ Profit at drawdown start               │ 148.557 USDT                              │
│ Profit at drawdown end                 │ 93.505 USDT                               │
│ Drawdown start                         │ 2026-08-30 20:00:00                       │
│ Drawdown end                           │ 2026-10-05 12:00:00                       │
│                                        │                                           │
│ Wallet based Metrics                   │                                           │
│ Min/Max balance (wallet balance)       │ 974.469 USDT / 1181.195 USDT              │
│ Min/Max balance dates (wallet balance) │ 2024-11-05 20:00:00 / 2026-08-22 04:00:00 │
│ Max % of account underwater (balance)  │ 7.92%                                     │
│ Absolute drawdown (wallet balance)     │ 93.518 USDT (7.92%)                       │
│ Drawdown duration                      │ 41 days 16:00:00                          │
│ Profit at drawdown start               │ 181.195 USDT                              │
│ Profit at drawdown end                 │ 87.677 USDT                               │
│ Drawdown start                         │ 2026-08-22 04:00:00                       │
│ Drawdown end                           │ 2026-10-02 20:00:00                       │
│ Sharpe (daily wallet balance)          │ 0.51                                      │
│ Sortino (daily wallet balance)         │ 0.52                                      │
│ Calmar (daily wallet balance)          │ 2.40                                      │
└────────────────────────────────────────┴───────────────────────────────────────────┘

                                                            STRATEGY SUMMARY                                                            
┏━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃   Strategy ┃ Trades ┃ Avg Profit % ┃ Tot Profit USDT ┃ Tot Profit % ┃     Avg Duration ┃  Win  Draw  Loss  Win% ┃           Drawdown ┃
┡━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ TrendRider │    134 │         0.59 │          93.505 │         9.35 │ 3 days, 19:42:00 │   52     0    82  38.8 │ 55.052 USDT  4.79% │
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
