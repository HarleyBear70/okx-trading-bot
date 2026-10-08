"""
BATTERY (Oct 8 2026, Jeff: "dca, grid, scalping, shorts, longs, buy and hold, 15 min, 1 hr, test them").

Markets
  crypto: BTC ETH SOL XRP BNB, Binance archive, cost 0.05% a side (Binance.US 0.02% fee + 0.03% slippage)
  forex : EUR GBP AUD NZD CAD CHF JPY vs USD + gold, OANDA Practice candles, cost = OANDA's real spread at the bar
Timeframes 15m and 1H, 2019-now; halves 2019-2022 / 2023-now. Entries fill at the NEXT candle's open.

Directional (0.5% risk a trade, one trade per instrument, each instrument its own $1,000, portfolio = equal mix;
leverage cap crypto 1x (spot), forex 20x):
  TR      Trend Rider both ways: break of the last swing + 50 EMA + higher-timeframe 50 EMA, 3 ATR trail
  DON     Donchian 20/10 breakout both ways, 2 ATR first stop
  SCALP   9/21 EMA cross with the 200 EMA, stop 1.5 ATR, target 1.5 ATR, max 16 candles
  RSI2    RSI(2) 5/95 snap-back both ways, 200 average filter, exit at the 5 average, 3 ATR stop
Non-directional (whole $1,000 per instrument):
  HOLD    buy and hold (crypto only)
  DCA     3Commas-style: base order + 5 safety orders (x1.5 size) every 2% (crypto) / 0.25% (forex, 5x lev),
          take profit 1.5% / 0.2% above the average price, no stop
  GRID    spot grid +/-15% (crypto) / +/-2% (forex, 5x lev), 20 levels, rebuilt (selling what it holds) when
          price closes outside the range

  python3 research/battery.py            (needs oanda_hist/ from the OANDA history workflow for forex)
"""
import datetime as dt
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import hourly as hr  # noqa: E402
import m15  # noqa: E402

UTC = dt.timezone.utc
START = dt.datetime(2019, 1, 1, tzinfo=UTC)
CUT = dt.datetime(2023, 1, 1, tzinfo=UTC)
CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB"]
FOREX = ["EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY", "XAU_USD"]
FXDIR = os.path.join(ROOT, "oanda_hist")
RISK = 0.005
MS = {"15m": 900000, "1H": 3600000}
HTF = {"15m": 4 * 3600000, "1H": 86400000}


def ms(d):
    return int(d.timestamp() * 1000)


# ───────── data ─────────
def load(market, inst, tf):
    if market == "crypto":
        raw = m15.m15(inst) if tf == "15m" else hr.hourly(inst)
        bars = [dict(b, sp=0.0) for b in raw if b["ts"] >= ms(START) - 60 * 86400000]
    else:
        with gzip.open(os.path.join(FXDIR, f"{inst}_{'M15' if tf == '15m' else 'H1'}.json.gz"), "rt") as f:
            bars = [{"ts": r[0], "o": r[1], "h": r[2], "l": r[3], "c": r[4], "sp": r[5], "v": r[6]} for r in json.load(f)]
    return bars


def cost(market, b, px):
    """cost per side, in price units"""
    return 0.0005 * px if market == "crypto" else b["sp"] / 2


# ───────── indicators ─────────
def ema(x, n):
    k, out, e = 2 / (n + 1), [], None
    for i, v in enumerate(x):
        e = v if e is None else e + k * (v - e)
        out.append(e if i >= n - 1 else None)
    return out


def sma(x, n):
    out, s = [], 0.0
    for i, v in enumerate(x):
        s += v
        if i >= n:
            s -= x[i - n]
        out.append(s / n if i >= n - 1 else None)
    return out


def atr(b, n=14):
    out, a = [], None
    for i, x in enumerate(b):
        tr = x["h"] - x["l"] if i == 0 else max(x["h"] - x["l"], abs(x["h"] - b[i - 1]["c"]), abs(x["l"] - b[i - 1]["c"]))
        a = tr if a is None else (a * (n - 1) + tr) / n
        out.append(a if i >= n else None)
    return out


