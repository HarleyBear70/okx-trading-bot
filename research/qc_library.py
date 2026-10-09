"""
QUANTCONNECT STRATEGY LIBRARY: the ones that fit Jeff (crypto/forex, rules fully public), Oct 8 2026.
Already covered elsewhere: time-series momentum (F38 M90/M200), coin rotation (F32, N2), forex trend/momentum (F38).

PLAN (written before any results). Rules copied from the library pages:
  DT   Dual Thrust: each UTC day, range = max(HH-LC, HC-LL) of the last 4 daily candles; buy level = day open
       + 0.5 x range, sell level = day open - 0.5 x range. Price through the buy level = long, through the sell
       level = short (crypto spot: flat). Always-in reversal system, run on 1H candles.
  DB2  Dynamic Breakout II: daily. Lookback starts at 20, changes with 30-day volatility,
       numdays = round(numdays x (1 + (vol_today - vol_yday) / vol_today)), kept 20-60. Long when the close is
       above the upper Bollinger band (EMA, 2 std, numdays) and at a numdays high; short the mirror (crypto: none).
       Exit when the close crosses the numdays simple average. Fills at the next day's open.
  TOM  Turn of the Month: hold from the close of the month's last day to the close of the 3rd day (crypto only).
  Costs: crypto 0.05% a side (Binance.US 0.02% + slippage); forex OANDA spread. 1x size, no leverage.

PASS RULES: profit factor 1.3+ with 100+ trades, PF 1.1+ in BOTH halves (2019-22 / 2023-now), and on the
never-seen markets PF 1.1+ as well. Main: crypto BTC ETH SOL XRP BNB, forex EUR/USD GBP/USD gold.

  python3 research/qc_library.py
"""
import calendar
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402
from brad_more import COINS23  # noqa: E402

UTC = dt.timezone.utc
DAY = 86400000


def daily(b):
    return J.resample(b, DAY)


def dual_thrust(market, b, longs_only, n=4, k=0.5):
    d = daily(b)
    idx = {x["ts"]: i for i, x in enumerate(d)}
    out, pos, t0 = [], None, B.ms(B.START)  # pos = (side, entry, cost, ts)

    def close(x, px):
        nonlocal pos
        sd, ent, ec, ts = pos
        out.append((ts, (sd * (px - ent) - ec - B.cost(market, x, px)) / ent))
        pos = None

    day, cap, floor = None, None, None
    for x in b:
        dk = x["ts"] - x["ts"] % DAY
        if dk != day:
            day = dk
            i = idx.get(dk)
            cap = floor = None
            if i is not None and i >= n:
                w = d[i - n:i]
                hh, ll = max(y["h"] for y in w), min(y["l"] for y in w)
                hc, lc = max(y["c"] for y in w), min(y["c"] for y in w)
                rng = max(hh - lc, hc - ll)
                cap, floor = x["o"] + k * rng, x["o"] - k * rng
        if x["ts"] < t0 or cap is None:
            continue
        up, dn = x["h"] >= cap, x["l"] <= floor
        if up and dn:  # both in one candle: take the one nearer the open
            up = abs(cap - x["o"]) <= abs(x["o"] - floor)
            dn = not up
        if up and (not pos or pos[0] == -1):
            px = max(cap, x["o"])
            if pos:
                close(x, px)
            pos = (1, px, B.cost(market, x, px), x["ts"])
        elif dn and (not pos or pos[0] == 1):
            px = min(floor, x["o"])
            if pos:
                close(x, px)
            if not longs_only:
                pos = (-1, px, B.cost(market, x, px), x["ts"])
    return out


