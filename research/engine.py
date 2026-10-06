"""
Shared research engine for the new bots (N1-N4) and the portfolio checks.

- bot_sim(): bot.py's own strategies (v4, Trend Rider) on several coins with one shared balance, like
  research/score_test.py's simulator but for any strategy, and it also returns the equity curve.
- trade_sim(): a plain simulator for new bots. Each coin gives, per candle, either None or an entry
  {"stop", "target", "max_bars"}; entries fill at the candle close, stops / targets are checked on later
  candles (gaps fill at the open), sizing is bot.py's (risk % of balance from the stop, capped by free cash),
  fees each side, max open trades shared.
- curves -> monthly returns, correlation, and combined portfolios with fixed capital weights.
"""
import datetime as dt
import math
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import long_history as lh  # noqa: E402

UTC = dt.timezone.utc
CUT = dt.datetime(2022, 1, 1, tzinfo=UTC)
START = dt.datetime(2018, 5, 1, tzinfo=UTC)
DESIGN = ["BTC", "ETH", "XRP"]
UNSEEN = ["SOL", "LTC", "DOGE", "XLM", "ADA", "BNB", "LINK", "BCH", "AVAX", "SUI", "LUNA", "FTT"]
TR_COINS = ["BTC", "ETH", "SOL", "BNB", "SUI"]
HALVES = [("1st half", START, CUT), ("2nd half", CUT, None)]


def now():
    return dt.datetime.now(UTC)


def ms(x):
    return int(x.timestamp() * 1000)


def load(coins):
    return {c: lh.load(c) for c in coins}


# ───────── indicators ─────────
def adx(h, l, c, n=14):
    """Wilder's ADX."""
    size = len(c)
    pdm, ndm, tr = [0.0] * size, [0.0] * size, [0.0] * size
    for i in range(1, size):
        up, dn = h[i] - h[i - 1], l[i - 1] - l[i]
        pdm[i] = up if up > dn and up > 0 else 0.0
        ndm[i] = dn if dn > up and dn > 0 else 0.0
        tr[i] = max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
    atr_, p, m = bot.rma(tr[1:], n), bot.rma(pdm[1:], n), bot.rma(ndm[1:], n)
    dx = [None]
    for a, pp, mm in zip(atr_, p, m):
        if a is None or pp is None or mm is None:
            dx.append(None)
            continue
        if a == 0:  # flat filled-in candles
            dx.append(0.0)
            continue
        pdi, ndi = 100 * pp / a, 100 * mm / a
        dx.append(100 * abs(pdi - ndi) / (pdi + ndi) if pdi + ndi else 0.0)
    first = next((i for i, x in enumerate(dx) if x is not None), size)
    out = [None] * first + bot.rma(dx[first:], n)
    return out[:size]


# ───────── simulators ─────────
def _stats(trades, curve, eq_end):
    won = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    lost = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    peak, dd = 1000.0, 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return {"trades": len(trades), "win": sum(t["pnl"] > 0 for t in trades) / len(trades) * 100 if trades else 0.0,
            "ret": eq_end / 10 - 100, "dd": dd * 100, "pf": won / lost if lost else (float("inf") if won else 0.0),
            "won": won, "lost": lost, "pnl": eq_end - 1000, "list": trades, "curve": curve}


