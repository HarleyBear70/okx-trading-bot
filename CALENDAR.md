# P/L calendar and strategy cards

Updated automatically every hour (2026-10-05 21:25 EDT). Days are Eastern time. Green = closed profit that day, red = closed loss, grey = no closed trades; stronger colour = bigger day (full colour at 2% of the balance). Each square: the day's % change of the balance and the $ amount. DEMO = OKX demo account orders, PAPER = simulated, no orders. Made by pl_calendar.py.

## Combined OKX demo account

Closed P/L so far: +$1.73 · 1 win day · 1 loss day

![Combined OKX demo account](calendars/combined.svg)

## The three piles

- HOLD (long-term, PAPER): weekly dip-DCA buyer, $10/week into BTC + XRP, double when 20%+ below the 200-day average. Paid $10.00, worth $9.90. Profit sweeper (25% of wins into this pile): OFF until real money. Buys: hold_pile.csv.
- ACTIVE (trading, OKX demo): SP-12 v4, Trend Rider
- INCUBATING (paper forward tests): B1c breakout retest (paper), B3 pairs (paper), NNFX Aroon (paper), SP-12 v4 (Kraken paper)
- RANGE: none yet. No range bot has passed a test (research/N1_RANGE.md, B2), so this pile stays empty until one does.
- PAUSED: SP-12 v2, SP-12 v2 (gold paper), Trend Rider (gold paper)

## Growth: demo vs paper

Average balance per bot, each bot starting at $1,000: the active demo bots (2, solid) vs the paper bots (4, dashed). Demo now $1,001.70 (+0.17%), paper now $1,002.52 (+0.25%).

![Demo vs paper growth](calendars/cards/growth.svg)

## Strategy cards

One card per bot. Chart: blue = the bot's real balance (demo or paper fills, open trades valued now); dashed grey = the same bot.py code replayed on the same candles since the start (the backtest engine). A gap between them = fills, timing, or a settings change during the period (see journal/changes.json). 'Backtest' stats are the long-run research numbers (2022-now).

### SP-12 v4  ·  DEMO

OKX · BTC ETH XRP XLM BNB · 4-hour candles · started 2026-10-04 · balance now 1,005.05

![SP-12 v4 live vs backtest](calendars/cards/v4-okx.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 34% | 1.40 | -9.6% |
| Backtest replay since start | 1 | 0% | 0.00 | -0.8% |
| Live (demo) since start | 2 | 50% | 7.01 | -0.2% |

### SP-12 v4 (Kraken paper)  ·  PAPER

Kraken · XBTUSD ETHUSD XRPUSD · 4-hour candles · started 2026-10-04 · balance now 1,010.09

![SP-12 v4 (Kraken paper) live vs backtest](calendars/cards/v4-kraken.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 33% | 1.46 | -9.5% |
| Backtest replay since start | 1 | 0% | 0.00 | -0.7% |
| Live (paper) since start | 1 | 100% | inf | 0.0% |

### SP-12 v2  ·  PAUSED

OKX · ETH SOL · 4-hour candles · started 2026-10-04 · balance now 996.68

![SP-12 v2 live vs backtest](calendars/cards/v2-okx.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | - | - | - |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paused) since start | 1 | 0% | 0.00 | -0.3% |

### SP-12 v2 (gold paper)  ·  PAUSED

OKX · XAUT · 4-hour candles · started 2026-10-04 · balance now 1,000.00

![SP-12 v2 (gold paper) live vs backtest](calendars/cards/v2-gold.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | - | - | - |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paused) since start | 0 | - | - | 0.0% |

### Trend Rider  ·  DEMO

OKX · BTC ETH SOL BNB SUI TRX · 4-hour candles · started 2026-10-04 · balance now 998.35

![Trend Rider live vs backtest](calendars/cards/tr-okx.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 40% | 2.33 | -10.6% |
| Backtest replay since start | 0 | - | - | -0.3% |
| Live (demo) since start | 0 | - | - | -0.2% |

### B1c breakout retest (paper)  ·  PAPER

OKX · BTC ETH XRP · 1-hour candles · started 2026-10-05 · balance now 1,000.00

![B1c breakout retest (paper) live vs backtest](calendars/cards/b1-paper.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 46% | 1.17 | -5.8% |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paper) since start | 0 | - | - | 0.0% |

### B3 pairs (paper)  ·  PAPER

OKX · ETH XRP BTC · daily candles · started 2026-10-05 · balance now 1,000.00

![B3 pairs (paper) live vs backtest](calendars/cards/b3-paper.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 44% | 1.52 | -5.1% |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paper) since start | 0 | - | - | 0.0% |

### NNFX Aroon (paper)  ·  PAPER

OKX · BTC ETH XRP · daily candles · started 2026-10-05 · balance now 1,000.00

![NNFX Aroon (paper) live vs backtest](calendars/cards/nnfx-paper.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | 61% | 2.20 | -5.4% |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paper) since start | 0 | - | - | 0.0% |

### Trend Rider (gold paper)  ·  PAUSED

OKX · XAUT · 4-hour candles · started 2026-10-04 · balance now 1,000.00

![Trend Rider (gold paper) live vs backtest](calendars/cards/tr-gold.svg)

| | Trades | Win % | PF | Max DD |
|---|---|---|---|---|
| Backtest, long run (research, 2022-now) | - | - | - | - |
| Backtest replay since start | 0 | - | - | 0.0% |
| Live (paused) since start | 0 | - | - | 0.0% |

## Per-bot P/L calendars

### SP-12 v4

Closed P/L so far: +$5.05 · 1 win day · 1 loss day

![SP-12 v4](calendars/v4-okx.svg)

### SP-12 v4 (Kraken paper)

Closed P/L so far: +$9.19 · 1 win day · 0 loss days

![SP-12 v4 (Kraken paper)](calendars/v4-kraken.svg)

### Trend Rider

Closed P/L so far: +$0.00 · 0 win days · 0 loss days

![Trend Rider](calendars/tr-okx.svg)

### B1c breakout retest (paper)

Closed P/L so far: +$0.00 · 0 win days · 0 loss days

![B1c breakout retest (paper)](calendars/b1-paper.svg)

### B3 pairs (paper)

Closed P/L so far: +$0.00 · 0 win days · 0 loss days

![B3 pairs (paper)](calendars/b3-paper.svg)

### NNFX Aroon (paper)

Closed P/L so far: +$0.00 · 0 win days · 0 loss days

![NNFX Aroon (paper)](calendars/nnfx-paper.svg)

