"""
F14: candlestick and chart patterns at the real fee (research/F14_PLAN.md). Research only.

  python research/f14_patterns.py <C1|C2|C3|P1|P2> [u]      u = never-seen coins
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035


def clamp_stop(c, low, a):
    s = low * 0.998
    return min(max(s, c - 3 * a), c - a)


def entries_for(p):
    def entries(coin, bars, _daily):
        o, h, l, c = ([x[f] for x in bars] for f in "ohlc")
        a = bot.atr(h, l, c, 14)
        s50 = bot.sma(c, 50)
        n = len(bars)
        out = [None] * n
        last_sig = -99
        for k in range(60, n):
            if a[k] is None:
                continue
            low = None
            if p in ("C1", "C2", "C3"):
                if s50[k] is None or c[k] <= s50[k]:
                    continue
                body = abs(c[k] - o[k])
                if p == "C1" and c[k - 1] < o[k - 1] and c[k] > o[k] and c[k] >= o[k - 1] and o[k] <= c[k - 1]:
                    low = min(l[k], l[k - 1])
                elif p == "C2" and c[k - 1] < c[k - 2] and body > 0 and min(o[k], c[k]) - l[k] >= 2 * body \
                        and h[k] - max(o[k], c[k]) <= body:
                    low = l[k]
                elif p == "C3":
                    b1 = o[k - 2] - c[k - 2]
                    if b1 >= 0.6 * a[k] and abs(c[k - 1] - o[k - 1]) <= 0.3 * b1 and c[k] > o[k] \
                            and c[k] > (o[k - 2] + c[k - 2]) / 2:
                        low = min(l[k - 2:k + 1])
            elif p == "P1":
                # second low at j2 = a recent swing low (lowest of the 5 days each side), confirmed by day k
                for j2 in range(k - 20, k - 4):
                    if l[j2] != min(l[j2 - 5:j2 + 6]):
                        continue
                    for j1 in range(j2 - 60, j2 - 9):
                        if j1 < 5 or l[j1] != min(l[j1 - 5:j1 + 6]) or abs(l[j1] / l[j2] - 1) > 0.03:
                            continue
                        neck = max(h[j1:j2 + 1])
                        if neck >= max(l[j1], l[j2]) * 1.05 and c[k] > neck and max(c[j2:k]) <= neck:
                            low = min(l[j1], l[j2])
                            break
                    if low:
                        break
            elif p == "P2":
                top = max(h[k - 30:k])
                tol = top * 0.015
                touches, last = 0, -99
                for j in range(k - 30, k):
                    if h[j] >= top - tol and j - last >= 3:
                        touches, last = touches + 1, j
                if touches >= 2 and min(l[k - 10:k]) >= min(l[k - 30:k - 10]) * 1.02 and c[k] > top and c[k - 1] <= top:
                    low = min(l[k - 10:k])
            if low is not None and k - last_sig > 1:
                stop = clamp_stop(c[k], low, a[k])
                if c[k] > stop:
                    out[k] = {"stop": stop, "target": None, "max_bars": None}
                    last_sig = k
        return out
    return entries


def manage(p, bars, k):
    return min(x["l"] for x in bars[k - 9:k + 1]) if k >= 9 else None


def main():
    p = sys.argv[1]
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    opts = sys.argv[2:]  # "u" = never-seen coins, a number = risk (F14b)
    if "u" in opts:
        cs = [c for c in e.UNSEEN if c not in cs]
    risk = next((float(x) for x in opts if x != "u"), 0.0035)
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}
    out = {"pattern": p, "opts": opts}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = e.trade_sim(cs, data, entries_for(p), t0, t1, risk=risk, max_open=5, fee=FEE, manage=manage)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
