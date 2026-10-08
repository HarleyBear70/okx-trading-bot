"""Live Trend Rider (4H) and Turtle 55/20 (daily) on the live coin lists vs 23 Binance.US USD coins (Oct 8 2026,
Jeff: more trades, faster). Portfolio judged as a whole, both halves; 0.07%/side (0.02% fee + 0.05% slip), 0.5% risk.
4H and daily candles built from the Binance 1H archive for every coin. Fear filter not modeled."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import bot, engine as e, hourly as hr, long_history as lh  # noqa: E402

TR6 = ["BTC", "ETH", "SOL", "BNB", "SUI", "TRX"]
TU5 = ["BTC", "ETH", "SOL", "XRP", "BNB"]
ALL = "BTC ETH SOL XRP BNB ADA DOGE AVAX LINK LTC DOT XLM BCH HBAR NEAR UNI ATOM SHIB TRX SUI AAVE ETC ALGO".split()
COST = 0.0007
data = {}
for c in ALL:
    b4 = hr.to_4h(hr.hourly(c))
    data[c] = (b4, lh.to_daily(b4))
daily = {c: (data[c][1], data[c][1]) for c in ALL}


def tr(coins, mo):
    atrs = {}
    def ent(coin, bars, d):
        a = bot.analyse_tr(bars, d, 5); atrs[id(bars)] = a["atr"]
        return [{"stop": a["info"][i]["sl"]} if a["signal"][i] else None for i in range(len(bars))]
    def man(p, bars, k):
        x = atrs[id(bars)][k]; p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * x if x is not None else None
    return lambda t0, t1: e.trade_sim(coins, data, ent, t0, t1, risk=0.005, max_open=mo, fee=COST, manage=man)


def turtle(coins, mo):
    tr_ = {}
    def ent(coin, bars, d):
        a = bot.analyse_donchian(bars, {"entry": 55, "exit": 20}); tr_[id(bars)] = a["trail"]
        return [{"stop": a["info"][i]["sl"]} if a["signal"][i] else None for i in range(len(bars))]
    def man(p, bars, k):
        return tr_[id(bars)][k]
    return lambda t0, t1: e.trade_sim(coins, daily, ent, t0, t1, risk=0.005, max_open=mo, fee=COST, manage=man)


print("| Bot | Coins | Max open | 2018-now | 1st half | 2nd half (2022-now) | Trades/week (2022-now) |\n|---|---|---|---|---|---|---|")
for name, fn, sets in (("Trend Rider 4H", tr, [(TR6, 3), (ALL, 3), (ALL, 6)]), ("Turtle 55/20", turtle, [(TU5, 5), (ALL, 5), (ALL, 10)])):
    for coins, mo in sets:
        sim = fn(coins, mo)
        rs = [sim(a, b) for a, b in [(e.START, None)] + [(h[1], h[2]) for h in e.HALVES]]
        wk = (e.now() - e.CUT).days / 7
        cell = lambda r: f"{r['ret']:+.0f}% / {r['dd']:.1f}% / PF {r['pf']:.2f}"
        print(f"| {name} | {len(coins)} | {mo} | {cell(rs[0])} | {cell(rs[1])} | {cell(rs[2])} | {rs[2]['trades'] / wk:.1f} |", flush=True)
