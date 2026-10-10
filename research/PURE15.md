# PURE15: Jeff's pure 15m fib-pullback method (Oct 9 2026)

Script research/pure15.py (header = every rule and where it came from). Jeff's answers: To Claude/ideas/looking for answers.txt. BTC trial also tested trail-to-breakeven: worse in all 16 versions, left out.


### crypto: BTC ETH SOL XRP, 15m only. Crypto: taker 0.02% + 0.02% slippage, maker 0% targets. Forex: OANDA spread

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| swing 3, cushion 0, touch, target near | 4054 | 22% | +3.43R | -1.36R | 0.70 | -0.32R | 10021R | 0.76 | 0.66 | 0.69 | 0.71 |
| swing 3, cushion 0, touch, target 2R | 4334 | 24% | +3.21R | -1.24R | 0.81 | -0.18R | 6089R | 0.80 | 0.82 | 0.83 | 0.79 |
| swing 3, cushion 0, green, target near | 1674 | 23% | +3.07R | -1.34R | 0.69 | -0.32R | 4209R | 0.74 | 0.64 | 0.71 | 0.67 |
| swing 3, cushion 0, green, target 2R | 2880 | 24% | +3.01R | -1.23R | 0.78 | -0.20R | 4578R | 0.79 | 0.77 | 0.80 | 0.76 |
| swing 3, cushion 0.05%, touch, target near | 3253 | 22% | +3.20R | -1.24R | 0.74 | -0.25R | 6359R | 0.76 | 0.72 | 0.74 | 0.74 |
| swing 3, cushion 0.05%, touch, target 2R | 4012 | 24% | +3.12R | -1.16R | 0.84 | -0.14R | 4406R | 0.84 | 0.84 | 0.84 | 0.84 |
| swing 3, cushion 0.05%, green, target near | 1194 | 24% | +2.94R | -1.24R | 0.73 | -0.25R | 2341R | 0.76 | 0.71 | 0.78 | 0.69 |
| swing 3, cushion 0.05%, green, target 2R | 2708 | 24% | +2.97R | -1.18R | 0.80 | -0.18R | 3766R | 0.80 | 0.80 | 0.82 | 0.78 |
| swing 5, cushion 0, touch, target near | 2599 | 22% | +3.44R | -1.29R | 0.75 | -0.26R | 5169R | 0.77 | 0.72 | 0.74 | 0.75 |
| swing 5, cushion 0, touch, target 2R | 2952 | 23% | +3.24R | -1.17R | 0.83 | -0.15R | 3476R | 0.84 | 0.82 | 0.85 | 0.82 |
| swing 5, cushion 0, green, target near | 1583 | 22% | +3.28R | -1.27R | 0.74 | -0.26R | 3180R | 0.76 | 0.72 | 0.72 | 0.75 |
| swing 5, cushion 0, green, target 2R | 2259 | 23% | +3.18R | -1.19R | 0.81 | -0.17R | 3062R | 0.81 | 0.81 | 0.80 | 0.82 |
| swing 5, cushion 0.05%, touch, target near | 2184 | 22% | +3.23R | -1.21R | 0.76 | -0.22R | 3802R | 0.76 | 0.76 | 0.77 | 0.76 |
| swing 5, cushion 0.05%, touch, target 2R | 2775 | 23% | +3.14R | -1.14R | 0.83 | -0.15R | 3205R | 0.82 | 0.84 | 0.84 | 0.82 |
| swing 5, cushion 0.05%, green, target near | 1264 | 22% | +3.13R | -1.21R | 0.75 | -0.24R | 2340R | 0.75 | 0.74 | 0.74 | 0.75 |
| swing 5, cushion 0.05%, green, target 2R | 2139 | 23% | +3.09R | -1.16R | 0.81 | -0.17R | 2894R | 0.79 | 0.82 | 0.80 | 0.81 |
| ZERO FEES: swing 3, cushion 0.05%, touch, target 2R | 4012 | 24% | +3.19R | -1.00R | 1.00 | -0.00R | 313R | 0.98 | 1.01 | 1.00 | 1.00 |
| ZERO FEES: swing 5, cushion 0.05%, green, target near | 1264 | 22% | +3.22R | -1.00R | 0.93 | -0.05R | 556R | 0.92 | 0.94 | 0.93 | 0.93 |

