"""F25: Jeff's Trend Analysis Strategy (research/F25_PLAN.md). Research only.

  python research/f25_tas.py <C1|C2|C3> [u]      u = never-seen coins
Take-profits are simulated as three one-third pieces (keys coin#1..#3).
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f24_jeff2 as f24  # noqa: E402

FEE, RISK = 0.0035, 0.004
state = {}


def wma(src, n):
    out, w = [None] * len(src), n * (n + 1) / 2
    for i in range(n - 1, len(src)):
        win = src[i - n + 1:i + 1]
        if None not in win:
            out[i] = sum((j + 1) * x for j, x in enumerate(win)) / w
    return out


def linreg(src, n):
    out, xm = [None] * len(src), (n - 1) / 2
    sxx = sum((j - xm) ** 2 for j in range(n))
    for i in range(n - 1, len(src)):
        y = src[i - n + 1:i + 1]
        ym = sum(y) / n
        slope = sum((j - xm) * (v - ym) for j, v in enumerate(y)) / sxx
        out[i] = ym + slope * (n - 1 - xm)
    return out


def hma(src, n):
    a, b = wma(src, n // 2), wma(src, n)
    return wma([None if None in (x, y) else 2 * x - y for x, y in zip(a, b)], int(math.sqrt(n)))


def dmi(h, l, c, n=14):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    pdm = [0.0] + [max(h[i] - h[i - 1], 0) if h[i] - h[i - 1] > l[i - 1] - l[i] else 0.0 for i in range(1, len(c))]
    mdm = [0.0] + [max(l[i - 1] - l[i], 0) if l[i - 1] - l[i] > h[i] - h[i - 1] else 0.0 for i in range(1, len(c))]
    rt, rp, rm = bot.rma(tr, n), bot.rma(pdm, n), bot.rma(mdm, n)
    return ([None if not t else 100 * p / t for p, t in zip(rp, rt)], [None if not t else 100 * m / t for m, t in zip(rm, rt)])


def analyse(bars):
    h, l, c = ([x[f] for x in bars] for f in "hlc")
    n = len(bars)
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    a = wma(tr, 14)
    trk, d = [None] * n, [1] * n
    t, di = None, 1
    for i in range(n):
        if a[i] is None:
            continue
        up, dn = h[i] + a[i] * 2.2, l[i] - a[i] * 2.2
        if t is None:
            t = dn
        elif di == 1:
            t = max(t, dn)
            if c[i] < t:
                di, t = -1, up
        else:
            t = min(t, up)
            if c[i] > t:
                di, t = 1, dn
        trk[i], d[i] = t, di
    eq = hma(linreg(c, 55), 9)
    r = bot.rsi(c, 14)
    rm = bot.sma(r, 14)
    dp, dm = dmi(h, l, c)
    ratr = bot.atr(h, l, c, 14)
    sig, stop = [False] * n, [None] * n
    signaled, start = False, 0
    for k in range(1, n):
        flip_up = d[k] == 1 and d[k - 1] == -1
        if flip_up or (d[k] == -1 and d[k - 1] == 1):
            signaled, start = False, k
        if None in (trk[k], eq[k], eq[k - 1], r[k], rm[k], dp[k], dm[k], ratr[k]):
            continue
        s = d[k] + (1 if c[k] > eq[k] else -1) + (1 if eq[k] > eq[k - 1] else -1) + (1 if r[k] > 50 else -1) \
            + (1 if r[k] > rm[k] else -1) + (1 if dp[k] > dm[k] else -1)
        cand = d[k] == 1 and (flip_up or (not signaled and k - start <= 10))
        if cand and not signaled and s / 6 * 100 >= 50:
            signaled = True
            sig[k] = True
            st = trk[k]
            stop[k] = st if st < c[k] else c[k] - 2 * ratr[k]
    return {"sig": sig, "stop": stop, "trk": trk, "dir": d}


def run(v, unseen, periods=None, coins=None):
    cs = coins or ([c for c in e.UNSEEN if c not in f24.DESIGN] if unseen else f24.DESIGN)
    raw = e.load(cs)
    data = {}
    for c, (b, d) in raw.items():
        if not d:
            continue
        bars = b if v == "C3" else d
        a = state[id(bars)] = analyse(bars)
        if v == "C2":
            data[c] = (bars, a, None)
        else:
            for j, tp in ((1, 1.5), (2, 2.5), (3, 3.5)):
                data[f"{c}#{j}"] = (bars, a, tp)

    def entries(key, bars, a):
        tp = data[key][2]
        out = [None] * len(bars)
        for k, s in enumerate(a["sig"]):
            if s:
                risk = bars[k]["c"] - a["stop"][k]
                out[k] = {"stop": a["stop"][k], "target": bars[k]["c"] + tp * risk if tp else None, "max_bars": None,
                          "tag": (bars[k]["c"], risk)}
        return out

    def manage(p, bars, k):
        a = state[id(bars)]
        if a["dir"][k] == -1 and a["dir"][k - 1] == 1 and k > p["k"]:
            return "exit"
        if v == "C2":
            return a["trk"][k] if a["dir"][k] == 1 else None
        entry, risk = p["tag"]
        return entry if max(x["h"] for x in bars[p["k"] + 1:k + 1]) >= entry + 1.5 * risk else None

    keys = list(data)
    sim_data = {kk: (bars, a) for kk, (bars, a, _) in data.items()}
    pieces = 1 if v == "C2" else 3
    out = {"variant": v, "coins": sorted({kk.split("#")[0] for kk in keys})}
    for lab, t0, t1 in periods or [("full", e.START, None), *e.HALVES]:
        r = e.trade_sim(keys, sim_data, entries, t0, t1, risk=RISK / pieces, max_open=5 * pieces, fee=FEE, manage=manage)
        coin_trades = {(t["coin"].split("#")[0], t["entry_ts"]) for t in r["list"]}
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2),
                    "trades": len(coin_trades), "win_pieces": round(r["win"])}
        out.setdefault("_curve", r["curve"])
    return out


if __name__ == "__main__":
    v, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
    res = run(v, unseen)
    cv = res.pop("_curve")
    if not unseen:
        res["corr_dc"] = round(e.corr(e.monthly(cv), f24.run("DC", False)["_monthly"]), 2)
    print(json.dumps(res), flush=True)
