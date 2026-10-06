# Bot report card

Generated 2026-10-06 by research/report_card.py: bot.py's own code replayed on 2018-05 to now at the real OKX fee (0.35% per buy and per sell), each bot with its live settings (Trend Rider without its fear filter). A backtest is the best case; live results will be a bit worse. Trades still open at the end are valued at entry price where a coin's saved history stops early (ETH ends 2026-08-31), so totals can be a few points below the research numbers (e.g. Donchian +148% here vs +154% with open trades closed at their last price).

| Bot | Total | Per year | Worst drop | Longest time below a high | Months up | Years up | Best year | Worst year | Worst month | Trades a year | Win % | PF |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Trend Rider (demo) | +134% | +11% | -9.6% | 711 days | 47% | 78% | 2023 +22% | 2022 -4% | -2.8% | 83 | 35% | 1.71 |
| Donchian Trend (demo) | +148% | +11% | -9.7% | 790 days | 37% | 67% | 2021 +41% | 2022 -4% | -3.7% | 27 | 35% | 3.30 |
| NNFX Aroon (demo) | +45% | +5% | -7.6% | 818 days | 47% | 78% | 2024 +14% | 2018 -4% | -2.3% | 23 | 59% | 2.00 |
| Follow Line (paper) | +251% | +16% | -10.0% | 793 days | 39% | 67% | 2021 +93% | 2022 -6% | -4.7% | 28 | 38% | 3.89 |
| Double Bottom (paper) | +56% | +5% | -7.5% | 790 days | 32% | 67% | 2020 +22% | 2026 -5% | -4.1% | 9 | 49% | 2.77 |
| BTC Protected Hold (paper) | +1907% | +43% | -41.2% | 755 days | 37% | 67% | 2020 +163% | 2022 -24% | -19.1% | 7 | 20% | 2.25 |
| All 3 demo bots together | +109% | +9% | -7.4% | 783 days | 46% | 78% | 2021 +19% | 2022 -4% | -2.2% | - | - | - |

## Year by year

| Bot | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|
| Trend Rider (demo) | -2% | +13% | +18% | +14% | -4% | +22% | +21% | +8% | +2% |
| Donchian Trend (demo) | -2% | +6% | +22% | +41% | -4% | +20% | +16% | +7% | -3% |
| NNFX Aroon (demo) | -4% | +9% | +12% | +2% | -3% | +6% | +14% | +2% | +2% |
| Follow Line (paper) | -4% | +8% | +27% | +93% | -6% | +22% | +18% | +4% | -1% |
| Double Bottom (paper) | -1% | +0% | +22% | +6% | -3% | +9% | +12% | +8% | -5% |
| BTC Protected Hold (paper) | -17% | +124% | +163% | +73% | -24% | +76% | +59% | -3% | +13% |
| All 3 demo bots together | -2% | +9% | +17% | +19% | -4% | +17% | +17% | +6% | +0% |