### forex/gold: EUR_USD GBP_USD AUD_USD USD_JPY XAU_USD, 15m only. Crypto: taker 0.02% + 0.02% slippage, maker 0% targets. Forex: OANDA spread

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| swing 3, cushion 0, touch, target near | 3692 | 21% | +3.23R | -1.51R | 0.57 | -0.51R | 14786R | 0.56 | 0.57 | 0.57 | 0.57 |
| swing 3, cushion 0, touch, target 2R | 3267 | 23% | +3.07R | -1.30R | 0.71 | -0.29R | 7495R | 0.70 | 0.71 | 0.71 | 0.71 |
| swing 3, cushion 0, green, target near | 1409 | 22% | +2.90R | -1.52R | 0.55 | -0.53R | 5846R | 0.53 | 0.57 | 0.56 | 0.54 |
| swing 3, cushion 0, green, target 2R | 2374 | 23% | +2.92R | -1.34R | 0.66 | -0.35R | 6430R | 0.63 | 0.70 | 0.67 | 0.65 |
| swing 3, cushion 0.05%, touch, target near | 1138 | 24% | +2.82R | -1.18R | 0.75 | -0.23R | 2042R | 0.76 | 0.74 | 0.77 | 0.73 |
| swing 3, cushion 0.05%, touch, target 2R | 2031 | 26% | +2.69R | -1.13R | 0.82 | -0.15R | 2348R | 0.83 | 0.82 | 0.83 | 0.82 |
| swing 3, cushion 0.05%, green, target near | 300 | 25% | +2.64R | -1.18R | 0.73 | -0.24R | 564R | 0.75 | 0.71 | 0.70 | 0.76 |
| swing 3, cushion 0.05%, green, target 2R | 1725 | 25% | +2.78R | -1.14R | 0.82 | -0.16R | 2103R | 0.81 | 0.82 | 0.82 | 0.82 |
| swing 5, cushion 0, touch, target near | 2468 | 21% | +3.32R | -1.40R | 0.63 | -0.41R | 7817R | 0.61 | 0.65 | 0.62 | 0.64 |
| swing 5, cushion 0, touch, target 2R | 2264 | 23% | +3.10R | -1.25R | 0.74 | -0.25R | 4375R | 0.71 | 0.78 | 0.75 | 0.74 |
| swing 5, cushion 0, green, target near | 1390 | 22% | +3.19R | -1.39R | 0.63 | -0.40R | 4362R | 0.61 | 0.65 | 0.61 | 0.65 |
| swing 5, cushion 0, green, target 2R | 1894 | 23% | +3.06R | -1.27R | 0.72 | -0.28R | 4050R | 0.72 | 0.72 | 0.71 | 0.73 |
| swing 5, cushion 0.05%, touch, target near | 949 | 24% | +2.88R | -1.29R | 0.70 | -0.30R | 2214R | 0.62 | 0.80 | 0.63 | 0.77 |
| swing 5, cushion 0.05%, touch, target 2R | 1508 | 25% | +2.77R | -1.12R | 0.83 | -0.14R | 1700R | 0.82 | 0.83 | 0.83 | 0.82 |
| swing 5, cushion 0.05%, green, target near | 439 | 24% | +2.84R | -1.16R | 0.79 | -0.18R | 622R | 0.74 | 0.85 | 0.82 | 0.77 |
| swing 5, cushion 0.05%, green, target 2R | 1398 | 25% | +2.85R | -1.12R | 0.83 | -0.15R | 1601R | 0.86 | 0.79 | 0.86 | 0.80 |
| ZERO FEES: swing 3, cushion 0.05%, touch, target 2R | 2031 | 26% | +2.81R | -1.01R | 0.96 | -0.03R | 551R | 0.98 | 0.95 | 0.97 | 0.96 |
| ZERO FEES: swing 5, cushion 0.05%, green, target near | 439 | 24% | +3.00R | -1.01R | 0.96 | -0.03R | 135R | 0.92 | 1.00 | 0.99 | 0.92 |


