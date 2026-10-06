"""
F4: volume and RSI at the real fee (research/F4_PLAN.md). Research only, bot.py is not changed.

  python research/f4_test.py <V1|V1base|V2|V2base|R1|R2>
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
from w1_volume import masked  # noqa: E402

FEE = 0.0035
bot.FEE, bot.BE_BUFFER = FEE, 2 * FEE
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB"]


def daily(coins):
    return {c: (d, d) for c, (_, d) in e.load(coins).items()}


def settings(bid):
    b = next(b for b in bot.BOTS if b["id"] == bid)
    return {k: b[k] for k in ("risk", "half_at_2r", "max_open") if k in b}


def v4(mode):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "v4-okx")["coins"]]
    d = e.load(cs)
    an = masked(lambda b, dd: bot.analyse_sp(b, dd, bot.SP_SETTINGS["v4"]), mode)
    return lambda t0, t1: e.bot_sim("v4", cs, d, an, t0, t1, settings=settings("v4-okx"))


def donchian(mode):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    d = daily(cs)
    an = masked(lambda b, dd: bot.analyse_donchian(b), mode)
    return lambda t0, t1: e.bot_sim("donchian", cs, d, an, t0, t1, settings=settings("dc-okx"))


UNSEEN = [c for c in e.UNSEEN if c not in COINS]


def rsi_bot(kind, risk=0.005, coins=COINS):
    d = daily(coins)
    exits = {}

    def entries(coin, bars, _daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a, s200, s5 = bot.atr(h, l, c, 14), bot.sma(c, 200), bot.sma(c, 5)
        r = bot.rsi(c, 2 if kind == "R1" else 14)
        out, ex = [None] * len(bars), [False] * len(bars)
        for k in range(1, len(bars)):
            if None in (a[k], s200[k], r[k], r[k - 1]):
                continue
            if kind == "R1":
                if c[k] > s200[k] and r[k] < 10:
                    out[k] = {"stop": c[k] - 3 * a[k], "target": None, "max_bars": None}
                ex[k] = s5[k] is not None and c[k] > s5[k]
            else:
                if c[k] > s200[k] and r[k] > 60 >= r[k - 1]:
                    out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
                ex[k] = r[k] < 40 <= r[k - 1]
        exits[id(bars)] = ex
        return out

    def manage(p, bars, k):
        return "exit" if exits[id(bars)][k] and k > p["k"] else None

    return lambda t0, t1: e.trade_sim(coins, d, entries, t0, t1, risk=risk, max_open=5, fee=FEE, manage=manage)


def main():
    v = sys.argv[1]
    sim = {"V1": lambda: v4("WV1"), "V1base": lambda: v4(None), "V2": lambda: donchian("WV1"),
           "V2base": lambda: donchian(None), "R1": lambda: rsi_bot("R1"), "R2": lambda: rsi_bot("R2"),
           "R2r20": lambda: rsi_bot("R2", 0.002), "R2r25": lambda: rsi_bot("R2", 0.0025),
           "R2u": lambda: rsi_bot("R2", coins=UNSEEN)}[v]()
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
