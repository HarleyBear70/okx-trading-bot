"""
Silver Bullet forward test, PAPER (Jeff, Oct 10 2026): two bots next to the Brad day forward test (brad_day_bot.py).
Version A (9 AM ET 1H candle swept 10-11 AM ET), displacement 3x, stop past the sweep, swing 5, BTC ETH SOL XRP.
  sb-near : limit at the FVG's near edge      sb-50 : limit at the FVG's 50% line
Every run replays the EXACT backtest code (research/silver_bullet.py day_run) over the last 20 days of Binance.US 5m
candles and records any trade that started after go-live. Recorded trades are never changed. Never places real orders.

  python sb_bot.py      (state sb_state.json, trades sb_trades.csv)
"""
import array
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "research"))
from bot import binanceus_candles  # noqa: E402
import brad_day as D  # noqa: E402
import silver_bullet as S  # noqa: E402

COINS = ["BTC", "ETH", "SOL", "XRP"]
BOTS = {"sb-near": "near", "sb-50": "50%"}
N, X, DAYS, RISK = 5, 3.0, 20, 0.005
STATE = os.path.join(HERE, "sb_state.json")
TRADES = os.path.join(HERE, "sb_trades.csv")
UTC = dt.timezone.utc


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d %H:%M")


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = int(dt.datetime.now(UTC).timestamp() * 1000)
    for b in BOTS:
        st.setdefault(b, {"go_live": now, "trades": []})
    for coin in COINS:
        try:
            raw = [x for x in binanceus_candles(coin + "-USDT", "5m", DAYS * 288) if x["confirm"]]
        except Exception as e:
            print(f"sb {coin}: data ERROR {e}")
            continue
        d = {"ts": array.array("q", (x["ts"] for x in raw)), **{k: array.array("d", (x[k] for x in raw)) for k in "ohlc"}}
        mins, spans = S.clock(d["ts"])
        sides = [(s, dd, S.prep(dd, (N,))) for s, dd in ((1, d), (-1, D.mirror(d)))]
        for name, en in BOTS.items():
            acc = st[name]
            seen = {(t["coin"], t["ts"]) for t in acc["trades"]}
            for a, b in spans:
                got = []
                for s, dd, pre in sides:
                    swb, tr = S.day_run(dd, pre, mins, a, b, "A", N, X, en, "sweep")
                    if swb is not None:
                        got.append((swb, s, tr))
                if not got:
                    continue
                swb, s, tr = min(got)  # the first sweep decides the side for the day
                if tr and tr[0] >= acc["go_live"] and (coin, tr[0]) not in seen:
                    acc["trades"].append({"coin": coin, "side": s, "ts": tr[0], "x_ts": tr[1], "R": round(tr[2], 3)})
                    print(f"sb [{name}] {coin}: {'LONG' if s == 1 else 'SHORT'} {iso(tr[0])} {tr[2]:+.2f}R")
        print(f"sb {coin}: {iso(d['ts'][-1])} close {d['c'][-1]}")
    rows = []
    for name in BOTS:
        acc = st[name]
        acc["trades"].sort(key=lambda t: t["ts"])
        bal = 1000.0
        for t in acc["trades"]:
            pnl = bal * RISK * t["R"]
            bal += pnl
            rows.append([name, iso(t["ts"]), t["coin"], "long" if t["side"] == 1 else "short", iso(t["x_ts"]), t["R"],
                         round(pnl, 2), round(bal, 2)])
        acc["balance"] = round(bal, 2)
        print(f"sb [{name}]: {len(acc['trades'])} trades since {iso(acc['go_live'])}, balance ${bal:.2f}")
    with open(TRADES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["bot", "entry_utc", "coin", "side", "exit_utc", "R", "pnl_usd", "balance"])
        w.writerows(rows)
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)


if __name__ == "__main__":
    main()
