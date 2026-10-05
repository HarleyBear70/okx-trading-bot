# Hold pile test (M3 rotation vs buy-and-hold vs DCA vs dip DCA; covers H4)

Contenders and decision rules fixed beforehand in research/HOLD_PLAN.md. Daily closes, Monday trades, 0.1% fee. Return, max DD, worst year and time underwater are on a time-weighted unit value, so weekly deposits don't count as gains. Script: research/hold_test.py.

## 2018-05 to now

| Contender | Return | Max DD | Return / DD | Worst year | Days underwater | Longest underwater | Paid in | Final value | Value / paid | Avg price BTC | Avg price XRP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Buy-and-hold BTC ($1,000) | +739% | -77% | 9.65 | -64% (2022) | 97% | 846 days | $1,000 | $8,127 | 8.13 | $9669 | - |
| Buy-and-hold 50/50 BTC+XRP ($1,000) | +406% | -77% | 5.31 | -63% (2022) | 98% | 1306 days | $1,000 | $4,861 | 4.86 | $9669 | $0.866 |
| M3 rotation ($1,000) | +287% | -39% | 7.39 | -16% (2019) | 86% | 918 days | $1,000 | $3,864 | 3.86 | - | - |
| Plain DCA $5 BTC + $5 XRP weekly | +373% | -78% | 4.79 | -62% (2022) | 98% | 1310 days | $4350 | $16,616 | 3.82 | $16531 | $0.478 |
| Dip DCA (2x when 20% below 200-day) | +420% | -77% | 5.42 | -62% (2022) | 98% | 1310 days | $5210 | $21,530 | 4.13 | $14798 | $0.466 |
| M3 rotation, $10 weekly | +287% | -39% | 7.39 | -16% (2019) | 86% | 918 days | $4350 | $9,869 | 2.27 | - | - |

## 1st half (2018-05 to 2021)

| Contender | Return | Max DD | Return / DD | Worst year | Days underwater | Longest underwater | Paid in | Final value | Value / paid | Avg price BTC | Avg price XRP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Buy-and-hold BTC ($1,000) | +410% | -66% | 6.23 | -60% (2018) | 96% | 485 days | $1,000 | $4,936 | 4.94 | $9669 | - |
| Buy-and-hold 50/50 BTC+XRP ($1,000) | +208% | -66% | 3.15 | -59% (2018) | 97% | 919 days | $1,000 | $2,959 | 2.96 | $9669 | $0.866 |
| M3 rotation ($1,000) | +118% | -39% | 3.05 | -16% (2019) | 71% | 509 days | $1,000 | $2,180 | 2.18 | - | - |
| Plain DCA $5 BTC + $5 XRP weekly | +186% | -67% | 2.78 | -58% (2018) | 97% | 924 days | $1910 | $7,249 | 3.80 | $9321 | $0.344 |
| Dip DCA (2x when 20% below 200-day) | +214% | -66% | 3.26 | -57% (2018) | 97% | 508 days | $2245 | $9,462 | 4.21 | $8290 | $0.326 |
| M3 rotation, $10 weekly | +118% | -39% | 3.05 | -16% (2019) | 71% | 509 days | $1910 | $3,682 | 1.93 | - | - |

## 2nd half (2022 to now)

| Contender | Return | Max DD | Return / DD | Worst year | Days underwater | Longest underwater | Paid in | Final value | Value / paid | Avg price BTC | Avg price XRP |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Buy-and-hold BTC ($1,000) | +69% | -67% | 1.04 | -64% (2022) | 97% | 682 days | $1,000 | $1,660 | 1.66 | $47333 | - |
| Buy-and-hold 50/50 BTC+XRP ($1,000) | +67% | -64% | 1.06 | -62% (2022) | 98% | 703 days | $1,000 | $1,633 | 1.63 | $47333 | $0.859 |
| M3 rotation ($1,000) | +78% | -34% | 2.28 | -3% (2026) | 75% | 327 days | $1,000 | $1,777 | 1.78 | - | - |
| Plain DCA $5 BTC + $5 XRP weekly | +75% | -64% | 1.17 | -61% (2022) | 98% | 701 days | $2440 | $4,739 | 1.94 | $41900 | $0.687 |
| Dip DCA (2x when 20% below 200-day) | +77% | -64% | 1.21 | -61% (2022) | 98% | 701 days | $2965 | $6,020 | 2.03 | $38719 | $0.679 |
| M3 rotation, $10 weekly | +78% | -34% | 2.28 | -3% (2026) | 75% | 327 days | $2440 | $3,343 | 1.37 | - | - |

## Verdicts (rules from HOLD_PLAN.md)

- M3 for the hold pile: not recommended (needs a smaller max DD than buy-and-hold BTC and a higher return / DD in both halves)
- Dip DCA over plain DCA: RECOMMENDED (needs a lower average price for BTC and XRP and no lower value / paid in, in both halves)
