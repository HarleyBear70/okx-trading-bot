"""
TEAM TEST (Oct 8 2026, Jeff: "if they can work together and win why not"): Turtle 55/20 (live turtle bots) and
Dynamic Breakout II (research/QC_LIBRARY.md), mixed and combined. Crypto, daily, long only, Binance.US costs.

PLAN (written before any results). Each coin gets an equal slice of the money (no leverage); fills at the next
day's open; 0.05% a side. Versions:
  T        Turtle 55/20: buy on a close above the 55-day high, sell on a close below the 20-day low.
  D        Dynamic Breakout II (research/qc_library.py rules).
  T-adapt  Turtle with DB2's lookback (20-60 days, stretches with volatility) for the entry high.
  T-avg    Turtle entry, DB2's exit (close below the 55-day average).
  TEAM     half the money in T, half in D.
  +BTC     the same, but no new buys while BTC closes below its 200-day average (exits unchanged).
Judged on growth per worst drop (MAR = yearly growth / worst drop), both halves (2019-22 / 2023-now),
and the never-seen coins. A change only wins if it is better in both halves AND on never-seen coins.

  python3 research/team_test.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import hourly as hr  # noqa: E402
import qc_library as Q  # noqa: E402
from brad_more import COINS23  # noqa: E402

DAY = 86400000
COST = 0.0005


def btc_ok():
    d = Q.daily([dict(x, sp=0.0) for x in hr.hourly("BTC")])
    c = [x["c"] for x in d]
    sma = B.sma(c, 200)
    return {x["ts"]: (sma[i] is not None and c[i] > sma[i]) for i, x in enumerate(d)}


def signals(d, kind, ok=None):
    """list of (entry_i, exit_i): signal on day i's close, filled at day i+1's open"""
    c = [x["c"] for x in d]
    out, ent, num, pv = [], None, 20, None
    for i in range(61, len(d) - 1):
        w = c[i - 29:i + 1]
        m = sum(w) / 30
        vol = (sum((v - m) ** 2 for v in w) / 30) ** 0.5
        if pv and vol:
            num = min(60, max(20, round(num * (1 + (vol - pv) / vol))))
        pv = vol
        if ent is not None:
            if kind in ("T", "T-adapt"):
                out_ = c[i] < min(x["l"] for x in d[i - 20:i])
            elif kind == "T-avg":
                out_ = c[i] < sum(c[i - 54:i + 1]) / 55
            else:
                out_ = c[i] < sum(c[i - num + 1:i + 1]) / num
            if out_:
                out.append((ent, i + 1))
                ent = None
            continue
        if ok is not None and not ok.get(d[i]["ts"], False):
            continue
        if kind in ("T", "T-avg"):
            go = c[i] > max(x["h"] for x in d[i - 55:i])
        elif kind == "T-adapt":
            go = c[i] > max(x["h"] for x in d[i - num:i])
        else:
            seg = c[i - num + 1:i + 1]
            sma = sum(seg) / num
            sd = (sum((v - sma) ** 2 for v in seg) / num) ** 0.5
            go = c[i] > B.ema(c[:i + 1], num)[-1] + 2 * sd and d[i]["h"] >= max(x["h"] for x in d[i - num:i])
        if go:
            ent = i + 1
    if ent is not None:
        out.append((ent, None))
    return out


def sleeve(d, sig, t0):
    """daily equity {ts: value} of one coin's slice, starting at 1.0 on t0"""
    eq, curve, k, pos = 1.0, {}, 0, None
    sig = sorted(sig)
    for i, x in enumerate(d):
        if x["ts"] < t0:
            continue
        while pos is None and k < len(sig) and sig[k][0] < i and (sig[k][1] is not None and sig[k][1] <= i):
            k += 1  # trades that started before t0
        if pos is None and k < len(sig) and sig[k][0] == i:
            pos = (x["o"] * (1 + COST), sig[k][1], eq)
        if pos and pos[1] == i:
            eq = pos[2] * x["o"] * (1 - COST) / pos[0]
            pos = None
            k += 1
            if k < len(sig) and sig[k][0] == i:
                pos = (x["o"] * (1 + COST), sig[k][1], eq)
        curve[x["ts"]] = pos[2] * x["c"] / pos[0] if pos else eq
    return curve


def stats(curve, a, z):
    ks = [k for k in sorted(curve) if a <= k < z]
    if len(ks) < 30:
        return None
    v = [curve[k] for k in ks]
    v = [x / v[0] for x in v]
    peak, dd = 0, 0
    for x in v:
        peak = max(peak, x)
        dd = max(dd, 1 - x / peak)
    yrs = (ks[-1] - ks[0]) / DAY / 365.25
    cagr = v[-1] ** (1 / yrs) - 1
    return {"g": v[-1], "cagr": cagr, "dd": dd, "mar": cagr / dd if dd else 0}


def main():
    ok = btc_ok()
    t0, cut, end = B.ms(B.START), B.ms(B.CUT), 10 ** 14
    for title, coins in (("main 5 (BTC ETH SOL XRP BNB)", COINS23[:5]), ("never-seen 18", COINS23[5:])):
        days = {c: Q.daily(B.load("crypto", c, "1H")) for c in coins}
        port = {}
        for kind in ("T", "D", "T-adapt", "T-avg"):
            for btc in (False, True):
                curves = [sleeve(d, signals(d, kind, ok if btc else None), t0) for d in days.values()]
                keys = sorted(set().union(*curves))
                last = [1.0] * len(curves)
                pc = {}
                for k in keys:
                    for j, cv in enumerate(curves):
                        last[j] = cv.get(k, last[j])
                    pc[k] = sum(last) / len(last)
                port[kind + (" +BTC" if btc else "")] = pc
        for btc in ("", " +BTC"):
            a, b = port["T" + btc], port["D" + btc]
            port["TEAM (T+D)" + btc] = {k: (a[k] + b[k]) / 2 for k in a if k in b}
        print(f"\n### {title}\n")
        print("| Version | Growth | Per year | Worst drop | MAR | 2019-22 MAR | 2023-now MAR |")
        print("|---|---|---|---|---|---|---|")
        order = ["T", "D", "T-adapt", "T-avg", "TEAM (T+D)"]
        for name in order + [n + " +BTC" for n in order]:
            f, h1, h2 = (stats(port[name], x, y) for x, y in ((t0, end), (t0, cut), (cut, end)))
            m = lambda s: "-" if not s else f"{s['mar']:.2f}"
            print(f"| {name} | {f['g']:.1f}x | {100 * f['cagr']:+.0f}% | -{100 * f['dd']:.0f}% | {f['mar']:.2f} | "
                  f"{m(h1)} | {m(h2)} |", flush=True)


if __name__ == "__main__":
    main()
