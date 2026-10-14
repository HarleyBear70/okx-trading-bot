"""
PATTERN_TEST: Jeff, Oct 14 2026: "the sweep is them getting fuel. the different candle set up is what i dont know. like big
candle sweeping a doji, or hammer being covered up by another one, or three small sellers... v shape, twin tops... has
to be a pattern somewhere." After every Tier 1 sweep (ORANGE), which candle pattern in the next candles actually leads to
the move the other way? 15m and 1H, BTC ETH SOL XRP, 2019 to Sep 2026. Read-only research.
  Sweep   Tier 1 orange (research/orange_test.py): a high swept -> look for a SHORT pattern; a low swept -> LONG (mirror).
  Window  the pattern must finish on the sweep candle or one of the next 3 candles, before price passes the sweep wick.
  Entry   that candle's close. Stop past the sweep wick + 0.05%, max 1.35%. Target 2R. Binance.US costs.
  Patterns (short side; textbook shapes, the numbers are textbook fill-ins [CLAUDE]):
    engulfing     red candle whose body covers the last candle's green body ("big candle swallowing")
    pin           the sweep candle itself: upper wick >= 2x body, closes in its lower third (shooting star / pin bar)
    doji+big      last candle a doji (body <= 10% of its range), this one red with body >= 1.5x the 14-candle average
    star          evening star: big green, small body (<= 30% of it), then red closing below the green's middle
    3 crows       three red candles in a row, each closing lower ("three small sellers")
    3 over big    the last 3 candles close below the open of a big green candle (body >= 1.5x avg) right before them
    inside break  last candle inside the one before it (lower high, higher low); this one closes below its low
    double top    the swept high is within 0.1% of an earlier high in the last 50 candles (twin tops)
    none          confirmation only: a close below the sweep candle's low (orange_test.py "(b)")
  python3 research/pattern_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
import struct_t1 as T  # noqa: E402
from orange_test import trade  # noqa: E402

CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP"]
NAMES = ["engulfing", "pin", "doji+big", "star", "3 crows", "3 over big", "inside break", "double top", "none"]


def patterns(o, h, l, c, j, b, down, avg):
    """which patterns finish on candle j (short side if down; mirror for longs)"""
    s = 1 if down else -1  # flip prices for longs
    O = lambda x: s * o[x]
    C = lambda x: s * c[x]
    Hh = lambda x: s * h[x] if down else s * l[x]
    Ll = lambda x: s * l[x] if down else s * h[x]
    body = lambda x: abs(c[x] - o[x])
    red = lambda x: C(x) < O(x)
    green = lambda x: C(x) > O(x)
    out = set()
    if j >= 1 and red(j) and green(j - 1) and C(j) <= O(j - 1) and O(j) >= C(j - 1):
        out.add("engulfing")
    if j == b:
        rng = Hh(j) - Ll(j)
        top = max(O(j), C(j))
        if rng > 0 and (Hh(j) - top) >= 2 * body(j) and (C(j) - Ll(j)) <= rng / 3:
            out.add("pin")
    if j >= 1:
        r1 = abs(h[j - 1] - l[j - 1])
        if r1 > 0 and body(j - 1) <= 0.1 * r1 and red(j) and body(j) >= 1.5 * avg:
            out.add("doji+big")
    if j >= 2 and green(j - 2) and body(j - 1) <= 0.3 * body(j - 2) and red(j) and C(j) < (O(j - 2) + C(j - 2)) / 2:
        out.add("star")
    if j >= 2 and all(red(x) for x in (j - 2, j - 1, j)) and C(j) < C(j - 1) < C(j - 2):
        out.add("3 crows")
    if j >= 3 and green(j - 3) and body(j - 3) >= 1.5 * avg and all(C(x) < O(j - 3) for x in (j - 2, j - 1, j)):
        out.add("3 over big")
    if j >= 2 and Hh(j - 1) < Hh(j - 2) and Ll(j - 1) > Ll(j - 2) and C(j) < Ll(j - 1):
        out.add("inside break")
    if C(j) < Ll(b):
        out.add("none")
    return out


def run(coin, size):
    d = D.load(coin)
    ts = d["ts"]
    O, H, L, C, e = D.resample(ts, d["o"], d["h"], d["l"], d["c"], size)
    tt = [0] * len(C)
    for i, k in enumerate(e):
        if k >= 0:
            tt[k] = ts[i]
    del d
    gc.collect()
    o, h, l, c = list(O), list(H), list(L), list(C)
    s = T.Tier1(h, l, c)
    n = len(c)
    res = []
    for k in range(n):
        tr = s.trend
        for b, ev, _ in s.step(k):
            if not ev.startswith("sweep") or tr == 0:
                continue
            up = tr == 1
            if ev == "sweep of WEAK":
                down = up
            elif ev == "sweep of STRONG":
                down = not up
            elif ev.startswith("sweep of key"):
                down = ev.endswith("high")
            else:
                down = not up
            wick = max(h[b:k + 1]) if down else min(l[b:k + 1])
            look = 50
            dbl = any(abs(h[x] - wick) <= 0.001 * wick if down else abs(l[x] - wick) <= 0.001 * wick
                      for x in range(max(b - look, 0), max(b - 2, 0)))
            seen = set()
            for j in range(b, min(k + 4, n)):
                if j > k and ((h[j] > wick) if down else (l[j] < wick)):
                    break
                avg = sum(abs(c[x] - o[x]) for x in range(max(j - 14, 0), j)) / max(min(14, j), 1)
                for p in patterns(o, h, l, c, j, b, down, avg) - seen:
                    seen.add(p)
                    stop = max(h[b:j + 1]) if down else min(l[b:j + 1])
                    R = trade(h, l, c, j, c[j], stop, down)
                    if R is not None:
                        res.append((tt[j], p, R))
                        if dbl and p == "none":
                            res.append((tt[j], "double top", R))
    return res


def stats(rs):
    if not rs:
        return "     0"
    w = sum(1 for r in rs if r > 0)
    return f"{len(rs):6} | win {100 * w / len(rs):3.0f}% | avg {sum(rs) / len(rs):+.2f}R"


def main():
    for size, tf in ((3600000, "1H"), (900000, "15m")):
        allx = []
        for coin in COINS:
            allx += run(coin, size)
            gc.collect()
        print(f"\n### {tf}: pattern right after a sweep (orange), trade the other way, 2R target  (BTC ETH SOL XRP)")
        print(f"  {'pattern':14} {'ALL YEARS':38} {'2019-22':38} 2023-on")
        for p in NAMES:
            xs = [x for x in allx if x[1] == p]
            print(f"  {p:14} {stats([x[2] for x in xs]):38} {stats([x[2] for x in xs if x[0] < CUT]):38} {stats([x[2] for x in xs if x[0] >= CUT])}", flush=True)


if __name__ == "__main__":
    main()