def bot_sim(strat, coins, data, analyse, t0, t1=None, extra=None, settings=None):
    """bot.py's strategy `strat` ("v4", "v2", "tr") on `coins`, one shared $1,000, bar by bar.
    settings: per-bot keys from bot.BOTS ("risk", "half_at_2r") to test a bot with its live settings."""
    t1 = t1 or now()
    b = {"id": "sim", "name": "sim", "strat": strat, "venue": "okx", "mode": "paper", "coins": coins, "equity": 1000.0,
         **(settings or {})}
    bs = {"equity": 1000.0, "positions": {}, "last_bar": {}}
    trades, open_id = [], {}

    def log_trade(_bot, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
        if side == "buy" and coin in open_id and str(reason).startswith("add-on"):
            pass  # pyramid add-on: same trade
        elif side == "buy":
            open_id[coin] = len(trades)
            trades.append({"coin": coin, "pnl": 0.0})
        else:
            trades[open_id[coin]]["pnl"] += pnl
    o_lt, o_log = bot.log_trade, bot.log
    bot.log_trade, bot.log = log_trade, lambda *a: None
    try:
        per = {}
        for c in coins:
            bars, daily = data[c]
            per[c] = (bars, analyse(bars, daily), {x["ts"]: k for k, x in enumerate(bars)})
        times = sorted({x["ts"] for bars, _, _ in per.values() for x in bars if ms(t0) <= x["ts"] < ms(t1)})
        curve, entry_k = [], {}
        for ts in times:
            for c in coins:
                bars, a, idx = per[c]
                k = idx.get(ts)
                if k is None:
                    continue
                x = bars[k]
                if c in bs["positions"] and x["ts"] > bs["positions"][c]["entry_ts"]:
                    if not bot.check_hit(None, b, bs, c, x):
                        bot.manage_on_close(None, b, bs, c, a, k, x, k - entry_k[c])
                if c not in bs["positions"] and a["signal"][k]:
                    bot.open_position(None, b, bs, c, x, a["info"][k],
                                      extra(x) if extra else bot.entry_extra(b, x, a["info"][k]))
                    entry_k[c] = k
            mtm = bs["equity"]
            for c, p in bs["positions"].items():
                bars, _, idx = per[c]
                k = idx.get(ts)
                px = bars[k]["c"] if k is not None else p["entry_px"]
                mtm += (p["qty"] * px * (1 - bot.FEE) - p["cost"]) * p.get("pnl_scale", 1.0)
            curve.append((ts, mtm))
        for c in list(bs["positions"]):
            bars, _, _ = per[c]
            last = max(k for k, x in enumerate(bars) if x["ts"] < ms(t1))
            bot.close_position(None, b, bs, c, "end of test", bars[last]["c"])
    finally:
        bot.log_trade, bot.log = o_lt, o_log
    return _stats(trades, curve, bs["equity"])


def v4_sim(data, t0, t1=None, coins=DESIGN):
    return bot_sim("v4", coins, data, lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), t0, t1)


def tr_sim(data, t0, t1=None, coins=TR_COINS):
    return bot_sim("tr", coins, data, lambda b, d: bot.analyse_tr(b, d, 5), t0, t1, extra=lambda x: {"hi": x["c"]})


