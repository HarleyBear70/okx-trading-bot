"""
F2: new ideas at the real OKX fee (research/F2_PLAN.md). Research only, bot.py is not changed.

  python research/f2_test.py <idea>      idea: A1 A2 A3 B1 B2 B3 BH (buy-and-hold BTC) D
prints one JSON line per idea (full period + halves, monthly returns for correlation).
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
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB"]
PERIODS = [("full", e.START, None)] + list(e.HALVES)


def daily_data(coins):
    return {c: (d, d) for c, (_, d) in e.load(coins).items()}


# ───────── A: Donchian trend ─────────
def hh(h, k, n):
    return max(h[k - n:k]) if k >= n else None  # prior n days, not including today


def ll(l, k, n):
    return min(l[k - n:k]) if k >= n else None


def donchian(entry_ns, exit_n, need):
    """Buy when today's close is above the prior N-day high for at least `need` of entry_ns; 2 ATR stop."""
    def entries(coin, bars, daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a = bot.atr(h, l, c, 20)
        out = [None] * len(bars)
        for k in range(max(entry_ns) + 1, len(bars)):
            votes = sum(1 for n in entry_ns if c[k] > hh(h, k, n))
            if votes >= need and a[k]:
                out[k] = {"stop": c[k] - 2 * a[k], "target": None, "max_bars": None}
        return out

    def manage(p, bars, k):
        """Trail the stop at the lowest low of the last exit_n days (only ever raised by trade_sim)."""
        return min(x["l"] for x in bars[k - exit_n + 1:k + 1]) if k >= exit_n else None
    return entries, manage


UNSEEN = [c for c in e.UNSEEN if c not in COINS]


def run_a(name):
    """A1 / A2 / A3, optional suffix: "r" = 0.35% risk, "u" = never-seen coins (F2b)."""
    cfg = {"A1": ([55], 20, 1), "A2": ([20], 10, 1), "A3": ([20, 40, 80, 160], 20, 3)}[name[:2]]
    ent, man = donchian(*cfg)
    coins = UNSEEN if "u" in name[2:] else COINS
    risk = 0.0035 if "r" in name[2:] else 0.005
    d = daily_data(coins)
    return lambda t0, t1: e.trade_sim(coins, d, ent, t0, t1, risk=risk, max_open=5, fee=FEE, manage=man)


# ───────── B: protected BTC hold ─────────
def run_b(name):
    n, band = {"B1": (200, 0.0), "B2": (200, 0.03), "B3": (100, 0.0), "BH": (None, 0.0)}[name]
    _, daily = e.load(["BTC"])["BTC"]
    c = [x["c"] for x in daily]
    ma = bot.sma(c, n) if n else None

    def sim(t0, t1):
        t1 = t1 or e.now()
        eq, units, trades, curve, entry_val = 1000.0, 0.0, [], [], None
        for k, x in enumerate(daily):
            if not (e.ms(t0) <= x["ts"] < e.ms(t1)):
                continue
            want = True if n is None else (ma[k] is not None and (c[k] > ma[k] * (1 + band) or (units > 0 and c[k] >= ma[k] * (1 - band))))
            if want and units == 0:
                units, entry_val = eq * (1 - FEE) / c[k], eq
                eq = 0.0
            elif not want and units > 0:
                eq = units * c[k] * (1 - FEE)
                trades.append({"coin": "BTC", "pnl": eq - entry_val})
                units = 0.0
            curve.append((x["ts"], eq + units * c[k] * (1 - FEE)))
        if units > 0:
            eq = curve[-1][1]
            trades.append({"coin": "BTC", "pnl": eq - entry_val})
        return e._stats(trades, curve, curve[-1][1])
    return sim


# ───────── D: SP-12 v4 on daily candles ─────────
def run_d():
    cs = ["BTC", "ETH", "XRP", "XLM", "BNB"]
    d = daily_data(cs)
    an = lambda b, dd: bot.analyse_sp(b, dd, bot.SP_SETTINGS["v4"])  # noqa: E731
    return lambda t0, t1: e.bot_sim("v4", cs, d, an, t0, t1, settings={"risk": 0.004, "half_at_2r": False})


def main():
    idea = sys.argv[1]
    run = run_a(idea) if idea.startswith("A") else run_b(idea) if idea[0] == "B" else run_d()
    out = {"idea": idea}
    for lab, t0, t1 in PERIODS:
        r = run(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2) if r["pf"] != float("inf") else None,
                    "trades": r["trades"], "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
