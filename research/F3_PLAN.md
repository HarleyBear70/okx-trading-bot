# F3: smart-money entries on Trend Rider (plan, written before running)

2026-10-06. The user learned smart-money concepts (market structure, BOS, order blocks, premium/discount, supply/demand, liquidity) and asked for a bot that fits that style: "if u suggest something then lets try it and see if it works." Trend Rider already buys a break of structure (4H close above the last swing high, with the 4H and daily trend up). Smart-money traders usually avoid buying the break itself, which is in premium. They wait for a pullback into discount, or for a liquidity sweep first. This test checks whether either makes Trend Rider better.

Research only. Script: research/f3_smc.py. Results: research/F3.md. Real fee 0.35% per side, Trend Rider's coins (BTC ETH SOL BNB SUI TRX), 4H, 0.4% risk, max 3 open, 2018-05 to now plus the halves. Every variant runs in the same simulator (engine.trade_sim) with the same exit: Trend Rider's first stop, then trailing at the highest close − 3 ATR(14). Only the entry differs.

- S0 (baseline): buy the BOS candle's close (Trend Rider's entry, no fear filter).
- S1 BOS + discount: after a BOS, wait up to 12 candles (2 days) for price to trade down to the 50% level (equilibrium) between the stop and the BOS close. Buy at that candle's close if it is still above the stop. Same stop.
- S2 liquidity sweep + BOS: take the BOS only if, in the 20 candles before it, a candle wicked below the last confirmed swing low and closed back above it (sell-side liquidity taken).

Pass: better than S0 on return/DD in both halves, with PF ≥ 1.3 and DD ≤ 10%. Otherwise Trend Rider stays as it is.
Note: S1 could also use a limit order (0.20% maker fee instead of 0.35%), which would help it further. Not modeled here, so S1 is judged at the worse fee.
