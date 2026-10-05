# NNFX-style daily system

Plan and rules fixed beforehand in research/IDEAS_PLAN.md. Choices made on the SELECTION period only (forex 2012-2018 long+short, crypto 2018-05 to 2021 long only); the finished system is judged once on the later period. Script: research/nnfx.py.

## Step 1: C1 confirmation (selection period)

| Candidate | Pooled PF | Forex trades / return / PF | Crypto trades / return / PF |
|---|---|---|---|
| Aroon(25) | 1.86 | 171 / +16.4% / 1.54 | 80 / +23.3% / 2.48 |
| Vortex(14) | 1.16 | 320 / -3.3% / 0.93 | 181 / +16.0% / 1.53 |
| SSL(10) | 1.16 | 267 / -10.7% / 0.80 | 154 / +24.4% / 1.83 |

Kept: **Aroon(25)** (pooled PF 1.86).

## Step 2: baseline

| Candidate | Pooled PF | Forex trades / return / PF | Crypto trades / return / PF |
|---|---|---|---|
| Aroon(25) + Kijun(26) | 1.72 | 159 / +5.3% / 1.19 | 64 / +24.2% / 2.85 |
| Aroon(25) + HMA(30) | 1.47 | 136 / +4.8% / 1.20 | 53 / +10.5% / 2.15 |
| Aroon(25) + KAMA(10,2,30) | 1.80 | 146 / +4.4% / 1.17 | 54 / +24.7% / 3.37 |

No baseline beats C1 alone (1.86); none kept.

## Step 3: volume / strength filter

| Candidate | Pooled PF | Forex trades / return / PF | Crypto trades / return / PF |
|---|---|---|---|
| ... + ADX(14) > 20 | 1.69 | 75 / +9.3% / 1.80 | 45 / +5.2% / 1.56 |
| ... + ADX(14) rising | 1.73 | 78 / +12.4% / 2.11 | 23 / -0.6% / 0.89 |
| ... + ATR(14) above its 50-day average | 1.45 | 67 / +0.1% / 1.01 | 18 / +6.0% / 3.76 |

No filter beats step 2 (1.86); none kept.

## Step 4: exit indicator for the runner half

| Candidate | Pooled PF | Forex trades / return / PF | Crypto trades / return / PF |
|---|---|---|---|
| ... exit: opposite C1 flip | 1.86 | 171 / +16.4% / 1.54 | 80 / +23.3% / 2.48 |
| ... exit: PSAR flip | 1.18 | 206 / -5.6% / 0.82 | 80 / +13.5% / 2.04 |

Kept: **opposite C1 flip** (pooled PF 1.86).

Finished system: {'c1': 'Aroon(25)', 'exit': 'opposite C1 flip'}

## The finished system on the LATER period (judged once)

| Group | Period | Trades | Win % | Return | Max DD | PF |
|---|---|---|---|---|---|---|
| forex (long+short) | 2019-now | 168 | 60% | -8.4% | -8.8% | 0.74 |
| crypto (long only) | 2022-now | 113 | 61% | +26.8% | -5.4% | 2.20 |
| never-seen forex (AUDUSD, NZDUSD, USDCAD, USDCHF) | later period | 240 | | P/L -148 USD | worst -8.9% | 0.72 |
| never-seen crypto (SOL, LTC, DOGE, XLM, ADA, BNB, LINK, BCH, AVAX, SUI) | later period | 364 | | P/L +246 USD | worst -10.6% | 1.34 |

Crypto version 2018-05 to now: +55.8% / DD -7.3% / PF 2.28; correlation with v4+TR 0.75; portfolio return/DD 14.54 vs v4+TR 15.07.

Result: FAIL - forex not profitable; never-seen forex PF 0.72; crypto correlation 0.75; portfolio return/DD 14.54 not above 15.07
