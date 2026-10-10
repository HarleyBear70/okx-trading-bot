"""
Brad DAY-TRADE forward test, PAPER (Jeff, Oct 10 2026): the best round-3 version from research/BRAD_DAY.md,
on live Binance.US data from Oct 10 2026 on. BTC ETH SOL XRP only. Never places real orders.

  Version  swing 5, range zones, maker entry, killzones (2-5 AM / 7-10 AM ET), BOS/iBOS rule, stop below the
           15m STRONG (+0.05%, no cap), no trades 0.40-0.60, target = 15m WEAK (min 2:1), 3% daily loss limit.
  How      every run replays the EXACT backtest code (research/brad_day.py run()) over the last 45 days of
           Binance.US 5m candles and records any trade that started after go-live. Recorded trades are never
           changed later. Results in R (1R = the risk of one trade) and on a $1,000 paper account at 0.5% risk.
  Note     the backtest version failed on never-seen coins (PF 0.83); Jeff wants to watch it live anyway.

  python brad_day_bot.py            (update; state brad_day_state.json, trades brad_day_trades.csv)
  python brad_day_bot.py --report   (weekly summary text)
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

COINS = ["BTC", "ETH", "SOL", "XRP"]
KW = dict(kz=True, maker=True, rng=True, stopm="strong", cap=None, band=0.10)
N, ZONE, DAYS, RISK = 5, "range", 45, 0.005
STATE = os.path.join(HERE, "brad_day_state.json")
TRADES = os.path.join(HERE, "brad_day_trades.csv")
UTC = dt.timezone.utc
COLS = ["entry_utc", "coin", "side", "entry", "stop", "target", "exit_utc", "exit", "R", "pnl_usd", "balance"]


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d %H:%M")


def fetch(coin):
    b = [x for x in binanceus_candles(coin + "-USDT", "5m", DAYS * 288) if x["confirm"]]
    return {"ts": array.array("q", (x["ts"] for x in b)),
            **{k: array.array("d", (x[k] for x in b)) for k in "ohlc"}}


def main():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    now = int(dt.datetime.now(UTC).timestamp() * 1000)
    st.setdefault("go_live", now)
    st.setdefault("trades", [])
    seen = {(t["coin"], t["side"], t["ts"]) for t in st["trades"]}
    new, opens = [], {}
    for coin in COINS:
        try:
            d = fetch(coin)
        except Exception as e:
            print(f"brad-day {coin}: data ERROR {e}")
            continue
        both = []
        for side, dd in ((1, d), (-1, D.mirror(d))):
            log, end = [], {}
            D.run(dd, N, ZONE, log=log, state=end, **KW)
            both += [dict(x, side=side) for x in log]
            for k in ("pos", "pend"):
                if end.get(k):
                    opens[f"{coin} {'long' if side == 1 else 'short'} {k}"] = {
                        a: side * end[k][a] for a in ("e", "stop", "tgt")}
        busy = -1
        for x in sorted(both, key=lambda x: x["ts"]):  # one trade per coin at a time, like the backtest
            if x["ts"] > busy:
                busy = x["x_ts"]
                if x["ts"] >= st["go_live"] and (coin, x["side"], x["ts"]) not in seen:
                    s = x["side"]
                    new.append({"coin": coin, "side": s, "ts": x["ts"], "x_ts": x["x_ts"], "R": round(x["R"], 3),
                                "e": s * x["e"], "stop": s * x["stop"], "tgt": s * x["tgt"], "x": s * x["x"]})
        print(f"brad-day {coin}: {iso(d['ts'][-1])} close {d['c'][-1]}")
    # 3% daily loss limit (= 6R at 0.5% risk), all coins one account, same as the backtest
    for t in sorted(new, key=lambda t: t["ts"]):
        day = t["ts"] // 86400000
        lost = -sum(x["R"] for x in st["trades"] if x["x_ts"] // 86400000 == day and x["x_ts"] <= t["ts"])
        if lost >= 6.0:
            print(f"brad-day {t['coin']}: skipped (3% daily loss limit)")
            continue
        st["trades"].append(t)
        print(f"brad-day {t['coin']}: {'LONG' if t['side'] == 1 else 'SHORT'} {iso(t['ts'])} {t['R']:+.2f}R")
    st["open"] = opens
    st["trades"].sort(key=lambda t: t["ts"])
    bal = 1000.0
    rows = []
    for t in st["trades"]:
        pnl = bal * RISK * t["R"]
        bal += pnl
        rows.append([iso(t["ts"]), t["coin"], "long" if t["side"] == 1 else "short", round(t["e"], 6),
                     round(t["stop"], 6), round(t["tgt"], 6), iso(t["x_ts"]), round(t["x"], 6), t["R"],
                     round(pnl, 2), round(bal, 2)])
    with open(TRADES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(COLS)
        w.writerows(rows)
    st["balance"] = round(bal, 2)
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    print(f"brad-day: {len(st['trades'])} trades since {iso(st['go_live'])}, balance ${bal:.2f}, open {list(opens)}")


def report():
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"trades": [], "go_live": 0, "open": {}}
    tr = st["trades"]
    week = int(dt.datetime.now(UTC).timestamp() * 1000) - 7 * 86400000
    wk = [t for t in tr if t["x_ts"] >= week]
    f = lambda ts: (f"{len(ts)} trades, {sum(t['R'] > 0 for t in ts)} wins, {sum(t['R'] for t in ts):+.2f}R"
                    if ts else "0 trades")
    lines = [f"Brad day-trade PAPER forward test (since {iso(st['go_live'])} UTC; BTC ETH SOL XRP)",
             f"- This week: {f(wk)}", f"- Since start: {f(tr)}, paper balance ${st.get('balance', 1000):.2f} (from $1,000)",
             f"- Open now: {', '.join(st.get('open', {})) or 'nothing'}",
             "- Backtest expectation: about 16 trades a year on 4 coins, ~30% wins, +0.2R a trade "
             "(but it failed on never-seen coins, PF 0.83)."]
    lines += [f"  {iso(t['ts'])} {t['coin']} {'long' if t['side'] == 1 else 'short'} {t['R']:+.2f}R" for t in wk]
    # Silver Bullet forward-test bots (sb_bot.py), side by side (Jeff, Oct 10)
    sbp = os.path.join(HERE, "sb_state.json")
    if os.path.exists(sbp):
        sb = json.load(open(sbp))
        lines += ["", "Silver Bullet PAPER forward test (version A, 3x displacement, stop past the sweep, swing 5)"]
        for name, acc in sb.items():
            tr2 = acc["trades"]
            wk2 = [t for t in tr2 if t["x_ts"] >= week]
            lines.append(f"- {name}: this week {f(wk2)}; since start {f(tr2)}, paper balance ${acc.get('balance', 1000):.2f}")
            lines += [f"  {iso(t['ts'])} {t['coin']} {'long' if t['side'] == 1 else 'short'} {t['R']:+.2f}R" for t in wk2]
        lines.append("- Backtest expectation: near ~7 trades/yr, 50% ~11 trades/yr on 4 coins (PF 1.42 / 1.33).")
    print("\n".join(lines))


if __name__ == "__main__":
    report() if sys.argv[1:] == ["--report"] else main()
