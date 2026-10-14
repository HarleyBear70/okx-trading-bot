"""
ORANGE_TEST: Jeff, Oct 14 2026: "i seen two orange candles sweep and then booom big drop the floor fell out. i missed a
huge short." Do Tier 1 sweeps (ORANGE on Jeff's chart) lead to a move the other way?
Tier 1 exactly as on the chart (research/struct_t1.py) on 15m, 4H trend = same rules on 4H (last closed 4H candle).
  Sweeps of a HIGH -> short: sweep of WEAK in an uptrend, sweep of STRONG in a downtrend, sweep of a key high (downtrend),
                             MS undone in a downtrend (a close above STRONG that the next candle took back).
  Sweeps of a LOW -> long:   the mirror.
  Entry   (a) at the orange candle's close (for "MS undone": the candle that took it back)
          (b) confirmed: within the next 3 candles, a candle closes past the orange candle's far end (below its low for
              a short); entry at that close.                                                 [CLAUDE: 3 candles]
  Stop    past the sweep wick (the highest high of the orange candle(s)) + Jeff's 0.05%; skip if more than 1.35% away.
  Target  2R (Jeff's minimum). Binance.US costs: 0.02% taker + 0.02% slippage on entry and stop.
          [CLAUDE: stop/target placement is this test's choice]
  Splits  which level was swept, 4H with/against, "two oranges" (another orange in the 4 candles before), 2019-22/2023+.
  python3 research/orange_test.py
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


def trade(h, l, c, k, e_raw, stop_raw, down):
    """R of a trade entered at candle k's close; None if it never finished"""
    n = len(c)
    e = e_raw * (1 - COST) if down else e_raw * (1 + COST)
    stop = stop_raw * (1 + GAP) if down else stop_raw * (1 - GAP)
    r = (stop - e) if down else (e - stop)
    if r <= 0 or r / e_raw > MAXSTOP:
        return None
    tgt = e - 2 * r if down else e + 2 * r
    for j in range(k + 1, n):
        if (h[j] >= stop) if down else (l[j] <= stop):
            return -(abs(stop - e) + COST * stop) / r
        if (l[j] <= tgt) if down else (h[j] >= tgt):
            return 2.0
    return None


def run(coin):
    d = D.load(coin)
    ts = d["ts"]
    O, H, L, C, e15 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 900000)
    _, H4, L4, C4, e4 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 14400000)
    t15 = [0] * len(C)
    for i, k in enumerate(e15):
        if k >= 0:
            t15[k] = ts[i]
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
    h, l, c = list(H), list(L), list(C)
    s = T.Tier1(h, l, c)
    n = len(c)
    orange = [False] * n
    out = []
    for k in range(n):
        tr = s.trend
        for b, ev, lvl in s.step(k):
            if not ev.startswith("sweep"):
                continue
            orange[b] = True
            if tr == 0:
                continue
            up = tr == 1
            if ev == "sweep of WEAK":
                down, kind = up, "WEAK"
            elif ev == "sweep of STRONG":
                down, kind = not up, "STRONG"
            elif ev.startswith("sweep of key"):
                down, kind = ev.endswith("high"), "key"
            else:  # MS undone: candle b closed past STRONG, candle k took it back
                down, kind = not up, "MS undone"
            first = b
            last = k
            wick = max(h[first:last + 1]) if down else min(l[first:last + 1])
            two = any(orange[x] for x in range(max(first - 4, 0), first))
            with4 = tr4[k] == (-1 if down else 1)
            Ra = trade(h, l, c, k, c[k], wick, down)
            Rb = None
            far = min(l[first:last + 1]) if down else max(h[first:last + 1])
            for j in range(k + 1, min(k + 4, n)):
                if (h[j] > wick) if down else (l[j] < wick):
                    break
                if (c[j] < far) if down else (c[j] > far):
                    Rb = trade(h, l, c, j, c[j], wick, down)
                    break
            out.append((t15[k], down, kind, two, with4, Ra, Rb))
    return out


def stats(rs):
    rs = [r for r in rs if r is not None]
    if not rs:
        return "     0"
    w = sum(1 for r in rs if r > 0)
    return f"{len(rs):6} | win {100 * w / len(rs):3.0f}% | avg {sum(rs) / len(rs):+.2f}R"


def main():
    allx = []
    for coin in COINS:
        allx += run(coin)
        gc.collect()
        print(f"  {coin} done", flush=True)
    for col, name in ((5, "(a) enter at the orange close"), (6, "(b) enter on confirmation (close past the orange candle)")):
        print(f"\n### {name}   BTC ETH SOL XRP 15m, 2019 to Sep 2026, target 2R")
        groups = [("all", lambda x: True), ("shorts (swept a high)", lambda x: x[1]), ("longs (swept a low)", lambda x: not x[1]),
                  ("swept WEAK", lambda x: x[2] == "WEAK"), ("swept STRONG", lambda x: x[2] == "STRONG"),
                  ("swept key level", lambda x: x[2] == "key"), ("MS undone", lambda x: x[2] == "MS undone"),
                  ("with the 4H", lambda x: x[4]), ("against the 4H", lambda x: not x[4]),
                  ("TWO oranges (another in the 4 before)", lambda x: x[3]),
                  ("two oranges + with the 4H", lambda x: x[3] and x[4]),
                  ("2019-22", lambda x: x[0] < CUT), ("2023-on", lambda x: x[0] >= CUT)]
        for g, f in groups:
            print(f"  {g:40}", stats([x[col] for x in allx if f(x)]))


if __name__ == "__main__":
    main()
