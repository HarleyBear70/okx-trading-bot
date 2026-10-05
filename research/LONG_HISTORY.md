# Long-history stress test (job 2b)

Run 2026-10-05. bot.py as it is now: 0.5% risk per trade, 0.1% fee each side, bot.py's own paper-mode functions bar by bar. One coin at a time, fresh $1,000 each period. Max DD is mark-to-market at each 4H close. Script: research/long_history.py.

## Data

| Coin | Source | Pair | First 4H candle | Last |
|---|---|---|---|---|
| ADA | binance | ADAUSDT | 2018-04-17 | 2026-08-31 |
| AVAX | bitfinex | tAVAX:USD | 2020-09-23 | 2026-10-05 |
| BCH | binance | BCHUSDT | 2019-11-28 | 2026-08-31 |
| BNB | binance | BNBUSDT | 2017-11-06 | 2026-08-31 |
| BTC | bitfinex | tBTCUSD | 2013-01-14 | 2026-10-05 |
| DOGE | binance | DOGEUSDT | 2019-07-05 | 2026-08-31 |
| ETH | bitfinex | tETHUSD | 2016-03-09 | 2026-10-05 |
| FTT | binance | FTTUSDT | 2019-12-20 | 2026-08-31 |
| LINK | binance | LINKUSDT | 2019-01-16 | 2026-08-31 |
| LTC | bitfinex | tLTCUSD | 2013-05-19 | 2026-10-05 |
| LUNA | binance | LUNAUSDT | 2020-08-21 | 2022-05-12 |
| SOL | binance | SOLUSDT | 2020-08-11 | 2026-08-31 |
| SUI | bitfinex | tSUIUSD | 2023-05-03 | 2026-10-05 |
| XAUT | bitfinex | tXAUT:USD | 2020-01-24 | 2026-10-05 |
| XLM | bitfinex | tXLMUSD | 2018-05-01 | 2026-10-05 |
| XRP | bitfinex | tXRPUSD | 2017-05-19 | 2026-10-05 |

LUNA is the original Terra coin only, cut at 2022-05-13 (Binance later reused the ticker for Terra 2.0). Binance coins end at the last full month. SUI's first Bitfinex candle (open 10,000) was dropped as a listing glitch.

A period that starts before a coin's first candle starts at that first candle (see the B&H return for that partial period). Early years are thin, wild markets: a stress test, not proof.

## Coins the bots trade now (in-sample)

