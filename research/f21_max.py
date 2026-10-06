"""F21: Quantpedia's MAX strategy (research/F21_PLAN.md). python research/f21_max.py <M1|M2|M3|HOLD|PH> [COIN]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035


def want_series(v, c):
    n = len(c)
    w = [False] * n
    s100 = bot.sma(c, 100)
    for k in range(n):
        if v in ("M1", "M2"):
            lb = 10 if v == "M1" else 20
            w[k] = k >= lb and c[k] >= max(c[k - lb:k + 1])
        elif v == "M3":
            if k >= 10:
                if c[k] >= max(c[k - 10:k + 1]):
                    w[k] = True
                elif c[k] < min(c[k - 10:k]):
                    w[k] = False
                else:
                    w[k] = w[k - 1]
        elif v == "HOLD":
            w[k] = True
        elif v == "PH":
            w[k] = s100[k] is not None and c[k] > s100[k]
    return w


def run(v, coin, t0, t1):
    d = e.load([coin])[coin][1]
    c = [x["c"] for x in d]
    w = want_series(v, c)
    t1 = t1 or e.now()
    eq, units, curve, trades, entry = 1000.0, 0.0, [], [], None
    for k, x in enumerate(d):
        if not (e.ms(t0) <= x["ts"] < e.ms(t1)):
            continue
        if w[k] and units == 0:
            units, entry, eq = eq * (1 - FEE) / c[k], eq, 0.0
        elif not w[k] and units > 0:
            eq = units * c[k] * (1 - FEE)
            trades.append({"coin": coin, "pnl": eq - entry})
            units = 0.0
        curve.append((x["ts"], eq + units * c[k] * (1 - FEE)))
    if units > 0:
        trades.append({"coin": coin, "pnl": curve[-1][1] - entry})
    return e._stats(trades, curve, curve[-1][1])


if __name__ == "__main__":
    v = sys.argv[1]
    coin = sys.argv[2] if len(sys.argv) > 2 else "BTC"
    out = {"variant": v, "coin": coin}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = run(v, coin, t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "trades": r["trades"], "win": round(r["win"])}
    print(json.dumps(out))
