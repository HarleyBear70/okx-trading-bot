# Forex and DXY filter test (job 2c)

Run 2026-10-05. bot.py as it is now (0.5% risk), long only, no leverage, bot.py's own paper-mode functions bar by bar, fresh $1,000 per period. Script: research/forex_dxy.py.

Forex fee 0.075% each side; crypto 0.1%. Median 4H ATR of BTC/ETH/XRP since Mar 2024: 1.82%.

- EURUSD: 22280 4H candles from 2012-01-02, median 4H ATR 0.255%, scale 0.140 (v4 min stop 0.14%, max 0.56%)
- GBPUSD: 22279 4H candles from 2012-01-02, median 4H ATR 0.274%, scale 0.151 (v4 min stop 0.15%, max 0.60%)
- USDJPY: 22280 4H candles from 2012-01-02, median 4H ATR 0.281%, scale 0.155 (v4 min stop 0.15%, max 0.62%)

## DXY filter verdict

Helps = higher PF and no lower return (within 0.5 points) in BOTH halves.

- Forex, SP-12 v4 crypto settings: helps on 2 of 3 pairs (EURUSD yes, GBPUSD yes, USDJPY no)
- Forex, SP-12 v4 ATR-scaled: helps on 1 of 3 pairs (EURUSD no, GBPUSD no, USDJPY yes)
- Forex, SP-12 v2 crypto settings: helps on 2 of 3 pairs (EURUSD no, GBPUSD yes, USDJPY yes)
- Forex, SP-12 v2 ATR-scaled: helps on 0 of 3 pairs (EURUSD no, GBPUSD no, USDJPY no)
- Forex, Trend Rider: helps on 0 of 3 pairs (EURUSD no, GBPUSD no, USDJPY no)
- Crypto, SP-12 v4: helps on 0 of 3 coins (BTC no, ETH no, XRP no)
- Crypto, SP-12 v2: helps on 0 of 3 coins (BTC no, ETH no, XRP no)
- Crypto, Trend Rider: helps on 0 of 3 coins (BTC no, ETH no, XRP no)

## Forex: full period and halves

| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 crypto settings | EURUSD | Full 2012-now | 199 | 44% | -16.8% | -17.4% **>10%** | 0.69 | -13% |
| SP-12 v4 crypto settings | EURUSD | 1st half 2012-18 | 106 | 41% | -10.9% | -11.7% **>10%** | 0.66 | -12% |
| SP-12 v4 crypto settings | EURUSD | 2nd half 2019-now | 95 | 46% | -7.9% | -8.1% | 0.70 | -2% |
| SP-12 v4 crypto settings + DXY | EURUSD | Full 2012-now | 153 | 46% | -11.2% | -11.2% **>10%** | 0.73 | -13% |
| SP-12 v4 crypto settings + DXY | EURUSD | 1st half 2012-18 | 84 | 44% | -6.3% | -6.3% | 0.74 | -12% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2nd half 2019-now | 70 | 47% | -5.4% | -5.9% | 0.72 | -2% |
| SP-12 v4 ATR-scaled | EURUSD | Full 2012-now | 177 | 24% | -28.8% | -28.9% **>10%** | 0.38 | -13% |
| SP-12 v4 ATR-scaled | EURUSD | 1st half 2012-18 | 79 | 18% | -17.0% | -17.1% **>10%** | 0.25 | -12% |
| SP-12 v4 ATR-scaled | EURUSD | 2nd half 2019-now | 98 | 30% | -14.3% | -14.3% **>10%** | 0.50 | -2% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | Full 2012-now | 129 | 22% | -23.1% | -23.2% **>10%** | 0.36 | -13% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 1st half 2012-18 | 60 | 18% | -13.5% | -13.6% **>10%** | 0.27 | -12% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2nd half 2019-now | 69 | 26% | -11.1% | -11.1% **>10%** | 0.46 | -2% |
| SP-12 v2 crypto settings | EURUSD | Full 2012-now | 256 | 40% | -15.1% | -16.7% **>10%** | 0.68 | -13% |
| SP-12 v2 crypto settings | EURUSD | 1st half 2012-18 | 123 | 41% | -6.7% | -7.9% | 0.71 | -12% |
| SP-12 v2 crypto settings | EURUSD | 2nd half 2019-now | 133 | 39% | -9.1% | -10.3% **>10%** | 0.64 | -2% |
| SP-12 v2 crypto settings + DXY | EURUSD | Full 2012-now | 172 | 39% | -12.2% | -12.7% **>10%** | 0.63 | -13% |
| SP-12 v2 crypto settings + DXY | EURUSD | 1st half 2012-18 | 83 | 40% | -4.6% | -6.2% | 0.70 | -12% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2nd half 2019-now | 89 | 38% | -8.1% | -8.3% | 0.57 | -2% |
| SP-12 v2 ATR-scaled | EURUSD | Full 2012-now | 359 | 20% | -48.5% | -48.5% **>10%** | 0.36 | -13% |
| SP-12 v2 ATR-scaled | EURUSD | 1st half 2012-18 | 181 | 18% | -32.3% | -32.3% **>10%** | 0.28 | -12% |
| SP-12 v2 ATR-scaled | EURUSD | 2nd half 2019-now | 178 | 22% | -24.0% | -24.0% **>10%** | 0.48 | -2% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | Full 2012-now | 274 | 20% | -40.7% | -40.7% **>10%** | 0.36 | -13% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 1st half 2012-18 | 139 | 19% | -24.5% | -24.5% **>10%** | 0.31 | -12% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2nd half 2019-now | 135 | 21% | -21.4% | -21.4% **>10%** | 0.42 | -2% |
| Trend Rider | EURUSD | Full 2012-now | 198 | 26% | -20.6% | -21.4% **>10%** | 0.55 | -13% |
| Trend Rider | EURUSD | 1st half 2012-18 | 100 | 23% | -12.8% | -13.7% **>10%** | 0.50 | -12% |
| Trend Rider | EURUSD | 2nd half 2019-now | 98 | 30% | -8.7% | -8.8% | 0.61 | -2% |
| Trend Rider + DXY | EURUSD | Full 2012-now | 177 | 25% | -17.5% | -20.9% **>10%** | 0.57 | -13% |
| Trend Rider + DXY | EURUSD | 1st half 2012-18 | 87 | 23% | -9.9% | -12.8% **>10%** | 0.56 | -12% |
| Trend Rider + DXY | EURUSD | 2nd half 2019-now | 90 | 28% | -8.2% | -9.2% | 0.60 | -2% |
| SP-12 v4 crypto settings | GBPUSD | Full 2012-now | 217 | 47% | -16.1% | -16.8% **>10%** | 0.72 | -15% |
| SP-12 v4 crypto settings | GBPUSD | 1st half 2012-18 | 101 | 48% | -7.4% | -8.7% | 0.74 | -18% |
| SP-12 v4 crypto settings | GBPUSD | 2nd half 2019-now | 116 | 47% | -9.4% | -10.4% **>10%** | 0.70 | +4% |
| SP-12 v4 crypto settings + DXY | GBPUSD | Full 2012-now | 154 | 52% | -5.8% | -7.4% | 0.85 | -15% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 1st half 2012-18 | 75 | 51% | -4.0% | -7.3% | 0.79 | -18% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2nd half 2019-now | 79 | 53% | -1.8% | -3.7% | 0.90 | +4% |
| SP-12 v4 ATR-scaled | GBPUSD | Full 2012-now | 171 | 32% | -22.7% | -23.3% **>10%** | 0.53 | -15% |
| SP-12 v4 ATR-scaled | GBPUSD | 1st half 2012-18 | 84 | 35% | -10.4% | -13.9% **>10%** | 0.57 | -18% |
| SP-12 v4 ATR-scaled | GBPUSD | 2nd half 2019-now | 87 | 29% | -13.7% | -15.0% **>10%** | 0.50 | +4% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | Full 2012-now | 115 | 30% | -18.1% | -18.4% **>10%** | 0.46 | -15% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 1st half 2012-18 | 59 | 32% | -9.0% | -11.3% **>10%** | 0.50 | -18% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2nd half 2019-now | 56 | 27% | -10.0% | -10.3% **>10%** | 0.40 | +4% |
| SP-12 v2 crypto settings | GBPUSD | Full 2012-now | 260 | 40% | -18.0% | -19.7% **>10%** | 0.67 | -15% |
| SP-12 v2 crypto settings | GBPUSD | 1st half 2012-18 | 123 | 40% | -8.4% | -9.7% | 0.69 | -18% |
| SP-12 v2 crypto settings | GBPUSD | 2nd half 2019-now | 138 | 41% | -10.5% | -12.2% **>10%** | 0.66 | +4% |
| SP-12 v2 crypto settings + DXY | GBPUSD | Full 2012-now | 165 | 39% | -9.3% | -9.9% | 0.71 | -15% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 1st half 2012-18 | 77 | 39% | -3.9% | -5.7% | 0.76 | -18% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2nd half 2019-now | 88 | 40% | -5.6% | -5.8% | 0.68 | +4% |
| SP-12 v2 ATR-scaled | GBPUSD | Full 2012-now | 347 | 20% | -43.2% | -44.7% **>10%** | 0.44 | -15% |
| SP-12 v2 ATR-scaled | GBPUSD | 1st half 2012-18 | 149 | 23% | -18.4% | -20.8% **>10%** | 0.53 | -18% |
| SP-12 v2 ATR-scaled | GBPUSD | 2nd half 2019-now | 198 | 18% | -30.4% | -31.1% **>10%** | 0.36 | +4% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | Full 2012-now | 235 | 19% | -35.2% | -36.7% **>10%** | 0.37 | -15% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 1st half 2012-18 | 100 | 23% | -15.3% | -18.2% **>10%** | 0.46 | -18% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2nd half 2019-now | 135 | 16% | -23.5% | -23.8% **>10%** | 0.29 | +4% |
| Trend Rider | GBPUSD | Full 2012-now | 198 | 30% | -14.8% | -17.6% **>10%** | 0.69 | -15% |
| Trend Rider | GBPUSD | 1st half 2012-18 | 87 | 33% | -4.4% | -8.9% | 0.79 | -18% |
| Trend Rider | GBPUSD | 2nd half 2019-now | 111 | 27% | -10.8% | -13.9% **>10%** | 0.60 | +4% |
| Trend Rider + DXY | GBPUSD | Full 2012-now | 147 | 29% | -11.0% | -14.2% **>10%** | 0.68 | -15% |
| Trend Rider + DXY | GBPUSD | 1st half 2012-18 | 66 | 33% | -4.1% | -7.9% | 0.74 | -18% |
| Trend Rider + DXY | GBPUSD | 2nd half 2019-now | 81 | 26% | -7.2% | -11.1% **>10%** | 0.62 | +4% |
| SP-12 v4 crypto settings | USDJPY | Full 2012-now | 231 | 54% | +8.2% | -8.9% | 1.15 | +105% |
| SP-12 v4 crypto settings | USDJPY | 1st half 2012-18 | 115 | 52% | +2.1% | -5.7% | 1.07 | +43% |
| SP-12 v4 crypto settings | USDJPY | 2nd half 2019-now | 116 | 56% | +6.0% | -5.5% | 1.24 | +44% |
| SP-12 v4 crypto settings + DXY | USDJPY | Full 2012-now | 169 | 56% | +11.7% | -6.6% | 1.30 | +105% |
| SP-12 v4 crypto settings + DXY | USDJPY | 1st half 2012-18 | 82 | 57% | +6.5% | -3.9% | 1.35 | +43% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2nd half 2019-now | 87 | 54% | +4.9% | -3.4% | 1.25 | +44% |
| SP-12 v4 ATR-scaled | USDJPY | Full 2012-now | 210 | 34% | -13.5% | -17.7% **>10%** | 0.76 | +105% |
| SP-12 v4 ATR-scaled | USDJPY | 1st half 2012-18 | 103 | 33% | -5.7% | -8.9% | 0.80 | +43% |
| SP-12 v4 ATR-scaled | USDJPY | 2nd half 2019-now | 107 | 35% | -8.2% | -10.5% **>10%** | 0.72 | +44% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | Full 2012-now | 136 | 33% | -6.4% | -12.6% **>10%** | 0.83 | +105% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 1st half 2012-18 | 65 | 32% | -2.1% | -6.4% | 0.89 | +43% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2nd half 2019-now | 71 | 34% | -4.4% | -6.7% | 0.77 | +44% |
| SP-12 v2 crypto settings | USDJPY | Full 2012-now | 279 | 48% | -0.5% | -12.6% **>10%** | 0.99 | +105% |
| SP-12 v2 crypto settings | USDJPY | 1st half 2012-18 | 136 | 48% | -0.3% | -7.4% | 0.99 | +43% |
| SP-12 v2 crypto settings | USDJPY | 2nd half 2019-now | 143 | 48% | -0.3% | -6.4% | 0.99 | +44% |
| SP-12 v2 crypto settings + DXY | USDJPY | Full 2012-now | 187 | 51% | +8.4% | -9.4% | 1.25 | +105% |
| SP-12 v2 crypto settings + DXY | USDJPY | 1st half 2012-18 | 93 | 47% | +0.6% | -5.3% | 1.03 | +43% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2nd half 2019-now | 94 | 55% | +7.8% | -4.9% | 1.56 | +44% |
| SP-12 v2 ATR-scaled | USDJPY | Full 2012-now | 361 | 25% | -28.7% | -29.1% **>10%** | 0.64 | +105% |
| SP-12 v2 ATR-scaled | USDJPY | 1st half 2012-18 | 168 | 29% | -10.8% | -11.3% **>10%** | 0.73 | +43% |
| SP-12 v2 ATR-scaled | USDJPY | 2nd half 2019-now | 193 | 22% | -20.1% | -20.6% **>10%** | 0.55 | +44% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | Full 2012-now | 244 | 26% | -20.8% | -21.6% **>10%** | 0.63 | +105% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 1st half 2012-18 | 112 | 30% | -8.6% | -9.0% | 0.69 | +43% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2nd half 2019-now | 132 | 23% | -13.3% | -13.9% **>10%** | 0.57 | +44% |
| Trend Rider | USDJPY | Full 2012-now | 241 | 31% | -9.0% | -13.4% **>10%** | 0.85 | +105% |
| Trend Rider | USDJPY | 1st half 2012-18 | 105 | 31% | -2.2% | -8.0% | 0.92 | +43% |
| Trend Rider | USDJPY | 2nd half 2019-now | 136 | 31% | -6.9% | -7.8% | 0.78 | +44% |
| Trend Rider + DXY | USDJPY | Full 2012-now | 174 | 31% | -7.1% | -11.9% **>10%** | 0.84 | +105% |
| Trend Rider + DXY | USDJPY | 1st half 2012-18 | 78 | 33% | -1.7% | -7.8% | 0.92 | +43% |
| Trend Rider + DXY | USDJPY | 2nd half 2019-now | 96 | 29% | -5.5% | -7.5% | 0.77 | +44% |

