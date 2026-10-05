"""
Candle pattern test: do the popular "watch for this candle" signals actually work?

Same method and skeptic check as concept_test.py: for each bullish candle pattern on 4H
candles, compare the price move 1, 2 and 4 days later with an ordinary candle, separately
for Mar 2024 - Jun 2025 and Jul 2025 - now. Each pattern is tested on its own and again
only when the daily trend is up (daily close above its 50-day average).

  python research/candle_test.py <data_dir> <out_file>
"""
import math
import sys

import pandas as pd

from concept_test import COINS, HORIZONS, SPLIT, START, fwd_returns, load, shift_pvalue, stats, verdict_for


def patterns(df, daily):
    o, h, l, c = (df[k].tolist() for k in ("open", "high", "low", "close"))
    n = len(df)
    body = [abs(c[i] - o[i]) for i in range(n)]
    avg_body = pd.Series(body).rolling(20).mean().tolist()
    low10 = pd.Series(l).rolling(10).min().tolist()

    d = daily.copy()
    d["ema50"] = d["close"].ewm(span=50, adjust=False).mean()
    d["up"] = d["close"] > d["ema50"]
    up_by_day = dict(zip(d["date"].dt.floor("D") + pd.Timedelta(days=1), d["up"]))
    day_up = [bool(up_by_day.get(t.floor("D"), False)) for t in df["date"]]

    ev = {k: [] for k in ("Bullish engulfing", "Hammer", "Morning star", "Three white soldiers",
                          "Inside bar breakout", "Big breakout candle")}
    for i in range(3, n):
        if avg_body[i] is None or math.isnan(avg_body[i]) or avg_body[i] == 0:
            continue
        green = c[i] > o[i]
        rng = h[i] - l[i]
        lower_w = min(c[i], o[i]) - l[i]
        upper_w = h[i] - max(c[i], o[i])
        # engulfing: green body swallows the previous red body
        if green and c[i - 1] < o[i - 1] and c[i] >= o[i - 1] and o[i] <= c[i - 1]:
            ev["Bullish engulfing"].append(i)
        # hammer at a recent low: long lower wick, small upper wick
        if body[i] > 0 and lower_w >= 2 * body[i] and upper_w <= body[i] and l[i] <= low10[i] * 1.001:
            ev["Hammer"].append(i)
        # morning star: big red, small candle, big green closing past the red's midpoint
        if (c[i - 2] < o[i - 2] and body[i - 2] > avg_body[i] and body[i - 1] < 0.5 * avg_body[i]
                and green and body[i] > avg_body[i] and c[i] > (o[i - 2] + c[i - 2]) / 2):
            ev["Morning star"].append(i)
        # three white soldiers: three green candles, each closing higher
        if all(c[k] > o[k] for k in (i - 2, i - 1, i)) and c[i] > c[i - 1] > c[i - 2] \
                and min(body[i - 2], body[i - 1], body[i]) > 0.5 * avg_body[i]:
            ev["Three white soldiers"].append(i)
        # inside bar breakout: candle i-1 inside i-2, then candle i closes above i-2's high
        if h[i - 1] <= h[i - 2] and l[i - 1] >= l[i - 2] and c[i] > h[i - 2]:
            ev["Inside bar breakout"].append(i)
        # big breakout candle: body 2x normal, closes in the top quarter of its range
        if green and body[i] > 2 * avg_body[i] and rng > 0 and (c[i] - l[i]) / rng >= 0.75:
            ev["Big breakout candle"].append(i)
    out = {}
    for name, idx in ev.items():
        out[name] = idx
        out[name + " + daily uptrend"] = [i for i in idx if day_up[i]]
    return out


def main():
    data_dir, out = sys.argv[1], sys.argv[2]
    halves = {"first half": (START, SPLIT), "second half": (SPLIT, None)}
    rows, base, coins_used, shift_data = {}, {}, [], {}
    for coin in COINS:
        df4, d1 = load(data_dir, coin, "4h"), load(data_dir, coin, "1d")
        if df4 is None or d1 is None:
            continue
        coins_used.append(coin)
        ev = patterns(df4, d1)
        dates = df4["date"]
        first = int((dates >= START).idxmax())
        for name, idx in ev.items():
            shift_data.setdefault(name, []).append((df4["close"].tolist(), idx, first))
        for hname, (a, b) in halves.items():
            in_half = [(dates[i] >= a) and (b is None or dates[i] < b) for i in range(len(df4))]
            idx_all = [i for i in range(len(df4)) if in_half[i]]
            for hz in HORIZONS:
                base.setdefault((hz, hname), []).extend(fwd_returns(df4, idx_all, hz))
                for name, idx in ev.items():
                    rows.setdefault((name, hz, hname), []).extend(
                        fwd_returns(df4, [i for i in idx if in_half[i]], hz))

    lines = ["# Candle pattern test: do the popular candle signals work?", "",
             f"OKX 4H candles, {', '.join(coins_used)}. Edge = average % move 2 days after the candle "
             "minus the average move after any candle. **Real** = positive in both halves "
             "(Mar 2024 - Jun 2025 and Jul 2025 - now) and passed the shift test (p under 0.005: the same "
             "candles slid to random times did as well less than 0.5% of the time).", "",
             "| Candle | Times seen | Edge 1st half | Edge 2nd half | Edge +4 days (all) | Up % | Verdict |",
             "|---|---|---|---|---|---|---|"]
    for name in sorted({k[0] for k in rows}, key=lambda s: (s.replace(" + daily uptrend", ""), s)):
        e, tot, tot4 = {}, [], []
        for hname in halves:
            s, b = stats(rows[(name, 12, hname)]), stats(base[(12, hname)])
            e[hname] = (s[0] - b[0]) if s and b else None
            tot += rows[(name, 12, hname)]
        st = stats(tot)
        e4 = []
        for hname in halves:
            s4, b4 = stats(rows[(name, 24, hname)]), stats(base[(24, hname)])
            if s4 and b4:
                e4.append((s4[0] - b4[0]) * s4[3])
        n4 = sum(len(rows[(name, 24, h)]) for h in halves)
        edge4 = sum(e4) / n4 if n4 else None
        a1, a2 = e["first half"], e["second half"]
        p = shift_pvalue(shift_data[name])
        verdict = verdict_for(p, a1, a2, st[3] if st else 0)
        if p is not None:
            verdict += f" (p={p:.2f})"
        fmt = lambda x: "-" if x is None else f"{x:+.2f}%"
        lines.append(f"| {name} | {0 if not st else st[3]} | {fmt(a1)} | {fmt(a2)} | {fmt(edge4)} | "
                     f"{'-' if not st else f'{st[1]:.0f}%'} | {verdict} |")
    lines += ["", "Baseline (any candle, 2-day move): " + ", ".join(
        f"{h} {stats(base[(12, h)])[0]:+.2f}%" for h in halves if stats(base[(12, h)])), ""]
    open(out, "w").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
