"""
F12: range trading on daily candles (research/F12_PLAN.md). Research only, bot.py is not changed.

  python research/f12_range.py <R1|R2|R3> [u]      u = never-seen coins
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
N, MIN_H, MAX_H = 30, 0.08, 0.40


def touches(vals, level, tol, above):
    """Days (indexes) whose high/low came within tol of level; separate touches need 5+ days between them."""
    days = [i for i, v in enumerate(vals) if (v >= level - tol if above else v <= level + tol)]
    n, last = 0, -99
    for d in days:
        if d - last >= 5:
            n, last = n + 1, d
    return n


def range_at(h, l, k):
    """The prior-30-day range before day k, or None if it isn't a clean range."""
    if k < N:
        return None
    hh, ll = max(h[k - N:k]), min(l[k - N:k])
    if ll <= 0 or not (MIN_H <= (hh - ll) / ll <= MAX_H):
        return None
    tol = 0.1 * (hh - ll)
    if touches(h[k - N:k], hh, tol, True) < 2 or touches(l[k - N:k], ll, tol, False) < 2:
        return None
    return hh, ll


def entries_for(variant):
    def entries(coin, bars, _daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        a = bot.atr(h, l, c, 14)
        out = [None] * len(bars)
        pending = None  # R2/R3: (old range high, old range low, day of breakout)
        for k in range(N, len(bars)):
            if a[k] is None:
                continue
            rg = range_at(h, l, k)
            if variant == "R1":
                if rg:
                    hh, ll = rg
                    if l[k] <= ll + 0.2 * (hh - ll) and c[k] > ll:
                        stop = ll - a[k]
                        tgt = ll + 0.8 * (hh - ll)
                        if c[k] < tgt and c[k] > stop:
                            out[k] = {"stop": stop, "target": tgt, "max_bars": None}
                continue
            if pending and k - pending[2] > 10:
                pending = None
            if pending and l[k] <= pending[0] * 1.01 and c[k] > pending[0]:
                stop = pending[0] - 1.5 * a[k] if variant == "R2" else (pending[0] + pending[1]) / 2
                if c[k] > stop:
                    out[k] = {"stop": stop, "target": None, "max_bars": None}
                pending = None
            elif rg and c[k] > rg[0] and not pending:
                pending = (rg[0], rg[1], k)
        return out
    return entries


def manage_for(variant):
    if variant == "R1":
        return None
    return lambda p, bars, k: min(x["l"] for x in bars[k - 9:k + 1]) if k >= 9 else None


def main():
    v = sys.argv[1]
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    if len(sys.argv) > 2 and sys.argv[2] == "u":
        cs = [c for c in e.UNSEEN if c not in cs]
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}
    out = {"variant": v, "coins": cs}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = e.trade_sim(cs, data, entries_for(v), t0, t1, risk=0.0035, max_open=5, fee=FEE, manage=manage_for(v))
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
