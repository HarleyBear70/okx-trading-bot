"""F22: anchored VWAP, OBV and overbought filters (research/F22_PLAN.md). python research/f22_filters.py <TR|DC> <base|V1|V2|V3> [u]"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402


def allowed(v, bars):
    h, l, c, vol = ([x[f] for x in bars] for f in "hlcv")
    n = len(bars)
    ok = [True] * n
    if v == "V1":
        pl = bot.pivots(l, 5, False)  # value at the confirming candle (5 after the low)
        anchor = None
        pv = cv = 0.0
        for k in range(n):
            if pl[k] is not None:
                anchor = k - 5
                pv = sum((h[j] + l[j] + c[j]) / 3 * vol[j] for j in range(anchor, k + 1))
                cv = sum(vol[j] for j in range(anchor, k + 1))
            elif anchor is not None:
                pv += (h[k] + l[k] + c[k]) / 3 * vol[k]
                cv += vol[k]
            ok[k] = anchor is not None and cv > 0 and c[k] > pv / cv
    elif v == "V2":
        obv = [0.0] * n
        for k in range(1, n):
            obv[k] = obv[k - 1] + (vol[k] if c[k] > c[k - 1] else -vol[k] if c[k] < c[k - 1] else 0)
        ok = [k >= 20 and obv[k] >= max(obv[k - 20:k]) for k in range(n)]
    elif v == "V3":
        r = bot.rsi(c, 14)
        ok = [r[k] is None or r[k] <= 80 for k in range(n)]
    return ok


def main():
    kind, v = sys.argv[1], sys.argv[2]
    unseen = len(sys.argv) > 3 and sys.argv[3] == "u"
    cs, per, risk, mo = f10.prepare(kind, 3.0, unseen=unseen, leash=(kind == "DC"))
    if kind == "DC":
        risk = 0.0032
    if v != "base":
        for c in cs:
            bars, ent, trail = per[c]
            ok = allowed(v, bars)
            per[c] = (bars, {k: s for k, s in ent.items() if ok[k]}, trail)
    out = {"bot": kind, "variant": v, "unseen": unseen}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = f10.sim(cs, per, risk, mo, kind == "DC", t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"]}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
