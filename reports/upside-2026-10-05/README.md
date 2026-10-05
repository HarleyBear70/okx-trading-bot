# Getting more out of the bots (Oct 5 2026)

Jeff asked whether the bots can get to 60-70%. This tests three ideas on 8 years of prices (May 2018 to now), plus each half on its own. Nothing live has changed. Full tables: [TABLES.md](TABLES.md).

## The short version

- **60-70% in total: yes, easily.** The current setup already makes +144% over 8 years (v4 + Trend Rider together).
- **60-70% per year: no.** Even the riskiest setup tested made about 35% a year, with a 17.5% drop. Anything near 60% a year would mean drops of 30% or more.
- **The best change by far is to stop selling half at +2R.** Both main bots made much more money, in both halves of the test, with only a small rise in the worst drop.
- **Best setup that stays under the 10% drop rule:** no half sell, 0.5% risk, and 70% of the money in Trend Rider. That's **+286% over 8 years (about +17% a year), worst drop 9.4%**. The current setup gives +144% (about +11% a year), worst drop 7.4%.

## A. Stop selling half at +2R

| Bot | Now (half at +2R) | No half sell |
|---|---|---|
| SP-12 v4 | +93%, +8.1%/yr, drop 10.2%, PF 1.35 | **+170%, +12.5%/yr, drop 11.9%, PF 1.52** |
| Trend Rider | +195%, +13.7%/yr, drop 8.4%, PF 1.87 | **+336%, +19.1%/yr, drop 9.8%, PF 2.20** |
| SP-12 v2 (paused, test run) | -4%, drop 17.3% | +0%, drop 17.5% |

- **It held up in both halves of the test.** v4 went +50% → +77% (2018-2021) and +28% → +53% (2022-now). Trend Rider went +59% → +84% and +86% → +137%.
- **Freqtrade on OKX prices agrees.** That test was run separately, on 2024 to now: v4 went +26% → +57%.
- **Why it works:** these bots make their money on a few big runners. Selling half at +2R cuts every one of those in half.
- **The catch:** v4's worst drop without the half sell is 11.9%. That's over the 10% "stop the bot" rule, and it would have been hit once (2022-now). Trend Rider stays under at 9.8%.
- **SP-12 v2 test run:** it has no edge with or without the half sell, so it should stay paused.

## B. More risk per trade on the v4 + Trend Rider pair

Each bot keeps its own $1,000, the same as live. These are the two bots' results added together.

| Half sell | Risk | Split v4 / TR | 8 years | Per year | Worst drop |
|---|---|---|---|---|---|
| yes (now) | 0.5% | 50 / 50 | +144% | +11.2% | 7.4% |
| yes | 0.75% | 50 / 50 | +276% | +17.0% | 11.1% |
| yes | 1% | 50 / 50 | +470% | +22.9% | 13.6% |
| **no** | **0.5%** | **30 / 70** | **+286%** | **+17.4%** | **9.4%** |
| no | 0.5% | 50 / 50 | +253% | +16.1% | 9.1% |
| no | 0.75% | 30 / 70 | +629% | +26.6% | 13.6% |
| no | 1% | 30 / 70 | +1179% | +35.3% | 17.5% |

More risk grows the money faster, but every setup above 0.5% breaks the 10% drop rule. Removing the half sell gets about the same gain as going to 0.75% risk, with a smaller drop. That makes it the better first step.

## C. More money behind Trend Rider

A 30/70 split (v4 / Trend Rider) beat 50/50 in every row, by about +1 to +2% a year. The worst drop rose by about half a point. Be careful with this one, though: Trend Rider is favoured because it did better *in this same data*. It's a sensible tilt, not a sure thing.

## What I'd suggest (Jeff decides)

1. **Turn off the half sell on Trend Rider first.** It gains the most (+195% → +336%) and stays under 10% drop.
2. **For v4, pick one:**
   - keep the half sell, or
   - drop the half sell and lower v4's risk to about 0.4% so its drop stays under 10%.

   I can test the 0.4% version.
3. **Keep risk at 0.5%** while the 10% rule stands.
4. **Before anything goes live:** run the no-half-sell change on never-seen coins (the usual pass rule), then forward test it on paper next to the live bots for 2-3 weeks.

## Things to keep in mind

- Backtests are best-case (exact fills, no slippage), so live results will be a bit lower.
- Trend Rider is tested without the Fear & Greed filter, which has no history back to 2018.
- The pair here uses each bot's live coins. The scoreboard's "50/50 v4 + Trend Rider" reference line uses the older 3-coin lists, so its +99% isn't comparable.