def breakout2(market, b, longs_only):
    d = daily(b)
    c = [x["c"] for x in d]
    out, pos, t0 = [], None, B.ms(B.START)
    num, prev_vol, sig = 20, None, 0
    for i in range(31, len(d)):
        x = d[i]
        if sig and d[i]["ts"] >= t0:  # act on yesterday's signal at today's open
            if pos and sig == -9:
                sd, ent, ec, ts = pos
                out.append((ts, (sd * (x["o"] - ent) - ec - B.cost(market, x, x["o"])) / ent))
                pos = None
            elif not pos and sig in (1, -1):
                pos = (sig, x["o"], B.cost(market, x, x["o"]), x["ts"])
        sig = 0
        w = c[i - 29:i + 1]
        m = sum(w) / 30
        vol = (sum((v - m) ** 2 for v in w) / 30) ** 0.5
        if prev_vol and vol:
            num = min(60, max(20, round(num * (1 + (vol - prev_vol) / vol))))
        prev_vol = vol
        if i < num + 1:
            continue
        seg = c[i - num + 1:i + 1]
        sma = sum(seg) / num
        e = B.ema(c[:i + 1], num)[-1]
        sd_ = (sum((v - sma) ** 2 for v in seg) / num) ** 0.5
        hi, lo = max(y["h"] for y in d[i - num:i]), min(y["l"] for y in d[i - num:i])
        if pos:
            if (pos[0] == 1 and c[i] < sma) or (pos[0] == -1 and c[i] > sma):
                sig = -9
        elif c[i] > e + 2 * sd_ and d[i]["h"] >= hi:
            sig = 1
        elif not longs_only and c[i] < e - 2 * sd_ and d[i]["l"] <= lo:
            sig = -1
    return out


def turn_of_month(market, b):
    d = daily(b)
    out, t0 = [], B.ms(B.START)
    for i, x in enumerate(d):
        t = dt.datetime.fromtimestamp(x["ts"] / 1000, UTC)
        if x["ts"] < t0 or t.day != calendar.monthrange(t.year, t.month)[1] or i + 3 >= len(d):
            continue
        y = d[i + 3]
        out.append((x["ts"], (y["c"] - x["c"] - B.cost(market, x, x["c"]) - B.cost(market, y, y["c"])) / x["c"]))
    return out


def stats(tr):
    if not tr:
        return None
    rs = [r for _, r in tr]
    win, loss = sum(r for r in rs if r > 0), -sum(r for r in rs if r < 0)
    return {"n": len(rs), "pf": win / loss if loss else 99, "avg": 100 * sum(rs) / len(rs),
            "win": 100 * sum(r > 0 for r in rs) / len(rs)}


def row(name, tr):
    cut = B.ms(B.CUT)
    f, h1, h2 = stats(tr), stats([t for t in tr if t[0] < cut]), stats([t for t in tr if t[0] >= cut])
    if not f:
        return f"| {name} | 0 | | | | | |"
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    return f"| {name} | {f['n']} | {f['win']:.0f}% | {f['pf']:.2f} | {f['avg']:+.2f}% | {p(h1)} | {p(h2)} |"


SETS = [("crypto main (BTC ETH SOL XRP BNB), long only", "crypto", COINS23[:5]),
        ("crypto never-seen (18 coins), long only", "crypto", COINS23[5:]),
        ("forex main (EUR GBP gold), long+short", "forex", ["EUR_USD", "GBP_USD", "XAU_USD"]),
        ("forex never-seen (AUD NZD CAD CHF JPY), long+short", "forex",
         ["AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY"])]


def main():
    for title, market, insts in SETS:
        data = {i: B.load(market, i, "1H") for i in insts}
        lo = market == "crypto"
        print(f"\n### {title}\n")
        print("| Strategy | Trades | Win % | PF | Avg trade | 2019-22 PF | 2023-now PF |")
        print("|---|---|---|---|---|---|---|")
        print(row("Dual Thrust", [t for b in data.values() for t in dual_thrust(market, b, lo)]), flush=True)
        print(row("Dynamic Breakout II", [t for b in data.values() for t in breakout2(market, b, lo)]), flush=True)
        if lo:
            print(row("Turn of the Month", [t for b in data.values() for t in turn_of_month(market, b)]), flush=True)


if __name__ == "__main__":
    main()
