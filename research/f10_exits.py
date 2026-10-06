"""
F10: pyramiding and trail width (research/F10_PLAN.md). Research only, bot.py is not changed.

  python research/f10_exits.py <baseTR|P1|T1|T2|baseDC|P2>

A small simulator like engine.trade_sim, but a coin's position can hold a second piece (add-on).
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


def prepare(kind, trail_mult, unseen=False):
    """Per coin: bars, entries {k: first stop}, trail(k, pos) -> new stop or None. unseen: never-seen coins (F10b)."""
    if kind == "TR":
        cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
        if unseen:
            cs = [c for c in e.UNSEEN + ["XRP"] if c not in cs]
        data = e.load(cs)
        per = {}
        for c, (bars, daily) in data.items():
            a = bot.analyse_tr(bars, daily, 5)
            ent = {i: a["info"][i]["sl"] for i, s in enumerate(a["signal"]) if s}
            atr = a["atr"]
            per[c] = (bars, ent, lambda k, p, bars=bars, atr=atr: (p["hi"] - trail_mult * atr[k]) if atr[k] else None)
        return cs, per, 0.004, 3
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    if unseen:
        cs = [c for c in e.UNSEEN if c not in cs]
    data = {c: d for c, (_, d) in e.load(cs).items()}
    per = {}
    for c, bars in data.items():
        a = bot.analyse_donchian(bars)
        ent = {i: a["info"][i]["sl"] for i, s in enumerate(a["signal"]) if s}
        per[c] = (bars, ent, lambda k, p, tr=a["trail"]: tr[k])
    return cs, per, 0.0035, 5


def sim(cs, per, risk, max_open, pyramid, t0, t1=None):
    t1 = t1 or e.now()
    idx = {c: {x["ts"]: k for k, x in enumerate(per[c][0])} for c in cs}
    times = sorted({x["ts"] for c in cs for x in per[c][0] if e.ms(t0) <= x["ts"] < e.ms(t1)})
    eq, pos, trades, curve = 1000.0, {}, [], []

    def close(c, px):
        nonlocal eq
        p = pos.pop(c)
        pnl = sum(u["qty"] * px * (1 - FEE) - u["cost"] for u in p["units"])
        eq += pnl
        trades.append({"coin": c, "pnl": pnl})

    for ts in times:
        for c in cs:
            k = idx[c].get(ts)
            if k is None:
                continue
            bars, ent, trail = per[c]
            x = bars[k]
            if c in pos:
                p = pos[c]
                if x["l"] <= p["stop"]:
                    close(c, min(p["stop"], x["o"]))
                else:
                    p["hi"] = max(p["hi"], x["c"])
                    new = trail(k, p)
                    if new is not None:
                        p["stop"] = max(p["stop"], new)
                    one_r = p["entry"] - p["sl0"]
                    if pyramid and not p["added"] and x["c"] >= p["entry"] + one_r and x["c"] > p["stop"]:
                        in_use = sum(u["cost"] for q in pos.values() for u in q["units"])
                        qty = min(eq * risk / (x["c"] - p["stop"]), max(eq - in_use, 0.0) / x["c"])
                        if qty * x["c"] >= 5:
                            p["units"].append({"qty": qty, "cost": qty * x["c"] * (1 + FEE)})
                        p["added"] = True
                        p["stop"] = max(p["stop"], p["entry"])
            if c not in pos and k in ent and len(pos) < max_open and x["c"] > ent[k]:
                in_use = sum(u["cost"] for q in pos.values() for u in q["units"])
                qty = min(eq * risk / (x["c"] - ent[k]), max(eq - in_use, 0.0) / x["c"])
                if qty * x["c"] >= 5:
                    pos[c] = {"units": [{"qty": qty, "cost": qty * x["c"] * (1 + FEE)}], "stop": ent[k],
                              "sl0": ent[k], "entry": x["c"], "hi": x["c"], "added": False}
        mtm = eq
        for c, p in pos.items():
            k = idx[c].get(ts)
            px = per[c][0][k]["c"] if k is not None else p["entry"]
            mtm += sum(u["qty"] * px * (1 - FEE) - u["cost"] for u in p["units"])
        curve.append((ts, mtm))
    for c in list(pos):
        bars = per[c][0]
        last = max(k for k, x in enumerate(bars) if x["ts"] < e.ms(t1))
        close(c, bars[last]["c"])
    return e._stats(trades, curve, eq)


def main():
    v = sys.argv[1]
    opt = sys.argv[2] if len(sys.argv) > 2 else ""  # F10b: "u" = never-seen coins, or a risk such as 0.0027
    kind = "DC" if v in ("baseDC", "P2") else "TR"
    trail = {"T1": 2.5, "T2": 4.0}.get(v, 3.0)
    cs, per, risk, mo = prepare(kind, trail, unseen=opt == "u")
    if opt and opt != "u":
        risk = float(opt)
    pyr = v in ("P1", "P2")
    out = {"variant": v, "opt": opt}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(cs, per, risk, mo, pyr, t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
