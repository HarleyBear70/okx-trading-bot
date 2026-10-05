# More coins for SP-12 v4 (job 2d)

Run 2026-10-05. Rules fixed beforehand in research/COINS_PLAN.md. bot.py as it is now (0.5% risk, 0.1% fee each side). Script: research/coins_test.py.

## Step 1 (pick, data to end of 2021) and step 2 (check, 2022-now)

| Coin | Pick: trades | Win % | Return | Max DD | PF | Picked? | Check: trades | Win % | Return | Max DD | PF | Passed? |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| LTC | 109 | 30% | +7.6% | -5.1% | 1.24 | no | - | | | |  | - |
| DOGE | 31 | 35% | +35.8% | -14.6% | 5.04 | no | - | | | |  | - |
| XLM | 43 | 37% | +5.5% | -4.4% | 1.52 | yes | 70 | 37% | +8.2% | -3.3% | 1.48 | yes |
| ADA | 37 | 43% | +5.7% | -2.9% | 1.69 | yes | 46 | 24% | -3.4% | -8.5% | 0.75 | no |
| BNB | 64 | 41% | +9.6% | -2.7% | 1.68 | yes | 132 | 36% | +3.0% | -6.2% | 1.10 | yes |
| LINK | 26 | 27% | +0.2% | -4.1% | 1.02 | no | - | | | |  | - |
| BCH | 28 | 39% | +2.4% | -3.6% | 1.30 | no | - | | | |  | - |
| AVAX | 3 | 33% | +0.9% | -0.8% | 2.81 | no | - | | | |  | - |
| SUI | no data | | | |  | no | - | | | |  | - |
| LUNA | 11 | 27% | +1.1% | -1.8% | 1.42 | no | - | | | |  | - |
| FTT | 38 | 39% | +1.7% | -6.7% | 1.16 | no | - | | | |  | - |

Passed both steps: XLM, BNB

## Step 3: the v4 bot as it trades (one shared $1,000, max 3 open)

| Coins | Period | Trades | Win % | Return | Max DD | PF |
|---|---|---|---|---|---|---|
| BTC ETH XRP | Full (2018-05-now) | 493 | 35% | +55.4% | -9.9% | 1.34 |
| BTC ETH XRP | 2022-now (out-of-sample) | 311 | 36% | +20.0% | -9.9% | 1.23 |
| BTC ETH XRP XLM BNB | Full (2018-05-now) | 735 | 36% | +93.2% | -10.2% | 1.35 |
| BTC ETH XRP XLM BNB | 2022-now (out-of-sample) | 461 | 36% | +28.4% | -10.2% | 1.23 |
