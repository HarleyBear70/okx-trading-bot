"""F24: Jeff's Trendline Break Pro + Confluence Rank Trend (research/F24_PLAN.md). Research only.

  python research/f24_jeff2.py <A1|A2|A3|B1|B2|B3> [u]      u = never-seen coins
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE, RISK, MAX_OPEN = 0.0035, 0.004, 5
DESIGN = ["BTC", "ETH", "SOL", "XRP", "BNB"]
rules = {}  # id(bars) -> per-candle exit flags


def pivots(src, n, high):
    out = [None] * len(src)
    for k in range(2 * n, len(src)):
        m = k - n
        left, right = src[m - n:m], src[m + 1:k + 1]
        if high and src[m] > max(left) and src[m] >= max(right):
            out[k] = src[m]
        if not high and src[m] < min(left) and src[m] <= min(right):
            out[k] = src[m]
    return out


def tlb_entries(take_profit):
    def entries(coin, bars, _daily):
        h, l, c = ([x[f] for x in bars] for f in "hlc")
        a = bot.atr(h, l, c, 14)
        hl2 = [(x + y) / 2 for x, y in zip(h, l)]
        f, s = bot.sma(hl2, 5), bot.ema(hl2, 34)
        ao = bot.ema([None if None in (x, y) else x - y for x, y in zip(f, s)], 5)
        ph, pl = pivots(h, 5, True), pivots(l, 5, False)
        out, ex = [None] * len(bars), [False] * len(bars)
        st = {"res": [None, None, None, None, False, False, None], "sup": [None, None, None, None, False, False, None]}

        def new_pivot(line, y, k, up):
            x1, y1, x2, y2 = line[2], line[3], k - 5, y
            valid = y1 is not None and ((y2 < y1) if up else (y2 > y1)) and (x2 - x1) >= 8
            line[:] = [x1, y1, x2, y2, valid, False, (y2 - y1) / (x2 - x1) if valid else None]
            if valid:
                for i in range(6):
                    lvl = y2 + line[6] * ((k - i) - x2)
                    if (c[k - i] > lvl) if up else (c[k - i] < lvl):
                        line[5] = True

        for k in range(40, len(bars)):
            if ph[k] is not None:
                new_pivot(st["res"], ph[k], k, True)
            if pl[k] is not None:
                new_pivot(st["sup"], pl[k], k, False)
            if a[k] is None or ao[k] is None or ao[k - 1] is None:
                continue
            r, sp = st["res"], st["sup"]
            up = r[4] and not r[5] and k - r[2] <= 150 and c[k] > r[3] + r[6] * (k - r[2]) + 0.1 * a[k]
            dn = sp[4] and not sp[5] and k - sp[2] <= 150 and c[k] < sp[3] + sp[6] * (k - sp[2]) - 0.1 * a[k]
            if up:
                r[5] = True
            if dn:
                sp[5] = True
            if up and ao[k] > ao[k - 1]:
                risk = 1.5 * a[k]
                out[k] = {"stop": c[k] - risk, "target": c[k] + 2 * risk if take_profit else None, "max_bars": None,
                          "tag": (c[k], risk)}
            ex[k] = dn and ao[k] < ao[k - 1]
        rules[id(bars)] = (ex, a)
        return out

    def manage(p, bars, k):
        ex, a = rules[id(bars)]
        if ex[k] and k > p["k"]:
            return "exit"
        entry, risk = p["tag"]
        p["mh"] = max(p.get("mh", 0), bars[k]["h"])
        new = None
        if p["mh"] >= entry + risk:
            new = entry
        if p.get("trail") or p["mh"] >= entry + 1.5 * risk:
            p["trail"] = True
            new = max(new or 0, bars[k]["c"] - 2 * a[k])
        return new
    return entries, manage


def crts_entries(thr):
    def entries(coin, bars, _daily):
        o, h, l, c, v = ([x[f] for x in bars] for f in "ohlcv")
        ef, es, r, a = bot.ema(c, 55), bot.ema(c, 233), bot.rsi(c, 14), bot.atr(h, l, c, 14)
        vm = bot.sma(v, 20)
        n = len(bars)
        score = [None] * n
        out, ex = [None] * n, [False] * n
        clamp = lambda x: max(0.0, min(1.0, x))  # noqa: E731
        for k in range(234, n):
            if None in (es[k], r[k], a[k], vm[k]) or any(x is None for x in a[k - 200:k]):
                continue
            pr = sum(a[k - j] <= a[k] for j in range(1, 201)) / 2
            chg = c[k] - c[k - 20]
            path = sum(abs(c[i] - c[i - 1]) for i in range(k - 19, k + 1))
            er = abs(chg) / path if path > 0 else 0.0
            trend = (10 if c[k] > es[k] else 0) + (10 if ef[k] > es[k] else 0)
            mom = 20 * clamp((r[k] - 50) / 20)
            eff = 20 * clamp(er / 0.4) if chg > 0 else 0.0
            vol = 20 * pr / 20 if pr < 20 else 20 * clamp((100 - pr) / 15) if pr > 85 else 20.0
            part = (20 * clamp(v[k] / vm[k] - 0.5) if c[k] > o[k] else 0.0) if vm[k] > 0 else 10.0
            score[k] = trend + mom + eff + vol + part
            if score[k - 1] is not None and score[k] >= thr > score[k - 1]:
                out[k] = {"stop": c[k] - 3 * a[k], "target": None, "max_bars": None}
            ex[k] = score[k] < 35
        rules[id(bars)] = (ex, a)
        return out

    def manage(p, bars, k):
        ex, a = rules[id(bars)]
        if ex[k] and k > p["k"]:
            return "exit"
        return bars[k]["c"] - 3 * a[k]
    return entries, manage


def dc_entries(coin, bars, _daily):
    a = bot.analyse_donchian(bars)
    rules[id(bars)] = a["trail"]
    return [{"stop": a["info"][k]["sl"], "target": None, "max_bars": None} if s else None for k, s in enumerate(a["signal"])]


def dc_manage(p, bars, k):
    return rules[id(bars)][k]


def run(v, unseen):
    cs = [c for c in e.UNSEEN if c not in DESIGN] if unseen else DESIGN
    raw = e.load(cs)
    four_h = v in ("A2", "B2")
    data = {c: (b if four_h else d, d) for c, (b, d) in raw.items() if d}
    cs = list(data)
    ent, man = {"A1": lambda: tlb_entries(True), "A2": lambda: tlb_entries(True), "A3": lambda: tlb_entries(False),
                "B1": lambda: crts_entries(85), "B2": lambda: crts_entries(85), "B3": lambda: crts_entries(75),
                "DC": lambda: (dc_entries, dc_manage)}[v]()
    out = {"variant": v, "coins": cs}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = e.trade_sim(cs, data, ent, t0, t1, risk=RISK if v != "DC" else 0.0035, max_open=MAX_OPEN, fee=FEE, manage=man)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
        if lab == "full":
            out["_monthly"] = e.monthly(r["curve"])
    return out


if __name__ == "__main__":
    v, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
    res = run(v, unseen)
    if v != "DC" and not unseen:
        res["corr_dc"] = round(e.corr(res["_monthly"], run("DC", False)["_monthly"]), 2)
    res.pop("_monthly")
    print(json.dumps(res), flush=True)
