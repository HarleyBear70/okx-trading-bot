"""
IBOS_TEST: Jeff's iBOS entry idea (Oct 11 2026, LINK): after buyers push a 15m up leg, the first candle BODY that closes
below the low of the candle that made the top = internal BOS = "sellers took control of the small moves" -> short right
at that close, stop above the top, target 2R / 3R (Jeff's LINK study: R:R 2.82). Longs = the exact mirror.
Paper research only. Fixed rules decided BEFORE looking at results.

  Structure    research/jeff_struct.py Heart, swing 1, on 15m (from Binance 5m candles 2019 - Sep 2026).
  iBOS A       close below the LOW OF THE TOP CANDLE (the candle that made the leg's high) - Jeff's LINK example.
  iBOS B       close below the most recent swing low INSIDE the leg (swing 1), above MUST HOLD - Jeff's rule 18 wording.
               Both: the leg is still UP (close stays above MUST HOLD, so it is not the full MS), one try per top / low.
  Entry        at the signal candle's close (market: 0.02% taker + 0.02% slippage).
  Stop         the top + 0.05% (Jeff's cushion). Skip if more than 1.35% away (Jeff's max stop).
  Target       2R or 3R, limit (0%). Stop pays 0.02% + 0.02%. Exits checked on 5m candles; both in one = stop.
  Splits (to learn, not filters): 1H leg with / against, 4H leg with / against, RSI(14) 15m above 70 (below 30 for
  longs) in the 5 candles before, top in the 1H premium (bottom in discount for longs).

  python3 research/ibos_test.py
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


def rsi(c, n=14):
    out, g, l = [50.0] * len(c), 0.0, 0.0
    for i in range(1, len(c)):
        ch = c[i] - c[i - 1]
        up, dn = max(ch, 0.0), max(-ch, 0.0)
        if i <= n:
            g += up / n
            l += dn / n
        else:
            g = (g * (n - 1) + up) / n
            l = (l * (n - 1) + dn) / n
        out[i] = 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    return out


def signals(d):
    """shorts on this data (run on mirrored data for longs). returns list of (5m index, kind, entry, top, splits)"""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    O, H, L, C, e15 = D.resample(ts, o, h, l, c, 900000)
    t1, t4 = D.resample(ts, o, h, l, c, 3600000), D.resample(ts, o, h, l, c, 14400000)
    s15, s1, s4 = Heart(H, L, C, 1), Heart(t1[1], t1[2], t1[3], 1), Heart(t4[1], t4[2], t4[3], 1)
    r = rsi(C)
    out, usedA, usedB = [], -1, -1
    for i in range(len(ts)):
        for s, t in ((s1, t1), (s4, t4)):
            k = t[4][i]
            if k >= 0:
                s.step(k)
        k = e15[i]
        if k < 0:
            continue
        tr, wb, weak, strong, pl, plb, sb = s15.trend, s15.wb, s15.weak, s15.strong, s15.pl, s15.plb, s15.sb
        s15.step(k)
        if tr != 1 or s15.pend is not None or H[k] > weak or C[k] < strong or k <= wb:
            continue
        kinds = []
        if C[k] < L[wb] and wb != usedA:
            kinds.append("A")
            usedA = wb
        if pl is not None and plb > sb and plb > wb and pl > strong and C[k] < pl and plb != usedB:
            kinds.append("B")
            usedB = plb
        if not kinds:
            continue
        lo1, hi1 = s1.rng
        sp = {"1H with": s1.trend == -1, "4H with": s4.trend == -1, "RSI hot": max(r[max(0, k - 5):k]) > 70,
              "top in 1H premium": lo1 is not None and weak > (lo1 + hi1) / 2}
        for kind in kinds:
            out.append((i, kind, C[k], weak, sp))
    return out


def sim(d, sigs, kind, tr):
    ts, h, l = d["ts"], d["h"], d["l"]
    n, free, res = len(ts), -1, []
    for i, kd, c, top, sp in sigs:
        if kd != kind or i <= free:
            continue
        e = c - COST * abs(c)  # selling: get a bit less
        stop = top + GAP * abs(top)
        r = stop - e
        if r <= 0 or r / abs(e) > MAXSTOP:
            continue
        tgt = e - tr * r
        j, x = i + 1, None
        while j < n:
            if h[j] >= stop:
                x = -(stop + COST * abs(stop) - e) / r
                break
            if l[j] <= tgt:
                x = float(tr)
                break
            j += 1
        if x is None:
            break
        res.append((ts[i], x, sp))
        free = j
    return res


def stats(xs):
    if not xs:
        return "0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return f"{len(xs):5} trades, win {100 * len(w) / len(xs):3.0f}%, avg {sum(xs) / len(xs):+.3f}R, PF {sum(w) / gl if gl else 99:.2f}"


def main():
    res = {(k, t, side): [] for k in "AB" for t in (2, 3) for side in ("short", "long")}
    for coin in COINS:
        d = D.load(coin)
        for side, dd in (("short", d), ("long", D.mirror(d))):
            sigs = signals(dd)
            for k in "AB":
                for t in (2, 3):
                    res[(k, t, side)] += [(coin,) + x for x in sim(dd, sigs, k, t)]
            del sigs
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    for k in "AB":
        for t in (2, 3):
            allx = res[(k, t, "short")] + res[(k, t, "long")]
            print(f"\n### iBOS {k} ({'top candle low' if k == 'A' else 'last swing low inside the leg'}), target {t}R")
            print("all             ", stats([x[2] for x in allx]))
            print("shorts          ", stats([x[2] for x in res[(k, t, 'short')]]))
            print("longs           ", stats([x[2] for x in res[(k, t, 'long')]]))
            print("2019-22         ", stats([x[2] for x in allx if x[1] < CUT]))
            print("2023-now        ", stats([x[2] for x in allx if x[1] >= CUT]))
            for key in ("1H with", "4H with", "RSI hot", "top in 1H premium"):
                print(f"{key + ' yes':16}", stats([x[2] for x in allx if x[3][key]]))
                print(f"{key + ' no':16}", stats([x[2] for x in allx if not x[3][key]]))
            both = [x[2] for x in allx if x[3]["1H with"] and x[3]["top in 1H premium"]]
            print("1H with+premium ", stats(both))
            for coin in COINS:
                print(f"   {coin:5}", stats([x[2] for x in allx if x[0] == coin]))


if __name__ == "__main__":
    main()
