# Forex and DXY filter test (job 2c), low-fee check: 0.01% each side (about a typical EUR/USD spread)

Run 2026-10-05. bot.py as it is now (0.5% risk), long only, no leverage, bot.py's own paper-mode functions bar by bar, fresh $1,000 per period. Script: research/forex_dxy.py.

Forex fee 0.01% each side; crypto 0.1%. Median 4H ATR of BTC/ETH/XRP since Mar 2024: 1.82%.

- EURUSD: 22280 4H candles from 2012-01-02, median 4H ATR 0.255%, scale 0.140 (v4 min stop 0.14%, max 0.56%)
- GBPUSD: 22279 4H candles from 2012-01-02, median 4H ATR 0.274%, scale 0.151 (v4 min stop 0.15%, max 0.60%)
- USDJPY: 22280 4H candles from 2012-01-02, median 4H ATR 0.281%, scale 0.155 (v4 min stop 0.15%, max 0.62%)

## DXY filter verdict

Helps = higher PF and no lower return (within 0.5 points) in BOTH halves.

- Forex, SP-12 v4 crypto settings: helps on 2 of 3 pairs (EURUSD yes, GBPUSD yes, USDJPY no)
- Forex, SP-12 v4 ATR-scaled: helps on 0 of 3 pairs (EURUSD no, GBPUSD no, USDJPY no)
- Forex, SP-12 v2 crypto settings: helps on 1 of 3 pairs (EURUSD no, GBPUSD yes, USDJPY no)
- Forex, SP-12 v2 ATR-scaled: helps on 0 of 3 pairs (EURUSD no, GBPUSD no, USDJPY no)
- Forex, Trend Rider: helps on 0 of 3 pairs (EURUSD no, GBPUSD no, USDJPY no)
- Crypto, SP-12 v4: helps on 0 of 3 coins (BTC no, ETH no, XRP no)
- Crypto, SP-12 v2: helps on 0 of 3 coins (BTC no, ETH no, XRP no)
- Crypto, Trend Rider: helps on 0 of 3 coins (BTC no, ETH no, XRP no)

## Forex: full period and halves

| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 crypto settings | EURUSD | Full 2012-now | 199 | 44% | -6.8% | -11.0% **>10%** | 0.87 | -13% |
| SP-12 v4 crypto settings | EURUSD | 1st half 2012-18 | 106 | 42% | -5.5% | -7.3% | 0.81 | -12% |
| SP-12 v4 crypto settings | EURUSD | 2nd half 2019-now | 95 | 46% | -2.7% | -5.6% | 0.89 | -2% |
| SP-12 v4 crypto settings + DXY | EURUSD | Full 2012-now | 153 | 46% | -3.0% | -6.7% | 0.92 | -13% |
| SP-12 v4 crypto settings + DXY | EURUSD | 1st half 2012-18 | 84 | 45% | -1.6% | -4.1% | 0.93 | -12% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2nd half 2019-now | 70 | 47% | -1.5% | -3.2% | 0.92 | -2% |
| SP-12 v4 ATR-scaled | EURUSD | Full 2012-now | 173 | 32% | -8.6% | -10.7% **>10%** | 0.78 | -13% |
| SP-12 v4 ATR-scaled | EURUSD | 1st half 2012-18 | 77 | 27% | -6.0% | -9.5% | 0.67 | -12% |
| SP-12 v4 ATR-scaled | EURUSD | 2nd half 2019-now | 96 | 35% | -2.8% | -6.0% | 0.88 | -2% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | Full 2012-now | 125 | 30% | -6.8% | -8.3% | 0.77 | -13% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 1st half 2012-18 | 58 | 28% | -4.3% | -8.3% | 0.71 | -12% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2nd half 2019-now | 67 | 33% | -2.7% | -5.4% | 0.83 | -2% |
| SP-12 v2 crypto settings | EURUSD | Full 2012-now | 254 | 42% | -5.8% | -9.4% | 0.87 | -13% |
| SP-12 v2 crypto settings | EURUSD | 1st half 2012-18 | 123 | 44% | -2.3% | -5.6% | 0.89 | -12% |
| SP-12 v2 crypto settings | EURUSD | 2nd half 2019-now | 131 | 40% | -3.7% | -5.9% | 0.84 | -2% |
| SP-12 v2 crypto settings + DXY | EURUSD | Full 2012-now | 171 | 41% | -5.6% | -6.6% | 0.82 | -13% |
| SP-12 v2 crypto settings + DXY | EURUSD | 1st half 2012-18 | 83 | 43% | -1.4% | -4.0% | 0.90 | -12% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2nd half 2019-now | 88 | 39% | -4.4% | -4.9% | 0.74 | -2% |
| SP-12 v2 ATR-scaled | EURUSD | Full 2012-now | 342 | 24% | -17.9% | -20.2% **>10%** | 0.73 | -13% |
| SP-12 v2 ATR-scaled | EURUSD | 1st half 2012-18 | 174 | 23% | -14.4% | -14.4% **>10%** | 0.60 | -12% |
| SP-12 v2 ATR-scaled | EURUSD | 2nd half 2019-now | 168 | 26% | -4.1% | -6.8% | 0.88 | -2% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | Full 2012-now | 265 | 24% | -15.3% | -16.8% **>10%** | 0.72 | -13% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 1st half 2012-18 | 136 | 26% | -8.9% | -11.3% **>10%** | 0.69 | -12% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2nd half 2019-now | 129 | 22% | -7.0% | -7.0% | 0.75 | -2% |
| Trend Rider | EURUSD | Full 2012-now | 195 | 37% | -4.4% | -10.9% **>10%** | 0.89 | -13% |
| Trend Rider | EURUSD | 1st half 2012-18 | 98 | 33% | -4.4% | -8.0% | 0.79 | -12% |
| Trend Rider | EURUSD | 2nd half 2019-now | 97 | 41% | +0.3% | -5.1% | 1.02 | -2% |
| Trend Rider + DXY | EURUSD | Full 2012-now | 173 | 37% | -2.3% | -10.3% **>10%** | 0.93 | -13% |
| Trend Rider + DXY | EURUSD | 1st half 2012-18 | 85 | 33% | -2.1% | -7.6% | 0.88 | -12% |
| Trend Rider + DXY | EURUSD | 2nd half 2019-now | 88 | 41% | +0.1% | -5.0% | 1.01 | -2% |
| SP-12 v4 crypto settings | GBPUSD | Full 2012-now | 217 | 48% | -5.2% | -8.5% | 0.91 | -15% |
| SP-12 v4 crypto settings | GBPUSD | 1st half 2012-18 | 101 | 49% | -2.0% | -6.5% | 0.92 | -18% |
| SP-12 v4 crypto settings | GBPUSD | 2nd half 2019-now | 116 | 47% | -3.3% | -5.4% | 0.89 | +4% |
| SP-12 v4 crypto settings + DXY | GBPUSD | Full 2012-now | 154 | 54% | +2.7% | -4.9% | 1.08 | -15% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 1st half 2012-18 | 75 | 52% | +0.1% | -4.9% | 1.01 | -18% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2nd half 2019-now | 79 | 56% | +2.6% | -3.1% | 1.15 | +4% |
| SP-12 v4 ATR-scaled | GBPUSD | Full 2012-now | 169 | 35% | -4.4% | -7.2% | 0.89 | -15% |
| SP-12 v4 ATR-scaled | GBPUSD | 1st half 2012-18 | 84 | 38% | +0.1% | -6.5% | 1.00 | -18% |
| SP-12 v4 ATR-scaled | GBPUSD | 2nd half 2019-now | 85 | 32% | -4.5% | -7.2% | 0.80 | +4% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | Full 2012-now | 113 | 34% | -5.1% | -6.2% | 0.82 | -15% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 1st half 2012-18 | 59 | 36% | -1.3% | -5.7% | 0.91 | -18% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2nd half 2019-now | 54 | 31% | -3.9% | -5.6% | 0.70 | +4% |
| SP-12 v2 crypto settings | GBPUSD | Full 2012-now | 260 | 44% | -8.6% | -11.1% **>10%** | 0.84 | -15% |
| SP-12 v2 crypto settings | GBPUSD | 1st half 2012-18 | 123 | 42% | -3.7% | -5.6% | 0.85 | -18% |
| SP-12 v2 crypto settings | GBPUSD | 2nd half 2019-now | 138 | 46% | -5.0% | -7.1% | 0.82 | +4% |
| SP-12 v2 crypto settings + DXY | GBPUSD | Full 2012-now | 165 | 47% | -2.4% | -5.2% | 0.92 | -15% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 1st half 2012-18 | 77 | 43% | -0.6% | -4.1% | 0.96 | -18% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2nd half 2019-now | 88 | 50% | -1.9% | -4.0% | 0.88 | +4% |
| SP-12 v2 ATR-scaled | GBPUSD | Full 2012-now | 330 | 25% | -13.0% | -16.7% **>10%** | 0.81 | -15% |
| SP-12 v2 ATR-scaled | GBPUSD | 1st half 2012-18 | 145 | 27% | -1.9% | -6.4% | 0.94 | -18% |
| SP-12 v2 ATR-scaled | GBPUSD | 2nd half 2019-now | 185 | 23% | -11.3% | -12.8% **>10%** | 0.69 | +4% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | Full 2012-now | 223 | 24% | -13.2% | -15.4% **>10%** | 0.71 | -15% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 1st half 2012-18 | 98 | 27% | -3.8% | -7.8% | 0.82 | -18% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2nd half 2019-now | 125 | 22% | -9.8% | -10.3% **>10%** | 0.60 | +4% |
| Trend Rider | GBPUSD | Full 2012-now | 197 | 32% | +0.1% | -8.5% | 1.00 | -15% |
| Trend Rider | GBPUSD | 1st half 2012-18 | 87 | 37% | +2.9% | -5.3% | 1.17 | -18% |
| Trend Rider | GBPUSD | 2nd half 2019-now | 110 | 29% | -2.7% | -8.5% | 0.88 | +4% |
| Trend Rider + DXY | GBPUSD | Full 2012-now | 146 | 32% | -0.0% | -8.1% | 1.00 | -15% |
| Trend Rider + DXY | GBPUSD | 1st half 2012-18 | 66 | 38% | +1.3% | -3.7% | 1.10 | -18% |
| Trend Rider + DXY | GBPUSD | 2nd half 2019-now | 80 | 28% | -1.3% | -8.1% | 0.92 | +4% |
| SP-12 v4 crypto settings | USDJPY | Full 2012-now | 231 | 56% | +23.6% | -5.2% | 1.45 | +105% |
| SP-12 v4 crypto settings | USDJPY | 1st half 2012-18 | 115 | 53% | +8.8% | -4.3% | 1.33 | +43% |
| SP-12 v4 crypto settings | USDJPY | 2nd half 2019-now | 116 | 59% | +13.6% | -4.2% | 1.59 | +44% |
| SP-12 v4 crypto settings + DXY | USDJPY | Full 2012-now | 169 | 58% | +23.6% | -4.6% | 1.64 | +105% |
| SP-12 v4 crypto settings + DXY | USDJPY | 1st half 2012-18 | 82 | 59% | +11.6% | -3.4% | 1.68 | +43% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2nd half 2019-now | 87 | 57% | +10.8% | -2.7% | 1.60 | +44% |
| SP-12 v4 ATR-scaled | USDJPY | Full 2012-now | 204 | 42% | +13.4% | -6.8% | 1.27 | +105% |
| SP-12 v4 ATR-scaled | USDJPY | 1st half 2012-18 | 101 | 39% | +6.2% | -4.5% | 1.26 | +43% |
| SP-12 v4 ATR-scaled | USDJPY | 2nd half 2019-now | 103 | 45% | +6.8% | -5.8% | 1.28 | +44% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | Full 2012-now | 134 | 40% | +10.5% | -6.2% | 1.33 | +105% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 1st half 2012-18 | 65 | 35% | +5.1% | -3.3% | 1.33 | +43% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2nd half 2019-now | 69 | 43% | +5.2% | -3.7% | 1.33 | +44% |
| SP-12 v2 crypto settings | USDJPY | Full 2012-now | 278 | 50% | +12.3% | -9.0% | 1.24 | +105% |
| SP-12 v2 crypto settings | USDJPY | 1st half 2012-18 | 136 | 50% | +5.8% | -5.5% | 1.22 | +43% |
| SP-12 v2 crypto settings | USDJPY | 2nd half 2019-now | 142 | 50% | +6.1% | -5.2% | 1.27 | +44% |
| SP-12 v2 crypto settings + DXY | USDJPY | Full 2012-now | 187 | 53% | +17.7% | -6.8% | 1.56 | +105% |
| SP-12 v2 crypto settings + DXY | USDJPY | 1st half 2012-18 | 93 | 51% | +5.1% | -3.6% | 1.28 | +43% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2nd half 2019-now | 94 | 56% | +11.9% | -4.2% | 1.95 | +44% |
| SP-12 v2 ATR-scaled | USDJPY | Full 2012-now | 344 | 29% | +11.0% | -9.2% | 1.15 | +105% |
| SP-12 v2 ATR-scaled | USDJPY | 1st half 2012-18 | 161 | 34% | +10.4% | -3.6% | 1.31 | +43% |
| SP-12 v2 ATR-scaled | USDJPY | 2nd half 2019-now | 183 | 26% | +0.6% | -8.4% | 1.02 | +44% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | Full 2012-now | 237 | 29% | +5.0% | -8.4% | 1.11 | +105% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 1st half 2012-18 | 108 | 32% | +3.6% | -3.5% | 1.17 | +43% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2nd half 2019-now | 129 | 26% | +1.3% | -5.7% | 1.06 | +44% |
| Trend Rider | USDJPY | Full 2012-now | 240 | 38% | +11.4% | -5.3% | 1.23 | +105% |
| Trend Rider | USDJPY | 1st half 2012-18 | 104 | 35% | +6.6% | -4.8% | 1.29 | +43% |
| Trend Rider | USDJPY | 2nd half 2019-now | 136 | 40% | +4.4% | -4.9% | 1.17 | +44% |
| Trend Rider + DXY | USDJPY | Full 2012-now | 173 | 37% | +8.1% | -5.2% | 1.22 | +105% |
| Trend Rider + DXY | USDJPY | 1st half 2012-18 | 77 | 36% | +5.2% | -5.0% | 1.31 | +43% |
| Trend Rider + DXY | USDJPY | 2nd half 2019-now | 96 | 38% | +2.7% | -4.1% | 1.14 | +44% |

