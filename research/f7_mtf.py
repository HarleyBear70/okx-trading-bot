"""
F7: weekly trend filter and fib golden pocket (research/F7_PLAN.md). Research only, bot.py is not changed.

  python research/f7_mtf.py <W1|W2|G1>
"""
import datetime as dt
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


def weekly_up(daily):
    """{day number: True/False}: was the last COMPLETED week's close above its 20-week EMA on that day?"""
    weeks, keys = [], []
    for d in daily:
        wk = dt.datetime.fromtimestamp(d["ts"] / 1000, dt.timezone.utc).isocalendar()[:2]
        if keys and keys[-1] == wk:
            weeks[-1] = d["c"]
        else:
            keys.append(wk)
            weeks.append(d["c"])
    em = bot.ema(weeks, 20)
    up_after = {}  # week index -> trend state, usable from the next week on
    for i, k in enumerate(keys):
        up_after[k] = em[i] is not None and weeks[i] > em[i]
    out = {}
    for d in daily:
        t = dt.datetime.fromtimestamp(d["ts"] / 1000, dt.timezone.utc)
        prev = (t - dt.timedelta(days=7)).isocalendar()[:2]
        out[bot.day_of(d["ts"])] = up_after.get(prev, False)
    return out


def tr_coins():
    return [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]


def tr_sim(mode):
    cs = tr_coins()
    data = e.load(cs)
    atrs = {}

    def entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        wk = weekly_up(daily) if mode == "W1" else None
        l, c = [x["l"] for x in bars], [x["c"] for x in bars]
        out = [None] * len(bars)
        for i, sig in enumerate(a["signal"]):
            if not sig:
                continue
            sl = a["info"][i]["sl"]
            if mode == "W1":
                if wk.get(bot.day_of(bars[i]["ts"])):
                    out[i] = {"stop": sl, "target": None, "max_bars": None}
            else:  # G1: golden pocket, 61.8% retracement of stop -> BOS close
                lvl = c[i] - 0.618 * (c[i] - sl)
                for j in range(i + 1, min(len(bars), i + 13)):
                    if l[j] <= sl:
                        break
                    if l[j] <= lvl and c[j] > sl:
                        out[j] = out[j] or {"stop": sl, "target": None, "max_bars": None}
                        break
        atrs[id(bars)] = a["atr"]
        return out

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def dc_sim():
    b = next(b for b in bot.BOTS if b["id"] == "dc-okx")
    cs = [c.split("-")[0] for c in b["coins"]]
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}
    st = {k: b[k] for k in ("risk", "half_at_2r", "max_open") if k in b}

    def an(bars, daily):
        a = bot.analyse_donchian(bars)
        wk = weekly_up(daily)
        return {**a, "signal": [s and wk.get(bot.day_of(bars[k]["ts"]), False) for k, s in enumerate(a["signal"])]}
    return lambda t0, t1: e.bot_sim("donchian", cs, data, an, t0, t1, settings=st)


def main():
    v = sys.argv[1]
    sim = {"W1": lambda: tr_sim("W1"), "G1": lambda: tr_sim("G1"), "W2": dc_sim}[v]()
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
