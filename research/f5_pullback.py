"""
F5: buy the pullback to the 20 EMA in a strong trend (research/F5_PLAN.md). Research only, bot.py is not changed.

  python research/f5_pullback.py <P1|P2>
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


def coins(bid):
    return [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def p1():
    cs = coins("tr-okx")
    data = e.load(cs)
    atrs = {}

    def entries(coin, bars, daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        e20, e50, a = bot.ema(c, 20), bot.ema(c, 50), bot.atr(h, l, c, 14)
        dc = [d["c"] for d in daily]
        de = bot.ema(dc, 50)
        dk = bot.daily_lookup(bars, daily)
        out = [None] * len(bars)
        for k in range(10, len(bars)):
            if None in (e20[k], e50[k], a[k]):
                continue
            j = dk[k]
            daily_ok = j is not None and de[j] is not None and dc[j] > de[j]
            if daily_ok and c[k] > e50[k] and e20[k] > e50[k] and l[k] <= e20[k] < c[k]:
                s = min(l[k - 10:k + 1]) * 0.998
                s = min(max(s, c[k] - 3 * a[k]), c[k] - a[k])
                out[k] = {"stop": s, "target": None, "max_bars": None}
        atrs[id(bars)] = a
        return out

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def p2():
    cs = coins("dc-okx")
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}

    def entries(coin, bars, daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        e20, e50, a = bot.ema(c, 20), bot.ema(c, 50), bot.atr(h, l, c, 20)
        out = [None] * len(bars)
        for k in range(len(bars)):
            if None in (e20[k], e50[k], a[k]):
                continue
            if c[k] > e50[k] and e20[k] > e50[k] and l[k] <= e20[k] < c[k]:
                out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
        return out

    def manage(p, bars, k):
        return min(x["l"] for x in bars[k - 9:k + 1]) if k >= 9 else None

    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.0035, max_open=5, fee=FEE, manage=manage)


def main():
    v = sys.argv[1]
    sim = {"P1": p1, "P2": p2}[v]()
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