def trade_sim(coins, data, entries_fn, t0, t1=None, risk=None, max_open=3, fee=None, manage=None, cooldown=0):
    """New-bot simulator. entries_fn(coin, bars, daily) -> list (per candle) of None or
    {"stop": px, "target": px or None, "max_bars": n or None, "side": 1 (long, default) or -1 (short)}.
    manage(pos, bars, k) may return a new stop (only ever tightened), or "exit" to close at this candle's close.
    An entry's optional "tag" is kept on the position (pos["tag"])."""
    t1, risk, fee = t1 or now(), risk or bot.RISK_PCT, bot.FEE if fee is None else fee
    per = {}
    for c in coins:
        bars, daily = data[c]
        per[c] = (bars, entries_fn(c, bars, daily), {x["ts"]: k for k, x in enumerate(bars)})
    times = sorted({x["ts"] for bars, _, _ in per.values() for x in bars if ms(t0) <= x["ts"] < ms(t1)})
    eq, pos, trades, curve, last_exit = 1000.0, {}, [], [], {}

    def close(c, px, reason, k=None):
        nonlocal eq
        p = pos.pop(c)
        if k is not None:
            last_exit[c] = k
        if p["side"] == 1:
            pnl = p["qty"] * px * (1 - fee) - p["cost"]
        else:
            pnl = p["qty"] * p["entry"] * (1 - fee) - p["qty"] * px * (1 + fee)
        eq += pnl
        trades.append({"coin": c, "pnl": pnl, "entry_ts": p["ts"], "reason": reason})

    for ts in times:
        for c in coins:
            bars, ent, idx = per[c]
            k = idx.get(ts)
            if k is None:
                continue
            x = bars[k]
            if c in pos:
                p = pos[c]
                long_ = p["side"] == 1
                if (x["l"] <= p["stop"]) if long_ else (x["h"] >= p["stop"]):
                    close(c, min(p["stop"], x["o"]) if long_ else max(p["stop"], x["o"]), "stop", k)
                elif p["target"] and ((x["h"] >= p["target"]) if long_ else (x["l"] <= p["target"])):
                    close(c, max(p["target"], x["o"]) if long_ else min(p["target"], x["o"]), "target", k)
                elif p["max_bars"] and k - p["k"] >= p["max_bars"]:
                    close(c, x["c"], "time", k)
                elif manage:
                    new = manage(p, bars, k)
                    if new == "exit":
                        close(c, x["c"], "rule", k)
                    elif new is not None:
                        p["stop"] = max(p["stop"], new) if long_ else min(p["stop"], new)
            if (c not in pos and ent[k] and len(pos) < max_open
                    and (x["c"] - ent[k]["stop"]) * ent[k].get("side", 1) > 0
                    and (not cooldown or k - last_exit.get(c, -10 ** 9) > cooldown)):
                e = ent[k]
                in_use = sum(p["cost"] for p in pos.values())
                qty = min(eq * risk / abs(x["c"] - e["stop"]), max(eq - in_use, 0.0) / x["c"])
                if qty * x["c"] >= 5:
                    pos[c] = {"qty": qty, "cost": qty * x["c"] * (1 + fee), "stop": e["stop"], "target": e.get("target"),
                              "max_bars": e.get("max_bars"), "k": k, "ts": ts, "entry": x["c"], "hi": x["c"],
                              "lo": x["c"], "side": e.get("side", 1), "tag": e.get("tag")}
        mtm = eq
        for c, p in pos.items():
            bars, _, idx = per[c]
            k = idx.get(ts)
            px = bars[k]["c"] if k is not None else p["entry"]
            if p["side"] == 1:
                mtm += p["qty"] * px * (1 - fee) - p["cost"]
            else:
                mtm += p["qty"] * p["entry"] * (1 - fee) - p["qty"] * px * (1 + fee)
        curve.append((ts, mtm))
    for c in list(pos):
        bars, _, _ = per[c]
        last = max(k for k, x in enumerate(bars) if x["ts"] < ms(t1))
        close(c, bars[last]["c"], "end of test")
    return _stats(trades, curve, eq)


def unseen_pooled(sim_one, coins=UNSEEN, loader=None):
    """sim_one(coin, data, t0, t1) -> result. Each coin alone per job-2b period; pooled per half."""
    out = {h: {"won": 0.0, "lost": 0.0, "pnl": 0.0, "trades": 0, "worst": 0.0} for h in ("1st half", "2nd half")}
    for c in coins:
        data = (loader or load)([c])
        if not data.get(c) or not data[c][0]:
            continue
        bars = data[c][0]
        for p, t0, t1 in lh.PERIODS:
            t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC))
            t1 = t1 or now()
            if t0 >= t1 or bars[-1]["ts"] < ms(t0):
                continue
            r = sim_one(c, data, t0, t1)
            h = out["1st half" if t0 < CUT else "2nd half"]
            for key in ("won", "lost", "pnl", "trades"):
                h[key] += r[key]
            h["worst"] = min(h["worst"], r["dd"])
    for h in out.values():
        h["pf"] = h["won"] / h["lost"] if h["lost"] else (float("inf") if h["won"] else 0.0)
    return out


# ───────── portfolio maths ─────────
def monthly(curve):
    """{YYYY-MM: return} from a (ts, equity) curve."""
    last = {}
    for ts, v in curve:
        last[bot.ts_iso(ts)[:7]] = v
    months = sorted(last)
    out, prev = {}, curve[0][1] if curve else 1000.0
    for m in months:
        out[m] = last[m] / prev - 1
        prev = last[m]
    return out


def corr(a, b):
    keys = sorted(set(a) & set(b))
    if len(keys) < 3:
        return float("nan")
    x, y = [a[k] for k in keys], [b[k] for k in keys]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    sx = math.sqrt(sum((v - mx) ** 2 for v in x))
    sy = math.sqrt(sum((v - my) ** 2 for v in y))
    return sum((u - mx) * (v - my) for u, v in zip(x, y)) / (sx * sy) if sx and sy else float("nan")


