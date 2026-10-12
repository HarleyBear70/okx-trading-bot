"""
BRAD3_TEST: Brad Goh "Price Action Was Hard, Until I Discovered This SIMPLE 3-Step Trick" + "How I Find My Daily Bias"
(videos Jeff sent, Oct 12 2026). Direction (4H) -> Location (discount/premium of the 4H swing range) -> Execution (15m,
three price-action confluences), stop past the rejection candle, target 3R. The video shows the idea but no exact
numbers, so the marked parts are Claude's fill-ins, fixed BEFORE the results. Paper research only.

  Direction  4H leg (research/jeff_struct.py Heart, BOS-based swing range) is UP (shorts = mirrored prices).
  Location   the 15m candle closes in the discount of the 4H range: below the 50% and above MUST HOLD.
             [NOT IN VIDEO: Brad also wants a 1H demand zone there; zones are not tested here]
  Execution  on one 15m close, all three:
             1 strong rejection: the candle engulfs the last candle's body, OR the last candle is a pin (lower wick at
               least 2x its body) and this candle is "displacement" (body at least the 14-candle average)  [NOT IN VIDEO: 2x, 14]
             2 break and close: this candle is green and closes above the last candle's high
             3 failure to continue: the last candle made a lower low than the one before it but closed back above
               that low (sellers pushed and failed)                                       [NOT IN VIDEO: exact shape]
  Entry      at that 15m close (market: 0.02% taker + 0.02% slippage)
  Stop       below the lowest low of the last 2 candles - 0.05% (Jeff's cushion); skip if more than 1.35% (Jeff's max)
  Exit       3R (video), also 2R shown. Checked on 5m candles; stop and target in one 5m candle = the stop.
  Splits (to learn, not filters): the low swept the prior UTC day's low (daily bias video), no location step,
             no direction step.

  python3 research/brad3_test.py
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
DAY = 86400000
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]
TGTS = (2, 3)


def run(d):
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    n = len(ts)
    t4 = D.resample(ts, o, h, l, c, 14400000)
    s4 = Heart(t4[1], t4[2], t4[3], 1)
    O, H, L, C, e15 = D.resample(ts, o, h, l, c, 900000)
    sigs = []
    pdl, dlo, day = None, None, None  # prior day low, today's running low
    for i in range(n):
        dd = ts[i] // DAY
        if dd != day:
            pdl, dlo, day = dlo, l[i], dd
        elif l[i] < dlo:
            dlo = l[i]
        k4 = t4[4][i]
        if k4 >= 0:
            s4.step(k4)
        k = e15[i]
        if k < 16:
            continue
        b0, b1 = C[k] - O[k], C[k - 1] - O[k - 1]
        if b0 <= 0 or C[k] <= H[k - 1]:  # 2 break and close
            continue
        avg = sum(abs(C[j] - O[j]) for j in range(k - 15, k - 1)) / 14
        engulf = b1 < 0 and C[k] >= O[k - 1] and O[k] <= C[k - 1]
        pin = (min(O[k - 1], C[k - 1]) - L[k - 1]) >= 2 * abs(b1) and b0 >= avg
        if not (engulf or pin):  # 1 strong rejection
            continue
        if not (L[k - 1] < L[k - 2] and C[k - 1] > L[k - 2]):  # 3 failure to continue
            continue
        lo4, hi4 = s4.rng
        with4 = s4.trend == 1
        disc = with4 and lo4 is not None and lo4 < C[k] < (lo4 + hi4) / 2
        low = min(L[k], L[k - 1])
        sigs.append((i, C[k], low, with4, disc, pdl is not None and low < pdl))
    out = {t: [] for t in TGTS}
    free = {t: -1 for t in TGTS}
    for i, cl, low, with4, disc, swept in sigs:
        e = cl + COST * abs(cl)
        stop = low - GAP * abs(low)
        r = e - stop
        if r <= 0 or r / abs(cl) > MAXSTOP:
            continue
        for t in TGTS:
            tgt, j, R = e + t * r, i + 1, None
            while j < n:
                if l[j] <= stop:
                    R = (stop - COST * abs(stop) - e) / r
                    break
                if h[j] >= tgt:
                    R = float(t)
                    break
                j += 1
            if R is None:
                continue
            full = disc and i > free[t]  # the full model trades one at a time
            if full:
                free[t] = j
            out[t].append((ts[i], R, with4, disc, swept, full))
    return out


def stats(xs):
    if not xs:
        return "     0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return f"{len(xs):6} trades, win {100 * len(w) / len(xs):3.0f}%, avg {sum(xs) / len(xs):+.3f}R, PF {sum(w) / gl if gl else 99:.2f}"


def main():
    res = {(t, s): [] for t in TGTS for s in ("long", "short")}
    for coin in COINS:
        d = D.load(coin)
        for side, dd in (("long", d), ("short", D.mirror(d))):
            for t, rows in run(dd).items():
                res[(t, side)] += rows
            gc.collect()
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    for t in TGTS:
        allx = res[(t, "long")] + res[(t, "short")]
        full = [x for x in allx if x[5]]
        print(f"\n### Brad 3-step, target {t}R")
        print("FULL MODEL (4H with + discount + 15m 3 confluences, one at a time)")
        print("  all          ", stats([x[1] for x in full]))
        print("  longs        ", stats([x[1] for x in res[(t, 'long')] if x[5]]))
        print("  shorts       ", stats([x[1] for x in res[(t, 'short')] if x[5]]))
        print("  2019-22      ", stats([x[1] for x in full if x[0] < CUT]))
        print("  2023-on      ", stats([x[1] for x in full if x[0] >= CUT]))
        print("  swept PDL yes", stats([x[1] for x in full if x[4]]))
        print("  swept PDL no ", stats([x[1] for x in full if not x[4]]))
        print("WHAT EACH STEP ADDS (every signal, overlapping trades allowed)")
        print("  15m only              ", stats([x[1] for x in allx]))
        print("  15m + 4H with         ", stats([x[1] for x in allx if x[2]]))
        print("  15m + 4H against      ", stats([x[1] for x in allx if not x[2]]))
        print("  15m + 4H with + disc  ", stats([x[1] for x in allx if x[3]]))
        print("  15m + 4H with, no disc", stats([x[1] for x in allx if x[2] and not x[3]]))


if __name__ == "__main__":
    main()
