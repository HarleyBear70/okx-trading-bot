"""
BROWN_TEST: Jeff, Oct 14 2026: "i just see a few brown candles that say internal down but they really dont drop that much
and then before u know it something huge happens." Which browns (and teals) lead to a real move, and which fizzle?
Tier 1 rules exactly as on Jeff's chart (research/struct_t1.py) on 15m candles, 4H trend = the same rules on 4H candles
(last closed 4H candle). Read-only research, nothing traded.
  Trade per brown (teal = mirror):  short at the brown candle's close.
    Stop    above the high the brown came from (the top it broke down from) + Jeff's 0.05% cushion; skip if the stop
            is more than 1.35% away (Jeff's max stop).
    Target  2R (Jeff's minimum). Costs: Binance.US 0.02% taker + 0.02% slippage on entry and stop.
    [CLAUDE: stop/target placement is this test's choice, not one of Jeff's written rules]
  Also "how far did it go": the best move in R within the next 16 candles (4 hours), before the stop.
  Groups (learning splits, not filters): 15m trend, 4H trend, premium/discount of the 15m fib, and SWEPT $$$: the
  top the brown came from took out an older untaken top (a green-then-red top, same as the chart's $$$ list) or
  yesterday's high = it grabbed liquidity first (Brad: "no sweep, no entry"). Teal = mirror.
  python3 research/brown_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
import struct_t1 as T  # noqa: E402

COST, GAP, MAXSTOP = 0.0004, 0.0005, 0.0135
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP"]


def run(coin):
    d = D.load(coin)
    ts = d["ts"]
    O, H, L, C, e15 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 900000)
    _, H4, L4, C4, e4 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 14400000)
    t15 = [0] * len(C)
    for i, k in enumerate(e15):
        if k >= 0:
            t15[k] = ts[i]
    # 4H trend known at the close of each 15m candle (last closed 4H candle)
    s4 = T.Tier1(list(H4), list(L4), list(C4))
    tr4, cur4 = [0] * len(C), 0
    for i in range(len(ts)):
        if e4[i] >= 0:
            s4.step(e4[i])
            cur4 = s4.trend
        if e15[i] >= 0:
            tr4[e15[i]] = cur4
    del d, s4
    gc.collect()
    h, l, c, o = list(H), list(L), list(C), list(O)
    s = T.Tier1(h, l, c)
    out = []
    n = len(c)
    # which candles took liquidity: a wick past an untaken top (bottom) or past yesterday's high (low)
    swh, swl = [False] * n, [False] * n
    tops, bots = [], []
    day, dhi, dlo, pdh, pdl = None, None, None, None, None
    for k in range(n):
        dd = t15[k] // 86400000
        if dd != day:
            pdh, pdl, day, dhi, dlo = dhi, dlo, dd, h[k], l[k]
        else:
            dhi, dlo = max(dhi, h[k]), min(dlo, l[k])
        nt = [t for t in tops if h[k] <= t]
        swh[k] = len(nt) < len(tops) or (pdh is not None and h[k] > pdh)
        tops = nt
        nb = [b for b in bots if l[k] >= b]
        swl[k] = len(nb) < len(bots) or (pdl is not None and l[k] < pdl)
        bots = nb
        if k and c[k - 1] > o[k - 1] and c[k] < o[k]:
            tops.append(max(h[k - 1], h[k]))
        if k and c[k - 1] < o[k - 1] and c[k] > o[k]:
            bots.append(min(l[k - 1], l[k]))
        if len(tops) > 400:
            tops = tops[-400:]
        if len(bots) > 400:
            bots = bots[-400:]
    for k in range(n):
        ihi, ilo = s.ihi, s.ilo
        for b, ev, lvl in s.step(k):
            if b != k or not ev.startswith("iBOS"):
                continue
            down = ev == "iBOS down"
            src = ihi if down else ilo
            if src is None:
                continue
            e = c[k] * (1 - COST) if down else c[k] * (1 + COST)
            stop = h[src] * (1 + GAP) if down else l[src] * (1 - GAP)
            r = (stop - e) if down else (e - stop)
            if r <= 0 or r / c[k] > MAXSTOP:
                continue
            tgt = e - 2 * r if down else e + 2 * r
            R, best, j = None, 0.0, k + 1
            while j < n:
                hit_stop = h[j] >= stop if down else l[j] <= stop
                if hit_stop:
                    R = -(abs(stop - e) + COST * stop) / r
                    break
                fav = (e - l[j]) / r if down else (h[j] - e) / r
                if j <= k + 16:
                    best = max(best, fav)
                if (l[j] <= tgt) if down else (h[j] >= tgt):
                    R = 2.0
                    if j <= k + 16:
                        best = max(best, fav)
                    break
                j += 1
            if R is None:
                continue
            mid = (s.strong + s.weak) / 2 if s.strong is not None else c[k]
            prem = c[k] > mid
            with15 = s.trend == (-1 if down else 1)
            with4 = tr4[k] == (-1 if down else 1)
            right_half = prem if down else not prem
            swept = any(swh[x] for x in range(max(src - 1, 0), src + 1)) if down else any(swl[x] for x in range(max(src - 1, 0), src + 1))
            out.append((t15[k], down, R, best, with15, with4, right_half, swept))
    return out


def stats(xs):
    if not xs:
        return "     0"
    w = sum(1 for x in xs if x[2] > 0)
    avg = sum(x[2] for x in xs) / len(xs)
    big = sum(1 for x in xs if x[3] >= 2) / len(xs)
    fizz = sum(1 for x in xs if x[3] < 0.5) / len(xs)
    return f"{len(xs):6} | win {100 * w / len(xs):3.0f}% | avg {avg:+.2f}R | went 2R+ in 4h {100 * big:3.0f}% | fizzled (<0.5R) {100 * fizz:3.0f}%"


def main():
    allx = []
    for coin in COINS:
        allx += run(coin)
        gc.collect()
        print(f"  {coin} done", flush=True)
    for name, side in (("BROWN (internal down) -> short", True), ("TEAL (internal up) -> long", False)):
        xs = [x for x in allx if x[1] == side]
        print(f"\n### {name}   (BTC ETH SOL XRP 15m, 2019 to Sep 2026)")
        print("  all                                 ", stats(xs))
        print("  2019-22                             ", stats([x for x in xs if x[0] < CUT]))
        print("  2023-on                             ", stats([x for x in xs if x[0] >= CUT]))
        print("  with the 15m trend                  ", stats([x for x in xs if x[4]]))
        print("  against the 15m trend               ", stats([x for x in xs if not x[4]]))
        print("  with the 4H trend                   ", stats([x for x in xs if x[5]]))
        print("  against the 4H trend                ", stats([x for x in xs if not x[5]]))
        print("  right half of the fib               ", stats([x for x in xs if x[6]]))
        print("  wrong half of the fib               ", stats([x for x in xs if not x[6]]))
        print("  4H with + right half                ", stats([x for x in xs if x[5] and x[6]]))
        print("  4H with + 15m with + right half     ", stats([x for x in xs if x[4] and x[5] and x[6]]))
        print("  4H with + 15m AGAINST + right half  ", stats([x for x in xs if not x[4] and x[5] and x[6]]))
        print("  SWEPT $$$ first                     ", stats([x for x in xs if x[7]]))
        print("  no sweep                            ", stats([x for x in xs if not x[7]]))
        print("  swept + 4H with                     ", stats([x for x in xs if x[7] and x[5]]))
        print("  swept + 4H with + right half        ", stats([x for x in xs if x[7] and x[5] and x[6]]))
        print("  swept + 4H with + right half, 2023+ ", stats([x for x in xs if x[7] and x[5] and x[6] and x[0] >= CUT]))


if __name__ == "__main__":
    main()