| Bot | Coin | Period | Trades | Win % | Return | Max DD | PF | B&H return | B&H DD | Best month share of profit | Longest losing streak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SP-12 v4 | BTC | 2013-14 bubble + crash | 36 | 33% | +4.2% | -5.9% | 1.40 | +2117% | -78% | 63% (2014-11) | 9 |
| SP-12 v4 | BTC | 2015-17 bull | 80 | 49% | +28.3% | -4.1% | 2.52 | +4169% | -43% | 21% (2016-12) | 5 |
| SP-12 v4 | BTC | 2018 crash | 17 | 29% | -0.2% | -2.3% | 0.95 | -72% | -81% | - | 5 |
| SP-12 v4 | BTC | 2019-21 bull | 68 | 40% | +22.7% | -3.9% | 2.36 | +1106% | -66% | 15% (2019-06) | 7 |
| SP-12 v4 | BTC | 2022 crash | 13 | 38% | +0.5% | -2.4% | 1.20 | -64% | -67% | 189% (2022-12) | 7 |
| SP-12 v4 | BTC | 2023-now | 104 | 42% | +10.5% | -5.7% | 1.39 | +420% | -53% | 37% (2024-11) | 6 |
| SP-12 v4 | ETH | 2015-17 bull | 23 | 39% | +0.2% | -2.5% | 1.03 | +7055% | -71% | 782% (2017-11) | 3 |
| SP-12 v4 | ETH | 2018 crash | 4 | 25% | -0.5% | -1.0% | 0.58 | -82% | -94% | - | 2 |
| SP-12 v4 | ETH | 2019-21 bull | 50 | 32% | +4.6% | -7.6% | 1.35 | +2605% | -70% | 66% (2020-01) | 12 |
| SP-12 v4 | ETH | 2022 crash | 12 | 33% | -1.0% | -2.9% | 0.74 | -67% | -76% | - | 3 |
| SP-12 v4 | ETH | 2023-now | 95 | 32% | +3.0% | -4.1% | 1.13 | +128% | -68% | 114% (2025-07) | 9 |
| SP-12 v4 | XRP | 2015-17 bull | 6 | 17% | +0.6% | -0.8% | 2.14 | +417% | -63% | 188% (2017-10) | 3 |
| SP-12 v4 | XRP | 2018 crash | 5 | 40% | +0.3% | -1.1% | 1.31 | -82% | -92% | 281% (2018-12) | 2 |
| SP-12 v4 | XRP | 2019-21 bull | 43 | 30% | +2.6% | -2.9% | 1.25 | +130% | -76% | 67% (2020-04) | 5 |
| SP-12 v4 | XRP | 2022 crash | 13 | 38% | -2.2% | -2.7% | 0.47 | -59% | -67% | - | 4 |
| SP-12 v4 | XRP | 2023-now | 74 | 32% | +9.3% | -4.8% | 1.39 | +348% | -73% | 134% (2024-11) | 8 |
| SP-12 v2 | ETH | 2015-17 bull | 43 | 28% | -2.2% | -4.0% | 0.84 | +7055% | -71% | - | 6 |
| SP-12 v2 | ETH | 2018 crash | 14 | 14% | -4.4% | -4.9% | 0.17 | -82% | -94% | - | 10 |
| SP-12 v2 | ETH | 2019-21 bull | 125 | 30% | +0.2% | -8.5% | 1.01 | +2605% | -70% | 1603% (2019-02) | 10 |
| SP-12 v2 | ETH | 2022 crash | 31 | 26% | -1.3% | -3.4% | 0.86 | -67% | -76% | - | 5 |
| SP-12 v2 | ETH | 2023-now | 156 | 29% | +3.2% | -4.4% | 1.08 | +128% | -68% | 84% (2025-08) | 12 |
| SP-12 v2 | SOL | 2019-21 bull | 48 | 23% | -7.3% | -10.0% | 0.58 | +5865% | -75% | - | 12 |
| SP-12 v2 | SOL | 2022 crash | 24 | 29% | -0.2% | -2.7% | 0.97 | -94% | -95% | - | 6 |
| SP-12 v2 | SOL | 2023-now | 171 | 30% | +6.4% | -8.8% | 1.14 | +934% | -78% | 65% (2024-03) | 18 |
| SP-12 v2 | XAUT | 2019-21 bull | 57 | 39% | -1.3% | -6.0% | 0.88 | +13% | -17% | - | 6 |
| SP-12 v2 | XAUT | 2022 crash | 30 | 27% | -3.5% | -5.3% | 0.57 | -1% | -21% | - | 5 |
| SP-12 v2 | XAUT | 2023-now | 122 | 43% | +14.5% | -3.5% | 1.59 | +129% | -29% | 21% (2026-01) | 6 |
| Trend Rider | BTC | 2013-14 bubble + crash | 34 | 56% | +10.1% | -1.5% | 3.15 | +2117% | -78% | 28% (2013-04) | 4 |
| Trend Rider | BTC | 2015-17 bull | 78 | 49% | +28.3% | -2.0% | 3.67 | +4169% | -43% | 20% (2016-06) | 5 |
| Trend Rider | BTC | 2018 crash | 8 | 25% | -0.8% | -1.5% | 0.33 | -72% | -81% | - | 5 |
| Trend Rider | BTC | 2019-21 bull | 72 | 42% | +12.7% | -3.3% | 1.79 | +1106% | -66% | 27% (2019-04) | 5 |
| Trend Rider | BTC | 2022 crash | 6 | 17% | -0.7% | -1.8% | 0.56 | -64% | -67% | - | 5 |
| Trend Rider | BTC | 2023-now | 78 | 46% | +20.4% | -3.4% | 2.34 | +420% | -53% | 28% (2023-01) | 7 |
| Trend Rider | ETH | 2015-17 bull | 41 | 41% | +13.2% | -2.1% | 2.97 | +7055% | -71% | 34% (2017-03) | 4 |
| Trend Rider | ETH | 2018 crash | 11 | 36% | -0.5% | -1.9% | 0.82 | -82% | -94% | - | 3 |
| Trend Rider | ETH | 2019-21 bull | 82 | 35% | +12.5% | -2.8% | 1.73 | +2605% | -70% | 49% (2020-08) | 8 |
| Trend Rider | ETH | 2022 crash | 12 | 17% | -2.2% | -2.8% | 0.34 | -67% | -76% | - | 5 |
| Trend Rider | ETH | 2023-now | 75 | 25% | +6.8% | -5.1% | 1.45 | +128% | -68% | 55% (2026-08) | 17 |
| Trend Rider | SOL | 2019-21 bull | 31 | 42% | +6.1% | -1.8% | 2.17 | +5865% | -75% | 44% (2021-08) | 4 |
| Trend Rider | SOL | 2022 crash | 5 | 20% | -0.2% | -0.8% | 0.27 | -94% | -95% | - | 3 |
| Trend Rider | SOL | 2023-now | 61 | 44% | +14.5% | -3.5% | 2.42 | +934% | -78% | 34% (2023-11) | 6 |
| Trend Rider | BNB | 2015-17 bull | 0 | 0% | +0.0% | 0.0% | 0.00 | +469% | -39% | - | 0 |
| Trend Rider | BNB | 2018 crash | 15 | 33% | +1.0% | -2.5% | 1.32 | -29% | -83% | 169% (2018-01) | 3 |
| Trend Rider | BNB | 2019-21 bull | 73 | 45% | +19.8% | -2.3% | 2.66 | +8265% | -78% | 32% (2021-02) | 5 |
| Trend Rider | BNB | 2022 crash | 10 | 30% | -0.2% | -2.1% | 0.92 | -52% | -65% | - | 3 |
| Trend Rider | BNB | 2023-now | 75 | 35% | +6.0% | -4.5% | 1.35 | +181% | -60% | 44% (2024-02) | 8 |
| Trend Rider | SUI | 2023-now | 53 | 38% | +2.3% | -3.5% | 1.21 | -5% | -88% | 69% (2024-09) | 7 |
| Trend Rider (gold, pivot 3) | XAUT | 2019-21 bull | 39 | 23% | -3.0% | -5.6% | 0.73 | +13% | -17% | - | 10 |
| Trend Rider (gold, pivot 3) | XAUT | 2022 crash | 16 | 31% | -1.4% | -2.8% | 0.65 | -1% | -21% | - | 3 |
| Trend Rider (gold, pivot 3) | XAUT | 2023-now | 148 | 34% | +3.3% | -10.8% **>10%** | 1.10 | +129% | -29% | 100% (2026-01) | 13 |