Verdict: FAILS. With zero costs the method is break-even (PF 0.93-1.00), so there's no edge for fees to eat; real costs
take it to PF 0.55-0.84. It also trades far more than Jeff does (1,000-4,000 trades a year on 4 coins).
Cushion 0.05% beats no cushion in every pair (forex much more: 0.57 -> 0.75), because it widens the tiny stops.

## Oct 9 round 2: Jeff's rules 1-4 (flat filter, opposite shift cancels, smaller swings, deeper entry) + enter only on a candle CLOSE

`python3 research/pure15.py v2`

### BTC ETH SOL XRP, 15m only, 0.05% cushion, buy on a candle CLOSE at/below the fib level, 2:1 target, Binance.US costs

| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |
|---|---|---|---|---|---|---|---|---|---|---|---|
| swing 1, flat off, entry at 50.0% | 8039 | 23% | +3.26R | -1.31R | 0.74 | -0.27R | 16702R | 0.75 | 0.72 | 0.72 | 0.75 |
| swing 1, flat off, entry at 61.8% | 8790 | 21% | +3.45R | -1.42R | 0.66 | -0.38R | 25775R | 0.68 | 0.65 | 0.65 | 0.67 |
| swing 1, flat off, entry at 70.5% | 8110 | 20% | +3.75R | -1.53R | 0.61 | -0.48R | 30492R | 0.62 | 0.59 | 0.60 | 0.61 |
| swing 1, flat off, entry at 78.6% | 6386 | 17% | +4.59R | -1.65R | 0.57 | -0.59R | 29365R | 0.58 | 0.55 | 0.57 | 0.57 |
| swing 1, flat after 8 candles, entry at 50.0% | 7340 | 23% | +3.23R | -1.30R | 0.73 | -0.27R | 15553R | 0.74 | 0.72 | 0.71 | 0.75 |
| swing 1, flat after 8 candles, entry at 61.8% | 7687 | 21% | +3.44R | -1.41R | 0.66 | -0.38R | 22652R | 0.67 | 0.65 | 0.65 | 0.67 |
| swing 1, flat after 8 candles, entry at 70.5% | 6801 | 20% | +3.75R | -1.52R | 0.60 | -0.48R | 25552R | 0.62 | 0.59 | 0.60 | 0.61 |
| swing 1, flat after 8 candles, entry at 78.6% | 5144 | 17% | +4.63R | -1.64R | 0.57 | -0.60R | 23816R | 0.58 | 0.55 | 0.57 | 0.56 |
| swing 1, flat after 16 candles, entry at 50.0% | 7996 | 23% | +3.26R | -1.31R | 0.74 | -0.27R | 16527R | 0.75 | 0.72 | 0.72 | 0.76 |
| swing 1, flat after 16 candles, entry at 61.8% | 8717 | 21% | +3.45R | -1.42R | 0.66 | -0.38R | 25522R | 0.68 | 0.65 | 0.65 | 0.67 |
| swing 1, flat after 16 candles, entry at 70.5% | 8010 | 20% | +3.76R | -1.53R | 0.61 | -0.48R | 30021R | 0.62 | 0.59 | 0.60 | 0.61 |
| swing 1, flat after 16 candles, entry at 78.6% | 6281 | 17% | +4.59R | -1.65R | 0.57 | -0.59R | 28746R | 0.59 | 0.56 | 0.57 | 0.57 |
| swing 1, flat after 32 candles, entry at 50.0% | 8038 | 23% | +3.26R | -1.31R | 0.74 | -0.27R | 16703R | 0.75 | 0.72 | 0.72 | 0.75 |
| swing 1, flat after 32 candles, entry at 61.8% | 8790 | 21% | +3.45R | -1.42R | 0.66 | -0.38R | 25777R | 0.68 | 0.65 | 0.65 | 0.67 |
| swing 1, flat after 32 candles, entry at 70.5% | 8109 | 20% | +3.75R | -1.53R | 0.61 | -0.48R | 30483R | 0.62 | 0.59 | 0.60 | 0.61 |
| swing 1, flat after 32 candles, entry at 78.6% | 6386 | 17% | +4.59R | -1.65R | 0.57 | -0.59R | 29355R | 0.58 | 0.55 | 0.57 | 0.57 |
| swing 3, flat off, entry at 50.0% | 4158 | 22% | +3.39R | -1.22R | 0.79 | -0.20R | 6368R | 0.81 | 0.78 | 0.79 | 0.79 |
| swing 3, flat off, entry at 61.8% | 4734 | 21% | +3.63R | -1.30R | 0.73 | -0.28R | 10366R | 0.75 | 0.70 | 0.73 | 0.73 |
| swing 3, flat off, entry at 70.5% | 4652 | 19% | +4.03R | -1.40R | 0.67 | -0.38R | 13617R | 0.70 | 0.64 | 0.67 | 0.66 |
| swing 3, flat off, entry at 78.6% | 3868 | 15% | +5.34R | -1.51R | 0.62 | -0.49R | 14842R | 0.65 | 0.59 | 0.63 | 0.61 |
| swing 3, flat after 8 candles, entry at 50.0% | 2685 | 23% | +3.23R | -1.20R | 0.79 | -0.19R | 4005R | 0.79 | 0.80 | 0.77 | 0.82 |
| swing 3, flat after 8 candles, entry at 61.8% | 2564 | 21% | +3.49R | -1.28R | 0.73 | -0.27R | 5384R | 0.73 | 0.74 | 0.71 | 0.75 |
| swing 3, flat after 8 candles, entry at 70.5% | 2119 | 19% | +3.95R | -1.36R | 0.67 | -0.37R | 6031R | 0.68 | 0.66 | 0.66 | 0.68 |
| swing 3, flat after 8 candles, entry at 78.6% | 1523 | 14% | +5.27R | -1.47R | 0.60 | -0.51R | 6042R | 0.62 | 0.58 | 0.59 | 0.60 |
| swing 3, flat after 16 candles, entry at 50.0% | 3664 | 22% | +3.34R | -1.21R | 0.78 | -0.21R | 5962R | 0.79 | 0.77 | 0.78 | 0.78 |
| swing 3, flat after 16 candles, entry at 61.8% | 4021 | 21% | +3.58R | -1.30R | 0.71 | -0.29R | 9198R | 0.73 | 0.70 | 0.71 | 0.72 |
| swing 3, flat after 16 candles, entry at 70.5% | 3751 | 19% | +3.98R | -1.39R | 0.66 | -0.39R | 11269R | 0.67 | 0.65 | 0.65 | 0.66 |
| swing 3, flat after 16 candles, entry at 78.6% | 2965 | 15% | +5.28R | -1.50R | 0.60 | -0.52R | 11927R | 0.62 | 0.57 | 0.60 | 0.60 |
| swing 3, flat after 32 candles, entry at 50.0% | 4130 | 22% | +3.40R | -1.22R | 0.79 | -0.19R | 6271R | 0.81 | 0.78 | 0.79 | 0.80 |
| swing 3, flat after 32 candles, entry at 61.8% | 4690 | 21% | +3.64R | -1.30R | 0.73 | -0.28R | 10184R | 0.76 | 0.71 | 0.73 | 0.73 |
| swing 3, flat after 32 candles, entry at 70.5% | 4590 | 19% | +4.04R | -1.40R | 0.67 | -0.38R | 13446R | 0.70 | 0.64 | 0.67 | 0.66 |
| swing 3, flat after 32 candles, entry at 78.6% | 3796 | 15% | +5.34R | -1.51R | 0.61 | -0.50R | 14682R | 0.65 | 0.58 | 0.62 | 0.61 |
| swing 5, flat off, entry at 50.0% | 2890 | 22% | +3.45R | -1.19R | 0.81 | -0.18R | 4056R | 0.79 | 0.82 | 0.80 | 0.81 |
| swing 5, flat off, entry at 61.8% | 3241 | 21% | +3.73R | -1.25R | 0.78 | -0.22R | 5605R | 0.78 | 0.78 | 0.78 | 0.77 |
| swing 5, flat off, entry at 70.5% | 3261 | 19% | +4.16R | -1.34R | 0.71 | -0.31R | 7886R | 0.71 | 0.72 | 0.71 | 0.72 |
| swing 5, flat off, entry at 78.6% | 2803 | 14% | +5.70R | -1.44R | 0.67 | -0.41R | 8933R | 0.68 | 0.66 | 0.65 | 0.68 |
| swing 5, flat after 8 candles, entry at 50.0% | 1502 | 22% | +3.29R | -1.17R | 0.80 | -0.18R | 2133R | 0.78 | 0.82 | 0.76 | 0.84 |
| swing 5, flat after 8 candles, entry at 61.8% | 1301 | 20% | +3.65R | -1.23R | 0.75 | -0.25R | 2524R | 0.73 | 0.76 | 0.74 | 0.75 |
| swing 5, flat after 8 candles, entry at 70.5% | 1012 | 17% | +4.26R | -1.31R | 0.68 | -0.35R | 2730R | 0.65 | 0.70 | 0.69 | 0.67 |
| swing 5, flat after 8 candles, entry at 78.6% | 703 | 13% | +5.90R | -1.41R | 0.61 | -0.48R | 2619R | 0.59 | 0.63 | 0.59 | 0.63 |
| swing 5, flat after 16 candles, entry at 50.0% | 2033 | 22% | +3.36R | -1.18R | 0.79 | -0.19R | 2995R | 0.76 | 0.83 | 0.78 | 0.80 |
| swing 5, flat after 16 candles, entry at 61.8% | 2148 | 21% | +3.62R | -1.24R | 0.76 | -0.23R | 3872R | 0.75 | 0.78 | 0.76 | 0.77 |
| swing 5, flat after 16 candles, entry at 70.5% | 1950 | 19% | +4.02R | -1.31R | 0.70 | -0.33R | 4936R | 0.69 | 0.70 | 0.70 | 0.69 |
| swing 5, flat after 16 candles, entry at 78.6% | 1522 | 14% | +5.57R | -1.41R | 0.64 | -0.43R | 5123R | 0.64 | 0.64 | 0.62 | 0.67 |
| swing 5, flat after 32 candles, entry at 50.0% | 2725 | 22% | +3.45R | -1.19R | 0.81 | -0.18R | 3854R | 0.79 | 0.82 | 0.80 | 0.82 |
| swing 5, flat after 32 candles, entry at 61.8% | 3024 | 21% | +3.73R | -1.25R | 0.77 | -0.23R | 5298R | 0.78 | 0.77 | 0.77 | 0.77 |
| swing 5, flat after 32 candles, entry at 70.5% | 2988 | 18% | +4.16R | -1.33R | 0.71 | -0.32R | 7383R | 0.71 | 0.70 | 0.70 | 0.71 |
| swing 5, flat after 32 candles, entry at 78.6% | 2505 | 14% | +5.74R | -1.44R | 0.67 | -0.41R | 7980R | 0.68 | 0.66 | 0.65 | 0.68 |


Verdict: FAILS. Best PF 0.81 (swing 5, 50%). Deeper fib entries are worse every time (tighter stops, more fee drag). The flat filter barely changes PF. Swing 1 doubles trades and is worse.