## Forex: by era

| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 crypto settings | EURUSD | 2012-14 | 40 | 42% | -1.9% | -4.6% | 0.83 | -7% |
| SP-12 v4 crypto settings | EURUSD | 2015-19 | 79 | 41% | -5.8% | -8.4% | 0.74 | -6% |
| SP-12 v4 crypto settings | EURUSD | 2020-22 | 37 | 51% | +0.1% | -5.3% | 1.01 | -5% |
| SP-12 v4 crypto settings | EURUSD | 2023-now | 44 | 50% | +1.5% | -2.9% | 1.14 | +5% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2012-14 | 32 | 47% | -1.4% | -2.4% | 0.84 | -7% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2015-19 | 60 | 43% | -2.3% | -6.7% | 0.86 | -6% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2020-22 | 25 | 56% | +2.1% | -3.0% | 1.41 | -5% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2023-now | 37 | 49% | -0.7% | -3.1% | 0.92 | +5% |
| SP-12 v4 ATR-scaled | EURUSD | 2012-14 | 34 | 21% | -4.6% | -5.8% | 0.43 | -7% |
| SP-12 v4 ATR-scaled | EURUSD | 2015-19 | 59 | 29% | -4.5% | -6.0% | 0.71 | -6% |
| SP-12 v4 ATR-scaled | EURUSD | 2020-22 | 31 | 45% | +2.0% | -3.5% | 1.28 | -5% |
| SP-12 v4 ATR-scaled | EURUSD | 2023-now | 49 | 35% | -1.1% | -6.0% | 0.90 | +5% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2012-14 | 26 | 19% | -3.7% | -5.2% | 0.46 | -7% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2015-19 | 39 | 28% | -3.0% | -4.7% | 0.72 | -6% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2020-22 | 23 | 52% | +3.7% | -1.6% | 1.87 | -5% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2023-now | 37 | 27% | -3.4% | -5.4% | 0.64 | +5% |
| SP-12 v2 crypto settings | EURUSD | 2012-14 | 48 | 48% | -1.1% | -3.1% | 0.86 | -7% |
| SP-12 v2 crypto settings | EURUSD | 2015-19 | 94 | 39% | -3.6% | -5.4% | 0.80 | -6% |
| SP-12 v2 crypto settings | EURUSD | 2020-22 | 53 | 40% | -1.0% | -4.5% | 0.89 | -5% |
| SP-12 v2 crypto settings | EURUSD | 2023-now | 59 | 46% | +0.6% | -3.2% | 1.06 | +5% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2012-14 | 34 | 38% | -1.9% | -2.5% | 0.70 | -7% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2015-19 | 62 | 42% | -2.0% | -4.6% | 0.81 | -6% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2020-22 | 32 | 41% | -0.4% | -3.6% | 0.94 | -5% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2023-now | 43 | 42% | -1.2% | -3.3% | 0.85 | +5% |
| SP-12 v2 ATR-scaled | EURUSD | 2012-14 | 74 | 24% | -7.0% | -7.5% | 0.56 | -7% |
| SP-12 v2 ATR-scaled | EURUSD | 2015-19 | 123 | 21% | -11.1% | -11.1% **>10%** | 0.59 | -6% |
| SP-12 v2 ATR-scaled | EURUSD | 2020-22 | 53 | 25% | -0.1% | -4.4% | 0.99 | -5% |
| SP-12 v2 ATR-scaled | EURUSD | 2023-now | 92 | 29% | +0.2% | -5.9% | 1.01 | +5% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2012-14 | 59 | 29% | -3.4% | -5.1% | 0.73 | -7% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2015-19 | 92 | 21% | -9.0% | -9.4% | 0.56 | -6% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2020-22 | 38 | 26% | +1.0% | -2.8% | 1.14 | -5% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2023-now | 76 | 25% | -3.8% | -7.0% | 0.77 | +5% |
| Trend Rider | EURUSD | 2012-14 | 36 | 44% | +1.4% | -1.8% | 1.25 | -7% |
| Trend Rider | EURUSD | 2015-19 | 71 | 24% | -7.7% | -8.0% | 0.57 | -6% |
| Trend Rider | EURUSD | 2020-22 | 37 | 38% | -0.8% | -4.9% | 0.88 | -5% |
| Trend Rider | EURUSD | 2023-now | 51 | 49% | +3.3% | -2.3% | 1.37 | +5% |
| Trend Rider + DXY | EURUSD | 2012-14 | 29 | 52% | +3.2% | -1.7% | 1.87 | -7% |
| Trend Rider + DXY | EURUSD | 2015-19 | 65 | 22% | -7.1% | -7.4% | 0.57 | -6% |
| Trend Rider + DXY | EURUSD | 2020-22 | 35 | 40% | -0.7% | -4.8% | 0.89 | -5% |
| Trend Rider + DXY | EURUSD | 2023-now | 44 | 48% | +3.0% | -2.0% | 1.42 | +5% |
| SP-12 v4 crypto settings | GBPUSD | 2012-14 | 45 | 51% | +0.5% | -2.7% | 1.05 | +0% |
| SP-12 v4 crypto settings | GBPUSD | 2015-19 | 74 | 45% | -3.4% | -6.3% | 0.83 | -14% |
| SP-12 v4 crypto settings | GBPUSD | 2020-22 | 48 | 50% | -0.3% | -4.0% | 0.97 | -9% |
| SP-12 v4 crypto settings | GBPUSD | 2023-now | 50 | 48% | -2.0% | -3.3% | 0.84 | +10% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2012-14 | 33 | 52% | -0.0% | -2.8% | 0.99 | +0% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2015-19 | 52 | 52% | -0.4% | -3.9% | 0.97 | -14% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2020-22 | 31 | 58% | +1.9% | -2.8% | 1.31 | -9% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2023-now | 38 | 55% | +1.2% | -2.2% | 1.15 | +10% |
| SP-12 v4 ATR-scaled | GBPUSD | 2012-14 | 52 | 38% | -0.1% | -3.0% | 0.99 | +0% |
| SP-12 v4 ATR-scaled | GBPUSD | 2015-19 | 41 | 37% | +1.2% | -5.1% | 1.13 | -14% |
| SP-12 v4 ATR-scaled | GBPUSD | 2020-22 | 27 | 33% | +0.6% | -2.7% | 1.10 | -9% |
| SP-12 v4 ATR-scaled | GBPUSD | 2023-now | 49 | 31% | -6.0% | -6.0% | 0.57 | +10% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2012-14 | 37 | 35% | -1.4% | -2.5% | 0.85 | +0% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2015-19 | 27 | 33% | +0.0% | -3.6% | 1.01 | -14% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2020-22 | 11 | 36% | +0.6% | -1.6% | 1.33 | -9% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2023-now | 38 | 32% | -4.4% | -4.4% | 0.55 | +10% |
| SP-12 v2 crypto settings | GBPUSD | 2012-14 | 52 | 50% | +0.4% | -2.0% | 1.05 | +0% |
| SP-12 v2 crypto settings | GBPUSD | 2015-19 | 89 | 37% | -4.5% | -6.9% | 0.79 | -14% |
| SP-12 v2 crypto settings | GBPUSD | 2020-22 | 59 | 42% | -3.4% | -5.3% | 0.73 | -9% |
| SP-12 v2 crypto settings | GBPUSD | 2023-now | 60 | 50% | -1.3% | -3.1% | 0.88 | +10% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2012-14 | 32 | 44% | -0.3% | -1.8% | 0.94 | +0% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2015-19 | 58 | 40% | -2.2% | -4.3% | 0.83 | -14% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2020-22 | 33 | 55% | +1.5% | -1.9% | 1.29 | -9% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2023-now | 42 | 52% | -1.4% | -2.1% | 0.80 | +10% |
| SP-12 v2 ATR-scaled | GBPUSD | 2012-14 | 67 | 30% | +1.5% | -2.8% | 1.10 | +0% |
| SP-12 v2 ATR-scaled | GBPUSD | 2015-19 | 104 | 25% | -3.2% | -7.0% | 0.85 | -14% |
| SP-12 v2 ATR-scaled | GBPUSD | 2020-22 | 72 | 25% | -3.8% | -5.4% | 0.74 | -9% |
| SP-12 v2 ATR-scaled | GBPUSD | 2023-now | 87 | 21% | -8.0% | -8.0% | 0.57 | +10% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2012-14 | 47 | 26% | -1.1% | -3.7% | 0.89 | +0% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2015-19 | 70 | 27% | -3.2% | -4.6% | 0.77 | -14% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2020-22 | 37 | 22% | -2.8% | -4.1% | 0.65 | -9% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2023-now | 69 | 20% | -6.7% | -6.7% | 0.53 | +10% |
| Trend Rider | GBPUSD | 2012-14 | 46 | 35% | +0.5% | -2.5% | 1.05 | +0% |
| Trend Rider | GBPUSD | 2015-19 | 56 | 38% | +2.1% | -5.3% | 1.20 | -14% |
| Trend Rider | GBPUSD | 2020-22 | 39 | 23% | -3.0% | -4.8% | 0.60 | -9% |
| Trend Rider | GBPUSD | 2023-now | 56 | 32% | +1.0% | -4.7% | 1.08 | +10% |
| Trend Rider + DXY | GBPUSD | 2012-14 | 34 | 29% | -1.9% | -2.5% | 0.75 | +0% |
| Trend Rider + DXY | GBPUSD | 2015-19 | 41 | 41% | +2.8% | -3.7% | 1.41 | -14% |
| Trend Rider + DXY | GBPUSD | 2020-22 | 29 | 17% | -2.9% | -5.5% | 0.50 | -9% |
| Trend Rider + DXY | GBPUSD | 2023-now | 42 | 36% | +2.5% | -3.6% | 1.30 | +10% |
| SP-12 v4 crypto settings | USDJPY | 2012-14 | 60 | 55% | +8.6% | -4.3% | 1.70 | +56% |
| SP-12 v4 crypto settings | USDJPY | 2015-19 | 68 | 50% | -1.0% | -3.3% | 0.94 | -9% |
| SP-12 v4 crypto settings | USDJPY | 2020-22 | 42 | 60% | +8.1% | -3.5% | 2.03 | +21% |
| SP-12 v4 crypto settings | USDJPY | 2023-now | 61 | 64% | +7.5% | -1.7% | 1.67 | +20% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2012-14 | 42 | 69% | +11.9% | -2.0% | 3.06 | +56% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2015-19 | 52 | 48% | -1.3% | -4.2% | 0.90 | -9% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2020-22 | 34 | 62% | +8.6% | -2.0% | 2.44 | +21% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2023-now | 41 | 59% | +3.7% | -1.6% | 1.45 | +20% |
| SP-12 v4 ATR-scaled | USDJPY | 2012-14 | 44 | 39% | +6.7% | -3.8% | 1.64 | +56% |
| SP-12 v4 ATR-scaled | USDJPY | 2015-19 | 78 | 36% | -4.0% | -5.1% | 0.78 | -9% |
| SP-12 v4 ATR-scaled | USDJPY | 2020-22 | 37 | 49% | +8.0% | -2.5% | 2.02 | +21% |
| SP-12 v4 ATR-scaled | USDJPY | 2023-now | 45 | 49% | +3.3% | -2.0% | 1.33 | +20% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2012-14 | 30 | 37% | +6.7% | -3.1% | 1.95 | +56% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2015-19 | 51 | 31% | -4.2% | -5.6% | 0.64 | -9% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2020-22 | 25 | 52% | +8.0% | -1.8% | 2.52 | +21% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2023-now | 28 | 46% | +0.1% | -2.5% | 1.02 | +20% |
| SP-12 v2 crypto settings | USDJPY | 2012-14 | 58 | 53% | +9.6% | -2.4% | 2.17 | +56% |
| SP-12 v2 crypto settings | USDJPY | 2015-19 | 96 | 47% | -4.8% | -5.9% | 0.76 | -9% |
| SP-12 v2 crypto settings | USDJPY | 2020-22 | 59 | 49% | +3.5% | -4.1% | 1.37 | +21% |
| SP-12 v2 crypto settings | USDJPY | 2023-now | 66 | 52% | +4.0% | -1.9% | 1.39 | +20% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2012-14 | 39 | 59% | +7.9% | -1.6% | 2.36 | +56% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2015-19 | 70 | 43% | -4.5% | -5.1% | 0.70 | -9% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2020-22 | 42 | 52% | +6.0% | -2.1% | 1.94 | +21% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2023-now | 37 | 68% | +7.3% | -1.5% | 3.35 | +20% |
| SP-12 v2 ATR-scaled | USDJPY | 2012-14 | 78 | 36% | +4.7% | -2.8% | 1.31 | +56% |
| SP-12 v2 ATR-scaled | USDJPY | 2015-19 | 108 | 30% | +5.4% | -2.8% | 1.25 | -9% |
| SP-12 v2 ATR-scaled | USDJPY | 2020-22 | 73 | 25% | -1.3% | -7.3% | 0.91 | +21% |
| SP-12 v2 ATR-scaled | USDJPY | 2023-now | 85 | 27% | +2.7% | -2.8% | 1.17 | +20% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2012-14 | 53 | 43% | +5.9% | -3.0% | 1.62 | +56% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2015-19 | 74 | 22% | -3.0% | -4.6% | 0.80 | -9% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2020-22 | 56 | 27% | +0.8% | -4.5% | 1.07 | +21% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2023-now | 54 | 26% | +1.4% | -3.2% | 1.15 | +20% |
| Trend Rider | USDJPY | 2012-14 | 47 | 40% | +8.4% | -3.5% | 1.84 | +56% |
| Trend Rider | USDJPY | 2015-19 | 73 | 27% | -4.0% | -4.8% | 0.73 | -9% |
| Trend Rider | USDJPY | 2020-22 | 46 | 50% | +9.7% | -2.2% | 2.25 | +21% |
| Trend Rider | USDJPY | 2023-now | 74 | 38% | -1.8% | -4.9% | 0.87 | +20% |
| Trend Rider + DXY | USDJPY | 2012-14 | 32 | 50% | +7.7% | -1.8% | 2.28 | +56% |
| Trend Rider + DXY | USDJPY | 2015-19 | 57 | 25% | -4.6% | -5.2% | 0.65 | -9% |
| Trend Rider + DXY | USDJPY | 2020-22 | 36 | 50% | +8.9% | -2.0% | 2.45 | +21% |
| Trend Rider + DXY | USDJPY | 2023-now | 48 | 33% | -3.5% | -4.1% | 0.65 | +20% |

