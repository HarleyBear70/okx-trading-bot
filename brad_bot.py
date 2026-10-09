"""
Brad Goh sweep + FVG bot, 1-hour PAPER (Oct 8 2026). Runs every hour (.github/workflows/brad-bot.yml).
Binance.US USD prices, 23 coins, buys only (Binance.US spot can't short). Rules and tests: research/brad_rules.py,
research/BRAD_RULES.md (this version: 23 coins, 1H, 48-candle sweep window, no discount rule, 3R;
buys only 2019-now ~2 trades/week, PF 1.30, +0.22R a trade; 2023-now PF 1.14).

  1. 4H trend up (Smoke Detector engine).
  2. A sweep of a swing low in the last 48 1H candles, then a 1H market shift up that left a fair value gap.
  3. Limit buy at the top of the newest gap, good for 1 day (cancelled if the stop or target trades first).
  4. Stop under the sweep's low - 0.1 ATR. Target 3R. Set and forget.
One paper account, $1,000, 0.5% risk a trade, 0.07% cost a side. Never places real orders.

  python brad_bot.py      (state: brad_state.json, trades: brad_trades.csv)
  python brad_bot.py --skip-mon-fri   paper COPY that takes no new setups on Mondays or Fridays (UTC); open trades
                                      and waiting orders still run (state: brad_monfri_state.json, trades:
                                      brad_monfri_trades.csv). Backtest research/BRAD_RULES.md: PF 1.36 vs 1.27.
"""
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "research"))
from bot import binanceus_candles  # noqa: E402
from brad_rules import CUSH, fvg  # noqa: E402
from jeff_bot import atr, htf, iso, view_at  # noqa: E402
from jeff_topdown import structure  # noqa: E402

COINS = "BTC ETH SOL XRP BNB ADA DOGE AVAX LINK LTC DOT XLM BCH HBAR NEAR UNI ATOM SHIB TRX SUI AAVE ETC ALGO".split()
RISK, COST, RR, WIN = 0.005, 0.0007, 3, 48
SKIP_MON_FRI = "--skip-mon-fri" in sys.argv
TAG = "brad-monfri" if SKIP_MON_FRI else "brad"
STATE = os.path.join(HERE, "brad_monfri_state.json" if SKIP_MON_FRI else "brad_state.json")
TRADES = os.path.join(HERE, "brad_monfri_trades.csv" if SKIP_MON_FRI else "brad_trades.csv")
H1, H4 = 3600000, 4 * 3600000


def log(row):
    new = not os.path.exists(TRADES)
    with open(TRADES, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "coin", "action", "price", "qty", "usd", "pnl_usd", "balance", "reason"])
        w.writerow(row)


def close_trade(acc, coin, cs, x, px, why):
    p = cs["pos"]
    pnl = (px - p["entry"]) * p["qty"] - COST * (p["entry"] + px) * p["qty"]
    acc["equity"] += pnl
    log([iso(x["ts"]), coin, "sell", px, round(p["qty"], 8), round(px * p["qty"], 2), round(pnl, 2),
         round(acc["equity"], 2), why])
    print(f"{TAG} {coin}: SELL {px} ({why}) P/L {pnl:+.2f}")
    cs["pos"] = None


def main():
    acc = json.load(open(STATE)) if os.path.exists(STATE) else {"equity": 1000.0, "coins": {}}
    for coin in COINS:
        try:
            bars = [b for b in binanceus_candles(coin + "-USDT", "1h", 1000) if b["confirm"]]
            h4 = htf(coin, "4h", H4, 500)
        except Exception as e:
            print(f"{TAG} {coin}: data ERROR {e}")
            continue
        s, a = structure(bars), atr(bars)
        cs = acc["coins"].setdefault(coin, {"last": bars[-2]["ts"], "pos": None, "order": None})
        for k, x in enumerate(bars):
            if x["ts"] <= cs["last"] or k < 100:
                continue
            cs["last"] = x["ts"]
            # 1) working limit buy
            o = cs["order"]
            if o and not cs["pos"]:
                if x["ts"] > o["expires"] or x["h"] >= o["tgt"] or x["o"] <= o["stop"]:
                    cs["order"] = None
                elif x["l"] <= o["entry"]:
                    px = min(o["entry"], x["o"])
                    qty = min(acc["equity"] * RISK / (px - o["stop"]), acc["equity"] / px)
                    cs["pos"] = {"entry": px, "stop": o["stop"], "tgt": o["tgt"], "qty": qty, "ts": x["ts"]}
                    cs["order"] = None
                    log([iso(x["ts"]), coin, "buy", px, round(qty, 8), round(px * qty, 2), "",
                         round(acc["equity"], 2), f"gap fill, stop {o['stop']:.6g}, target {o['tgt']:.6g}"])
                    print(f"{TAG} {coin}: BUY {px} stop {o['stop']:.6g} target {o['tgt']:.6g} (${px * qty:.2f})")
                    if x["l"] <= o["stop"]:  # stop in the fill candle
                        close_trade(acc, coin, cs, x, o["stop"], "stop")
                    continue
            # 2) open trade: stop first, then target
            p = cs["pos"]
            if p:
                if x["l"] <= p["stop"]:
                    close_trade(acc, coin, cs, x, min(p["stop"], x["o"]), "stop")
                elif x["h"] >= p["tgt"]:
                    close_trade(acc, coin, cs, x, max(p["tgt"], x["o"]), "target 3R")
                continue
            # 3) new setup at the close
            weekday = dt.datetime.fromtimestamp(x["ts"] / 1000, dt.timezone.utc).weekday()
            if SKIP_MON_FRI and weekday in (0, 4):
                continue
            if not cs["order"] and s["shift"][k] and s["trend"][k] == 1 and a[k]:
                if view_at(h4, x["ts"] + H1)[0] != 1:
                    continue
                js = [j for j in range(max(0, k - WIN), k + 1) if s["tdir"][j] == -1]
                gap = fvg(bars, 1, js[-1], k) if js else None
                if gap:
                    stop = min(y["l"] for y in bars[js[-1]:k + 1]) - CUSH * a[k]
                    entry = gap[0]
                    if entry > stop:
                        cs["order"] = {"entry": entry, "stop": stop, "tgt": entry + RR * (entry - stop),
                                       "expires": x["ts"] + 86400000}
                        print(f"{TAG} {coin}: limit buy {entry:.6g}, stop {stop:.6g}")
        print(f"{TAG} {coin}: {iso(bars[-1]['ts'])} close {bars[-1]['c']} | "
              f"{'IN TRADE' if cs['pos'] else 'order waiting' if cs['order'] else 'flat'}")
    with open(STATE, "w") as f:
        json.dump(acc, f, indent=1)
    print(f"{TAG} balance ${acc['equity']:.2f}, open {[c for c, v in acc['coins'].items() if v['pos']]}, "
          f"orders {[c for c, v in acc['coins'].items() if v['order']]}")


if __name__ == "__main__":
    main()
