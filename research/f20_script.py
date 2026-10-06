"""
F20: Jeff's half-written breakout script (research/F20_PLAN.md). Research only.

  python research/f20_script.py <X0|X1|X2|X3>      X0 = plain Donchian (comparison)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035


def entries_for(v):
    def entries(coin, bars, _daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a = bot.atr(h, l, c, 14)
        out = [None] * len(bars)
        for k in range(100, len(bars)):
            if a[k] is None:
                continue
            lb = 20
            if v == "X2":
                atrp = sorted(a[j] / c[j] for j in range(k - 99, k + 1) if a[j])
                ratio = atrp[len(atrp) // 2] / (a[k] / c[k])
                lb = int(round(min(max(20 * ratio, 10), 40)))
            if c[k] > max(h[k - lb:k]):
                if v == "X1":
                    out[k] = {"stop": c[k] - 1.5 * a[k], "target": c[k] + 2.0 * a[k], "max_bars": None}
                else:
                    out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
        return out
    return entries


def manage(p, bars, k):
    return min(x["l"] for x in bars[k - 9:k + 1]) if k >= 9 else None


def main():
    v = sys.argv[1]
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        if v == "X3":
            r = streak_trade_sim(cs, data, entries_for("X0"), t0, t1)
        else:
            r = e.trade_sim(cs, data, entries_for(v), t0, t1, risk=0.0035, max_open=5, fee=FEE,
                            manage=None if v == "X1" else manage)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


def streak_trade_sim(cs, data, entries_fn, t0, t1=None):
    """Copy of engine.trade_sim (long only, no cooldown) with X3's losing-streak layer: half risk after 3 losses in a
    row, back to full after the next win."""
    t1 = t1 or e.now()
    per = {}
    for c in cs:
        bars, daily = data[c]
        per[c] = (bars, entries_fn(c, bars, daily), {x["ts"]: k for k, x in enumerate(bars)})
    times = sorted({x["ts"] for bars, _, _ in per.values() for x in bars if e.ms(t0) <= x["ts"] < e.ms(t1)})
    eq, pos, trades, curve, losses = 1000.0, {}, [], [], 0

    def close(c, px):
        nonlocal eq, losses
        p = pos.pop(c)
        pnl = p["qty"] * px * (1 - FEE) - p["cost"]
        eq += pnl
        losses = 0 if pnl > 0 else losses + 1
        trades.append({"coin": c, "pnl": pnl})

    for ts in times:
        for c in cs:
            bars, ent, idx = per[c]
            k = idx.get(ts)
            if k is None:
                continue
            x = bars[k]
            if c in pos:
                p = pos[c]
                if x["l"] <= p["stop"]:
                    close(c, min(p["stop"], x["o"]))
                else:
                    new = manage(p, bars, k)
                    if new is not None:
                        p["stop"] = max(p["stop"], new)
            if c not in pos and ent[k] and len(pos) < 5 and x["c"] > ent[k]["stop"]:
                risk = 0.0035 * (0.5 if losses >= 3 else 1.0)
                in_use = sum(p["cost"] for p in pos.values())
                qty = min(eq * risk / (x["c"] - ent[k]["stop"]), max(eq - in_use, 0.0) / x["c"])
                if qty * x["c"] >= 5:
                    pos[c] = {"qty": qty, "cost": qty * x["c"] * (1 + FEE), "stop": ent[k]["stop"]}
        mtm = eq
        for c, p in pos.items():
            bars, _, idx = per[c]
            k = idx.get(ts)
            px = bars[k]["c"] if k is not None else p["cost"] / p["qty"]
            mtm += p["qty"] * px * (1 - FEE) - p["cost"]
        curve.append((ts, mtm))
    for c in list(pos):
        bars, _, _ = per[c]
        last = max(k for k, x in enumerate(bars) if x["ts"] < e.ms(t1))
        close(c, bars[last]["c"])
    return e._stats(trades, curve, eq)


if __name__ == "__main__":
    main()