## Forex: by era

| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |
|---|---|---|---|---|---|---|---|---|
| SP-12 v4 crypto settings | EURUSD | 2012-14 | 40 | 42% | -4.1% | -5.1% | 0.67 | -7% |
| SP-12 v4 crypto settings | EURUSD | 2015-19 | 79 | 39% | -9.9% | -11.2% **>10%** | 0.60 | -6% |
| SP-12 v4 crypto settings | EURUSD | 2020-22 | 37 | 51% | -2.0% | -6.5% | 0.80 | -5% |
| SP-12 v4 crypto settings | EURUSD | 2023-now | 44 | 50% | -1.1% | -3.7% | 0.91 | +5% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2012-14 | 32 | 47% | -3.3% | -3.3% | 0.66 | -7% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2015-19 | 60 | 42% | -5.5% | -7.6% | 0.69 | -6% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2020-22 | 25 | 56% | +0.7% | -3.7% | 1.12 | -5% |
| SP-12 v4 crypto settings + DXY | EURUSD | 2023-now | 37 | 49% | -2.8% | -3.9% | 0.73 | +5% |
| SP-12 v4 ATR-scaled | EURUSD | 2012-14 | 35 | 11% | -8.9% | -9.1% | 0.16 | -7% |
| SP-12 v4 ATR-scaled | EURUSD | 2015-19 | 60 | 22% | -13.4% | -13.4% **>10%** | 0.29 | -6% |
| SP-12 v4 ATR-scaled | EURUSD | 2020-22 | 31 | 39% | -2.5% | -5.3% | 0.73 | -5% |
| SP-12 v4 ATR-scaled | EURUSD | 2023-now | 51 | 27% | -7.5% | -7.7% | 0.49 | +5% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2012-14 | 27 | 11% | -7.3% | -7.9% | 0.18 | -7% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2015-19 | 40 | 20% | -9.6% | -9.6% | 0.27 | -6% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2020-22 | 23 | 43% | +0.1% | -2.7% | 1.03 | -5% |
| SP-12 v4 ATR-scaled + DXY | EURUSD | 2023-now | 39 | 21% | -8.4% | -8.4% | 0.33 | +5% |
| SP-12 v2 crypto settings | EURUSD | 2012-14 | 48 | 42% | -3.0% | -4.1% | 0.65 | -7% |
| SP-12 v2 crypto settings | EURUSD | 2015-19 | 94 | 39% | -6.9% | -7.3% | 0.64 | -6% |
| SP-12 v2 crypto settings | EURUSD | 2020-22 | 55 | 35% | -4.0% | -6.7% | 0.63 | -5% |
| SP-12 v2 crypto settings | EURUSD | 2023-now | 59 | 46% | -1.8% | -4.1% | 0.84 | +5% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2012-14 | 34 | 35% | -3.2% | -3.7% | 0.54 | -7% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2015-19 | 62 | 39% | -4.4% | -5.7% | 0.63 | -6% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2020-22 | 33 | 39% | -2.1% | -4.8% | 0.70 | -5% |
| SP-12 v2 crypto settings + DXY | EURUSD | 2023-now | 43 | 42% | -2.8% | -3.9% | 0.67 | +5% |
| SP-12 v2 ATR-scaled | EURUSD | 2012-14 | 78 | 17% | -15.9% | -16.3% **>10%** | 0.26 | -7% |
| SP-12 v2 ATR-scaled | EURUSD | 2015-19 | 128 | 17% | -25.2% | -25.2% **>10%** | 0.29 | -6% |
| SP-12 v2 ATR-scaled | EURUSD | 2020-22 | 54 | 24% | -5.7% | -8.0% | 0.59 | -5% |
| SP-12 v2 ATR-scaled | EURUSD | 2023-now | 99 | 25% | -12.8% | -13.1% **>10%** | 0.53 | +5% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2012-14 | 60 | 18% | -12.0% | -12.0% **>10%** | 0.28 | -7% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2015-19 | 94 | 18% | -19.0% | -19.0% **>10%** | 0.30 | -6% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2020-22 | 39 | 28% | -2.9% | -5.1% | 0.71 | -5% |
| SP-12 v2 ATR-scaled + DXY | EURUSD | 2023-now | 81 | 21% | -13.8% | -14.1% **>10%** | 0.40 | +5% |
| Trend Rider | EURUSD | 2012-14 | 36 | 31% | -1.7% | -2.6% | 0.78 | -7% |
| Trend Rider | EURUSD | 2015-19 | 73 | 18% | -13.9% | -14.2% **>10%** | 0.36 | -6% |
| Trend Rider | EURUSD | 2020-22 | 38 | 29% | -4.3% | -6.7% | 0.51 | -5% |
| Trend Rider | EURUSD | 2023-now | 51 | 35% | -1.6% | -3.5% | 0.86 | +5% |
| Trend Rider + DXY | EURUSD | 2012-14 | 29 | 34% | +0.6% | -2.6% | 1.12 | -7% |
| Trend Rider + DXY | EURUSD | 2015-19 | 67 | 16% | -13.0% | -13.3% **>10%** | 0.36 | -6% |
| Trend Rider + DXY | EURUSD | 2020-22 | 36 | 31% | -4.2% | -6.6% | 0.52 | -5% |
| Trend Rider + DXY | EURUSD | 2023-now | 45 | 31% | -1.2% | -3.3% | 0.87 | +5% |
| SP-12 v4 crypto settings | GBPUSD | 2012-14 | 45 | 51% | -2.2% | -3.4% | 0.81 | +0% |
| SP-12 v4 crypto settings | GBPUSD | 2015-19 | 74 | 43% | -7.1% | -9.8% | 0.67 | -14% |
| SP-12 v4 crypto settings | GBPUSD | 2020-22 | 48 | 48% | -3.0% | -5.1% | 0.77 | -9% |
| SP-12 v4 crypto settings | GBPUSD | 2023-now | 50 | 48% | -4.7% | -5.1% | 0.66 | +10% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2012-14 | 33 | 52% | -2.1% | -3.2% | 0.77 | +0% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2015-19 | 52 | 48% | -3.0% | -4.8% | 0.78 | -14% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2020-22 | 31 | 55% | +0.1% | -3.1% | 1.02 | -9% |
| SP-12 v4 crypto settings + DXY | GBPUSD | 2023-now | 38 | 55% | -0.9% | -2.5% | 0.90 | +10% |
| SP-12 v4 ATR-scaled | GBPUSD | 2012-14 | 52 | 37% | -6.7% | -7.4% | 0.58 | +0% |
| SP-12 v4 ATR-scaled | GBPUSD | 2015-19 | 41 | 32% | -3.9% | -7.0% | 0.66 | -14% |
| SP-12 v4 ATR-scaled | GBPUSD | 2020-22 | 28 | 32% | -2.9% | -5.1% | 0.62 | -9% |
| SP-12 v4 ATR-scaled | GBPUSD | 2023-now | 50 | 26% | -11.2% | -11.2% **>10%** | 0.35 | +10% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2012-14 | 37 | 32% | -6.1% | -6.5% | 0.47 | +0% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2015-19 | 27 | 30% | -3.6% | -5.3% | 0.57 | -14% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2020-22 | 12 | 33% | -1.2% | -2.3% | 0.60 | -9% |
| SP-12 v4 ATR-scaled + DXY | GBPUSD | 2023-now | 39 | 26% | -8.4% | -8.4% | 0.33 | +10% |
| SP-12 v2 crypto settings | GBPUSD | 2012-14 | 52 | 44% | -1.7% | -3.0% | 0.81 | +0% |
| SP-12 v2 crypto settings | GBPUSD | 2015-19 | 89 | 37% | -7.8% | -9.7% | 0.66 | -14% |
| SP-12 v2 crypto settings | GBPUSD | 2020-22 | 59 | 36% | -5.7% | -7.2% | 0.59 | -9% |
| SP-12 v2 crypto settings | GBPUSD | 2023-now | 60 | 47% | -4.0% | -5.4% | 0.68 | +10% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2012-14 | 32 | 44% | -1.6% | -2.3% | 0.71 | +0% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2015-19 | 58 | 33% | -4.6% | -5.6% | 0.67 | -14% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2020-22 | 33 | 45% | +0.2% | -2.3% | 1.03 | -9% |
| SP-12 v2 crypto settings + DXY | GBPUSD | 2023-now | 42 | 40% | -3.4% | -4.0% | 0.57 | +10% |
| SP-12 v2 ATR-scaled | GBPUSD | 2012-14 | 69 | 28% | -6.3% | -8.9% | 0.66 | +0% |
| SP-12 v2 ATR-scaled | GBPUSD | 2015-19 | 107 | 20% | -14.9% | -17.7% **>10%** | 0.45 | -14% |
| SP-12 v2 ATR-scaled | GBPUSD | 2020-22 | 77 | 18% | -12.9% | -13.4% **>10%** | 0.35 | -9% |
| SP-12 v2 ATR-scaled | GBPUSD | 2023-now | 94 | 17% | -18.2% | -18.2% **>10%** | 0.30 | +10% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2012-14 | 47 | 26% | -5.4% | -7.5% | 0.58 | +0% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2015-19 | 73 | 21% | -12.8% | -13.9% **>10%** | 0.36 | -14% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2020-22 | 42 | 14% | -7.8% | -8.3% | 0.32 | -9% |
| SP-12 v2 ATR-scaled + DXY | GBPUSD | 2023-now | 73 | 15% | -14.9% | -14.9% **>10%** | 0.25 | +10% |
| Trend Rider | GBPUSD | 2012-14 | 46 | 33% | -3.9% | -4.6% | 0.68 | +0% |
| Trend Rider | GBPUSD | 2015-19 | 56 | 34% | -1.8% | -7.1% | 0.86 | -14% |
| Trend Rider | GBPUSD | 2020-22 | 40 | 20% | -5.8% | -6.8% | 0.38 | -9% |
| Trend Rider | GBPUSD | 2023-now | 56 | 30% | -3.8% | -7.2% | 0.75 | +10% |
| Trend Rider + DXY | GBPUSD | 2012-14 | 34 | 26% | -5.0% | -5.1% | 0.48 | +0% |
| Trend Rider + DXY | GBPUSD | 2015-19 | 41 | 37% | +0.0% | -5.1% | 1.00 | -14% |
| Trend Rider + DXY | GBPUSD | 2020-22 | 30 | 17% | -5.0% | -6.9% | 0.32 | -9% |
| Trend Rider + DXY | GBPUSD | 2023-now | 42 | 33% | -1.1% | -5.2% | 0.89 | +10% |
| SP-12 v4 crypto settings | USDJPY | 2012-14 | 60 | 53% | +5.1% | -5.7% | 1.38 | +56% |
| SP-12 v4 crypto settings | USDJPY | 2015-19 | 68 | 50% | -4.9% | -6.3% | 0.73 | -9% |
| SP-12 v4 crypto settings | USDJPY | 2020-22 | 42 | 55% | +5.6% | -4.1% | 1.64 | +21% |
| SP-12 v4 crypto settings | USDJPY | 2023-now | 61 | 61% | +3.5% | -2.3% | 1.29 | +20% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2012-14 | 42 | 67% | +9.2% | -2.4% | 2.46 | +56% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2015-19 | 52 | 48% | -4.2% | -5.9% | 0.70 | -9% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2020-22 | 34 | 59% | +6.7% | -2.3% | 2.01 | +21% |
| SP-12 v4 crypto settings + DXY | USDJPY | 2023-now | 41 | 54% | +0.8% | -2.1% | 1.09 | +20% |
| SP-12 v4 ATR-scaled | USDJPY | 2012-14 | 45 | 33% | +1.2% | -4.9% | 1.09 | +56% |
| SP-12 v4 ATR-scaled | USDJPY | 2015-19 | 80 | 28% | -12.4% | -12.7% **>10%** | 0.45 | -9% |
| SP-12 v4 ATR-scaled | USDJPY | 2020-22 | 38 | 39% | +1.8% | -4.6% | 1.18 | +21% |
| SP-12 v4 ATR-scaled | USDJPY | 2023-now | 47 | 40% | -3.4% | -5.0% | 0.73 | +20% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2012-14 | 30 | 33% | +3.0% | -4.2% | 1.34 | +56% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2015-19 | 52 | 25% | -9.3% | -10.0% | 0.37 | -9% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2020-22 | 26 | 38% | +3.2% | -3.0% | 1.48 | +21% |
| SP-12 v4 ATR-scaled + DXY | USDJPY | 2023-now | 28 | 43% | -3.0% | -5.0% | 0.62 | +20% |
| SP-12 v2 crypto settings | USDJPY | 2012-14 | 58 | 50% | +6.6% | -2.8% | 1.73 | +56% |
| SP-12 v2 crypto settings | USDJPY | 2015-19 | 96 | 46% | -8.5% | -8.9% | 0.60 | -9% |
| SP-12 v2 crypto settings | USDJPY | 2020-22 | 59 | 47% | +1.1% | -4.6% | 1.11 | +21% |
| SP-12 v2 crypto settings | USDJPY | 2023-now | 67 | 48% | +0.8% | -2.9% | 1.07 | +20% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2012-14 | 39 | 54% | +5.4% | -2.1% | 1.85 | +56% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2015-19 | 70 | 41% | -7.1% | -7.5% | 0.56 | -9% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2020-22 | 42 | 52% | +4.3% | -2.2% | 1.61 | +21% |
| SP-12 v2 crypto settings + DXY | USDJPY | 2023-now | 37 | 65% | +5.8% | -1.6% | 2.63 | +20% |
| SP-12 v2 ATR-scaled | USDJPY | 2012-14 | 82 | 29% | -6.4% | -9.8% | 0.68 | +56% |
| SP-12 v2 ATR-scaled | USDJPY | 2015-19 | 111 | 27% | -6.9% | -7.1% | 0.74 | -9% |
| SP-12 v2 ATR-scaled | USDJPY | 2020-22 | 80 | 20% | -10.7% | -13.2% **>10%** | 0.49 | +21% |
| SP-12 v2 ATR-scaled | USDJPY | 2023-now | 88 | 24% | -7.7% | -8.0% | 0.65 | +20% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2012-14 | 55 | 38% | -1.2% | -5.8% | 0.91 | +56% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2015-19 | 76 | 21% | -10.2% | -10.4% **>10%** | 0.48 | -9% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2020-22 | 59 | 24% | -6.1% | -8.3% | 0.60 | +21% |
| SP-12 v2 ATR-scaled + DXY | USDJPY | 2023-now | 54 | 24% | -4.9% | -6.5% | 0.61 | +20% |
| Trend Rider | USDJPY | 2012-14 | 47 | 40% | +4.8% | -4.8% | 1.41 | +56% |
| Trend Rider | USDJPY | 2015-19 | 74 | 23% | -10.6% | -10.8% **>10%** | 0.45 | -9% |
| Trend Rider | USDJPY | 2020-22 | 46 | 39% | +5.3% | -3.5% | 1.54 | +21% |
| Trend Rider | USDJPY | 2023-now | 74 | 28% | -7.1% | -7.8% | 0.57 | +20% |
| Trend Rider + DXY | USDJPY | 2012-14 | 32 | 50% | +5.3% | -2.3% | 1.75 | +56% |
| Trend Rider + DXY | USDJPY | 2015-19 | 58 | 21% | -10.0% | -10.6% **>10%** | 0.40 | -9% |
| Trend Rider + DXY | USDJPY | 2020-22 | 36 | 39% | +5.6% | -2.7% | 1.71 | +21% |
| Trend Rider + DXY | USDJPY | 2023-now | 48 | 25% | -7.1% | -7.5% | 0.42 | +20% |

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
