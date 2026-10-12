"""
POC_TEST: volume-profile POC bounce (Nolan Vader video Jeff sent, Oct 12 2026, 30m chart). The video: price ranges,
breaks out of the value area, pulls back to the POC (the busiest price) and bounces -> long (short = mirror). The video
gives no exact numbers, so ALL numbers below are Claude's fill-ins, fixed before the results. Paper research only.

  Profile     the PREVIOUS UTC day: 5m volume put in 50 price bins at each candle's (H+L+C)/3.
              POC = busiest bin; value area = POC grown toward the bigger neighbour until 70% of the volume (VAH/VAL).
  Breakout    a 30m candle closes above VAH (that day).
  Entry       limit at the POC (0% fee), first touch after the breakout, same day. Cancelled if a 30m close below VAL
              comes first.
  Stop        VAL - 0.05% (the red box in the video ends near the bottom of the value area); skip if more than 1.35%.
  Exits       2R or 3R (limit, 0%); stop pays 0.02% + 0.02%. Checked on 5m candles; fill and stop in one candle = stop.
  Splits      4H leg (research/jeff_struct.py Heart) with the trade or not.
  One long and one short (mirrored prices) per day at most.

  python3 research/poc_test.py
"""
import array
import datetime as dt
import gc
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COST, GAP, MAXSTOP, BINS = 0.0004, 0.0005, 0.0135, 50
DAY, M30 = 86400000, 1800000
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]


def volume(coin, ts):
    with open(os.path.join(HERE, ".cache", f"M5_{coin}.json")) as f:
        vm = {r["ts"]: r["v"] for r in json.load(f)}
    return array.array("d", (vm.get(t, 0.0) for t in ts))


def profile(h, l, c, v, a, b):
    lo, hi = min(l[a:b]), max(h[a:b])
    if hi <= lo:
        return None
    w = (hi - lo) / BINS
    vol = [0.0] * BINS
    for i in range(a, b):
        vol[min(BINS - 1, int(((h[i] + l[i] + c[i]) / 3 - lo) / w))] += v[i]
    tot = sum(vol)
    if tot <= 0:
        return None
    p = max(range(BINS), key=lambda x: vol[x])
    i, j, s = p, p, vol[p]
    while s < 0.7 * tot:
        up = vol[j + 1] if j + 1 < BINS else -1
        dn = vol[i - 1] if i > 0 else -1
        if up >= dn:
            j += 1
            s += up
        else:
            i -= 1
            s += dn
    return lo + (p + 0.5) * w, lo + (j + 1) * w, lo + i * w  # POC, VAH, VAL


def run(d, v):
    ts, h, l, c = d["ts"], d["h"], d["l"], d["c"]
    n = len(ts)
    t4 = D.resample(ts, d["o"], h, l, c, 14400000)
    s4 = Heart(t4[1], t4[2], t4[3], 1)
    out = {2: [], 3: []}
    free = {2: -1, 3: -1}
    start, prof, stage = 0, None, None
    for i in range(n):
        k4 = t4[4][i]
        if k4 >= 0:
            s4.step(k4)
        if i > 0 and ts[i] // DAY != ts[i - 1] // DAY:  # new day: profile of the day that just ended
            prof, stage, start = profile(h, l, c, v, start, i), "wait", i
        if prof is None or stage is None:
            continue
        poc, vah, val = prof
        closes30 = (ts[i] + 300000) % M30 == 0
        if stage == "wait":
            if closes30 and c[i] > vah:
                stage = "armed"
            continue
        if stage == "armed":
            if l[i] <= poc:
                stage = None
                stop = val - GAP * abs(val)
                r = poc - stop
                if r <= 0 or r / abs(poc) > MAXSTOP:
                    continue
                for tr in (2, 3):
                    if i <= free[tr]:
                        continue
                    tgt, j, R = poc + tr * r, i, None
                    if l[i] <= stop:
                        R = (stop - COST * abs(stop) - poc) / r
                    else:
                        j = i + 1
                        while j < n:
                            if l[j] <= stop:
                                R = (stop - COST * abs(stop) - poc) / r
                                break
                            if h[j] >= tgt:
                                R = float(tr)
                                break
                            j += 1
                    if R is not None:
                        out[tr].append((ts[i], R, s4.trend == 1))
                        free[tr] = j
            elif closes30 and c[i] < val:
                stage = None
    return out


def stats(xs):
    if not xs:
        return "     0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return f"{len(xs):6} trades, win {100 * len(w) / len(xs):3.0f}%, avg {sum(xs) / len(xs):+.3f}R, PF {sum(w) / gl if gl else 99:.2f}"


def main():
    res = {(tr, side): [] for tr in (2, 3) for side in ("long", "short")}
    for coin in COINS:
        d = D.load(coin)
        v = volume(coin, d["ts"])
        for side, dd in (("long", d), ("short", D.mirror(d))):
            for tr, rows in run(dd, v).items():
                res[(tr, side)] += rows
        del d, v
        gc.collect()
        print(f"  {coin} done", flush=True)
    for tr in (2, 3):
        allx = res[(tr, "long")] + res[(tr, "short")]
        print(f"\n### POC bounce after a value-area breakout, target {tr}R")
        print("all          ", stats([x[1] for x in allx]))
        print("longs        ", stats([x[1] for x in res[(tr, 'long')]]))
        print("shorts       ", stats([x[1] for x in res[(tr, 'short')]]))
        print("2019-22      ", stats([x[1] for x in allx if x[0] < CUT]))
        print("2023-on      ", stats([x[1] for x in allx if x[0] >= CUT]))
        print("4H with      ", stats([x[1] for x in allx if x[2]]))
        print("4H against   ", stats([x[1] for x in allx if not x[2]]))


if __name__ == "__main__":
    main()
