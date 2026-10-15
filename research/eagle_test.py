"""
EAGLE_TEST: Jeff, Oct 15 2026: the "eagle" double top from a Trade Mastermind picture. "most people wait for the
retest and then when it doesnt go anywhere they go in." Test both entries on 7 years of data. Read-only research.
  Eagle (short; longs = mirror, a double bottom):
    top 1   a swing high (3 candles lower on each side)                                   [CLAUDE: 3]
    top 2   a later swing high within 50 candles that pokes ABOVE top 1 by at most 0.3%,
            no candle in between went above top 1, and top 2's candle closes back below
            top 1's high (= the sweep of the equal highs)                                  [CLAUDE: 50, 0.3%]
    neck    the lowest low between the two tops
    break   the first close below the neck within 30 candles after top 2 is known,
            before price goes above top 2                                                  [CLAUDE: 30]
  (b) BREAK   enter at the break candle's close
  (a) RETEST  after the break, wait up to 10 candles for price to come back up to the neck,
              enter there (limit at the neck). No retest in 10 = no trade. If the stop gets
              hit before the retest = no trade. Stop hit on the fill candle = counted a loss.   [CLAUDE: 10]
  Both: stop above top 2 + 0.05%, max stop 1.35%, target 2R, Binance.US costs (orange_test.trade).
  BTC ETH SOL XRP, 1H and 15m, 2019 to Sep 2026, split 2019-22 / 2023-on.
  python3 research/eagle_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from orange_test import trade  # noqa: E402

CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP"]
N, LOOK, POKE, BRK, RET = 3, 50, 0.003, 30, 10


def eagles(h, l, c, down):
    """yield (top1, top2, known, wick, neck) in price terms flipped so the code is written for a short"""
    n = len(c)
    piv = []
    for p in range(N, n - N):
        if all(h[p] > h[x] for x in range(p - N, p)) and all(h[p] >= h[x] for x in range(p + 1, p + N + 1)):
            piv.append(p)
    for i, p2 in enumerate(piv):
        for p1 in reversed(piv[:i]):
            if p2 - p1 > LOOK:
                break
            t1 = h[p1]
            if not (t1 <= h[p2] <= t1 + abs(t1) * POKE) or c[p2] >= t1:
                continue
            if any(h[x] > t1 for x in range(p1 + 1, p2)):
                continue
            yield p1, p2, p2 + N, h[p2], min(l[p1:p2 + 1])
            break


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
    h0, l0, c0 = list(H), list(L), list(C)
    n = len(c0)
    res = []
    for down in (True, False):
        # longs: flip prices so a double bottom looks like a double top
        h, l, c = (h0, l0, c0) if down else ([-x for x in l0], [-x for x in h0], [-x for x in c0])
        for p1, p2, k, wick, neck in eagles(h, l, c, down):
            b = None
            for j in range(k + 1, min(k + 1 + BRK, n)):
                if h[j] > wick:
                    break
                if c[j] < neck:
                    b = j
                    break
            if b is None:
                continue
            side = "SHORT" if down else "LONG"
            raw = (lambda x: x) if down else (lambda x: -x)
            # (b) break entry
            Rb = trade(h0, l0, c0, b, raw(c[b]), raw(wick), down)
            # (a) retest entry
            Ra, retest = None, False
            for j in range(b + 1, min(b + 1 + RET, n)):
                if h[j] >= neck:
                    retest = True
                    # filled at the neck; if this same candle also ran past top 2, start the check on it (= loss)
                    Ra = trade(h0, l0, c0, j - 1 if h[j] > wick else j, raw(neck), raw(wick), down)
                    break
            res.append((tt[b], side, Rb, Ra, retest))
    return res


def stats(rs):
    rs = [r for r in rs if r is not None]
    if not rs:
        return "     0"
    w = sum(1 for r in rs if r > 0)
    return f"{len(rs):5} | win {100 * w / len(rs):3.0f}% | avg {sum(rs) / len(rs):+.2f}R"


def main():
    for size, tf in ((3600000, "1H"), (900000, "15m")):
        allx = []
        for coin in COINS:
            allx += run(coin, size)
            gc.collect()
        print(f"\n### {tf} EAGLE (double top/bottom sweep -> break of the neck)  BTC ETH SOL XRP, 2019 to Sep 2026, 2R")
        print(f"  eagles that broke the neck: {len(allx)}; retest came within {RET} candles: "
              f"{sum(1 for x in allx if x[4])} ({100 * sum(1 for x in allx if x[4]) / max(len(allx), 1):.0f}%)")
        for lab, f in (("all", lambda x: True), ("shorts (double top)", lambda x: x[1] == "SHORT"),
                       ("longs (double bottom)", lambda x: x[1] == "LONG"),
                       ("2019-22", lambda x: x[0] < CUT), ("2023-on", lambda x: x[0] >= CUT)):
            xs = [x for x in allx if f(x)]
            print(f"  {lab:24} (b) BREAK  {stats([x[2] for x in xs]):36} (a) RETEST {stats([x[3] for x in xs])}")
        xs = [x for x in allx if not x[4]]
        print(f"  break entries where the retest NEVER came: {stats([x[2] for x in xs])}")
        xs = [x for x in allx if x[4]]
        print(f"  break entries where the retest DID come:   {stats([x[2] for x in xs])}", flush=True)


if __name__ == "__main__":
    main()
