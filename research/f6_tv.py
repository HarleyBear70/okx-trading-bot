"""
F6: popular TradingView trend indicators at the real fee (research/F6_PLAN.md). Research only, bot.py is not changed.

  python research/f6_tv.py <T1|T2|T3>
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
COINS = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
if len(sys.argv) > 2 and sys.argv[2] == "unseen":  # F6b
    COINS = [c for c in e.UNSEEN if c not in COINS]
DATA = None


def data():
    global DATA
    DATA = DATA or {c: (d, d) for c, (_, d) in e.load(COINS).items()}
    return DATA


def t1():
    b = next(b for b in bot.BOTS if b["id"] == "dc-okx")
    st = {k: b[k] for k in ("risk", "half_at_2r", "max_open") if k in b}

    def an(bars, _d):
        a = bot.analyse_donchian(bars)
        h, l, c = ([x[k] for x in bars] for k in "hlc")
        ax = e.adx(h, l, c, 14)
        return {**a, "signal": [s and ax[k] is not None and ax[k] > 20 for k, s in enumerate(a["signal"])]}
    return lambda t0, t1_: e.bot_sim("donchian", COINS, data(), an, t0, t1_, settings=st)


def flip_bot(kind):
    exits = {}

    def entries(coin, bars, _daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a = bot.atr(h, l, c, 20)
        n = len(bars)
        out, ex = [None] * n, [False] * n
        if kind == "T2":
            d = bot.supertrend(h, l, c, 3, 10)  # -1 = up (green), 1 = down (red)
            for k in range(1, n):
                if d[k] == -1 and d[k - 1] == 1 and a[k]:
                    out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
                ex[k] = d[k] == 1 and d[k - 1] == -1
        else:
            m = [x - y if None not in (x, y) else None for x, y in zip(bot.ema(c, 12), bot.ema(c, 26))]
            first = next(i for i, x in enumerate(m) if x is not None)
            sig = [None] * first + bot.ema(m[first:], 9)
            s200 = bot.sma(c, 200)
            for k in range(1, n):
                if None in (m[k], m[k - 1], sig[k], sig[k - 1]):
                    continue
                up, down = m[k] > sig[k] and m[k - 1] <= sig[k - 1], m[k] < sig[k] and m[k - 1] >= sig[k - 1]
                if up and s200[k] is not None and c[k] > s200[k] and a[k]:
                    out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
                ex[k] = down
        exits[id(bars)] = ex
        return out

    def manage(p, bars, k):
        return "exit" if exits[id(bars)][k] and k > p["k"] else None

    return lambda t0, t1_: e.trade_sim(COINS, data(), entries, t0, t1_, risk=0.0035, max_open=5, fee=FEE, manage=manage)


def main():
    v = sys.argv[1]
    sim = {"T1": t1, "T2": lambda: flip_bot("T2"), "T3": lambda: flip_bot("T3")}[v]()
    out = {"variant": v}
    for lab, t0, t1_ in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1_)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