def combine(curves, weights):
    """Fixed capital split, no rebalancing: each curve scaled to its weight of $1,000; returns a curve."""
    times = sorted({ts for cv in curves for ts, _ in cv})
    lookups = []
    for cv in curves:
        d = dict(cv)
        lookups.append((d, cv[0][1]))
    vals, last = [], [1000.0] * len(curves)
    for ts in times:
        tot = 0.0
        for j, (d, start) in enumerate(lookups):
            if ts in d:
                last[j] = d[ts]
            tot += weights[j] * 1000 * last[j] / start
        vals.append((ts, tot))
    return vals


def ret_dd(curve):
    peak, dd = curve[0][1], 0.0
    for _, v in curve:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    ret = curve[-1][1] / curve[0][1] - 1
    return ret * 100, dd * 100, (ret / -dd if dd else float("inf"))


# ───────── the common pass rules (research/NEWBOTS_PLAN.md) ─────────
_BASE = {}


def baseline():
    """v4 and Trend Rider curves, START to now (cached)."""
    if not _BASE:
        _BASE["v4"] = v4_sim(load(DESIGN), START)["curve"]
        _BASE["tr"] = tr_sim(load(TR_COINS), START)["curve"]
        _BASE["mix"] = combine([_BASE["v4"], _BASE["tr"]], [0.5, 0.5])
    return _BASE


def evaluate(variants, loader=None):
    """variants: {name: (design_sim(data, t0, t1), unseen_one(coin, data, t0, t1))}.
    Returns (rows for a table, verdict lines, best passing name or None)."""
    base = baseline()
    b_ret, b_dd, b_rd = ret_dd(base["mix"])
    data = (loader or load)(DESIGN)
    rows = ["| Variant | Half | Trades | Win % | Return | Max DD | PF | Never-seen trades | Never-seen PF | "
            "Never-seen worst DD |", "|---|---|---|---|---|---|---|---|---|---|"]
    verdicts, best = [], (None, 0.0)
    for name, (design_sim, unseen_one) in variants.items():
        why = []
        halves = {h: design_sim(data, t0, t1) for h, t0, t1 in HALVES}
        un = unseen_pooled(unseen_one, loader=loader)
        for h in halves:
            r, u = halves[h], un[h]
            rows.append(f"| {name} | {h} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}% | "
                        f"{r['pf']:.2f} | {u['trades']} | {u['pf']:.2f} | {u['worst']:.1f}% |")
            if not (r["pf"] > 1.0 and r["pnl"] > 0):
                why.append(f"design {h} not profitable (PF {r['pf']:.2f}, {r['ret']:+.1f}%)")
            if r["dd"] < -10:
                why.append(f"design {h} DD {r['dd']:.1f}%")
            if not u["pf"] > 1.0:
                why.append(f"never-seen {h} PF {u['pf']:.2f}")
        full = design_sim(data, START, None)
        cr = corr(monthly(full["curve"]), monthly(base["mix"]))
        n_ret, n_dd, n_rd = ret_dd(combine([base["v4"], base["tr"], full["curve"]], [1 / 3] * 3))
        verdicts.append(f"- {name}: correlation with v4+TR {cr:.2f}; portfolio return/DD {n_rd:.2f} "
                        f"({n_ret:+.0f}% / {n_dd:.1f}%) vs v4+TR {b_rd:.2f} ({b_ret:+.0f}% / {b_dd:.1f}%); "
                        f"own full period {full['ret']:+.1f}% / DD {full['dd']:.1f}% / PF {full['pf']:.2f}")
        if not cr < 0.5:
            why.append(f"correlation {cr:.2f}")
        if not n_rd > b_rd:
            why.append(f"portfolio return/DD {n_rd:.2f} not above {b_rd:.2f}")
        verdicts.append(f"  {'PASS' if not why else 'fail: ' + '; '.join(why)}")
        if not why and n_rd - b_rd > best[1]:
            best = (name, n_rd - b_rd)
        print(f"done {name}", flush=True)
    return rows, verdicts, best[0]


