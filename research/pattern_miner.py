"""
PATTERN_MINER: Jeff, Oct 14 2026: "find the one that for some reason keeps popping up over and over again."
Two tests, BTC ETH SOL XRP, 2019 to Sep 2026, read-only research.

TEST 1  1H setup, 15m entry (Jeff: "the one hr would work but i try to get in on the 15 for quicker in and out").
  1H setup  a Tier 1 sweep (orange) on 1H, then a 1H doji (body <= 10% of its range) on the sweep candle or one of the
            next 2 candles, before price passes the sweep wick.
  (a) 1H    enter at the close of the next 1H candle if it is a big candle the other way (body >= 1.5x the 14-candle
            average) = pattern_test.py "doji+big".
  (b) 15m   enter at the first 15m close past the doji's far end (below its low for a short) during the next hour:
            earlier, before the 1H candle is done.
  Both: stop past the sweep wick + 0.05% (max 1.35%), target 2R, Binance.US costs. Also the average time in the trade.

TEST 2  the miner. After every Tier 1 sweep (1H and 15m), describe the sweep candle + the next 2 candles:
  sweep candle  where it closed in its own range: far third (back away from the swept level), middle, near third.
  next candles  each one: direction (with the trade / against it) x size (small < 0.5x avg body, normal, big > 1.5x).
  = 3 x 6 x 6 = 108 shapes per side. Entry at the 2nd candle's close, stop past the sweep wick, 2R, costs as above.
  FIND on 2019-22 only (shapes with 40+ trades, ranked by average R), then CHECK the top 10 on 2023-on (never seen).
  A shape that is real should stay positive in 2023-on. [CLAUDE: thirds, 0.5x / 1.5x, 40 trades]
  python3 research/pattern_miner.py
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
H1, M15 = 3600000, 900000


def sweeps(h, l, c):
    """(b, k, down) for every Tier 1 sweep: b = orange candle, k = candle it was known on; down = trade short"""
    s = T.Tier1(h, l, c)
    out = []
    for k in range(len(c)):
        tr = s.trend
        for b, ev, _ in s.step(k):
            if not ev.startswith("sweep") or tr == 0:
                continue
            up = tr == 1
            if ev == "sweep of WEAK":
                down = up
            elif ev.startswith("sweep of key"):
                down = ev.endswith("high")
            else:
                down = not up
            out.append((b, k, down))
    return out


def avgbody(o, c, j):
    return sum(abs(c[x] - o[x]) for x in range(max(j - 14, 0), j)) / max(min(14, j), 1)


def shape(o, h, l, c, b, j, down, avg):
    rng = h[b] - l[b]
    pos = (c[b] - l[b]) / rng if rng > 0 else 0.5
    if not down:
        pos = 1 - pos
    third = "far" if pos < 1 / 3 else "mid" if pos < 2 / 3 else "near"
    parts = [f"sweep closes {third}"]
    for x in (j - 1, j):
        bd = abs(c[x] - o[x])
        with_t = (c[x] < o[x]) if down else (c[x] > o[x])
        size = "small" if bd < 0.5 * avg else "big" if bd > 1.5 * avg else "normal"
        parts.append(f"{size} {'WITH' if with_t else 'against'}")
    return " | ".join(parts)


def run(coin):
    d = D.load(coin)
    ts = d["ts"]
    res1, res2 = [], []
    o1, h1, l1, c1, e1 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], H1)
    o5, h5, l5, c5, e5 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], M15)
    t1, t5 = [0] * len(c1), [0] * len(c5)
    for i in range(len(ts)):
        if e1[i] >= 0:
            t1[e1[i]] = ts[i]
        if e5[i] >= 0:
            t5[e5[i]] = ts[i]
    del d
    gc.collect()
    o1, h1, l1, c1 = list(o1), list(h1), list(l1), list(c1)
    o5, h5, l5, c5 = list(o5), list(h5), list(l5), list(c5)
    first15 = {}  # 1H candle open time -> index of its first 15m candle
    for x, t in enumerate(t5):
        first15.setdefault((t // H1) * H1, x)
    for tf, (o, h, l, c, tt) in (("1H", (o1, h1, l1, c1, t1)), ("15m", (o5, h5, l5, c5, t5))):
        n = len(c)
        for b, k, down in sweeps(h, l, c):
            wick_end = k
            # TEST 2: the miner (sweep candle + next 2)
            j = b + 2
            if j < n and j >= k and not any((h[x] > max(h[b:k + 1])) if down else (l[x] < min(l[b:k + 1])) for x in range(k + 1, j + 1)):
                stop = max(h[b:j + 1]) if down else min(l[b:j + 1])
                R = trade(h, l, c, j, c[j], stop, down)
                if R is not None:
                    res2.append((tf, tt[j], "SHORT" if down else "LONG", shape(o, h, l, c, b, j, down, avgbody(o, c, j)), R))
            if tf != "1H":
                continue
            # TEST 1: 1H doji, then (a) 1H big candle or (b) 15m close past the doji
            wick = max(h[b:k + 1]) if down else min(l[b:k + 1])
            for dj in range(b, min(k + 3, n - 1)):
                if dj > wick_end and ((h[dj] > wick) if down else (l[dj] < wick)):
                    break
                r1 = h[dj] - l[dj]
                if r1 <= 0 or abs(c[dj] - o[dj]) > 0.1 * r1:
                    continue
                nx = dj + 1
                stop = max(wick, h[dj]) if down else min(wick, l[dj])
                if ((h[nx] > stop) if down else (l[nx] < stop)):
                    break
                avg = avgbody(o, c, nx)
                if (c[nx] < o[nx] if down else c[nx] > o[nx]) and abs(c[nx] - o[nx]) >= 1.5 * avg:
                    R = trade(h, l, c, nx, c[nx], stop, down)
                    if R is not None:
                        res1.append(("a", tt[nx], R, 60))
                # 15m inside the next 1H candle
                f = first15.get((tt[dj] // H1 + 1) * H1)
                if f is not None:
                    far = l[dj] if down else h[dj]
                    for y in range(f, min(f + 4, len(c5))):
                        if (h5[y] > stop) if down else (l5[y] < stop):
                            break
                        if (c5[y] < far) if down else (c5[y] > far):
                            R = trade(h5, l5, c5, y, c5[y], stop, down)
                            if R is not None:
                                res1.append(("b", t5[y], R, 15))
                            break
                break
    return res1, res2


def stats(rs):
    if not rs:
        return "     0"
    w = sum(1 for r in rs if r > 0)
    return f"{len(rs):5} | win {100 * w / len(rs):3.0f}% | avg {sum(rs) / len(rs):+.2f}R"


def main():
    r1, r2 = [], []
    for coin in COINS:
        a, b = run(coin)
        r1 += a
        r2 += b
        gc.collect()
        print(f"  {coin} done", flush=True)
    print("\n### TEST 1: 1H sweep + doji, then enter on (a) the 1H big candle or (b) the first 15m close past the doji")
    for v, name in (("a", "(a) 1H big candle close"), ("b", "(b) 15m close past the doji")):
        xs = [x for x in r1 if x[0] == v]
        print(f"  {name:30} all {stats([x[2] for x in xs])}   2019-22 {stats([x[2] for x in xs if x[1] < CUT])}   2023-on {stats([x[2] for x in xs if x[1] >= CUT])}")
    for tf in ("1H", "15m"):
        print(f"\n### TEST 2 ({tf}): FIND the best shapes on 2019-22, CHECK them on 2023-on (never seen)")
        groups = {}
        for x in r2:
            if x[0] == tf:
                groups.setdefault((x[2], x[3]), []).append(x)
        ranked = []
        for key, xs in groups.items():
            old = [x[4] for x in xs if x[1] < CUT]
            if len(old) >= 40:
                ranked.append((sum(old) / len(old), key, xs))
        ranked.sort(reverse=True)
        print(f"  {len(ranked)} shapes with 40+ trades in 2019-22. All shapes together: 2019-22 {stats([x[4] for x in r2 if x[0] == tf and x[1] < CUT])}, 2023-on {stats([x[4] for x in r2 if x[0] == tf and x[1] >= CUT])}")
        for avg, key, xs in ranked[:10]:
            print(f"  {key[0]:5} {key[1]:55}  FIND {stats([x[4] for x in xs if x[1] < CUT])}   CHECK {stats([x[4] for x in xs if x[1] >= CUT])}")


if __name__ == "__main__":
    main()
