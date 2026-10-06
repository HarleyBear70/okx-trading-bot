"""
F19: Trend Rider improvements (research/F19_PLAN.md). Research only.

  python research/f19_tr.py <base|E1|E2|E3_8h|E3_12h> [u]      u = never-seen coins
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402

TAKER, MAKER = 0.0035, 0.0020
H4 = 4 * 3600000


def resample(bars, hours):
    out = []
    for b in bars:
        k = b["ts"] - b["ts"] % (hours * 3600000)
        if out and out[-1]["ts"] == k:
            o = out[-1]
            o["h"], o["l"], o["c"], o["v"], o["n"] = max(o["h"], b["h"]), min(o["l"], b["l"]), b["c"], o["v"] + b["v"], o["n"] + 1
        else:
            out.append({"ts": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"], "n": 1})
    full = hours // 4
    return [b for b in out if b["n"] == full]


def prepare(variant, unseen):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
    if variant == "E2":
        cs = cs + ["XRP", "DOGE", "ADA", "LINK"]
    if unseen:
        cs = [c for c in e.UNSEEN + ["XRP"] if c not in cs]
    data = e.load(cs)
    hours = {"E3_8h": 8, "E3_12h": 12}.get(variant)
    per = {}
    for c, (bars, daily) in data.items():
        if hours:
            bars = resample(bars, hours)
        a = bot.analyse_tr(bars, daily, 5)
        ent = {i: a["info"][i]["sl"] for i, s in enumerate(a["signal"]) if s}
        atr = a["atr"]
        per[c] = (bars, ent, lambda k, p, atr=atr: (p["hi"] - 3 * atr[k]) if atr[k] else None)
    return cs, per


def limit_sim(cs, per, t0, t1=None):
    """f10.sim with E1's entry: a limit buy at the signal close, filled only by the next candle, maker fee."""
    t1 = t1 or e.now()
    idx = {c: {x["ts"]: k for k, x in enumerate(per[c][0])} for c in cs}
    times = sorted({x["ts"] for c in cs for x in per[c][0] if e.ms(t0) <= x["ts"] < e.ms(t1)})
    eq, pos, pend, trades, curve, filled, missed = 1000.0, {}, {}, [], [], 0, 0
    for ts in times:
        for c in cs:
            k = idx[c].get(ts)
            if k is None:
                continue
            bars, ent, trail = per[c]
            x = bars[k]
            if c in pend:  # the order placed at the last close: does this candle reach it?
                lim, sl = pend.pop(c)
                if x["l"] <= lim and c not in pos and len(pos) < 3:
                    in_use = sum(p["cost"] for p in pos.values())
                    qty = min(eq * 0.004 / (lim - sl), max(eq - in_use, 0.0) / lim)
                    if qty * lim >= 5:
                        pos[c] = {"qty": qty, "cost": qty * lim * (1 + MAKER), "stop": sl, "entry": lim, "hi": lim}
                        filled += 1
                else:
                    missed += 1
            if c in pos:
                p = pos[c]
                if x["l"] <= p["stop"] and x["ts"] > ts - 1:
                    px = min(p["stop"], x["o"])
                    pnl = p["qty"] * px * (1 - TAKER) - p["cost"]
                    eq += pnl
                    trades.append({"coin": c, "pnl": pnl})
                    del pos[c]
                else:
                    p["hi"] = max(p["hi"], x["c"])
                    new = trail(k, p)
                    if new is not None:
                        p["stop"] = max(p["stop"], new)
            if c not in pos and c not in pend and k in ent and x["c"] > ent[k]:
                pend[c] = (x["c"], ent[k])
        mtm = eq
        for c, p in pos.items():
            k = idx[c].get(ts)
            px = per[c][0][k]["c"] if k is not None else p["entry"]
            mtm += p["qty"] * px * (1 - TAKER) - p["cost"]
        curve.append((ts, mtm))
    for c in list(pos):
        bars = per[c][0]
        last = max(k for k, x in enumerate(bars) if x["ts"] < e.ms(t1))
        p = pos.pop(c)
        pnl = p["qty"] * bars[last]["c"] * (1 - TAKER) - p["cost"]
        eq += pnl
        trades.append({"coin": c, "pnl": pnl})
    r = e._stats(trades, curve, eq)
    r["fill_rate"] = round(filled / max(filled + missed, 1) * 100)
    return r


def main():
    v, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
    cs, per = prepare(v, unseen)
    out = {"variant": v, "unseen": unseen, "coins": cs}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = limit_sim(cs, per, t0, t1) if v == "E1" else f10.sim(cs, per, 0.004, 3, False, t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), **({"fill_rate": r["fill_rate"]} if "fill_rate" in r else {})}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
