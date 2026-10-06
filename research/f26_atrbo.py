"""F26: Jeff's ATR Breakout Trend Strategy (research/F26_PLAN.md). Research only.

  python research/f26_atrbo.py <D1|D2|D3|DC> [u]      u = never-seen coins; DC = plain Donchian (comparison)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f24_jeff2 as f24  # noqa: E402

rules = {}


def atrbo(trail_on):
    def entries(coin, bars, _daily):
        h, l, c = ([x[f] for x in bars] for f in "hlc")
        n = len(bars)
        tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
        a, s200 = bot.sma(tr, 20), bot.sma(c, 200)
        hi = [None] * n
        lo = [None] * n
        for k in range(20, n):
            hi[k], lo[k] = max(h[k - 20:k]), min(l[k - 20:k])
        out, ex = [None] * n, [False] * n
        for k in range(21, n):
            ex[k] = c[k] < lo[k]
            if None in (a[k], s200[k]):
                continue
            if c[k] > hi[k] and c[k - 1] <= hi[k - 1] and c[k] > s200[k]:
                out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
        rules[id(bars)] = (ex, a)
        return out

    def manage(p, bars, k):
        ex, a = rules[id(bars)]
        if ex[k] and k > p["k"]:
            return "exit"
        return bars[k]["h"] - 2 * a[k] if trail_on else None
    return entries, manage


def dc_sma():
    def entries(coin, bars, daily):
        s200 = bot.sma([x["c"] for x in bars], 200)
        base = f24.dc_entries(coin, bars, daily)
        return [b if b and s200[k] is not None and bars[k]["c"] > s200[k] else None for k, b in enumerate(base)]
    return entries, f24.dc_manage


def run(v, unseen):
    cs = [c for c in e.UNSEEN if c not in f24.DESIGN] if unseen else f24.DESIGN
    data = {c: (d, d) for c, (b, d) in e.load(cs).items() if d}
    cs = list(data)
    ent, man = {"D1": lambda: atrbo(False), "D2": lambda: atrbo(True), "D3": dc_sma,
                "DC": lambda: (f24.dc_entries, f24.dc_manage)}[v]()
    out = {"variant": v, "coins": cs}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = e.trade_sim(cs, data, ent, t0, t1, risk=0.0035, max_open=5, fee=0.0035, manage=man)
        rr, dd, ratio = e.ret_dd(r["curve"])
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "ret_dd": round(ratio, 1)}
        out.setdefault("_m", e.monthly(r["curve"]))
    return out


if __name__ == "__main__":
    v, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
    res = run(v, unseen)
    m = res.pop("_m")
    if v != "DC" and not unseen:
        res["corr_dc"] = round(e.corr(m, run("DC", False)["_m"]), 2)
    print(json.dumps(res), flush=True)
