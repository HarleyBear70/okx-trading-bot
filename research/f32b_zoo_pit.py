"""
F32b: F32 without hindsight. Each Monday the candidates are only the coins that were in the CoinMarketCap top 10 at
that time (research/universe.py snapshots, stablecoins removed, as in N2). Same rules otherwise: rank by the factor,
hold the top K equal weight while BTC is above its 100-day average, else cash; 0.35% fee per buy and sell.
Research only.
"""
import bisect
import datetime as dt
import n2_rotation as n2
import engine as e

FEE = 0.0035
DAY = 86400000


def run(D, hist_days, kind, k, t0, t1):
    btc_days = hist_days["BTC"]
    start, end = e.ms(t0), e.ms(t1)
    days = [d for d in btc_days if start <= d < end]
    cash, hold, curve = 1000.0, {}, []

    def closes_upto(sym, d, n):
        ds = hist_days.get(sym)
        if not ds:
            return None
        i = bisect.bisect_right(ds, d)
        if i < n:
            return None
        return [D.px[sym][x] for x in ds[i - n:i]]

    def px(sym, d):
        p = D.price(sym, d)
        if p is None:
            c = closes_upto(sym, d, 1)
            p = c[-1] if c else 0.0
        return p

    for d in days:
        if dt.datetime.fromtimestamp(d / 1000, e.UTC).weekday() == 0:
            b = closes_upto("BTC", d, 100)
            on = b is not None and b[-1] > sum(b) / 100
            want = []
            if on:
                scores = []
                for s in D.universe(d, 1, 10):
                    if kind == "high52w":
                        c = closes_upto(s, d, 365)
                        f = c[-1] / max(c) if c and D.price(s, d) else None
                    else:
                        c = closes_upto(s, d, 91)
                        f = c[-8] / c[0] - 1 if c and D.price(s, d) else None
                    if f is not None:
                        scores.append((f, s))
                want = [s for _, s in sorted(scores, reverse=True)[:k]]
            for s in list(hold):
                if s not in want:
                    cash += hold.pop(s) * px(s, d) * (1 - FEE)
            new = [s for s in want if s not in hold]
            if new:
                per = cash / len(new)
                for s in new:
                    hold[s] = per * (1 - FEE) / px(s, d)
                cash = 0.0
        curve.append((d, cash + sum(u * px(s, d) for s, u in hold.items())))
    peak, dd = 1000.0, 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return curve[-1][1] / 10 - 100, dd * 100


def main():
    D = n2.Data()
    hist_days = {s: sorted(p) for s, p in D.px.items() if p}
    periods = [("2018-now", e.START, e.now()), ("2018-21", e.START, e.CUT), ("2022-now", e.CUT, e.now())]
    print("| Factor | Top K | " + " | ".join(p for p, _, _ in periods) + " |")
    print("|---|---|---|---|---|")
    for kind in ("high52w", "mom"):
        for k in (2, 3, 5):
            cells = []
            for _, t0, t1 in periods:
                r, dd = run(D, hist_days, kind, k, t0, t1)
                cells.append(f"{r:+.0f}% / {dd:.0f}%")
            print(f"| {kind} | {k} | " + " | ".join(cells) + " |", flush=True)


if __name__ == "__main__":
    main()
