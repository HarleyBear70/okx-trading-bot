"""F23: Bollinger + RSI + volume dip-buy (research/F23_PLAN.md). python research/f23_bbrsi.py <T1|T2|T3>"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

v = sys.argv[1]
if v == "T1":
    import b_boxes as bb
    cs = e.DESIGN
    data = bb.load_1h(cs)
else:
    cs = ["BTC", "ETH", "SOL", "XRP", "BNB"]
    raw = e.load(cs)
    data = raw if v == "T2" else {c: (d, d) for c, (_, d) in raw.items()}
exits = {}


def entries(coin, bars, _daily):
    h, l, c, vol = ([x[f] for x in bars] for f in "hlcv")
    a, r, m, vm = bot.atr(h, l, c, 14), bot.rsi(c, 14), bot.sma(c, 20), bot.sma(vol, 20)
    out, ex = [None] * len(bars), [False] * len(bars)
    for k in range(20, len(bars)):
        if None in (a[k], r[k], m[k], vm[k]):
            continue
        sd = math.sqrt(sum((x - m[k]) ** 2 for x in c[k - 19:k + 1]) / 20)
        if c[k] < m[k] - 2 * sd and r[k] < 40 and vol[k] > vm[k]:
            out[k] = {"stop": c[k] - 1.5 * a[k], "target": None, "max_bars": None}
        ex[k] = c[k] > m[k]
    exits[id(bars)] = ex
    return out


def manage(p, bars, k):
    return "exit" if exits[id(bars)][k] and k > p["k"] else None


out = {"variant": v}
for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
    r = e.trade_sim(cs, data, entries, t0, t1, risk=0.005, max_open=3, fee=0.0035, manage=manage)
    out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"], "win": round(r["win"])}
print(json.dumps(out))
