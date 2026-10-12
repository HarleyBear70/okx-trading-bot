"""
PULLBACK_TEST: enter on the flip vs wait for the pullback (Oct 12 2026). From the David Delaney ad Jeff sent: entering
the moment a line flipped lost (-0.01R), waiting for the pullback made +0.20R. Jeff's own rule says the same: after an
MS, wait for the pullback before entering. ONE change only vs research/ibos_exit_test.py: the entry.
Fixed rules decided before the results. Paper research only.

  Signal   15m MS / BOS in the trade's direction (research/jeff_struct.py Heart swing 1), longs + mirrored shorts.
  Stop     past MUST HOLD (STRONG) - 0.05%; skip if more than 1.35% from the entry (Jeff's max stop).
  Entry A  "flip": at the signal candle's close (market: 0.02% taker + 0.02% slippage)  = ibos_exit_test entry
  Entry B  "pullback": limit at the 50% of the leg (Jeff's discount line), 0% fee        [NOT JEFF: wait limit below]
           cancelled if not filled within 24 candles (6 h), or if price reaches the 2R target / an opposite MS first.
           Fill and stop inside the same candle = counted as the stop.
  Entry C  "hold + break" (Tommy Galvin video Jeff sent, Oct 12): price pulls back to the 50% within 24 candles, then a
           candle CLOSES above the leg high within 24 more candles -> enter at that close (market). Cancelled if the
           stop is hit or an opposite MS comes first.                                   [NOT JEFF: the 24-candle windows]
  Exits    2R (limit, 0%) or MS only (stop, or the close of an MS against the trade); same for both entries.

  python3 research/pullback_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COST, GAP, MAXSTOP, WAIT = 0.0004, 0.0005, 0.0135, 24
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]


def prep(d):
    ts = d["ts"]
    O, H, L, C, e15 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 900000)
    T = [ts[i] for i in range(len(ts)) if e15[i] >= 0]
    s, sig, flip = Heart(H, L, C, 1), [], []
    for k in range(len(C)):
        ev = s.step(k)
        flip.append(ev == "MS DOWN")
        if ev in ("MS UP", "BOS up") and s.trend == 1 and s.rng[0] is not None:
            sig.append((k, "MS" if ev == "MS UP" else "BOS", s.strong - GAP * abs(s.strong), (s.rng[0] + s.rng[1]) / 2))
    return T, H, L, C, sig, flip


def walk(H, L, C, flip, j, e, stop, r, mode):
    """from candle j on, return (R, exit candle)"""
    n = len(C)
    tgt = e + 2 * r if mode == "2R" else None
    while j < n:
        if L[j] <= stop:
            return (stop - COST * abs(stop) - e) / r, j
        if tgt is not None and H[j] >= tgt:
            return 2.0, j
        if mode == "MS only" and flip[j]:
            return (C[j] - COST * abs(C[j]) - e) / r, j
        j += 1
    return None, n


def sim(T, H, L, C, sig, flip, kind, entry, mode):
    n, free, out = len(C), -1, []
    for k, kd, stop, mid in sig:
        if kd != kind or k <= free:
            continue
        if entry == "flip":
            e = C[k] + COST * abs(C[k])
            r = e - stop
            if r <= 0 or r / abs(C[k]) > MAXSTOP:
                continue
            R, j = walk(H, L, C, flip, k + 1, e, stop, r, mode)
        elif entry == "hold+break":
            top, j, touched, R = H[k], k + 1, None, None
            while j < n:
                if L[j] <= stop or flip[j] or j > (touched or k) + WAIT:
                    break
                if touched is None:
                    if L[j] <= mid:
                        touched = j
                    else:
                        top = max(top, H[j])
                elif C[j] > top:
                    e = C[j] + COST * abs(C[j])
                    r = e - stop
                    if 0 < r <= MAXSTOP * abs(C[j]):
                        R, j = walk(H, L, C, flip, j + 1, e, stop, r, mode)
                    break
                j += 1
            if R is None:
                free = j
                continue
        else:
            e, r = mid, mid - stop
            if r <= 0 or r / abs(mid) > MAXSTOP or C[k] <= mid:
                continue
            j, R = k + 1, None
            while j < n and j <= k + WAIT:
                if L[j] <= mid:  # filled
                    if L[j] <= stop:
                        R = (stop - COST * abs(stop) - e) / r
                    else:
                        R, j = walk(H, L, C, flip, j + 1, e, stop, r, mode) if not (mode == "MS only" and flip[j]) else ((C[j] - COST * abs(C[j]) - e) / r, j)
                    break
                if H[j] >= e + 2 * r or flip[j]:
                    break  # cancelled
                j += 1
            if R is None:
                free = j
                continue
        if R is None:
            break
        out.append((T[k], R))
        free = j
    return out


def stats(xs, signals):
    if not xs:
        return "0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return (f"{len(xs):6} trades" + (f" ({100 * len(xs) / signals:3.0f}% of signals)" if signals else "") + f", win {100 * len(w) / len(xs):3.0f}%, "
            f"avg {sum(xs) / len(xs):+.3f}R, total {sum(xs):+.0f}R, PF {sum(w) / gl if gl else 99:.2f}")


def main():
    keys = [(k, e, m) for k in ("MS", "BOS") for e in ("flip", "pullback", "hold+break") for m in ("2R", "MS only")]
    res, nsig = {x: [] for x in keys}, {"MS": 0, "BOS": 0}
    for coin in COINS:
        d = D.load(coin)
        for dd in (d, D.mirror(d)):
            p = prep(dd)
            for kd in nsig:
                nsig[kd] += sum(1 for s in p[4] if s[1] == kd)
            for x in keys:
                res[x] += sim(*p, *x)
            del p
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    for x in keys:
        t = res[x]
        print(f"\n### 15m {x[0]} signal, entry {x[1]}, exit {x[2]}")
        print("all     ", stats([r for _, r in t], nsig[x[0]]))
        print("2019-22 ", stats([r for ts, r in t if ts < CUT], 0))
        print("2023-on ", stats([r for ts, r in t if ts >= CUT], 0))


if __name__ == "__main__":
    main()
