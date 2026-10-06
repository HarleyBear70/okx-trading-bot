"""
F9: Jeff's own Pine Scripts ported to Python (research/F9_PLAN.md). Research only, bot.py is not changed.

  python research/f9_pine.py <AMD4|AMD1|V3|S0|CC1|CC2|CC3>
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
bot.FEE, bot.BE_BUFFER = FEE, 2 * FEE


# ───────── AMD + FVG (pine/amd_fvg), long side ─────────
def amd_entries(acc_len=30, range_atr=3.5, window=10, sl_atr=1.5, rr=2.0):
    def entries(coin, bars, daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a = bot.atr(h, l, c, 14)
        n = len(bars)
        out = [None] * n
        state, top, bot_, box_end, swept = 0, None, None, None, False
        for i in range(acc_len, n):
            if a[i] is None:
                continue
            hh, ll = max(h[i - acc_len + 1:i + 1]), min(l[i - acc_len + 1:i + 1])
            if state == 0 and hh - ll <= range_atr * a[i]:
                state, top, bot_, box_end, swept = 1, hh, ll, i, False
            elif state == 1:
                if i - box_end > window:
                    state = 0
                else:
                    if l[i] < bot_ and not swept:
                        swept = True
                    bull_fvg = l[i] > h[i - 2]
                    if swept and bull_fvg and c[i] > bot_:
                        risk = sl_atr * a[i]
                        out[i] = {"stop": c[i] - risk, "target": c[i] + rr * risk, "max_bars": None}
                        state = 0
        return out
    return entries


def amd(tf):
    import b_boxes as bb
    if tf == "4H":
        cs = ["BTC", "ETH", "SOL", "XRP", "BNB"]
        data = e.load(cs)
    else:
        cs = e.DESIGN
        data = bb.load_1h(cs)
    return lambda t0, t1: e.trade_sim(cs, data, amd_entries(), t0, t1, risk=0.005, max_open=3, fee=FEE)


# ───────── SP-12 v3 = v4 without the SAR trail ─────────
def v3():
    """Exactly the Pine v3 exits: fixed stop and fixed target, 120-candle time stop, no breakeven, no trail."""
    b = next(b for b in bot.BOTS if b["id"] == "v4-okx")
    cs = [c.split("-")[0] for c in b["coins"]]
    d = e.load(cs)
    cfg = bot.SP_SETTINGS["v4"]

    def entries(coin, bars, daily):
        a = bot.analyse_sp(bars, daily, cfg)
        return [{"stop": a["info"][i]["sl"], "target": a["info"][i]["tp"], "max_bars": cfg["max_bars"]} if s_ else None
                for i, s_ in enumerate(a["signal"])]
    return lambda t0, t1: e.trade_sim(cs, d, entries, t0, t1, risk=b["risk"], max_open=3, fee=FEE)


def v4sar():
    """pine/sp-12 v4 sar exactly: v3 entry; after +1R (high since entry) the target is dropped and the stop trails at
    max(first stop, Parabolic SAR) whenever SAR is below the close. No breakeven step (unlike bot.py's v4)."""
    b = next(b for b in bot.BOTS if b["id"] == "v4-okx")
    cs = [c.split("-")[0] for c in b["coins"]]
    d = e.load(cs)
    cfg = bot.SP_SETTINGS["v4"]
    sars = {}

    def entries(coin, bars, daily):
        a = bot.analyse_sp(bars, daily, cfg)
        sars[id(bars)] = a["sar"]
        return [{"stop": a["info"][i]["sl"], "target": a["info"][i]["tp"], "max_bars": cfg["max_bars"]} if s_ else None
                for i, s_ in enumerate(a["signal"])]

    def manage(p, bars, k):
        one_r = p["entry"] - p.setdefault("sl0", p["stop"])
        p["hs"] = max(p.get("hs", bars[k]["h"]), bars[k]["h"])
        if p["hs"] >= p["entry"] + one_r:
            p["target"] = None
            s_ = sars[id(bars)][k]
            if s_ is not None and s_ < bars[k]["c"]:
                return max(p["sl0"], s_)
        return None
    return lambda t0, t1: e.trade_sim(cs, d, entries, t0, t1, risk=b["risk"], max_open=3, fee=FEE, manage=manage)


# ───────── Command Center tags on Trend Rider buys ─────────
def pivots(src, L, high):
    """Pivot index p confirmed at p + L (Pine ta.pivothigh / pivotlow style)."""
    out = {}
    for p in range(L, len(src) - L):
        w = src[p - L:p + L + 1]
        if (src[p] == max(w)) if high else (src[p] == min(w)):
            out[p + L] = p
    return out


def profile(h, l, v, lo_i, hi_i, lo, hi, n_bins=40):
    w = (hi - lo) / n_bins
    bins = [0.0] * n_bins
    for idx in range(lo_i, hi_i + 1):
        bh, bl = min(h[idx], hi), max(l[idx], lo)
        k0 = max(0, min(n_bins - 1, int((bl - lo) / w)))
        k1 = max(0, min(n_bins - 1, int((bh - lo) / w)))
        a0, a1 = min(k0, k1), max(k0, k1)
        share = v[idx] / (a1 - a0 + 1)
        for k in range(a0, a1 + 1):
            bins[k] += share
    pk = max(range(n_bins), key=lambda k: bins[k])
    return {"lo": lo, "w": w, "bins": bins, "max": bins[pk], "poc": lo + (pk + 0.5) * w}


def cc(mode, unseen=False):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
    if unseen:  # F9b
        cs = [c for c in e.UNSEEN + ["XRP"] if c not in cs]
    data = e.load(cs)
    atrs = {}
    L = 5

    def entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, L)
        h, l, c, v = ([x[f] for x in bars] for f in "hlcv")
        atr14 = a["atr"]
        ph_at, pl_at = pivots(h, L, True), pivots(l, L, False)
        out = [None] * len(bars)
        ph_idx = pl_idx = None
        prof = None
        for i in range(len(bars)):
            if i in pl_at:
                pl_idx = pl_at[i]
            if i in ph_at:
                ph_idx = ph_at[i]
                if pl_idx is not None and pl_idx < ph_idx and ph_idx - pl_idx <= 400 and h[ph_idx] > l[pl_idx]:
                    prof = profile(h, l, v, pl_idx, ph_idx, l[pl_idx], h[ph_idx])
            if not a["signal"][i]:
                continue
            ok = True
            if mode != "S0":
                pb = min(l[ph_idx + 1:i]) if ph_idx is not None and i - ph_idx > 1 else l[i - 1]
                va = sum(v[i - 20:i]) / 20 if i >= 20 else None
                if mode == "CC1":
                    ok = prof is not None and atr14[i] is not None and abs(pb - prof["poc"]) <= atr14[i]
                elif mode == "CC2":
                    ok = va is not None and v[i] > 1.5 * va
                elif mode == "CC3" and prof is not None and pb > prof["lo"]:
                    k = int((pb - prof["lo"]) / prof["w"])
                    ok = not (0 <= k < len(prof["bins"]) and prof["bins"][k] < 0.25 * prof["max"])
            if ok:
                out[i] = {"stop": a["info"][i]["sl"], "target": None, "max_bars": None}
        atrs[id(bars)] = atr14
        return out

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def main():
    v = sys.argv[1]
    sim = {"AMD4": lambda: amd("4H"), "V4SAR": v4sar, "AMD1": lambda: amd("1H"), "V3": v3,
           "S0": lambda: cc("S0"), "CC1": lambda: cc("CC1"), "CC2": lambda: cc("CC2"), "CC3": lambda: cc("CC3"),
           "S0u": lambda: cc("S0", True), "CC3u": lambda: cc("CC3", True)}[v]()
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
