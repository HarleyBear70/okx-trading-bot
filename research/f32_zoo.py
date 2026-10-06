"""
F32: two academic factors from Vibe-Trading's Alpha Zoo (HKUDS/Vibe-Trading, agent/src/factors/zoo/academic),
adapted to a weekly crypto rotation with a BTC trend switch (the earlier rotation test N2 failed on drawdowns).

  - high52w: price / highest close of the last 365 days (closest to its yearly high ranks first)
  - mom (Carhart-style): return from 90 days ago to 7 days ago (skips the last week)
  - strev (short-term reversal, for contrast): minus the last 7 days' return (buys last week's losers)

Every Monday (UTC): if BTC's close is above its 100-day average, hold the top 3 coins by the factor, equal weight;
otherwise hold cash. Trades only what changes; 0.35% fee on every buy and sell. Universe includes coins that later
collapsed (LUNA, FTT) to limit survivorship bias. Research only.
"""
import datetime as dt
import engine as e

UNIVERSE = ["BTC", "ETH", "XRP", "BNB", "SOL", "ADA", "DOGE", "LTC", "LINK", "BCH", "XLM", "TRX", "AVAX", "LUNA", "FTT"]
FEE = 0.0035
TOP = 3


def daily_closes(coins):
    out = {}
    for c in coins:
        try:
            _, d = e.load([c])[c]
        except Exception:
            continue
        out[c] = {x["ts"]: x["c"] for x in d}
    return out


def factor(kind, hist):
    """hist: list of closes up to today (oldest first)."""
    if kind == "high52w":
        return hist[-1] / max(hist[-365:]) if len(hist) >= 365 else None
    if kind == "mom":
        return hist[-8] / hist[-91] - 1 if len(hist) >= 91 else None
    if kind == "strev":
        return -(hist[-1] / hist[-8] - 1) if len(hist) >= 8 else None


def run(kind, closes, t0, t1, use_filter=True):
    days = sorted(closes["BTC"])
    days = [d for d in days if e.ms(t0) <= d < e.ms(t1)]
    hist = {c: [] for c in closes}
    allk = sorted({d for c in closes for d in closes[c]})
    eq, hold, curve, trades = 1000.0, {}, [], 0   # hold: coin -> units
    btc_hist = []
    for d in allk:
        for c in closes:
            if d in closes[c]:
                hist[c].append(closes[c][d])
        if "BTC" in closes and d in closes["BTC"]:
            btc_hist.append(closes["BTC"][d])
        if d < e.ms(t0) or d >= e.ms(t1):
            continue
        val = sum(u * closes[c].get(d, hist[c][-1] if hist[c] else 0) for c, u in hold.items())
        cash = eq
        total = cash + val
        if dt.datetime.fromtimestamp(d / 1000, e.UTC).weekday() == 0:
            on = not use_filter or (len(btc_hist) >= 100 and btc_hist[-1] > sum(btc_hist[-100:]) / 100)
            want = []
            if on:
                ranked = [(factor(kind, hist[c]), c) for c in closes if d in closes[c] and factor(kind, hist[c]) is not None]
                want = [c for _, c in sorted(ranked, reverse=True)[:TOP]]
            # sell what's no longer wanted
            for c in list(hold):
                if c not in want:
                    px = closes[c].get(d, hist[c][-1])
                    cash += hold.pop(c) * px * (1 - FEE)
                    trades += 1
            # rebalance into equal weights (buy the missing ones with the cash)
            total = cash + sum(u * closes[c].get(d, hist[c][-1]) for c, u in hold.items())
            new = [c for c in want if c not in hold]
            if new:
                per = cash / len(new)
                for c in new:
                    hold[c] = per * (1 - FEE) / closes[c][d]
                    trades += 1
                cash = 0.0
            eq = cash
            total = cash + sum(u * closes[c].get(d, hist[c][-1]) for c, u in hold.items())
        curve.append((d, total))
    peak, dd = 1000.0, 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return curve[-1][1] / 10 - 100, dd * 100, trades


def main():
    closes = daily_closes(UNIVERSE)
    periods = [("2018-now", e.START, e.now()), ("2018-21", e.START, e.CUT), ("2022-now", e.CUT, e.now())]
    print("| Factor (top 3 weekly) | BTC switch | " + " | ".join(p for p, _, _ in periods) + " | Trades (full) |")
    print("|---|---|---|---|---|---|")
    for kind in ("high52w", "mom", "strev"):
        for filt in (True, False):
            cells, tr = [], 0
            for i, (_, t0, t1) in enumerate(periods):
                r, dd, n = run(kind, closes, t0, t1, filt)
                cells.append(f"{r:+.0f}% / {dd:.0f}%")
                tr = n if i == 0 else tr
            print(f"| {kind} | {'on' if filt else 'off'} | " + " | ".join(cells) + f" | {tr} |", flush=True)


if __name__ == "__main__":
    main()
