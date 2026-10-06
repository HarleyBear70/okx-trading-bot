"""
F17: a supervisor over Trend Rider, Donchian and NNFX (research/F17_PLAN.md). Research only.

  python research/f17_supervisor.py <S0|S1|S2|S3>
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
DAY, H20 = 86400000, 20 * 3600000


def coins(bid):
    return [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def setup():
    tr_c, dc_c, nx_c = coins("tr-okx"), coins("dc-okx"), coins("nnfx-okx")
    data = e.load(sorted(set(tr_c + dc_c + nx_c + ["BTC"])))
    btc_d = data["BTC"][1]
    tr, dc, nx = {}, {}, {}
    for c in tr_c:
        bars, daily = data[c]
        a = bot.analyse_tr(bars, daily, 5)
        tr[c] = (bars, {b["ts"]: k for k, b in enumerate(bars)}, a)
    for c in dc_c:
        d = data[c][1]
        a = bot.analyse_donchian(d)
        ok = bot.btc_leash(d, btc_d, c)
        a["signal"] = [s and o for s, o in zip(a["signal"], ok)]
        dc[c] = (d, {b["ts"]: k for k, b in enumerate(d)}, a)
    for c in nx_c:
        d = data[c][1]
        nx[c] = (d, {b["ts"]: k for k, b in enumerate(d)}, bot.analyse_nnfx(d))
    times = sorted({b["ts"] for c in tr for b in tr[c][0]})
    return tr, dc, nx, times


def run(mode, tr, dc, nx, times, t0, t1=None):
    t1 = t1 or e.now()
    acct = {name: {"eq": 1000.0, "pos": {}} for name in ("tr", "dc", "nx")}
    risk = {"tr": 0.004, "dc": 0.0032, "nx": 0.005}
    max_open = {"tr": 3, "dc": 5, "nx": 3}
    curve, blocked = [], 0

    def open_risk(p):
        return max(0.0, sum(q * (px - p["stop"]) for q, px in p["pieces"]))

    def allowed(name, coin, new_risk):
        nonlocal blocked
        if mode in ("S1", "S3"):
            tot = sum(open_risk(p) for a in acct.values() for p in a["pos"].values())
            if tot + new_risk > 0.05 * sum(a["eq"] for a in acct.values()):
                blocked += 1
                return False
        if mode in ("S2", "S3") and sum(coin in a["pos"] for a in acct.values()) >= 2:
            blocked += 1
            return False
        return True

    def buy(name, coin, px, sl, extra):
        a = acct[name]
        if coin in a["pos"] or len(a["pos"]) >= max_open[name] or px <= sl:
            return
        in_use = sum(p["cost"] for p in a["pos"].values())
        qty = min(a["eq"] * risk[name] / (px - sl), max(a["eq"] - in_use, 0) / px)
        if qty * px < 5 or not allowed(name, coin, qty * (px - sl)):
            return
        a["pos"][coin] = {"pieces": [(qty, px)], "qty": qty, "cost": qty * px * (1 + FEE), "entry": px, "sl": sl,
                          "stop": sl, **extra}

    def sell(name, coin, px, frac=1.0):
        a = acct[name]
        p = a["pos"][coin]
        q = p["qty"] * frac
        part = p["cost"] * frac
        a["eq"] += q * px * (1 - FEE) - part
        if frac >= 1.0:
            del a["pos"][coin]
        else:
            p["qty"] -= q
            p["cost"] -= part
            p["pieces"] = [(pq * (1 - frac), ppx) for pq, ppx in p["pieces"]]

    for ts in times:
        if not (e.ms(t0) <= ts < e.ms(t1)):
            continue
        # Trend Rider on this 4H candle
        for c, (bars, idx, a) in tr.items():
            k = idx.get(ts)
            if k is None:
                continue
            x = bars[k]
            p = acct["tr"]["pos"].get(c)
            if p and x["ts"] > p["ts"]:
                if x["l"] <= p["stop"]:
                    sell("tr", c, min(p["stop"], x["o"]))
                else:
                    one_r = p["entry"] - p["sl"]
                    if x["h"] >= p["entry"] + one_r:
                        p["be"] = True
                    p["hi"] = max(p["hi"], x["c"])
                    floor = max(p["sl"], p["entry"] * (1 + 2 * FEE)) if p.get("be") else p["sl"]
                    trail = p["hi"] - 3 * a["atr"][k] if a["atr"][k] else floor
                    p["stop"] = max(p["stop"], floor, trail)
            if c not in acct["tr"]["pos"] and a["signal"][k]:
                buy("tr", c, x["c"], a["info"][k]["sl"], {"ts": x["ts"], "hi": x["c"]})
        # daily bots act at the close of the day's last 4H candle
        if ts % DAY != H20:
            pass
        else:
            day_ts = ts - H20
            for c, (d, idx, a) in dc.items():
                k = idx.get(day_ts)
                if k is None:
                    continue
                x = d[k]
                p = acct["dc"]["pos"].get(c)
                if p and x["ts"] > p["ts"]:
                    if x["l"] <= p["stop"]:
                        sell("dc", c, min(p["stop"], x["o"]))
                    else:
                        if a["trail"][k] is not None:
                            p["stop"] = max(p["stop"], a["trail"][k])
                        one_r = p["entry"] - p["sl"]
                        if not p["added"] and x["c"] >= p["entry"] + one_r and x["c"] > p["stop"]:
                            p["added"] = True
                            ac = acct["dc"]
                            in_use = sum(q["cost"] for q in ac["pos"].values())
                            qty = min(ac["eq"] * risk["dc"] / (x["c"] - p["stop"]), max(ac["eq"] - in_use, 0) / x["c"])
                            if qty * x["c"] >= 5 and allowed("dc", "__addon__", qty * (x["c"] - p["stop"])):
                                p["pieces"].append((qty, x["c"]))
                                p["qty"] += qty
                                p["cost"] += qty * x["c"] * (1 + FEE)
                            p["stop"] = max(p["stop"], p["entry"])
                if c not in acct["dc"]["pos"] and a["signal"][k]:
                    buy("dc", c, x["c"], a["info"][k]["sl"], {"ts": x["ts"], "added": False})
            for c, (d, idx, a) in nx.items():
                k = idx.get(day_ts)
                if k is None:
                    continue
                x = d[k]
                p = acct["nx"]["pos"].get(c)
                if p and x["ts"] > p["ts"]:
                    if x["l"] <= p["stop"]:
                        sell("nx", c, min(p["stop"], x["o"]))
                    else:
                        if not p["half"] and x["h"] >= p["half_at"]:
                            sell("nx", c, max(p["half_at"], x["o"]), 0.5)
                            p["half"] = True
                            p["stop"] = max(p["stop"], p["entry"])
                        if a["exit"][k]:
                            sell("nx", c, x["c"])
                if c not in acct["nx"]["pos"] and a["signal"][k]:
                    inf = a["info"][k]
                    buy("nx", c, x["c"], inf["sl"], {"ts": x["ts"], "half_at": inf["half_at"], "half": False})
        # mark to market at this candle's closes
        mtm = 0.0
        for name, ac in acct.items():
            v = ac["eq"]
            src = tr if name == "tr" else dc if name == "dc" else nx
            for c, p in ac["pos"].items():
                bars, idx, _ = src[c]
                # daily bots: value at the last CLOSED day (today's close only exists at the day's last 4H candle)
                k = idx.get(ts if name == "tr" else ts - ts % DAY - (0 if ts % DAY == H20 else DAY))
                px = bars[k]["c"] if k is not None else p["entry"]
                v += p["qty"] * px * (1 - FEE) - p["cost"]
            mtm += v
        curve.append((ts, mtm))
    peak, dd = curve[0][1], 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return {"ret": round((curve[-1][1] / 3000 - 1) * 100, 1), "dd": round(dd * 100, 1), "blocked": blocked,
            "per_bot": {n: round(a["eq"], 0) for n, a in acct.items()}}


def main():
    mode = sys.argv[1]
    tr, dc, nx, times = setup()
    out = {"mode": mode}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        out[lab] = run(mode, tr, dc, nx, times, t0, t1)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