## Coins the bots were never built for (out-of-sample)

| Bot | Coin | Period | Trades | Win % | Return | Max DD | PF | B&H return | B&H DD | Best month share of profit | Longest losing streak |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SP-12 v4 | LTC | 2013-14 bubble + crash | 10 | 20% | -1.8% | -4.0% | 0.45 | -12% | -95% | - | 7 |
| SP-12 v4 | LTC | 2015-17 bull | 59 | 32% | +7.6% | -5.1% | 1.44 | +8093% | -69% | 59% (2015-06) | 9 |
| SP-12 v4 | LTC | 2018 crash | 5 | 40% | +2.3% | -1.0% | 5.22 | -86% | -92% | 80% (2018-04) | 2 |
| SP-12 v4 | LTC | 2019-21 bull | 35 | 29% | -0.5% | -4.4% | 0.95 | +372% | -79% | - | 7 |
| SP-12 v4 | LTC | 2022 crash | 16 | 38% | -0.3% | -1.7% | 0.90 | -52% | -72% | - | 4 |
| SP-12 v4 | LTC | 2023-now | 82 | 28% | -10.9% | -13.2% **>10%** | 0.55 | -0% | -72% | - | 9 |
| SP-12 v4 | DOGE | 2019-21 bull | 31 | 35% | +35.8% | -14.6% **>10%** | 5.04 | +3693% | -78% | 94% (2021-04) | 5 |
| SP-12 v4 | DOGE | 2022 crash | 7 | 29% | -0.7% | -2.5% | 0.68 | -59% | -74% | - | 4 |
| SP-12 v4 | DOGE | 2023-now | 41 | 39% | +3.9% | -2.6% | 1.48 | +18% | -85% | 50% (2023-12) | 5 |
| SP-12 v4 | XLM | 2018 crash | 5 | 40% | +1.0% | -1.0% | 2.91 | -74% | -79% | 152% (2018-11) | 2 |
| SP-12 v4 | XLM | 2019-21 bull | 38 | 37% | +4.4% | -4.4% | 1.45 | +136% | -79% | 61% (2020-04) | 13 |
| SP-12 v4 | XLM | 2022 crash | 7 | 43% | +1.1% | -2.5% | 1.52 | -73% | -76% | 151% (2022-03) | 3 |
| SP-12 v4 | XLM | 2023-now | 63 | 37% | +7.0% | -3.3% | 1.48 | +215% | -77% | 89% (2025-07) | 6 |
| SP-12 v4 | ADA | 2018 crash | 3 | 0% | -1.1% | -1.1% | 0.00 | -84% | -93% | - | 3 |
| SP-12 v4 | ADA | 2019-21 bull | 34 | 47% | +6.8% | -2.9% | 1.95 | +3124% | -79% | 32% (2020-01) | 5 |
| SP-12 v4 | ADA | 2022 crash | 3 | 67% | +1.2% | -1.0% | 31245.73 | -81% | -85% | 60% (2022-08) | 1 |
| SP-12 v4 | ADA | 2023-now | 43 | 21% | -4.6% | -8.5% | 0.67 | -20% | -89% | - | 9 |
| SP-12 v4 | BNB | 2015-17 bull | 0 | 0% | +0.0% | 0.0% | 0.00 | +469% | -39% | - | 0 |
| SP-12 v4 | BNB | 2018 crash | 11 | 27% | -0.3% | -2.5% | 0.91 | -29% | -83% | - | 5 |
| SP-12 v4 | BNB | 2019-21 bull | 53 | 43% | +10.1% | -2.7% | 1.92 | +8265% | -78% | 35% (2019-02) | 5 |
| SP-12 v4 | BNB | 2022 crash | 21 | 33% | -1.6% | -3.8% | 0.75 | -52% | -65% | - | 5 |
| SP-12 v4 | BNB | 2023-now | 111 | 37% | +4.7% | -6.0% | 1.19 | +181% | -60% | 66% (2025-09) | 10 |
| SP-12 v4 | LINK | 2019-21 bull | 26 | 27% | +0.2% | -4.1% | 1.02 | +3543% | -74% | 1401% (2019-10) | 7 |
| SP-12 v4 | LINK | 2022 crash | 7 | 29% | -0.5% | -3.1% | 0.83 | -71% | -81% | - | 5 |
| SP-12 v4 | LINK | 2023-now | 61 | 38% | +6.0% | -5.2% | 1.38 | +103% | -76% | 66% (2026-08) | 6 |
| SP-12 v4 | BCH | 2019-21 bull | 28 | 39% | +2.4% | -3.6% | 1.30 | +95% | -75% | 82% (2020-02) | 5 |
| SP-12 v4 | BCH | 2022 crash | 16 | 6% | -4.6% | -5.3% | 0.03 | -77% | -80% | - | 14 |
| SP-12 v4 | BCH | 2023-now | 67 | 24% | -7.6% | -7.7% | 0.57 | +155% | -74% | - | 12 |
| SP-12 v4 | AVAX | 2019-21 bull | 3 | 33% | +0.9% | -0.8% | 2.81 | +2506% | -83% | 155% (2021-11) | 2 |
| SP-12 v4 | AVAX | 2022 crash | 10 | 40% | -0.5% | -2.3% | 0.84 | -90% | -91% | - | 4 |
| SP-12 v4 | AVAX | 2023-now | 49 | 37% | +4.9% | -3.0% | 1.40 | +1% | -91% | 63% (2023-01) | 6 |
| SP-12 v4 | SUI | 2023-now | 37 | 32% | +2.9% | -4.3% | 1.27 | -5% | -88% | 103% (2026-05) | 7 |
| SP-12 v4 | LUNA | 2019-21 bull | 11 | 27% | +1.1% | -1.8% | 1.42 | +15735% | -82% | 186% (2020-11) | 4 |
| SP-12 v4 | LUNA | 2022 crash | 3 | 67% | +1.0% | -0.9% | 2.78 | -100% | -100% | 51% (2022-04) | 1 |
| SP-12 v4 | FTT | 2019-21 bull | 38 | 39% | +1.7% | -6.7% | 1.16 | +1872% | -65% | 131% (2021-08) | 9 |
| SP-12 v4 | FTT | 2022 crash | 11 | 64% | +3.1% | -2.1% | 2.82 | -96% | -98% | 51% (2022-03) | 3 |
| SP-12 v4 | FTT | 2023-now | 23 | 17% | -0.4% | -3.0% | 0.93 | -84% | -97% | - | 7 |
| SP-12 v2 | LTC | 2013-14 bubble + crash | 52 | 35% | +5.7% | -5.6% | 1.40 | -12% | -95% | 51% (2014-03) | 11 |
| SP-12 v2 | LTC | 2015-17 bull | 116 | 22% | -11.8% | -13.6% **>10%** | 0.66 | +8093% | -69% | - | 15 |
| SP-12 v2 | LTC | 2018 crash | 16 | 38% | +1.9% | -2.4% | 1.49 | -86% | -92% | 82% (2018-04) | 5 |
| SP-12 v2 | LTC | 2019-21 bull | 115 | 27% | +1.4% | -7.4% | 1.05 | +372% | -79% | 153% (2021-04) | 9 |
| SP-12 v2 | LTC | 2022 crash | 42 | 17% | -7.7% | -8.6% | 0.44 | -52% | -72% | - | 16 |
| SP-12 v2 | LTC | 2023-now | 162 | 18% | -16.7% | -20.1% **>10%** | 0.63 | -0% | -72% | - | 18 |
| SP-12 v2 | DOGE | 2019-21 bull | 81 | 28% | +2.5% | -7.6% | 1.12 | +3693% | -78% | 130% (2021-04) | 16 |
| SP-12 v2 | DOGE | 2022 crash | 28 | 25% | +0.4% | -2.2% | 1.07 | -59% | -74% | 713% (2022-08) | 7 |
| SP-12 v2 | DOGE | 2023-now | 132 | 26% | -6.1% | -9.2% | 0.83 | +18% | -85% | - | 12 |
| SP-12 v2 | XLM | 2018 crash | 13 | 31% | +1.0% | -2.7% | 1.31 | -74% | -79% | 320% (2018-11) | 6 |
| SP-12 v2 | XLM | 2019-21 bull | 116 | 28% | -1.7% | -8.2% | 0.94 | +136% | -79% | - | 12 |
| SP-12 v2 | XLM | 2022 crash | 20 | 35% | +2.0% | -2.6% | 1.46 | -73% | -76% | 82% (2022-03) | 5 |
| SP-12 v2 | XLM | 2023-now | 145 | 26% | -0.9% | -7.7% | 0.97 | +215% | -77% | - | 15 |
| SP-12 v2 | ADA | 2018 crash | 12 | 0% | -6.0% | -6.0% | 0.00 | -84% | -93% | - | 12 |
| SP-12 v2 | ADA | 2019-21 bull | 111 | 32% | +2.3% | -8.7% | 1.07 | +3124% | -79% | 119% (2019-02) | 12 |
| SP-12 v2 | ADA | 2022 crash | 21 | 19% | -2.8% | -3.9% | 0.56 | -81% | -85% | - | 8 |
| SP-12 v2 | ADA | 2023-now | 137 | 20% | -14.6% | -15.5% **>10%** | 0.61 | -20% | -89% | - | 13 |
| SP-12 v2 | BNB | 2015-17 bull | 4 | 50% | +1.1% | -1.1% | 1.98 | +469% | -39% | 100% (2017-12) | 2 |
| SP-12 v2 | BNB | 2018 crash | 34 | 15% | -6.1% | -7.1% | 0.43 | -29% | -83% | - | 14 |
| SP-12 v2 | BNB | 2019-21 bull | 126 | 26% | -1.8% | -6.2% | 0.95 | +8265% | -78% | - | 13 |
| SP-12 v2 | BNB | 2022 crash | 37 | 22% | -2.9% | -5.4% | 0.74 | -52% | -65% | - | 10 |
| SP-12 v2 | BNB | 2023-now | 170 | 32% | +9.4% | -4.9% | 1.23 | +181% | -60% | 42% (2024-11) | 10 |
| SP-12 v2 | LINK | 2019-21 bull | 123 | 25% | -10.4% | -13.7% **>10%** | 0.73 | +3543% | -74% | - | 10 |
| SP-12 v2 | LINK | 2022 crash | 37 | 19% | -5.5% | -7.6% | 0.57 | -71% | -81% | - | 16 |
| SP-12 v2 | LINK | 2023-now | 155 | 26% | -5.9% | -15.2% **>10%** | 0.86 | +103% | -76% | - | 10 |
| SP-12 v2 | BCH | 2019-21 bull | 80 | 29% | +4.5% | -5.9% | 1.22 | +95% | -75% | 36% (2021-05) | 10 |
| SP-12 v2 | BCH | 2022 crash | 39 | 8% | -8.0% | -8.1% | 0.27 | -77% | -80% | - | 18 |
| SP-12 v2 | BCH | 2023-now | 171 | 23% | -12.9% | -13.8% **>10%** | 0.73 | +155% | -74% | - | 12 |
| SP-12 v2 | AVAX | 2019-21 bull | 42 | 31% | +2.4% | -5.2% | 1.22 | +2506% | -83% | 67% (2021-12) | 9 |
| SP-12 v2 | AVAX | 2022 crash | 39 | 28% | -0.1% | -3.4% | 0.99 | -90% | -91% | - | 7 |
| SP-12 v2 | AVAX | 2023-now | 116 | 27% | -3.0% | -7.5% | 0.91 | +1% | -91% | - | 11 |
| SP-12 v2 | SUI | 2023-now | 114 | 23% | -7.9% | -9.0% | 0.75 | -5% | -88% | - | 12 |
| SP-12 v2 | LUNA | 2019-21 bull | 53 | 43% | +11.4% | -2.8% | 1.87 | +15735% | -82% | 29% (2021-02) | 5 |
| SP-12 v2 | LUNA | 2022 crash | 13 | 31% | -1.3% | -1.7% | 0.74 | -100% | -100% | - | 3 |
| SP-12 v2 | FTT | 2019-21 bull | 80 | 32% | +2.6% | -5.3% | 1.11 | +1872% | -65% | 126% (2021-07) | 8 |
| SP-12 v2 | FTT | 2022 crash | 29 | 31% | -0.8% | -3.4% | 0.91 | -96% | -98% | - | 6 |
| SP-12 v2 | FTT | 2023-now | 97 | 25% | -2.2% | -5.4% | 0.91 | -84% | -97% | - | 11 |
| Trend Rider | LTC | 2013-14 bubble + crash | 13 | 38% | +7.7% | -7.8% | 3.08 | -12% | -95% | 131% (2013-11) | 7 |
| Trend Rider | LTC | 2015-17 bull | 49 | 45% | +17.5% | -4.5% | 2.73 | +8093% | -69% | 24% (2015-07) | 11 |
| Trend Rider | LTC | 2018 crash | 7 | 14% | -2.2% | -2.4% | 0.05 | -86% | -92% | - | 5 |
| Trend Rider | LTC | 2019-21 bull | 65 | 34% | +7.6% | -3.1% | 1.50 | +372% | -79% | 29% (2020-08) | 6 |
| Trend Rider | LTC | 2022 crash | 11 | 27% | -1.4% | -2.8% | 0.49 | -52% | -72% | - | 6 |
| Trend Rider | LTC | 2023-now | 68 | 32% | -3.5% | -6.2% | 0.73 | -0% | -72% | - | 11 |
| Trend Rider | DOGE | 2019-21 bull | 39 | 31% | +13.6% | -3.0% | 2.67 | +3693% | -78% | 59% (2021-01) | 6 |
| Trend Rider | DOGE | 2022 crash | 10 | 10% | -1.9% | -2.7% | 0.24 | -59% | -74% | - | 8 |
| Trend Rider | DOGE | 2023-now | 50 | 30% | +1.5% | -3.7% | 1.13 | +18% | -85% | 186% (2024-11) | 5 |
| Trend Rider | XLM | 2018 crash | 7 | 14% | -1.2% | -2.2% | 0.47 | -74% | -79% | - | 5 |
| Trend Rider | XLM | 2019-21 bull | 61 | 34% | -0.6% | -3.5% | 0.95 | +136% | -79% | - | 6 |
| Trend Rider | XLM | 2022 crash | 5 | 40% | -0.4% | -1.9% | 0.68 | -73% | -76% | - | 3 |
| Trend Rider | XLM | 2023-now | 52 | 33% | +22.0% | -8.9% | 3.13 | +215% | -77% | 101% (2024-11) | 6 |
| Trend Rider | ADA | 2018 crash | 0 | 0% | +0.0% | 0.0% | 0.00 | -84% | -93% | - | 0 |
| Trend Rider | ADA | 2019-21 bull | 61 | 46% | +10.5% | -3.0% | 2.04 | +3124% | -79% | 35% (2021-02) | 6 |
| Trend Rider | ADA | 2022 crash | 7 | 0% | -2.1% | -2.3% | 0.00 | -81% | -85% | - | 7 |
| Trend Rider | ADA | 2023-now | 51 | 24% | -0.3% | -4.7% | 0.97 | -20% | -89% | - | 15 |
| Trend Rider | LINK | 2019-21 bull | 78 | 28% | +3.8% | -4.2% | 1.22 | +3543% | -74% | 75% (2020-02) | 8 |
| Trend Rider | LINK | 2022 crash | 10 | 20% | -0.7% | -1.5% | 0.67 | -71% | -81% | - | 5 |
| Trend Rider | LINK | 2023-now | 64 | 33% | +6.4% | -5.1% | 1.45 | +103% | -76% | 72% (2023-11) | 8 |
| Trend Rider | BCH | 2019-21 bull | 41 | 29% | +2.0% | -2.2% | 1.25 | +95% | -75% | 65% (2020-08) | 6 |
| Trend Rider | BCH | 2022 crash | 6 | 0% | -2.5% | -2.6% | 0.00 | -77% | -80% | - | 6 |
| Trend Rider | BCH | 2023-now | 62 | 29% | -2.7% | -6.0% | 0.81 | +155% | -74% | - | 13 |
| Trend Rider | AVAX | 2019-21 bull | 31 | 35% | +9.0% | -3.4% | 2.56 | +2506% | -83% | 64% (2021-08) | 5 |
| Trend Rider | AVAX | 2022 crash | 10 | 10% | -2.3% | -2.3% | 0.26 | -90% | -91% | - | 6 |
| Trend Rider | AVAX | 2023-now | 70 | 33% | -0.0% | -4.2% | 1.00 | +1% | -91% | - | 6 |
| Trend Rider | LUNA | 2019-21 bull | 40 | 38% | +15.9% | -4.0% | 2.61 | +15735% | -82% | 78% (2021-02) | 5 |
| Trend Rider | LUNA | 2022 crash | 7 | 43% | +0.5% | -0.8% | 1.40 | -100% | -100% | 125% (2022-03) | 1 |
| Trend Rider | FTT | 2019-21 bull | 61 | 38% | +5.0% | -4.9% | 1.43 | +1872% | -65% | 67% (2021-01) | 8 |
| Trend Rider | FTT | 2022 crash | 12 | 8% | -0.9% | -1.7% | 0.57 | -96% | -98% | - | 7 |
| Trend Rider | FTT | 2023-now | 29 | 28% | +2.4% | -3.6% | 1.36 | -84% | -97% | 124% (2023-11) | 5 |

