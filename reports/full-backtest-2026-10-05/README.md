# Full backtest, Oct 5 2026

Every bot, tested on its live coins and its live rules: selling half at +2R, 0.5% risk per trade and the same stops as `bot.py`. Read this page first. The other files have the full tables.

## The short version

1. **Trend Rider is the best bot by a long way.** +195% since May 2018 with a worst drop of 8.4%. It made money in both halves of the test and passes every rule on the scoreboard.
2. **SP-12 v4 is good but sits right on the line.** +93%, but its worst drop is 10.2%, just over the 10% rule. That drop came in the 2nd half (2022 to now).
3. **NNFX Aroon (paper backup) looks strong.** +56%, worst drop 7.3%, profit factor 2.28, and it made money in both halves. This is the first time it has been on the scoreboard.
4. **B3 pairs and B1c (paper) are small but steady.** About +15% each over 8 years, with drops under 6%. They're safe, but there isn't much to them.
5. **The paused bots should stay paused.** SP-12 v2 (+5%, 20.9% drop) and Trend Rider gold (-1%) still don't work.
6. **Keep risk step-ups OFF.** They push every bot's worst drop over 10%. They only add a lot of profit to Trend Rider, and even there the drop goes from 8.4% to 13.9%. Details are below and in [STEP_UPS.md](STEP_UPS.md).

## Test 1: every bot, 2018 to now (main test)

$1,000 start, 0.5% risk per trade, 0.1% fee each side, max 3 trades open. Each bot is tested on the coins it trades live, from May 2018 to today, then on each half separately (2018 to 2021, and 2022 to now). A bot that only works in one half is probably luck.

"Worst drop" is the biggest fall from a high point. "Return ÷ drop" is how much you earn for each 1% of pain, and higher is better. "PF" (profit factor) is the dollars won for every dollar lost.

### Bots running now

| Bot | Coins | Return | Worst drop | Return ÷ drop | PF | Trades | 2018-2021 | 2022-now |
|---|---|---|---|---|---|---|---|---|
| Trend Rider (demo) | BTC ETH SOL BNB SUI TRX | **+195%** | 8.4% | **23.1** | 1.87 | 684 | +59% | +86% |
| SP-12 v4 (demo) | BTC ETH XRP XLM BNB | +93% | **10.2%** | 9.2 | 1.35 | 735 | +50% | +28% |
| NNFX Aroon (paper) | BTC ETH XRP, daily | +56% | 7.3% | 7.6 | **2.28** | 193 | +23% | +27% |
| SP-12 v4 Kraken (paper) | BTC ETH XRP | +55% | 9.9% | 5.6 | 1.34 | 493 | +29% | +20% |
| B3 pairs (paper) | ETH/BTC, XRP/BTC | +14% | 5.4% | 2.6 | 1.52 | 105 | +6% | +8% |
| B1c breakout retest (paper) | BTC ETH XRP, 1H | +15% | 5.8% | 2.6 | 1.26 | 217 | +8% | +7% |

### Paused bots

| Bot | Coins | Return | Worst drop | PF | 2018-2021 | 2022-now |
|---|---|---|---|---|---|---|
| SP-12 v2 | ETH SOL XAUT | +5% | 20.9% | 1.02 | -12% | +19% |
| Trend Rider gold | XAUT (from 2020) | -1% | 16.3% | 0.97 | -3% | +2% |

The research bots that already failed were tested again and still fail. They're in the full table in [SCOREBOARD.md](../../SCOREBOARD.md).

**For comparison:**
- Running v4 and Trend Rider together, half the money each: +99% with a worst drop of 6.6%. That's a smoother ride than either bot alone.
- Just buying BTC and holding it: +863%, but with a 77% drop along the way. The bots make much less in total, but they never come close to that kind of drop.

## Test 2: risk step-ups off vs on

Step-ups raise risk from 0.5% to 1.25%, 1.5% or 2% as the balance grows 10%, 25% or 50%. Risk drops back to 0.5% if the balance falls 5% from its best. This only applies to the bots that size trades through `risk_pct()` in `bot.py`.

| Bot (full test) | Step-ups off | Step-ups on |
|---|---|---|
| Trend Rider | +195%, drop 8.4% | +527%, drop **13.9%** |
| SP-12 v4 | +93%, drop 10.2% | +82%, drop **15.8%** |
| SP-12 v4 Kraken | +55%, drop 9.9% | +44%, drop **15.3%** |
| NNFX Aroon | +56%, drop 7.3% | +62%, drop **11.3%** |

Step-ups break the 10% drop rule on every bot. On SP-12 v4 they make *less* money as well. Trend Rider is the only bot where they pay off a lot, but you'd have to accept drops near 14%. My advice is to keep them off. If you ever want them, try them on Trend Rider only.

The two paused bots don't change, because their balance never gets 10% above the start. The half-by-half numbers are in [STEP_UPS.md](STEP_UPS.md).

## Test 3: Freqtrade on OKX prices (March 2024 to now)

This is a second, independent check using Freqtrade (the free backtest software) on OKX's own prices. The period is shorter, and it uses the older coin lists. The full results are in [freqtrade/results/SUMMARY.md](../../freqtrade/results/SUMMARY.md).

| Strategy | Step-ups off | Step-ups on |
|---|---|---|
| SP-12 v4 | +26%, drop 7.0% | +21%, drop 11.8% |
| SP-12 v2 | +11%, drop 5.9% | +10%, drop 6.2% |
| Trend Rider | +10%, drop 4.3% | +7%, drop 4.3% |

- **Skeptic check:** v4, v2, Trend Rider and Trend Rider gold all made money in both halves, March 2024 to June 2025 and July 2025 to now ([SKEPTIC.md](../../freqtrade/results/SKEPTIC.md)).
- **Coin scan:**
  - Best coins for v4 were XRP, BNB and ETH. SOL, AVAX and ADA lost a little.
  - Best coins for Trend Rider were BNB and BTC. ETH and AVAX lost a little ([COINSCAN.md](../../freqtrade/results/COINSCAN.md)).

Over this short recent period Freqtrade has v4 ahead of Trend Rider. The 8-year test says the opposite. That's a reason not to read too much into any one period.

## Things to keep in mind

- **Backtests are best-case.** Fills happen exactly at the stop or target, with no slippage. Real results will be a bit worse.
- **The Trend Rider row doesn't include the Fear & Greed filter** (no new buys when the index is 25 or below). That filter was added today, and there's no Fear & Greed history going back to 2018.
- **SP-12 v4's 10.2% drop is right at the "stop the bot" line** (rule 3). It's worth watching. Running it alongside Trend Rider brings the combined drop down to 6.6%.
- **Fixed alongside this run:**
  - The scoreboard now includes NNFX, which was missing.
  - Trend Rider is now tested on its live coin list, which includes TRX.

## How this was run

- Test 1: `python research/scoreboard.py` (rewrites the table in SCOREBOARD.md)
- Test 2: `python research/steps_compare.py OUT.md`
- Test 3: GitHub Actions → Freqtrade backtest (run today, 17:00 UTC)
- Price data: Binance/Bitfinex 4H history up to Oct 5 2026 04:00 UTC
