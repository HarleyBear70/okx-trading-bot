"""
F15: spot grid bot (research/F15_PLAN.md). Research only.

  python research/f15_grid.py <G1|G2|G3|HOLD>
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import engine as e  # noqa: E402

MAKER, TAKER = 0.0020, 0.0035
CFG = {"G1": (20, MAKER), "G2": (50, MAKER), "G3": (20, TAKER)}


def month_of(ts):
    d = dt.datetime.fromtimestamp(ts / 1000, dt.timezone.utc)
    return d.year * 12 + d.month


def grid_sim(bars, t0, t1, n_grid, fee, capital=1000.0):
    """Returns (curve [(ts, equity)], round trips)."""
    cash, slots, levels, cur_month, curve, trips = capital, [], [], None, [], 0
    lo_i = None

    def liquidate(px):
        nonlocal cash
        for s in slots:
            if s["held"]:
                cash += s["units"] * px * (1 - TAKER)
        slots.clear()

    def setup(k, px):
        nonlocal cash, levels
        hi, lo = max(b["h"] for b in bars[k - 720:k]), min(b["l"] for b in bars[k - 720:k])
        lo, hi = min(lo, px * 0.95), max(hi, px * 1.05)
        step = (hi / lo) ** (1 / n_grid)
        levels = [lo * step ** i for i in range(n_grid + 1)]
        per = cash / n_grid
        for i in range(n_grid):
            u = per / levels[i]
            held = levels[i + 1] > px  # slots above the price start with coin to sell
            if held:
                cash -= u * px * (1 + TAKER)
            slots.append({"i": i, "units": u, "held": held})

    def move(frm, to):
        nonlocal cash, trips
        if to < frm:  # falling: buys fill at their line
            for s in slots:
                L = levels[s["i"]]
                if not s["held"] and to <= L < frm:
                    cash -= s["units"] * L * (1 + fee)
                    s["held"] = True
        elif to > frm:  # rising: sells fill at the next line up
            for s in slots:
                U = levels[s["i"] + 1]
                if s["held"] and frm < U <= to:
                    cash += s["units"] * U * (1 - fee)
                    s["held"] = False
                    trips += 1

    for k, b in enumerate(bars):
        if not (e.ms(t0) <= b["ts"] < e.ms(t1)) or k < 720:
            continue
        m = month_of(b["ts"])
        if m != cur_month:
            liquidate(b["o"])
            setup(k, b["o"])
            cur_month = m
        path = [b["o"], b["l"], b["h"], b["c"]] if b["c"] >= b["o"] else [b["o"], b["h"], b["l"], b["c"]]
        for a_, z in zip(path, path[1:]):
            move(a_, z)
        curve.append((b["ts"], cash + sum(s["units"] * b["c"] for s in slots if s["held"])))
    return curve, trips


def dd(curve):
    peak, worst = None, 0.0
    for _, v in curve:
        peak = v if peak is None else max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst * 100


def main():
    import b_boxes as bb
    v = sys.argv[1]
    data = bb.load_1h(e.DESIGN)
    out = {"variant": v}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        t1 = t1 or e.now()
        curves, trips = [], 0
        for c, (bars, _) in data.items():
            if v == "HOLD":
                b0 = next(b for b in bars if b["ts"] >= e.ms(t0))
                curves.append([(b["ts"], 1000 * b["c"] / b0["c"]) for b in bars if e.ms(t0) <= b["ts"] < e.ms(t1)])
            else:
                cv, tr = grid_sim(bars, t0, t1, *CFG[v])
                curves.append(cv)
                trips += tr
        # combine the three $1,000 grids (hours where a coin has no candle keep its last value)
        allts = sorted({ts for cv in curves for ts, _ in cv})
        last = [cv[0][1] for cv in curves]
        maps = [dict(cv) for cv in curves]
        tot = []
        for ts in allts:
            for j, mp in enumerate(maps):
                if ts in mp:
                    last[j] = mp[ts]
            tot.append((ts, sum(last)))
        start = 1000 * len(curves)
        out[lab] = {"ret": round((tot[-1][1] / start - 1) * 100, 1), "dd": round(dd(tot), 1), "round_trips": trips}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