# ───────── several bot.py bots stepped together (helper-bot tests) ─────────
def multi_sim(specs, t0, t1=None, on_bar=None, risk_mult=None):
    """specs: [(name, strat, coins, data, analyse, extra)], each bot with its own $1,000, bar by bar on one
    shared timeline, using bot.py's own functions.
    on_bar(ctx) is called after every timestamp with ctx = {"ts", "mtm": {name: balance}, "combined"};
    risk_mult(ctx, name, coin, bars, k) -> multiplier on bot.py's risk for that new trade (default 1).
    Returns {"bots": {name: stats}, "combined": curve}."""
    t1 = t1 or now()
    states, per, trades = {}, {}, {}
    for name, strat, coins, data, analyse, extra in specs:
        states[name] = ({"id": name, "name": name, "strat": strat, "venue": "okx", "mode": "paper", "coins": coins,
                         "equity": 1000.0}, {"equity": 1000.0, "positions": {}, "last_bar": {}}, extra)
        per[name] = {}
        for c in coins:
            bars, daily = data[c]
            per[name][c] = (bars, analyse(bars, daily), {x["ts"]: k for k, x in enumerate(bars)})
        trades[name] = []
    cur = {"bot": None, "m": 1.0}
    open_id = {}

    def log_trade(_bot, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
        key = (_bot["name"], coin)
        if side == "buy":
            open_id[key] = len(trades[_bot["name"]])
            trades[_bot["name"]].append({"coin": coin, "pnl": 0.0})
        else:
            trades[_bot["name"]][open_id[key]]["pnl"] += pnl
    o_lt, o_log, o_risk = bot.log_trade, bot.log, bot.risk_pct
    bot.log_trade, bot.log = log_trade, lambda *a: None
    bot.risk_pct = lambda b, bs: bot.RISK_PCT * cur["m"]
    times = sorted({x["ts"] for name in per for bars, _, _ in per[name].values() for x in bars
                    if ms(t0) <= x["ts"] < ms(t1)})
    curves = {name: [] for name in per}
    combined, entry_k = [], {}
    ctx = {"ts": None, "mtm": {name: 1000.0 for name in per}, "combined": 2000.0 if len(per) == 2 else 1000.0 * len(per)}
    try:
        for ts in times:
            ctx["ts"] = ts
            for name, (b, bs, extra) in states.items():
                for c in b["coins"]:
                    bars, a, idx = per[name][c]
                    k = idx.get(ts)
                    if k is None:
                        continue
                    x = bars[k]
                    if c in bs["positions"] and x["ts"] > bs["positions"][c]["entry_ts"]:
                        if not bot.check_hit(None, b, bs, c, x):
                            bot.manage_on_close(None, b, bs, c, a, k, x, k - entry_k[(name, c)])
                    if c not in bs["positions"] and a["signal"][k]:
                        cur["m"] = risk_mult(ctx, name, c, bars, k) if risk_mult else 1.0
                        bot.open_position(None, b, bs, c, x, a["info"][k], (extra or (lambda x: {}))(x))
                        cur["m"] = 1.0
                        entry_k[(name, c)] = k
            tot = 0.0
            for name, (b, bs, extra) in states.items():
                mtm = bs["equity"]
                for c, p in bs["positions"].items():
                    bars, _, idx = per[name][c]
                    k = idx.get(ts)
                    px = bars[k]["c"] if k is not None else p["entry_px"]
                    mtm += (p["qty"] * px * (1 - bot.FEE) - p["cost"]) * p.get("pnl_scale", 1.0)
                curves[name].append((ts, mtm))
                ctx["mtm"][name] = mtm
                tot += mtm
            ctx["combined"] = tot
            combined.append((ts, tot))
            if on_bar:
                on_bar(ctx)
        for name, (b, bs, extra) in states.items():
            for c in list(bs["positions"]):
                bars, _, _ = per[name][c]
                last = max(k for k, x in enumerate(bars) if x["ts"] < ms(t1))
                bot.close_position(None, b, bs, c, "end of test", bars[last]["c"])
    finally:
        bot.log_trade, bot.log, bot.risk_pct = o_lt, o_log, o_risk
    return {"bots": {name: _stats(trades[name], curves[name], states[name][1]["equity"]) for name in states},
            "combined": combined}


def demo_specs():
    """v4 and Trend Rider as they trade now (coins from bot.py)."""
    v4c = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "v4-okx")["coins"]]
    trc = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
    return [("v4", "v4", v4c, load(v4c), lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), None),
            ("tr", "tr", trc, load(trc), lambda b, d: bot.analyse_tr(b, d, 5), lambda x: {"hi": x["c"]})]