def htf_trend(b, span):
    """+1 / -1 / 0 per bar: last COMPLETED higher-timeframe candle's close vs its 50 EMA."""
    groups = {}
    for x in b:
        k = x["ts"] - x["ts"] % span
        groups[k] = x["c"]  # last close in that period
    keys = sorted(groups)
    closes = [groups[k] for k in keys]
    e = ema(closes, 50)
    state = {k + span: (0 if e[i] is None else (1 if closes[i] > e[i] else -1)) for i, k in enumerate(keys)}
    # a period's state is known once its last bar has closed (or, across gaps, once the next period starts)
    cur, out, prev_key = 0, [], None
    for x in b:
        key = x["ts"] - x["ts"] % span
        if prev_key is not None and key != prev_key:
            cur = state.get(prev_key + span, cur)
        close_t = x["ts"] + MS_CUR[0]
        if close_t % span == 0:
            cur = state.get(close_t, cur)
        out.append(cur)
        prev_key = key
    return out


MS_CUR = [3600000]


# ───────── directional strategies: per bar None or (side, stop, target, max_bars, exit_fn, trail_fn) ─────────
def strat_tr(b, tf):
    h, l, c = [x["h"] for x in b], [x["l"] for x in b], [x["c"] for x in b]
    e50, a, ht = ema(c, 50), atr(b), htf_trend(b, HTF[tf])
    ph_l, pl_l = bot.pivots_ge(h, 5, True), bot.pivots_ge(l, 5, False)
    ph = pl = None
    out = [None] * len(b)
    for i in range(1, len(b)):
        if ph_l[i] is not None:
            ph = ph_l[i]
        if pl_l[i] is not None:
            pl = pl_l[i]
        if a[i] is None or e50[i] is None:
            continue
        if ph is not None and c[i] > ph >= c[i - 1] and c[i] > e50[i] and ht[i] == 1:
            s = pl * 0.998 if pl is not None else c[i] - 2 * a[i]
            out[i] = (1, min(max(s, c[i] - 3 * a[i]), c[i] - a[i]), None, None, None, "atr3")
        elif pl is not None and c[i] < pl <= c[i - 1] and c[i] < e50[i] and ht[i] == -1:
            s = ph * 1.002 if ph is not None else c[i] + 2 * a[i]
            out[i] = (-1, max(min(s, c[i] + 3 * a[i]), c[i] + a[i]), None, None, None, "atr3")
    return out, {"atr": a}


def strat_don(b, tf):
    h, l, c = [x["h"] for x in b], [x["l"] for x in b], [x["c"] for x in b]
    a = atr(b)
    out = [None] * len(b)
    lo10 = [None] * len(b)
    hi10 = [None] * len(b)
    for i in range(20, len(b)):
        hi20, lo20 = max(h[i - 20:i]), min(l[i - 20:i])
        lo10[i], hi10[i] = min(l[i - 10:i]), max(h[i - 10:i])
        if a[i] is None:
            continue
        if c[i] > hi20:
            out[i] = (1, c[i] - 2 * a[i], None, None, "don", None)
        elif c[i] < lo20:
            out[i] = (-1, c[i] + 2 * a[i], None, None, "don", None)
    return out, {"lo10": lo10, "hi10": hi10}


def strat_scalp(b, tf):
    c = [x["c"] for x in b]
    e9, e21, e200, a = ema(c, 9), ema(c, 21), ema(c, 200), atr(b)
    out = [None] * len(b)
    for i in range(1, len(b)):
        if None in (e9[i], e21[i], e200[i], a[i], e9[i - 1], e21[i - 1]):
            continue
        if e9[i] > e21[i] and e9[i - 1] <= e21[i - 1] and c[i] > e200[i]:
            out[i] = (1, c[i] - 1.5 * a[i], c[i] + 1.5 * a[i], 16, None, None)
        elif e9[i] < e21[i] and e9[i - 1] >= e21[i - 1] and c[i] < e200[i]:
            out[i] = (-1, c[i] + 1.5 * a[i], c[i] - 1.5 * a[i], 16, None, None)
    return out, {}


def strat_rsi2(b, tf):
    c = [x["c"] for x in b]
    s200, s5, a, r2 = sma(c, 200), sma(c, 5), atr(b, 20), bot.rsi(c, 2)
    out = [None] * len(b)
    for i in range(len(b)):
        if None in (s200[i], a[i], r2[i]):
            continue
        if c[i] > s200[i] and r2[i] < 5:
            out[i] = (1, c[i] - 3 * a[i], None, None, "sma5", None)
        elif c[i] < s200[i] and r2[i] > 95:
            out[i] = (-1, c[i] + 3 * a[i], None, None, "sma5", None)
    return out, {"s5": s5}


DIRECTIONAL = {"TR": strat_tr, "DON": strat_don, "SCALP": strat_scalp, "RSI2": strat_rsi2}


