"""
F3: smart-money entries on Trend Rider (research/F3_PLAN.md). Research only, bot.py is not changed.

  python research/f3_smc.py <S0|S1|S2>
prints one JSON line (full period + halves).
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
COINS = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
WAIT, SWEEP_LOOKBACK, L = 12, 20, 5


def entries_for(variant):
    def entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, L)
        n = len(bars)
        l, c = [x["l"] for x in bars], [x["c"] for x in bars]
        out = [None] * n
        if variant == "S2":
            piv = bot.pivots_ge(l, L, False)
            last_pl, swept = None, [False] * n  # swept[k]: a sweep of the last swing low happened at k
            for k in range(n):
                if last_pl is not None and l[k] < last_pl < c[k]:
                    swept[k] = True
                if piv[k] is not None:
                    last_pl = piv[k]
        for i in range(n):
            if not a["signal"][i]:
                continue
            sl = a["info"][i]["sl"]
            if variant == "S0":
                out[i] = {"stop": sl, "target": None, "max_bars": None}
            elif variant == "S2":
                if any(swept[max(0, i - SWEEP_LOOKBACK):i + 1]):
                    out[i] = {"stop": sl, "target": None, "max_bars": None}
            elif variant == "S1":
                eq = (sl + c[i]) / 2
                for j in range(i + 1, min(n, i + 1 + WAIT)):
                    if l[j] <= sl:
                        break  # stop would have been hit first: setup failed
                    if l[j] <= eq and c[j] > sl:
                        if out[j] is None:
                            out[j] = {"stop": sl, "target": None, "max_bars": None}
                        break
        return out, a["atr"]
    return entries


def run(variant):
    data = e.load(COINS)
    atrs = {}
    ent_fn = entries_for(variant)

    def entries(coin, bars, daily):
        out, a = ent_fn(coin, bars, daily)
        atrs[id(bars)] = a
        return out

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    return lambda t0, t1: e.trade_sim(COINS, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def main():
    v = sys.argv[1]
    sim = run(v)
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
