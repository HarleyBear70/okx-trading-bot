# Plan: exchange-side stop orders (before real money)

2026-10-06. Jeff asked for this ("yes"). Plan only; nothing is built yet.

## Why
Today the bots check their stops once an hour on GitHub (and GitHub can start a run late). In a fast drop a stop can fill well below its level, and if GitHub is down nobody watches the trades. With an exchange-side stop, OKX holds a sell order that fires the moment price touches the stop, 24/7, whether or not the bot is running.

## What OKX offers (spot, works on demo with the demo header)
- Place: POST /api/v5/trade/order-algo, ordType "conditional", side sell, tdMode cash, sz = the coin amount, slTriggerPx = the stop, slOrdPx = -1 (sell at market when triggered), slTriggerPxType "last". algoClOrdId carries the bot's prefix (gh4/ghT/ghN/ghD) so each bot only touches its own stops.
- Move: POST /api/v5/trade/amend-algos with newSlTriggerPx (stop moved up) and/or newSz (size changed).
- Check: GET /api/v5/trade/orders-algo-pending and orders-algo-history (state "effective" = it fired; then read the fill).
- Cancel: POST /api/v5/trade/cancel-algos.

## How each bot event changes
| Event | Today | With exchange stops |
|---|---|---|
| Buy | market buy, stop kept in state.json | market buy, then place the conditional stop for the bought amount; save its algoId in the position |
| Stop moves up (breakeven, trail, 10-day low) | state.json only | amend the trigger price (only if it moved by more than a small step, to avoid hundreds of edits) |
| Pyramid add-on (Donchian) | qty += add-on | amend the size to the new total and the trigger to the new stop |
| NNFX half sell at +1 ATR | sell half | sell half, then amend the size to what's left |
| Bot's own exit (Aroon flip, Follow Line flip, time exit) | market sell | cancel the stop first, then market sell |
| Stop hit between runs | caught at the next hourly check | already filled by OKX; the next run sees "effective", reads the real fill price, logs the sell (reason "stop (exchange)") and frees the slot |

Paper bots keep today's hourly check (no orders). The hourly stop check stays as a backup for demo/live bots: if a stop order is missing or failed, the bot still sells on its own and the watcher raises ATTENTION.

## Safety rules
1. A per-bot switch, "exchange_stops": True in bot.py, default off; demo first, one bot at a time.
2. If placing a stop fails, retry once, then fall back to the hourly check and log ATTENTION (never leave a position silently unprotected).
3. Before selling for any other reason, always cancel the bot's stop first, so OKX can't sell the same coins twice.
4. Each bot only reads/edits algo orders with its own prefix.
5. The watcher gets a new check: every open demo/live position must have a live stop order on OKX with the right size and trigger.

## Questions to answer on demo first
- Does a pending conditional sell lock the coins (so a second bot holding the same coin, or the bot's own half sell, can't sell)? If it does, each bot's amounts must stay separate, or the half sell must amend first.
- How fast and how close are demo fills on triggered stops?
- Rate limits on amend calls across ~15 open positions per run.

## Steps
1. Write the OKX helpers (place/amend/cancel/check) with the demo header, plus tests against a fake API.
2. Turn it on for one demo bot (Trend Rider: the most trades, so it gets tested soonest) for 1-2 weeks; compare fills with the hourly check.
3. Turn it on for Donchian and NNFX.
4. Required before any real-money bot goes live.