## Crypto with and without the DXY filter

| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 | BTC | Full (start-now) | 318 | 42% | +81.9% | -5.9% | 1.77 | +592999% |
| SP-12 v4 | BTC | 1st half (start-2019) | 157 | 41% | +43.8% | -5.9% | 2.05 | +49485% |
| SP-12 v4 | BTC | 2nd half (2020-now) | 161 | 42% | +26.4% | -5.7% | 1.59 | +1096% |
| SP-12 v4 + DXY | BTC | Full (start-now) | 172 | 41% | +34.7% | -5.1% | 1.71 | +592999% |
| SP-12 v4 + DXY | BTC | 1st half (start-2019) | 75 | 43% | +18.6% | -5.1% | 1.95 | +49485% |
| SP-12 v4 + DXY | BTC | 2nd half (2020-now) | 97 | 40% | +13.6% | -4.4% | 1.55 | +1096% |
| SP-12 v2 | BTC | Full (start-now) | 503 | 33% | +36.7% | -10.5% **>10%** | 1.24 | +592999% |
| SP-12 v2 | BTC | 1st half (start-2019) | 248 | 32% | +21.9% | -7.0% | 1.32 | +49485% |
| SP-12 v2 | BTC | 2nd half (2020-now) | 255 | 33% | +12.1% | -10.5% **>10%** | 1.17 | +1096% |
| SP-12 v2 + DXY | BTC | Full (start-now) | 260 | 34% | +24.8% | -4.5% | 1.36 | +592999% |
| SP-12 v2 + DXY | BTC | 1st half (start-2019) | 121 | 31% | +9.1% | -4.5% | 1.29 | +49485% |
| SP-12 v2 + DXY | BTC | 2nd half (2020-now) | 139 | 36% | +14.3% | -3.6% | 1.41 | +1096% |
| Trend Rider | BTC | Full (start-now) | 276 | 46% | +88.9% | -3.4% | 2.32 | +592999% |
| Trend Rider | BTC | 1st half (start-2019) | 135 | 48% | +48.7% | -2.3% | 3.16 | +49485% |
| Trend Rider | BTC | 2nd half (2020-now) | 141 | 43% | +27.1% | -3.4% | 1.90 | +1096% |
| Trend Rider + DXY | BTC | Full (start-now) | 157 | 43% | +30.4% | -3.2% | 1.84 | +592999% |
| Trend Rider + DXY | BTC | 1st half (start-2019) | 66 | 47% | +18.0% | -2.0% | 2.66 | +49485% |
| Trend Rider + DXY | BTC | 2nd half (2020-now) | 91 | 40% | +10.5% | -3.2% | 1.49 | +1096% |
| SP-12 v4 | ETH | Full (start-now) | 184 | 33% | +6.4% | -10.5% **>10%** | 1.13 | +26364% |
| SP-12 v4 | ETH | 1st half (start-2019) | 46 | 39% | +5.2% | -3.0% | 1.48 | +1157% |
| SP-12 v4 | ETH | 2nd half (2020-now) | 138 | 30% | +1.1% | -10.5% **>10%** | 1.03 | +2008% |
| SP-12 v4 + DXY | ETH | Full (start-now) | 99 | 31% | +0.6% | -10.3% **>10%** | 1.02 | +26364% |
| SP-12 v4 + DXY | ETH | 1st half (start-2019) | 22 | 41% | +2.3% | -1.7% | 1.48 | +1157% |
| SP-12 v4 + DXY | ETH | 2nd half (2020-now) | 77 | 29% | -1.7% | -10.3% **>10%** | 0.92 | +2008% |
| SP-12 v2 | ETH | Full (start-now) | 369 | 28% | -4.6% | -9.8% | 0.95 | +26364% |
| SP-12 v2 | ETH | 1st half (start-2019) | 94 | 28% | -3.1% | -7.4% | 0.89 | +1157% |
| SP-12 v2 | ETH | 2nd half (2020-now) | 275 | 28% | -1.6% | -9.2% | 0.98 | +2008% |
| SP-12 v2 + DXY | ETH | Full (start-now) | 191 | 28% | -2.7% | -9.8% | 0.95 | +26364% |
| SP-12 v2 + DXY | ETH | 1st half (start-2019) | 42 | 29% | -0.7% | -3.3% | 0.95 | +1157% |
| SP-12 v2 + DXY | ETH | 2nd half (2020-now) | 149 | 28% | -2.0% | -9.8% | 0.95 | +2008% |
| Trend Rider | ETH | Full (start-now) | 220 | 33% | +33.0% | -6.1% | 1.64 | +26364% |
| Trend Rider | ETH | 1st half (start-2019) | 71 | 38% | +13.7% | -2.1% | 1.99 | +1157% |
| Trend Rider | ETH | 2nd half (2020-now) | 149 | 30% | +16.9% | -6.1% | 1.51 | +2008% |
| Trend Rider + DXY | ETH | Full (start-now) | 130 | 32% | +23.9% | -3.7% | 1.84 | +26364% |
| Trend Rider + DXY | ETH | 1st half (start-2019) | 40 | 35% | +6.1% | -2.8% | 1.73 | +1157% |
| Trend Rider + DXY | ETH | 2nd half (2020-now) | 90 | 31% | +16.7% | -3.7% | 1.88 | +2008% |
| SP-12 v4 | XRP | Full (start-now) | 141 | 32% | +10.8% | -6.8% | 1.26 | +300% |
| SP-12 v4 | XRP | 1st half (start-2019) | 28 | 25% | +0.4% | -2.9% | 1.06 | -49% |
| SP-12 v4 | XRP | 2nd half (2020-now) | 113 | 34% | +10.3% | -6.8% | 1.31 | +688% |
| SP-12 v4 + DXY | XRP | Full (start-now) | 76 | 29% | -2.1% | -7.9% | 0.90 | +300% |
| SP-12 v4 + DXY | XRP | 1st half (start-2019) | 14 | 14% | -1.6% | -3.0% | 0.57 | -49% |
| SP-12 v4 + DXY | XRP | 2nd half (2020-now) | 62 | 32% | -0.5% | -7.9% | 0.97 | +688% |
| SP-12 v2 | XRP | Full (start-now) | 294 | 26% | -10.7% | -17.0% **>10%** | 0.87 | +300% |
| SP-12 v2 | XRP | 1st half (start-2019) | 66 | 29% | -0.4% | -5.8% | 0.98 | -49% |
| SP-12 v2 | XRP | 2nd half (2020-now) | 228 | 25% | -10.3% | -17.0% **>10%** | 0.84 | +688% |
| SP-12 v2 + DXY | XRP | Full (start-now) | 150 | 24% | -10.6% | -12.8% **>10%** | 0.76 | +300% |
| SP-12 v2 + DXY | XRP | 1st half (start-2019) | 28 | 25% | -2.3% | -3.1% | 0.73 | -49% |
| SP-12 v2 + DXY | XRP | 2nd half (2020-now) | 122 | 24% | -8.4% | -12.8% **>10%** | 0.76 | +688% |
| Trend Rider | XRP | Full (start-now) | 142 | 28% | +7.0% | -9.1% | 1.20 | +300% |
| Trend Rider | XRP | 1st half (start-2019) | 30 | 33% | +4.1% | -3.1% | 1.59 | -49% |
| Trend Rider | XRP | 2nd half (2020-now) | 112 | 27% | +2.8% | -9.1% | 1.11 | +688% |
| Trend Rider + DXY | XRP | Full (start-now) | 85 | 21% | -4.4% | -10.6% **>10%** | 0.77 | +300% |
| Trend Rider + DXY | XRP | 1st half (start-2019) | 16 | 38% | +1.1% | -2.0% | 1.42 | -49% |
| Trend Rider + DXY | XRP | 2nd half (2020-now) | 69 | 17% | -5.4% | -10.6% **>10%** | 0.67 | +688% |
