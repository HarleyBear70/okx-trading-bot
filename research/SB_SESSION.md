# SB results: session-open breakout on crypto (Jeff's plan, Oct 7 2026)

Script: research/sb_session.py. BTC ETH SOL XRP, Binance 1H, 2022-now, 0.1% fee + 0.05% slippage each side, 0.5% risk, $1,000.
Tuned on 2022-2024, judged on 2025-now (unseen). 16 versions: trend (4H 50 EMA / Supertrend) x window (London / New York) x stop (box middle / opposite side) x exit (2R / breakeven + 2 ATR trail).

## Verdict: FAIL. Dropped.
- **All 16 versions lost money in 2022-2024** (PF 0.37-0.73). The best on that period (Supertrend, London, middle stop, trail) lost again on unseen 2025-now: PF 0.72, -$109, drop -21.6% (pass needs PF > 1.3, drop < 10%).
- **No better than random:** the same trades with a coin-flip direction average PF 0.71; the real strategy got 0.72.
- **Fragile:** every small change (box end +/-1 hour, volume 1.3x/2x, ATR 1.5x/2.5x) stays at PF 0.49-0.90.
- Profitable on 2 of 4 coins only (ETH, SOL); BTC and XRP lost.
- Shorts were the worst part (win 18%, PF 0.22); longs alone PF 1.36 but drop -10.1% on just 60 trades. Binance.US spot can't short anyway.
- Win rate 21-45%, far from the 60-70% target. Before costs the best version had PF 1.42; the 0.3% round trip on ~1% stops eats it.
- The two "opposite-side stop + trail" London versions made money on 2025-now (PF 1.6-1.7) but only ~45 trades and they lost in 2022-2024, so picking them would be hindsight.
- Same story as forex sessions (F40), the 1H day bots (D1) and BTC hours (Q1): 1H session timing has no edge after costs.
