"""
F13: the classic TradingView strategy families at the real fee (research/F13_PLAN.md). Research only.

  python research/f13_classics.py <1-12> [u]      u = never-seen coins
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035
NAMES = {1: "EMA cross 20/50", 2: "Golden cross 50/200", 3: "Ichimoku", 4: "UT Bot", 5: "Follow Line",
         6: "Keltner breakout", 7: "Hull MA 55", 8: "Parabolic SAR", 9: "Heikin Ashi", 10: "Kaufman AMA",
         11: "Traders Dynamic Index", 12: "Vortex", 13: "Triple RSI mean reversion",
         14: "Follow Line (exact)"}


def cross_up(a, b, k):
    return None not in (a[k], b[k], a[k - 1], b[k - 1]) and a[k] > b[k] and a[k - 1] <= b[k - 1]


def cross_dn(a, b, k):
    return cross_up(b, a, k)


def sma(x, n):
    return bot.sma(x, n)


def ema(x, n):
    first = next((i for i, v in enumerate(x) if v is not None), len(x))
    return [None] * first + bot.ema(x[first:], n)


def wma(x, n):
    out = [None] * len(x)
    w = list(range(1, n + 1))
    for i in range(n - 1, len(x)):
        seg = x[i - n + 1:i + 1]
        if None not in seg:
            out[i] = sum(a * b for a, b in zip(seg, w)) / sum(w)
    return out


def signals(sys_id, bars):
    """(buy[k], exit[k]) lists for one coin."""
    o, h, l, c = ([x[f] for x in bars] for f in "ohlc")
    n = len(c)
    buy, ex = [False] * n, [False] * n
    if sys_id in (1, 2):
        f, s = (ema(c, 20), ema(c, 50)) if sys_id == 1 else (sma(c, 50), sma(c, 200))
        for k in range(1, n):
            buy[k], ex[k] = cross_up(f, s, k), cross_dn(f, s, k)
    elif sys_id == 3:
        hl = lambda p, k: (max(h[k - p + 1:k + 1]) + min(l[k - p + 1:k + 1])) / 2 if k >= p - 1 else None  # noqa: E731
        ten = [hl(9, k) for k in range(n)]
        kij = [hl(26, k) for k in range(n)]
        sa = [None if ten[k] is None or kij[k] is None else (ten[k] + kij[k]) / 2 for k in range(n)]
        sb = [hl(52, k) for k in range(n)]
        for k in range(78, n):
            a_, b_ = sa[k - 26], sb[k - 26]  # cloud plotted 26 ahead = values from 26 days ago
            if None in (a_, b_, ten[k], kij[k]):
                continue
            top, bot_ = max(a_, b_), min(a_, b_)
            buy[k] = c[k] > top and ten[k] > kij[k] and c[k] > c[k - 26] and not (c[k - 1] > max(sa[k - 27] or 0, sb[k - 27] or 0) and ten[k - 1] > kij[k - 1] and c[k - 1] > c[k - 27])
            ex[k] = cross_dn(ten, kij, k) or c[k] < bot_ or (c[k] < top and c[k - 1] >= top)
    elif sys_id == 4:
        a = bot.atr(h, l, c, 10)
        st = [None] * n
        for k in range(1, n):
            if a[k] is None:
                continue
            loss, prev = a[k] * 1.0, st[k - 1] if st[k - 1] is not None else c[k]
            if c[k] > prev and c[k - 1] > prev:
                st[k] = max(prev, c[k] - loss)
            elif c[k] < prev and c[k - 1] < prev:
                st[k] = min(prev, c[k] + loss)
            else:
                st[k] = c[k] - loss if c[k] > prev else c[k] + loss
            if st[k - 1] is not None:
                buy[k] = c[k] > st[k - 1] and c[k - 1] <= st[k - 1]
                ex[k] = c[k] < st[k - 1] and c[k - 1] >= st[k - 1]
    elif sys_id == 5:
        a = bot.atr(h, l, c, 5)
        m = sma(c, 21)
        line, trend = [None] * n, [0] * n
        for k in range(21, n):
            if a[k] is None or m[k] is None:
                continue
            sd = math.sqrt(sum((x - m[k]) ** 2 for x in c[k - 20:k + 1]) / 21)
            up, dn = m[k] + sd, m[k] - sd
            prev = line[k - 1] if line[k - 1] is not None else c[k]
            if c[k] > up:
                line[k] = max(l[k] - a[k], prev) if trend[k - 1] == 1 else l[k] - a[k]
            elif c[k] < dn:
                line[k] = min(h[k] + a[k], prev) if trend[k - 1] == -1 else h[k] + a[k]
            else:
                line[k] = prev
            trend[k] = 1 if line[k] > prev else -1 if line[k] < prev else trend[k - 1]
            buy[k], ex[k] = trend[k] == 1 and trend[k - 1] != 1, trend[k] == -1 and trend[k - 1] == 1
    elif sys_id == 6:
        m, a = ema(c, 20), bot.atr(h, l, c, 10)
        for k in range(1, n):
            if None in (m[k], a[k], m[k - 1], a[k - 1]):
                continue
            buy[k] = c[k] > m[k] + 2 * a[k] and c[k - 1] <= m[k - 1] + 2 * a[k - 1]
            ex[k] = c[k] < m[k]
    elif sys_id == 7:
        half, full = wma(c, 27), wma(c, 55)
        raw = [None if None in (x, y) else 2 * x - y for x, y in zip(half, full)]
        hma = wma(raw, 7)
        for k in range(3, n):
            if None in (hma[k], hma[k - 2], hma[k - 1], hma[k - 3]):
                continue
            up, upp = hma[k] > hma[k - 2], hma[k - 1] > hma[k - 3]
            buy[k], ex[k] = up and not upp, upp and not up
    elif sys_id == 8:
        s = bot.psar(h, l, c, 0.02, 0.02, 0.2)
        for k in range(1, n):
            if None in (s[k], s[k - 1]):
                continue
            buy[k] = s[k] < c[k] and s[k - 1] >= c[k - 1]
            ex[k] = s[k] > c[k] and s[k - 1] <= c[k - 1]
    elif sys_id == 9:
        hc = [(o[k] + h[k] + l[k] + c[k]) / 4 for k in range(n)]
        ho = [0.0] * n
        ho[0] = (o[0] + c[0]) / 2
        for k in range(1, n):
            ho[k] = (ho[k - 1] + hc[k - 1]) / 2
        s50 = sma(c, 50)
        for k in range(1, n):
            green, pg = hc[k] > ho[k], hc[k - 1] > ho[k - 1]
            buy[k] = green and not pg and s50[k] is not None and c[k] > s50[k]
            ex[k] = not green and pg
    elif sys_id == 10:
        ka = [None] * n
        fast, slow = 2 / 3, 2 / 31
        for k in range(10, n):
            change = abs(c[k] - c[k - 10])
            vol = sum(abs(c[j] - c[j - 1]) for j in range(k - 9, k + 1))
            er = change / vol if vol else 0
            sc = (er * (fast - slow) + slow) ** 2
            ka[k] = c[k] if ka[k - 1] is None else ka[k - 1] + sc * (c[k] - ka[k - 1])
        for k in range(1, n):
            if None in (ka[k], ka[k - 1]):
                continue
            buy[k] = c[k] > ka[k] and c[k - 1] <= ka[k - 1] and ka[k] > ka[k - 1]
            ex[k] = c[k] < ka[k]
    elif sys_id == 11:
        r = bot.rsi(c, 13)
        pl, sg = sma(r, 2), sma(r, 7)
        for k in range(1, n):
            if None in (pl[k], sg[k], pl[k - 1], sg[k - 1]):
                continue
            buy[k] = cross_up(pl, sg, k) and pl[k] > 50 and sg[k] > 50
            ex[k] = cross_dn(pl, sg, k)
    elif sys_id == 12:
        p = 14
        vp, vm = [None] * n, [None] * n
        for k in range(p, n):
            tr = sum(max(h[j] - l[j], abs(h[j] - c[j - 1]), abs(l[j] - c[j - 1])) for j in range(k - p + 1, k + 1))
            if tr <= 0:
                continue  # flat days (no movement): no reading
            vp[k] = sum(abs(h[j] - l[j - 1]) for j in range(k - p + 1, k + 1)) / tr
            vm[k] = sum(abs(l[j] - h[j - 1]) for j in range(k - p + 1, k + 1)) / tr
        for k in range(1, n):
            buy[k], ex[k] = cross_up(vp, vm, k), cross_dn(vp, vm, k)
    elif sys_id == 14:  # the original Follow Line logic (F13c)
        a = bot.atr(h, l, c, 5)
        m = sma(c, 21)
        line, trend = [None] * n, [0] * n
        for k in range(21, n):
            if a[k] is None or m[k] is None:
                trend[k] = trend[k - 1]
                continue
            sd = math.sqrt(sum((x - m[k]) ** 2 for x in c[k - 20:k + 1]) / 21)
            sig = 1 if c[k] > m[k] + sd else -1 if c[k] < m[k] - sd else 0
            prev = line[k - 1]
            if sig == 1:
                line[k] = l[k] - a[k] if prev is None else max(l[k] - a[k], prev)
            elif sig == -1:
                line[k] = h[k] + a[k] if prev is None else min(h[k] + a[k], prev)
            else:
                line[k] = prev
            trend[k] = trend[k - 1]
            if line[k] is not None and prev is not None:
                if line[k] > prev:
                    trend[k] = 1
                elif line[k] < prev:
                    trend[k] = -1
            buy[k], ex[k] = trend[k] == 1 and trend[k - 1] != 1, trend[k] == -1 and trend[k - 1] == 1
    elif sys_id == 13:
        r, s200 = bot.rsi(c, 5), sma(c, 200)
        for k in range(4, n):
            if None in (r[k], r[k - 1], r[k - 2], r[k - 3], s200[k]):
                continue
            buy[k] = r[k] < 30 and r[k] < r[k - 1] < r[k - 2] < r[k - 3] and r[k - 3] < 60 and c[k] > s200[k]
            ex[k] = r[k] > 50
    return buy, ex


def run(sys_id, coins, risk=0.0035):
    data = {c: (d, d) for c, (_, d) in e.load(coins).items()}
    exits = {}

    def entries(coin, bars, _daily):
        buy, ex = signals(sys_id, bars)
        exits[id(bars)] = ex
        a = bot.atr([x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars], 14)
        return [{"stop": bars[k]["c"] - 2 * a[k], "target": None, "max_bars": None} if buy[k] and a[k] else None
                for k in range(len(bars))]

    def manage(p, bars, k):
        return "exit" if exits[id(bars)][k] and k > p["k"] else None
    return lambda t0, t1: e.trade_sim(coins, data, entries, t0, t1, risk=risk, max_open=5, fee=FEE, manage=manage)


def main():
    sid = int(sys.argv[1])
    opt = sys.argv[2] if len(sys.argv) > 2 else ""  # "u" = never-seen coins, or a risk such as 0.003 (F13b)
    coins = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "dc-okx")["coins"]]
    if opt == "u":
        coins = [c for c in e.UNSEEN if c not in coins]
    sim = run(sid, coins, float(opt) if opt and opt != "u" else 0.0035)
    out = {"id": sid, "name": NAMES[sid], "opt": opt}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