def run_dir(market, b, sigs, aux, lev):
    eq, pos, pend, trades, curve = 1000.0, None, None, [], []
    pend_exit = False
    t0 = ms(START)
    c = [x["c"] for x in b]
    for k, x in enumerate(b):
        if x["ts"] < t0:
            continue
        # 1) fills at the open
        if pos and pend_exit:
            eq += close_pnl(market, pos, x, x["o"])
            trades.append((pos["side"], pos["pnl"], pos["ts"]))
            pos, pend_exit = None, False
        if pend and not pos:
            side, stop, tgt_mult = pend
            px = x["o"]
            dist = (px - stop) * side
            if dist > 0:
                units = min(eq * RISK / dist, eq * lev / px)
                tgt = None if tgt_mult is None else px + side * tgt_mult * dist
                pos = {"side": side, "entry": px, "stop": stop, "tgt": tgt, "units": units, "k": k, "ts": x["ts"],
                       "best": px, "ec": cost(market, x, px), "pend_info": pend_info[0]}
        pend = None
        # 2) stop / target inside the candle (stop first)
        if pos:
            s = pos["side"]
            if (x["l"] <= pos["stop"]) if s == 1 else (x["h"] >= pos["stop"]):
                px = min(pos["stop"], x["o"]) if s == 1 else max(pos["stop"], x["o"])
                eq += close_pnl(market, pos, x, px)
                trades.append((s, pos["pnl"], pos["ts"]))
                pos = None
            elif pos["tgt"] and ((x["h"] >= pos["tgt"]) if s == 1 else (x["l"] <= pos["tgt"])):
                px = max(pos["tgt"], x["o"]) if s == 1 else min(pos["tgt"], x["o"])
                eq += close_pnl(market, pos, x, px)
                trades.append((s, pos["pnl"], pos["ts"]))
                pos = None
        # 3) at the close: exits, trail, new signals
        if pos:
            s, info = pos["side"], pos["pend_info"]
            pos["best"] = max(pos["best"], x["c"]) if s == 1 else min(pos["best"], x["c"])
            ex, mb, trail = info
            if mb and k - pos["k"] >= mb:
                pend_exit = True
            elif ex == "don" and ((x["c"] < aux["lo10"][k]) if s == 1 else (x["c"] > aux["hi10"][k])):
                pend_exit = True
            elif ex == "sma5" and aux["s5"][k] and ((x["c"] > aux["s5"][k]) if s == 1 else (x["c"] < aux["s5"][k])):
                pend_exit = True
            if trail == "atr3" and aux["atr"][k]:
                t = pos["best"] - s * 3 * aux["atr"][k]
                pos["stop"] = max(pos["stop"], t) if s == 1 else min(pos["stop"], t)
        elif sigs[k]:
            side, stop, tgt, mb, ex, trail = sigs[k]
            dist = abs(x["c"] - stop)
            pend = (side, stop, None if tgt is None else abs(tgt - x["c"]) / dist)
            pend_info[0] = (ex, mb, trail)
        if k % DAYBARS[0] == 0:
            curve.append((x["ts"], eq + (open_pnl(market, pos, x) if pos else 0)))
    if pos:
        eq += close_pnl(market, pos, b[-1], b[-1]["c"])
        trades.append((pos["side"], pos["pnl"], pos["ts"]))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


pend_info = [None]
DAYBARS = [24]


def close_pnl(market, pos, x, px):
    s = pos["side"]
    pnl = s * (px - pos["entry"]) * pos["units"] - (pos["ec"] + cost(market, x, px)) * pos["units"]
    pos["pnl"] = pnl
    return pnl


def open_pnl(market, pos, x):
    return pos["side"] * (x["c"] - pos["entry"]) * pos["units"]


# ───────── non-directional ─────────
def run_hold(market, b):
    t0 = ms(START)
    b = [x for x in b if x["ts"] >= t0]
    p0 = b[0]["o"] * 1.0005
    units = 1000 / p0
    curve = [(x["ts"], units * x["c"]) for i, x in enumerate(b) if i % DAYBARS[0] == 0]
    curve.append((b[-1]["ts"], units * b[-1]["c"] * 0.9995))
    return [(1, curve[-1][1] - 1000, b[0]["ts"])], curve