## Roll-up

- SP-12 v4, in-sample: 16 coin-periods, 12 profitable (75%), median return +2.6%, median PF 1.31, 0 broke 10% DD
- SP-12 v4, out-of-sample: 36 coin-periods, 22 profitable (61%), median return +1.1%, median PF 1.30, 2 broke 10% DD
- SP-12 v2, in-sample: 11 coin-periods, 4 profitable (36%), median return -1.3%, median PF 0.88, 0 broke 10% DD
- SP-12 v2, out-of-sample: 37 coin-periods, 14 profitable (38%), median return -1.7%, median PF 0.91, 6 broke 10% DD
- Trend Rider, in-sample: 19 coin-periods, 13 profitable (68%), median return +6.1%, median PF 1.45, 0 broke 10% DD
- Trend Rider, out-of-sample: 30 coin-periods, 15 profitable (50%), median return +0.5%, median PF 1.13, 0 broke 10% DD
- Trend Rider (gold, pivot 3), in-sample: 3 coin-periods, 1 profitable (33%), median return -1.4%, median PF 0.73, 1 broke 10% DD

- SP-12 v4 2013-14 bubble + crash: in-sample 1 coin-periods, 1 profitable (100%), median return +4.2%, median PF 1.40, 0 broke 10% DD; out-of-sample 1 coin-periods, 0 profitable (0%), median return -1.8%, median PF 0.45, 0 broke 10% DD
- SP-12 v4 2015-17 bull: in-sample 3 coin-periods, 3 profitable (100%), median return +0.6%, median PF 2.14, 0 broke 10% DD; out-of-sample 1 coin-periods, 1 profitable (100%), median return +7.6%, median PF 1.44, 0 broke 10% DD
- SP-12 v4 2018 crash: in-sample 3 coin-periods, 1 profitable (33%), median return -0.2%, median PF 0.95, 0 broke 10% DD; out-of-sample 4 coin-periods, 2 profitable (50%), median return +1.0%, median PF 2.91, 0 broke 10% DD
- SP-12 v4 2019-21 bull: in-sample 3 coin-periods, 3 profitable (100%), median return +4.6%, median PF 1.35, 0 broke 10% DD; out-of-sample 10 coin-periods, 9 profitable (90%), median return +2.4%, median PF 1.45, 1 broke 10% DD
- SP-12 v4 2022 crash: in-sample 3 coin-periods, 1 profitable (33%), median return -1.0%, median PF 0.74, 0 broke 10% DD; out-of-sample 10 coin-periods, 4 profitable (40%), median return -0.3%, median PF 0.90, 0 broke 10% DD
- SP-12 v4 2023-now: in-sample 3 coin-periods, 3 profitable (100%), median return +9.3%, median PF 1.39, 0 broke 10% DD; out-of-sample 10 coin-periods, 6 profitable (60%), median return +3.9%, median PF 1.27, 1 broke 10% DD
- SP-12 v2 2013-14 bubble + crash: in-sample no trades; out-of-sample 1 coin-periods, 1 profitable (100%), median return +5.7%, median PF 1.40, 0 broke 10% DD
- SP-12 v2 2015-17 bull: in-sample 1 coin-periods, 0 profitable (0%), median return -2.2%, median PF 0.84, 0 broke 10% DD; out-of-sample 2 coin-periods, 1 profitable (50%), median return +1.1%, median PF 1.98, 1 broke 10% DD
- SP-12 v2 2018 crash: in-sample 1 coin-periods, 0 profitable (0%), median return -4.4%, median PF 0.17, 0 broke 10% DD; out-of-sample 4 coin-periods, 2 profitable (50%), median return +1.0%, median PF 1.31, 0 broke 10% DD
- SP-12 v2 2019-21 bull: in-sample 3 coin-periods, 1 profitable (33%), median return -1.3%, median PF 0.88, 0 broke 10% DD; out-of-sample 10 coin-periods, 7 profitable (70%), median return +2.4%, median PF 1.11, 1 broke 10% DD
- SP-12 v2 2022 crash: in-sample 3 coin-periods, 0 profitable (0%), median return -1.3%, median PF 0.86, 0 broke 10% DD; out-of-sample 10 coin-periods, 2 profitable (20%), median return -1.3%, median PF 0.74, 0 broke 10% DD
- SP-12 v2 2023-now: in-sample 3 coin-periods, 3 profitable (100%), median return +6.4%, median PF 1.14, 0 broke 10% DD; out-of-sample 10 coin-periods, 1 profitable (10%), median return -5.9%, median PF 0.86, 4 broke 10% DD
- Trend Rider 2013-14 bubble + crash: in-sample 1 coin-periods, 1 profitable (100%), median return +10.1%, median PF 3.15, 0 broke 10% DD; out-of-sample 1 coin-periods, 1 profitable (100%), median return +7.7%, median PF 3.08, 0 broke 10% DD
- Trend Rider 2015-17 bull: in-sample 2 coin-periods, 2 profitable (100%), median return +28.3%, median PF 3.67, 0 broke 10% DD; out-of-sample 1 coin-periods, 1 profitable (100%), median return +17.5%, median PF 2.73, 0 broke 10% DD
- Trend Rider 2018 crash: in-sample 3 coin-periods, 1 profitable (33%), median return -0.5%, median PF 0.82, 0 broke 10% DD; out-of-sample 2 coin-periods, 0 profitable (0%), median return -1.2%, median PF 0.47, 0 broke 10% DD
- Trend Rider 2019-21 bull: in-sample 4 coin-periods, 4 profitable (100%), median return +12.7%, median PF 2.17, 0 broke 10% DD; out-of-sample 9 coin-periods, 8 profitable (89%), median return +7.6%, median PF 1.50, 0 broke 10% DD
- Trend Rider 2022 crash: in-sample 4 coin-periods, 0 profitable (0%), median return -0.2%, median PF 0.56, 0 broke 10% DD; out-of-sample 9 coin-periods, 1 profitable (11%), median return -1.4%, median PF 0.49, 0 broke 10% DD
- Trend Rider 2023-now: in-sample 5 coin-periods, 5 profitable (100%), median return +6.8%, median PF 1.45, 0 broke 10% DD; out-of-sample 8 coin-periods, 4 profitable (50%), median return +1.5%, median PF 1.13, 0 broke 10% DD
