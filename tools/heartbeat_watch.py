"""
Heartbeat watch (Jeff, Oct 11 2026): Claude watches the structure on every timeframe, top-down, and collects data.
Read-only: prices from OKX public candles (what Jeff's TradingView chart shows), never trades.

  Timeframes: 1D, 4H (HTF) -> 1H (MTF) -> 15m, 5m (LTF).  Jeff: day trade = 4H/1H/15m to read, 5m to execute;
              swing trade = daily/4H to read, 15m to execute.
  Structure = research/jeff_struct.py Heart, swing 1 (MUST HOLD = STRONG, MS = body close past it, confirmed 1 candle later).

Writes
  journal/heartbeat_now.md       the map right now: per coin and timeframe, which way, what must hold, where it flips
  journal/heartbeat_events.csv   every BOS / MS / sweep / fuel grab as it happens, with what the bigger timeframes
                                 were doing at that moment (for later: do moves WITH the HTF work better than against?)

  python tools/heartbeat_watch.py
"""
import bisect
import csv
import datetime as dt
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "research"))
sys.path.insert(0, os.path.join(HERE, "tools"))
from jeff_struct import Heart  # noqa: E402
import claude_hb_trader as trader  # noqa: E402

ET = dt.timezone(dt.timedelta(hours=-4))  # EDT (Oct 2026)
COINS = ["LINK", "BTC", "ETH", "SOL"]
TFS = [("1D", "1Dutc", 86400000), ("4H", "4H", 14400000), ("1H", "1H", 3600000), ("15m", "15m", 900000), ("5m", "5m", 300000)]
EVENTS = os.path.join(HERE, "journal", "heartbeat_events.csv")
NOW = os.path.join(HERE, "journal", "heartbeat_now.md")
COLS = ["time_et", "coin", "tf", "event", "close", "leg", "must_hold", "leg_extreme", "fifty",
        "1D", "4H", "1H", "15m"]


def fetch(inst, bar):
    rows, after = {}, ""
    for _ in range(3):
        url = f"https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar={bar}&limit=100{after}"
        data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "heartbeat"}), timeout=20))["data"]
        time.sleep(0.15)
        if not data:
            break
        for r in data:
            if r[8] == "1":
                rows[int(r[0])] = r
        after = f"&after={min(int(r[0]) for r in data)}"
    return [rows[k] for k in sorted(rows)]


def run(d, size):
    """steps Heart over the candles. returns (events, history of states by close time, final Heart, last close)"""
    h, l, c = ([float(r[i]) for r in d] for i in (2, 3, 4))
    s, evs, hist = Heart(h, l, c, 1), [], []
    for k in range(len(d)):
        ev = s.step(k)
        close_t = int(d[k][0]) + size
        st = (("UP" if s.trend == 1 else "DOWN" if s.trend == -1 else "-"), s.strong, s.weak)
        hist.append((close_t, st))
        if ev and ev.split()[0] in ("BOS", "MS", "sweep", "fuel", "start"):
            evs.append((close_t, ev, c[k], st))
    return evs, hist, s, c[-1], d


def state_at(hist, t):
    i = bisect.bisect_right([x[0] for x in hist], t) - 1
    if i < 0:
        return ""
    leg, strong, _ = hist[i][1]
    return f"{leg} (hold {strong})" if leg != "-" else ""


def main():
    seen = set()
    if os.path.exists(EVENTS):
        with open(EVENTS, newline="") as f:
            seen = {(r["time_et"], r["coin"], r["tf"], r["event"]) for r in csv.DictReader(f)}
    new, lines = [], [f"# Heartbeat map, {dt.datetime.now(ET):%b %d %I:%M %p} ET",
                      "", "Code = Jeff's heartbeat rules, swing 1. MUST HOLD = the level that has to hold; "
                      "a candle BODY closing past it (and the next candle not closing back) = market shift = the flip.", ""]
    for coin in COINS:
        inst = f"{coin}-USDT"
        runs = {}
        for name, bar, size in TFS:
            try:
                runs[name] = run(fetch(inst, bar), size)
            except Exception as ex:
                print(f"{coin} {name}: failed ({ex})")
        lines += [f"## {coin}", "", "| TF | Way | Stays that way while | Flips on a body close | Leg high/low | 50% | Price | Zone |",
                  "|---|---|---|---|---|---|---|---|"]
        for name, _, _ in TFS:
            if name not in runs:
                continue
            evs, hist, s, last, _ = runs[name]
            if not s.trend:
                continue
            up = s.trend == 1
            lo, hi = s.rng
            mid = (lo + hi) / 2
            zone = "premium" if last > mid else "discount"
            pend = " (MS? waiting 1 candle)" if s.pend is not None else ""
            lines.append(f"| {name} | {'BULLISH' if up else 'BEARISH'}{pend} | {'above' if up else 'below'} {s.strong} | "
                         f"{'below' if up else 'above'} {s.strong} | {s.weak} | {mid:.6g} | {last} | {zone} |")
            for close_t, ev, cl, (leg, strong, weak) in evs:
                t = dt.datetime.fromtimestamp(close_t / 1000, ET).strftime("%Y-%m-%d %H:%M")
                if (t, coin, name, ev) in seen:
                    continue
                lo2, hi2 = (strong, weak) if leg == "UP" else (weak, strong)
                row = {"time_et": t, "coin": coin, "tf": name, "event": ev, "close": cl, "leg": leg,
                       "must_hold": strong, "leg_extreme": weak, "fifty": f"{(lo2 + hi2) / 2:.6g}" if leg != "-" else ""}
                for big, _, _ in TFS[:4]:
                    row[big] = state_at(runs[big][1], close_t) if big in runs and big != name else ""
                new.append(row)
        lines.append("")
        try:
            lines += trader.step(coin, runs, state_at)
        except Exception as ex:
            print(f"{coin} trader failed: {ex}")
    trader.save()
    new.sort(key=lambda r: r["time_et"])
    exists = os.path.exists(EVENTS)
    with open(EVENTS, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if not exists:
            w.writeheader()
        w.writerows(new)
    with open(NOW, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"{len(new)} new events logged")


if __name__ == "__main__":
    main()