def run_dca(market, b):
    step, tp, lev = (0.02, 0.015, 1.0) if market == "crypto" else (0.0025, 0.002, 5.0)
    sizes = [1, 1, 1.5, 2.25, 3.375, 5.0625]
    t0 = ms(START)
    eq, deal, trades, curve = 1000.0, None, [], []
    for i, x in enumerate(b):
        if x["ts"] < t0:
            continue
        if deal is None:
            unit = eq * lev / sum(sizes)
            px = x["o"]
            deal = {"fills": [(px, unit / px)], "base": px, "n": 1, "ts": x["ts"], "cost": cost(market, x, px) * unit / px}
        # walk the candle in a likely order (down candle: high first; up candle: low first)
        path = (x["l"], x["h"]) if x["c"] >= x["o"] else (x["h"], x["l"])
        closed = False
        for px_path in path:
            while deal["n"] < len(sizes) and px_path <= deal["base"] * (1 - step * deal["n"]):
                px = deal["base"] * (1 - step * deal["n"])
                q = unit * sizes[deal["n"]] / px
                deal["fills"].append((px, q))
                deal["cost"] += cost(market, x, px) * q
                deal["n"] += 1
            qty = sum(q for _, q in deal["fills"])
            avg = sum(p * q for p, q in deal["fills"]) / qty
            target = avg * (1 + tp)
            if px_path >= target:
                pnl = (target - avg) * qty - deal["cost"] - cost(market, x, target) * qty
                eq += pnl
                trades.append((1, pnl, deal["ts"]))
                deal, closed = None, True
                break
        if closed:
            curve_val = eq
        else:
            curve_val = eq + (x["c"] - avg) * qty - deal["cost"]
        if i % DAYBARS[0] == 0:
            curve.append((x["ts"], curve_val))
        if curve_val <= 0:
            curve.append((x["ts"], 0.0))
            trades.append((1, -eq, x["ts"]))
            return trades, curve
    if deal:
        qty = sum(q for _, q in deal["fills"])
        avg = sum(p * q for p, q in deal["fills"]) / qty
        pnl = (b[-1]["c"] - avg) * qty - deal["cost"]
        eq += pnl
        trades.append((1, pnl, deal["ts"]))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


def run_grid(market, b):
    w, lev, n = (0.15, 1.0, 20) if market == "crypto" else (0.02, 5.0, 20)
    t0 = ms(START)
    b = [x for x in b if x["ts"] >= t0]
    cash, trades, curve = 1000.0, [], []

    def build(px, eqv):
        levels = [px * (1 - w) * ((1 + w) / (1 - w)) ** (j / n) for j in range(n + 1)]
        per = eqv * lev / n
        slots = []
        for j in range(n):  # slot j: buy at levels[j], sell at levels[j+1]
            holding = levels[j + 1] > px  # sell orders above price start with inventory bought now
            q = per / levels[j]
            slots.append({"buy": levels[j], "sell": levels[j + 1], "q": q, "hold": holding, "paid": px if holding else None})
        return levels, slots, per

    def value(slots, px):
        return sum(s["q"] * px for s in slots if s["hold"])

    # leveraged grid: track P/L instead of cash
    pnl_total, eq = 0.0, 1000.0
    levels, slots, per = build(b[0]["o"], eq)
    for s in slots:
        if s["hold"]:
            pnl_total -= cost(market, b[0], b[0]["o"]) * s["q"]
    for i, x in enumerate(b):
        path = (x["l"], x["h"]) if x["c"] >= x["o"] else (x["h"], x["l"])
        for px in path:
            for s in slots:
                if not s["hold"] and px <= s["buy"]:
                    s["hold"], s["paid"] = True, s["buy"]
                    pnl_total -= cost(market, x, s["buy"]) * s["q"]
                elif s["hold"] and px >= s["sell"]:
                    g = (s["sell"] - s["paid"]) * s["q"] - cost(market, x, s["sell"]) * s["q"]
                    pnl_total += g
                    trades.append((1, g, x["ts"]))
                    s["hold"], s["paid"] = False, None
        unreal = sum((x["c"] - s["paid"]) * s["q"] for s in slots if s["hold"])
        eq = 1000.0 + pnl_total + unreal
        if eq <= 0:
            curve.append((x["ts"], 0.0))
            return trades, curve
        if x["c"] < levels[0] or x["c"] > levels[-1]:  # out of range: sell everything, rebuild around price
            for s in slots:
                if s["hold"]:
                    g = (x["c"] - s["paid"]) * s["q"] - cost(market, x, x["c"]) * s["q"]
                    pnl_total += g
                    trades.append((1, g, x["ts"]))
            levels, slots, per = build(x["c"], eq)
            for s in slots:
                if s["hold"]:
                    s["paid"] = x["c"]
                    pnl_total -= cost(market, x, x["c"]) * s["q"]
        if i % DAYBARS[0] == 0:
            curve.append((x["ts"], eq))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


