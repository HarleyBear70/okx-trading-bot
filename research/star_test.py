"""
STAR_TEST: evening star (short) and morning star (long), textbook version (Oct 11 2026). Jeff's 15m BTC short at an
evening star won +3.09R tonight; he asked: does it work both ways, and is it "buyers out of fuel"? Jeff: "try both,
i dont trust my eyes" -> textbook pattern, fixed rules decided BEFORE the results. Paper research only.

  Pattern (evening star; morning star = exact mirror, run on mirrored prices):
    candle 1  green, body at least the average body of the 14 candles before it   [NOT JEFF: "strong move" number]
    candle 2  body no more than 1/3 of candle 1's body (the stall)
    candle 3  red, closes below the middle of candle 1's body
  Entry       candle 3's close (market: 0.02% taker + 0.02% slippage)
  Stop        highest high of the 3 candles + 0.05% (Jeff's cushion); skip if more than 1.35% away (Jeff's max stop)
  Exits       2R, 3R (limit, 0%), or MS only (no target: stop, or the close of an MS against the trade on the same TF)
              checked on 5m candles; stop and target in one 5m candle = the stop.
  Timeframes  5m, 15m, 1H (Heart swing 1 = research/jeff_struct.py for the MS exit and the splits)
  Splits (to learn, not filters): 4H leg with the trade, star in the 1H premium (discount for longs), both.

  python3 research/star_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COST, GAP, MAXSTOP = 0.0004, 0.0005, 0.0135
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]
TFS = {"5m": 300000, "15m": 900000, "1H": 3600000}
EXITS = ["2R", "3R", "MS only"]


def run(d):
    """shorts on this data. returns {tf: [(ts, {exit: R}, splits)]}"""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    n = len(ts)
    t4 = D.resample(ts, o, h, l, c, 14400000)
    s4 = Heart(t4[1], t4[2], t4[3], 1)
    tf = {}
    for name, size in TFS.items():
        O, H, L, C, e = D.resample(ts, o, h, l, c, size)
        tf[name] = (O, H, L, C, e, Heart(H, L, C, 1), [None] * len(C))
    sigs = {name: [] for name in TFS}
    for i in range(n):
        k4 = t4[4][i]
        if k4 >= 0:
            s4.step(k4)
        for name, (O, H, L, C, e, s, ev) in tf.items():
            k = e[i]
            if k < 0:
                continue
            ev[k] = s.step(k)
            if k < 16:
                continue
            b1, b2 = C[k - 2] - O[k - 2], abs(C[k - 1] - O[k - 1])
            avg = sum(abs(C[j] - O[j]) for j in range(k - 16, k - 2)) / 14
            if b1 <= 0 or b1 < avg or b2 > b1 / 3 or C[k] >= O[k] or C[k] >= (O[k - 2] + C[k - 2]) / 2:
                continue
            top = max(H[k - 2], H[k - 1], H[k])
            lo1, hi1 = tf["1H"][5].rng
            sigs[name].append((i, C[k], top, {"4H with": s4.trend == -1,
                                              "1H premium": lo1 is not None and top > (lo1 + hi1) / 2}))
    out = {}
    for name, sg in sigs.items():
        e, ev = tf[name][4], tf[name][6]
        res, free = [], {x: -1 for x in EXITS}
        for i, cl, top, sp in sg:
            entry = cl - COST * abs(cl)
            stop = top + GAP * abs(top)
            r = stop - entry
            if r <= 0 or r / abs(entry) > MAXSTOP:
                continue
            got = {}
            for x in EXITS:
                if i <= free[x]:
                    continue
                tgt = entry - (2 if x == "2R" else 3) * r if x != "MS only" else None
                j, R = i + 1, None
                while j < n:
                    if h[j] >= stop:
                        R = -(stop + COST * abs(stop) - entry) / r
                        break
                    if tgt is not None and l[j] <= tgt:
                        R = 2.0 if x == "2R" else 3.0
                        break
                    if tgt is None and e[j] >= 0 and ev[e[j]] == "MS UP":
                        R = (entry - c[j] - COST * abs(c[j])) / r
                        break
                    j += 1
                if R is not None:
                    got[x] = R
                    free[x] = j
            if got:
                res.append((ts[i], got, sp))
        out[name] = res
    return out


def stats(xs):
    if not xs:
        return "     0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return f"{len(xs):6} trades, win {100 * len(w) / len(xs):3.0f}%, avg {sum(xs) / len(xs):+.3f}R, PF {sum(w) / gl if gl else 99:.2f}"


def main():
    res = {(t, side): [] for t in TFS for side in ("short", "long")}
    for coin in COINS:
        d = D.load(coin)
        for side, dd in (("short", d), ("long", D.mirror(d))):
            for t, v in run(dd).items():
                res[(t, side)] += [(coin,) + x for x in v]
            gc.collect()
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    for t in TFS:
        allx = res[(t, "short")] + res[(t, "long")]
        for x in EXITS:
            g = lambda rows: [r[2][x] for r in rows if x in r[2]]
            print(f"\n### {t} stars, exit {x}")
            print("all               ", stats(g(allx)))
            print("evening (short)   ", stats(g(res[(t, 'short')])))
            print("morning (long)    ", stats(g(res[(t, 'long')])))
            print("2019-22           ", stats(g([r for r in allx if r[1] < CUT])))
            print("2023-now          ", stats(g([r for r in allx if r[1] >= CUT])))
            for key in ("4H with", "1H premium"):
                print(f"{key + ' yes':18}", stats(g([r for r in allx if r[3][key]])))
                print(f"{key + ' no':18}", stats(g([r for r in allx if not r[3][key]])))
            both = [r for r in allx if r[3]["4H with"] and r[3]["1H premium"]]
            print("4H with + zone    ", stats(g(both)))
            print("  same, 2023-now  ", stats(g([r for r in both if r[1] >= CUT])))


if __name__ == "__main__":
    main()
