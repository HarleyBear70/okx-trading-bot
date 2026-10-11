"""
Heartbeat page (Jeff, Oct 11 2026: "i wish i could see an ecogram to compare to a chart for the heart beat pattern").
Builds dashboard/heartbeat.html: per coin and timeframe, the candles with the code's heartbeat trace on top
(every high and low the structure code counts, joined like an ECG strip), BOS / MS marks, MUST HOLD and 50%.
Read-only. Publish the file as an artifact after running it.

  python tools/heartbeat_page.py
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "research"))
sys.path.insert(0, os.path.join(HERE, "tools"))
from heartbeat_watch import ET, fetch  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COINS = ["LINK", "BTC", "ETH", "SOL"]
TFS = [("4H", "4H"), ("1H", "1H"), ("15m", "15m")]
SHOW = 120
OUT = os.path.join(HERE, "dashboard", "heartbeat.html")
TEMPLATE = os.path.join(HERE, "dashboard", "heartbeat_template.html")


def beats(d):
    h, l, c = ([float(r[i]) for r in d] for i in (2, 3, 4))
    s, pts, marks = Heart(h, l, c, 1), [], []
    for k in range(len(d)):
        wb0, weak0, tr0 = s.wb, s.weak, s.trend
        ev = s.step(k)
        if not ev:
            continue
        if ev.startswith("start"):
            pts.append((s.sb, s.strong, "L" if s.trend == 1 else "H"))
            marks.append((k, ev, c[k]))
        elif ev in ("BOS up", "BOS down"):
            up = ev == "BOS up"
            pts += [(wb0, weak0, "H" if up else "L"), (s.sb, s.strong, "L" if up else "H")]
            marks.append((k, ev, c[k]))
        elif ev in ("MS UP", "MS DOWN"):
            pts.append((s.sb, s.strong, "L" if ev == "MS UP" else "H"))
            marks.append((k - 1, ev, c[k - 1]))
        elif ev.startswith("sweep") or ev.startswith("fuel"):
            marks.append((k, ev, c[k]))
    if s.trend:
        pts.append((s.wb, s.weak, "H" if s.trend == 1 else "L"))
    pts.sort()
    clean = []
    for p in pts:  # alternate high / low; two of a kind in a row -> keep the more extreme
        if clean and clean[-1][2] == p[2]:
            a = clean[-1]
            if (p[2] == "H" and p[1] >= a[1]) or (p[2] == "L" and p[1] <= a[1]):
                clean[-1] = p
            continue
        if clean and clean[-1][0] == p[0] and clean[-1][2] != p[2]:
            pass
        clean.append(p)
    return s, clean, marks, c[-1]


def main():
    data = {"made": dt.datetime.now(ET).strftime("%b %d, %I:%M %p ET"), "coins": {}}
    for coin in COINS:
        data["coins"][coin] = {}
        for name, bar in TFS:
            d = fetch(f"{coin}-USDT", bar)
            s, pts, marks, last = beats(d)
            a = max(0, len(d) - SHOW)
            lo, hi = s.rng
            data["coins"][coin][name] = {
                "t": [int(r[0]) for r in d[a:]],
                "o": [float(r[1]) for r in d[a:]], "h": [float(r[2]) for r in d[a:]],
                "l": [float(r[3]) for r in d[a:]], "c": [float(r[4]) for r in d[a:]],
                "beats": [[i - a, p, t] for i, p, t in pts if i >= a - 30],
                "marks": [[i - a, e, p] for i, e, p in marks if i >= a],
                "trend": "UP" if s.trend == 1 else "DOWN" if s.trend == -1 else "",
                "hold": s.strong, "extreme": s.weak, "fifty": (lo + hi) / 2 if lo is not None else None, "last": last,
            }
            print(coin, name, data["coins"][coin][name]["trend"], s.strong, len(pts), "beats")
    html = open(TEMPLATE).read().replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    with open(OUT, "w") as f:
        f.write(html)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
