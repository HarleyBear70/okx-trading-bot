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
