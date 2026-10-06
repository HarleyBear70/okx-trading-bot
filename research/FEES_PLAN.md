# F1: real OKX fees (plan, written before running)

2026-10-05. The user's OKX account (live and demo) is spot Lv1: **0.35% taker, 0.20% maker** (account_get_trade_fee). bot.py assumes 0.1%. At 0.35% SP-12 v4 loses money over 8 years (−2%, PF 0.99, DD −31%); Trend Rider still makes +185% (DD −11.8%). The user asked: "whatever will make me money, can we see what it will do if we change things."

Research only: bot.py is not changed (the bots are frozen until the Oct 19 review). Script: research/fees_test.py. Results: research/FEES.md.

## Fee setups
- **T (now):** market orders both ways, 0.35% buy + 0.35% sell. The breakeven buffer is the real round trip (0.7%).
- **M (limit entry):** limit buy at the signal candle's close (maker 0.20%); exits stay market orders (0.35%), since stops must fill. The breakeven buffer is 0.55%. Optimistic: it assumes every limit buy fills, though a real one can miss a fast breakout.

## Variants (max 3 per bot), each under T and M, with each bot's live settings (risk, no half sell)
- SP-12 v4 as now (min stop 1%, max 4%, score ≥ 2)
- V1: min stop 2% (fees become a smaller share of each R)
- V2: min stop 3%, max stop 6%
- V3: score ≥ 3 (fewer, stronger trades)
- Trend Rider as now (no fear filter, like SCOREBOARD.md)
- NNFX Aroon (daily, BTC ETH XRP; already a paper backup), as a possible replacement for v4

Periods: 2018-05 to now, plus the halves (2018-05 to 2021, 2022 to now), each starting with a fresh $1,000.

## Pass rules (SCOREBOARD.md)
Positive in both halves, PF ≥ 1.3 over the full period, max drawdown ≤ 10% (the stop rule). A bot that fails under T but passes under M passes only if it switches to limit entries.

## F1b (added 2026-10-05 after F1, before running): the remaining bots, and risk size
The user asked which bots can make money the way they trade. Same T fees, same pass rules.
- B3 pairs (daily, paper) and B1c breakout retest (1H, paper) at real fees
- Trend Rider at 0.4% risk (brings its 11.8% drop under the 10% rule?)
- NNFX at 0.75% and 1% risk (its 7.6% drop leaves room; does the profit scale up and stay under 10%?)