# ───────── stats ─────────
def mix(curves):
    """equal-weight portfolio of $1,000 curves, by day"""
    days = {}
    for cv in curves:
        last = {}
        for t, v in cv:
            last[t - t % 86400000] = v
        days_c = sorted(last)
        for d in days_c:
            days.setdefault(d, [])
    allday = sorted(days)
    port = []
    vals = []
    for cv in curves:
        m = {}
        for t, v in cv:
            m[t - t % 86400000] = v
        cur, row = 1000.0, []
        for d in allday:
            cur = m.get(d, cur)
            row.append(cur)
        vals.append(row)
    for j, d in enumerate(allday):
        port.append((d, sum(r[j] for r in vals) / len(vals)))
    return port


def summarize(trades, port, t0, t1):
    a, z = ms(t0), ms(t1) if t1 else 1 << 62
    seg = [(t, v) for t, v in port if a <= t < z]
    if len(seg) < 2:
        return None
    base = seg[0][1]
    peak, dd = base, 0.0
    for _, v in seg:
        peak, dd = max(peak, v), min(dd, v / peak - 1)
    tr = [p for s, p, t in trades if a <= t < z]
    won, lost = sum(p for p in tr if p > 0), -sum(p for p in tr if p < 0)
    weeks = (seg[-1][0] - seg[0][0]) / 604800000
    return {"ret": 100 * (seg[-1][1] / base - 1), "dd": 100 * dd, "pf": won / lost if lost else 99.0,
            "win": 100 * sum(p > 0 for p in tr) / len(tr) if tr else 0, "tpw": len(tr) / max(weeks, 1),
            "long_pf": side_pf(trades, 1, a, z), "short_pf": side_pf(trades, -1, a, z)}


def side_pf(trades, side, a, z):
    tr = [p for s, p, t in trades if s == side and a <= t < z]
    won, lost = sum(p for p in tr if p > 0), -sum(p for p in tr if p < 0)
    return None if not tr else (won / lost if lost else 99.0)


def cell(s):
    if s is None:
        return "-"
    return f"{s['ret']:+.0f}% / {s['dd']:.0f}% / PF {s['pf']:.2f}"


def main():
    markets = ["crypto"] + (["forex"] if os.path.isdir(FXDIR) else [])
    rows = []
    print("| Market | Chart | Strategy | 2019-now (return / worst drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for market in markets:
        insts = CRYPTO if market == "crypto" else FOREX
        lev = 1.0 if market == "crypto" else 20.0
        for tf in ("1H", "15m"):
            MS_CUR[0] = MS[tf]
            DAYBARS[0] = 86400000 // MS[tf]
            data = {i: load(market, i, tf) for i in insts}
            names = list(DIRECTIONAL) + (["HOLD"] if market == "crypto" else []) + ["DCA", "GRID"]
            for name in names:
                all_tr, curves = [], []
                for i in insts:
                    b = data[i]
                    if name in DIRECTIONAL:
                        sig, aux = DIRECTIONAL[name](b, tf)
                        tr, cv = run_dir(market, b, sig, aux, lev)
                    elif name == "HOLD":
                        tr, cv = run_hold(market, b)
                    elif name == "DCA":
                        tr, cv = run_dca(market, b)
                    else:
                        tr, cv = run_grid(market, b)
                    all_tr += tr
                    curves.append(cv)
                port = mix(curves)
                full, h1, h2 = (summarize(all_tr, port, a, z) for a, z in ((START, None), (START, CUT), (CUT, None)))
                lp = "-" if full["long_pf"] is None else f"{full['long_pf']:.2f}"
                sp = "-" if full["short_pf"] is None else f"{full['short_pf']:.2f}"
                line = (f"| {market} | {tf} | {name} | {cell(full)} | {cell(h1)} | {cell(h2)} | {full['win']:.0f}% | "
                        f"{full['tpw']:.1f} | {lp} | {sp} |")
                print(line, flush=True)
                rows.append({"market": market, "tf": tf, "name": name, "full": full, "h1": h1, "h2": h2})
    json.dump(rows, open(os.path.join(HERE, "battery.json"), "w"))


if __name__ == "__main__":
    main()
