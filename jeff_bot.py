"""
Jeff's top-down SMC bot, 15-minute PAPER (Oct 8 2026). Runs every 15 minutes (.github/workflows/jeff-bot.yml).
Binance.US USD prices, BTC ETH SOL XRP BNB, buys only (shorts lost in testing; Binance.US spot can't short).
Built on the Smoke Detector structure engine (research/jeff_topdown.py, results research/JEFF_TOPDOWN.md).

Two paper accounts, $1,000 each, 0.5% risk a trade, 0.07% cost a side:
  turnaround : daily trend up AND 4H trend up, then a 15m market shift up -> buy at the next open
  full-recipe: same, plus price in the 4H discount and a liquidity sweep in the last 12 candles (Brad Guan style)
Stop just under the pullback low (strong level - 0.15 ATR), trailed under each new strong level; sell at the next
open after a 15m market shift down. Never places real orders.

  python jeff_bot.py      (state: jeff_state.json, trades: jeff_trades.csv)
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
from jeff_topdown import CUSH, SWEEP_WIN, structure  # noqa: E402

COINS = ["BTC", "ETH", "SOL", "XRP", "BNB"]
ACCOUNTS = {"turnaround": "A", "full-recipe": "BC"}
RISK, COST = 0.005, 0.0007
STATE = os.path.join(HERE, "jeff_state.json")
TRADES = os.path.join(HERE, "jeff_trades.csv")
UTC = dt.timezone.utc
M15, H4, D1 = 900000, 4 * 3600000, 86400000


def atr(b, n=14):
    out, a = [], None
    for i, x in enumerate(b):
        tr = x["h"] - x["l"] if i == 0 else max(x["h"] - x["l"], abs(x["h"] - b[i - 1]["c"]), abs(x["l"] - b[i - 1]["c"]))
        a = tr if a is None else (a * (n - 1) + tr) / n
        out.append(a if i >= n else None)
    return out


def htf(coin, interval, span, limit):
    """{close time of each completed higher-timeframe candle: (trend, mid)}"""
    hb = [b for b in binanceus_candles(coin + "-USDT", interval, limit) if b["confirm"]]
    s = structure(hb)
    return {b["ts"] + span: (s["trend"][i], s["mid"][i]) for i, b in enumerate(hb)}


def view_at(known, close_ts):
    """latest completed higher-timeframe view as of a 15m candle's close"""
    ks = [k for k in known if k <= close_ts]
    return known[max(ks)] if ks else (0, None)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d %H:%M")


def log(row):
    new = not os.path.exists(TRADES)
    with open(TRADES, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "account", "coin", "action", "price", "qty", "usd", "pnl_usd", "balance", "reason"])
        w.writerow(row)


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    for name in ACCOUNTS:
        st.setdefault(name, {"equity": 1000.0, "coins": {}})
    for coin in COINS:
        try:
            bars = [b for b in binanceus_candles(coin + "-USDT", "15m", 1000) if b["confirm"]]
            d1, h4 = htf(coin, "1d", D1, 300), htf(coin, "4h", H4, 500)
        except Exception as e:
            print(f"jeff {coin}: data ERROR {e}")
            continue
        s, a = structure(bars), atr(bars)
        for name, variant in ACCOUNTS.items():
            acc = st[name]
            cs = acc["coins"].setdefault(coin, {"last": bars[-2]["ts"], "pos": None, "pend": None, "exit": False})
            for k, x in enumerate(bars):
                if x["ts"] <= cs["last"] or k < 50:
                    continue
                cs["last"] = x["ts"]
                pos = cs["pos"]
                # 1) fills at this candle's open
                if pos and cs["exit"]:
                    close_trade(acc, name, coin, cs, x, x["o"], "market shift down (15m)")
                    pos = None
                if cs["pend"] and not pos:
                    stop = cs["pend"]
                    px = x["o"]
                    if px > stop:
                        qty = min(acc["equity"] * RISK / (px - stop), acc["equity"] / px)
                        cs["pos"] = pos = {"entry": px, "stop": stop, "qty": qty, "ts": x["ts"]}
                        log([iso(x["ts"]), name, coin, "buy", px, round(qty, 8), round(px * qty, 2), "",
                             round(acc["equity"], 2), f"turnaround, stop {stop:.6g}"])
                        print(f"jeff [{name}] {coin}: BUY {px} stop {stop:.6g} (${px * qty:.2f})")
                cs["pend"] = None
                # 2) stop inside the candle
                if pos and x["l"] <= pos["stop"]:
                    close_trade(acc, name, coin, cs, x, min(pos["stop"], x["o"]), "stop")
                    pos = None
                # 3) at the close
                if pos:
                    if s["trend"][k] == -1:
                        cs["exit"] = True
                    elif s["strong"][k] is not None and a[k]:
                        pos["stop"] = max(pos["stop"], s["strong"][k] - CUSH * a[k])
                elif s["shift"][k] and s["trend"][k] == 1 and a[k] and s["strong"][k] is not None:
                    close_ts = x["ts"] + M15
                    ok = view_at(d1, close_ts)[0] == 1 and view_at(h4, close_ts)[0] == 1
                    if variant == "BC":
                        mid = view_at(h4, close_ts)[1]
                        ok = ok and any(s["trap"][max(0, k - SWEEP_WIN):k + 1]) and mid is not None and x["c"] <= mid
                    if ok:
                        cs["pend"] = s["strong"][k] - CUSH * a[k]
            print(f"jeff [{name}] {coin}: {iso(bars[-1]['ts'])} close {bars[-1]['c']} 15m trend "
                  f"{s['trend'][-1]:+d} | open: {'yes' if cs['pos'] else 'no'}")
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    for name in ACCOUNTS:
        print(f"jeff [{name}] balance ${st[name]['equity']:.2f}, open "
              f"{[c for c, v in st[name]['coins'].items() if v['pos']]}")


def close_trade(acc, name, coin, cs, x, px, why):
    p = cs["pos"]
    pnl = (px - p["entry"]) * p["qty"] - COST * (p["entry"] + px) * p["qty"]
    acc["equity"] += pnl
    log([iso(x["ts"]), name, coin, "sell", px, round(p["qty"], 8), round(px * p["qty"], 2), round(pnl, 2),
         round(acc["equity"], 2), why])
    print(f"jeff [{name}] {coin}: SELL {px} ({why}) P/L {pnl:+.2f}")
    cs["pos"], cs["exit"] = None, False


if __name__ == "__main__":
    main()
