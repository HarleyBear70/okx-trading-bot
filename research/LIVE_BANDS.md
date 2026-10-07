# Live bands: "unlucky" vs "broken" for the real-money bots

Set Oct 7 2026, BEFORE any live trade (Chrome Claude's idea #3), by `research/live_bands.py`. Each live bot was backtested with its live settings at the Binance.US 0.02% fee (2018-05 to now, bot.py's own strategy code), then its trades were reshuffled 5,000 times to see what bad luck alone can do.

| Live bot | Trades | Win | PF | Return | Worst drop (backtest) | Losing streak: backtest / normal limit (95%) | Drop: reshuffle 95% |
|---|---|---|---|---|---|---|---|
| Trend Rider | 684 | 40% | 2.38 | +391% | -9.3% | 16 / **16** | -8.1% |
| Turtle 55/20 | 117 | 44% | 5.42 | +315% | -13.6% | 8 / **11** | -5.7% |

**Bands used** (in research/scout.py EXPECTED, which the watcher reads):
- Trend Rider: up to **16 losses in a row** and a **9.3%** drop count as normal.
- Turtle: up to **11 losses in a row** and a **13.6%** drop count as normal.
- The drop limit is the worse of the real backtest and the reshuffle, because a reshuffle by trade understates drops when several trades are open at once.

**What happens:**
- **Inside the bands:** bad luck. Keep going, no changes.
- **Outside them:** the watcher raises ATTENTION, and Claude checks for a real problem (fills, slippage, a bug) before anything changes.
- **Retuning** only happens on a fixed schedule, never right after a losing streak.

Note: GUARD halts any bot at a 12% drop. Turtle's backtest once fell 13.6%, so the guard could pause it during a normal bad patch. Jeff decides whether to resume.
