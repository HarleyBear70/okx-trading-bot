"""
F43 research scout (2026-10-10). Rules written BEFORE testing, no tuning afterwards.
M  Month-end dollar flow (forex): daily bars. At the close of the 3rd-from-last trading day of each month, SHORT
   EUR/USD and GBP/USD (long dollar); exit at the close of the first trading day of the next month. Safety stop 3 ATR(20).
   Source idea: bank desks (BofA/Barclays/Deutsche) say month-end rebalancing sells EUR/GBP vs USD.
   Crypto mirror (long, "turn of the month" effect) tested too: buy at 3rd-from-last day close, sell at first day's close.
B  Bollinger stretch fade (daily, no trend filter): close below SMA20 - 2*sd -> long; close above SMA20 + 2*sd -> short
   (forex both ways, crypto long only). Exit at the first close back across SMA20. Safety stop 3 ATR(20).
Forex: f39_both.fx_sim, 0.01% a side, 2012-03 onward, halves 2012-18 / 2019-now. Crypto: engine.trade_sim, 0.5% risk,
fees 0.35% and 0.02%, BTC ETH SOL XRP BNB LINK, plus never-seen coins. Research only.
"""
import datetime as dt
import statistics as st
import engine as e
import bot
import forex_dxy as fx
import f39_both as f

FOREX = ["EURUSD", "GBPUSD"]
CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK"]


def month_ends(bars):
    """index list: k where bars[k] is 3rd-from-last trading day of its month; and first day of month."""
    ym = [dt.datetime.fromtimestamp(b["ts"] / 1000, e.UTC).strftime("%Y%m") for b in bars]
    third, first = set(), set()
    for k in range(len(bars)):
        if k == 0 or ym[k] != ym[k - 1]:
            first.add(k)
        if k + 3 < len(bars) and ym[k + 3] != ym[k] and ym[k + 2] == ym[k]:
            third.add(k)  # k+1,k+2 same month, k+3 new month  => k is 3rd from last
    return third, first


def month_signals(bars, side):
    c, h, l = [b["c"] for b in bars], [b["h"] for b in bars], [b["l"] for b in bars]
    a = bot.atr(h, l, c, 20)
    third, first = month_ends(bars)
    out = [None] * len(bars)
    for k in third:
        if a[k]:
            stop = c[k] - 3 * a[k] if side == 1 else c[k] + 3 * a[k]
            out[k] = (side, stop, None, (lambda k0: lambda j: j > k0 and j in first)(k))
    return out


def boll_signals(bars, shorts):
    c, h, l = [b["c"] for b in bars], [b["h"] for b in bars], [b["l"] for b in bars]
    a = bot.atr(h, l, c, 20)
    out = [None] * len(bars)
    for k in range(25, len(bars)):
        w = c[k - 19:k + 1]
        m, sd = sum(w) / 20, st.pstdev(w)
        if not a[k] or sd == 0:
            continue
        sma = lambda j: sum(c[j - 19:j + 1]) / 20
        if c[k] < m - 2 * sd:
            out[k] = (1, c[k] - 3 * a[k], None, lambda j: c[j] > sma(j))
        elif shorts and c[k] > m + 2 * sd:
            out[k] = (-1, c[k] + 3 * a[k], None, lambda j: c[j] < sma(j))
    return out


def cell(r):
    return f"{r['ret']:+.0f}% / {r['dd']:.1f}% / PF {r['pf']:.2f} / win {r['win']:.0f}% ({r['trades']})"


def crypto_run(kind, fee, coins=CRYPTO, data=None):
    data = data or {c: (d, d) for c, (_, d) in e.load(coins).items()}

    def ent(coin, bars, _d):
        if kind == "M":
            sig = month_signals(bars, 1)
        else:
            sig = boll_signals(bars, False)
        return [None if s is None else {"stop": s[1], "_ex": s[3]} for s in sig]
    cache = {}

    def man(p, bars, k):
        key = id(bars)
        if key not in cache:
            cache[key] = month_signals(bars, 1) if kind == "M" else boll_signals(bars, False)
        return None
    # manage needs per-position exit rule; implement directly
    def man2(p, bars, k):
        c = [b["c"] for b in bars[max(0, k - 19):k + 1]]
        if kind == "B":
            return "exit" if len(c) == 20 and bars[k]["c"] > sum(c) / 20 else None
        ym = lambda j: dt.datetime.fromtimestamp(bars[j]["ts"] / 1000, e.UTC).month
        return "exit" if k > 0 and ym(k) != ym(k - 1) else None
    return [e.trade_sim(coins, data, ent, a, b, risk=f.RISK, max_open=len(coins), fee=fee, manage=man2)
            for a, b in ((e.START, None), (e.START, e.CUT), (e.CUT, None))]


def main():
    h4 = {p: fx.fxcm(p) for p in FOREX}
    daily = {p: fx.fx_daily(h4[p]) for p in FOREX}
    periods = ((f.FX0, None), (f.FX0, f.FXCUT), (f.FXCUT, None))
    print("| Idea | Market | Full | 1st half | 2nd half |\n|---|---|---|---|---|")
    for name, mk in (("M month-end short USD-flow", lambda b: month_signals(b, -1)),
                     ("M2 month-end mirror (long)", lambda b: month_signals(b, 1)),
                     ("B Bollinger fade both ways", lambda b: boll_signals(b, True))):
        sig = {p: mk(daily[p]) for p in FOREX}
        rs = [f.fx_sim(sig, daily, a, b) for a, b in periods]
        print(f"| {name} | EUR/USD+GBP/USD | " + " | ".join(cell(r) for r in rs) + " |", flush=True)
        for p in FOREX:
            rs = [f.fx_sim({p: sig[p]}, {p: daily[p]}, a, b) for a, b in periods]
            print(f"| {name} | {p} alone | " + " | ".join(cell(r) for r in rs) + " |", flush=True)
    data = {c: (d, d) for c, (_, d) in e.load(CRYPTO).items()}
    for kind, nm in (("M", "M turn-of-month long"), ("B", "B Bollinger fade long")):
        for fee in (bot.FEE, 0.0002):
            rs = crypto_run(kind, fee, data=data)
            print(f"| {nm} | crypto fee {fee*100:.2f}% | " + " | ".join(cell(r) for r in rs) + " |", flush=True)


if __name__ == "__main__":
    main()
