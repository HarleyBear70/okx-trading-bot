"""
Strategy cards (job 5 / D2), shown on the same page as the P/L calendar (CALENDAR.md). Rebuilt every hour by
pl_calendar.py. NEVER trades.

One card per bot: status (demo / paper / paused / live), market + timeframe, and a chart with two lines since the
bot started:
  - live:     the bot's real balance (demo fills or paper fills) from trades.csv, plus open trades valued now
  - backtest: the SAME bot.py code replayed on the same candles since the start (paper, in memory only)
The gap between the two lines is slippage / timing / settings changes. Under the chart: win %, PF, max DD and
trades, long-run backtest (research) vs live.
"""

import csv
import datetime as dt
import json
import os
import sys

import bot

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "research"))
OUT = os.path.join(HERE, "calendars", "cards")
# when each bot started trading with roughly its current rules (journal/changes.json has the details)
START = {"v4-okx": "2026-10-04", "v4-kraken": "2026-10-04", "v2-okx": "2026-10-04", "v2-gold": "2026-10-04",
         "tr-okx": "2026-10-04", "tr-gold": "2026-10-04", "b1-paper": "2026-10-05", "b3-paper": "2026-10-05",
         "nnfx-paper": "2026-10-05", "nnfx-okx": "2026-10-06"}
W, H, PADL, PADR, PADT, PADB = 330, 130, 44, 10, 12, 22
# The three piles (job 4). RANGE is empty: no range bot has passed (research/N1_RANGE.md).
PILES = [("ACTIVE (trading, OKX demo)", ["tr-okx", "nnfx-okx"]),
         ("INCUBATING (paper forward tests)", ["b3-paper"]),
         ("RANGE", []),
         ("PAUSED", ["v4-okx", "v4-kraken", "b1-paper", "nnfx-paper", "v2-okx", "v2-gold", "tr-gold"])]


def expected():
    try:
        import scout
        return scout.EXPECTED
    except Exception:
        return {}


def status(b):
    if b.get("new_trades") is False:
        return "PAUSED"
    return {"demo": "DEMO", "paper": "PAPER", "live": "LIVE"}.get(b["mode"], b["mode"].upper())


def start_ms(b):
    return int(dt.datetime.fromisoformat(START.get(b["id"], "2026-10-05")).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def live_curve(b, rows, now_mtm):
    pts = [(start_ms(b), b["equity"])]
    for r in rows:
        if r["bot"] == b["name"] and r["side"] == "sell" and r.get("bot_balance"):
            t = dt.datetime.strptime(r["time_utc"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
            pts.append((int(t.timestamp() * 1000), float(r["bot_balance"])))
    if now_mtm is not None:
        pts.append((int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000), now_mtm))
    return pts


def replay(api, b, t0):
    """Run this bot's own code over the candles since t0, paper and in memory only. Returns (curve, closed P/Ls)."""
    pb = {**b, "mode": "paper"}  # never place an order
    bs = {"equity": b["equity"], "positions": {}, "last_bar": {}}
    pnls, cur = [], {}

    def log_trade(_b, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
        if side == "buy":
            cur[coin] = 0.0
        else:
            cur[coin] = cur.get(coin, 0.0) + (pnl or 0.0)
            if reason != "half profit +2R" and coin in cur:
                pnls.append(cur.pop(coin))
    o_lt, o_log, o_sweep = bot.log_trade, bot.log, bot.SWEEP["on"]
    bot.log_trade, bot.log, bot.SWEEP["on"] = log_trade, (lambda *a: None), False
    try:
        per = {}
        for coin in b["coins"]:
            tf, bars, forming, a = bot.analyse_for(api, pb, coin)
            per[coin] = (bars, a, {x["ts"]: k for k, x in enumerate(bars)})
        times = sorted({x["ts"] for bars, _, _ in per.values() for x in bars if x["ts"] >= t0})
        entry_k, curve = {}, []
        for ts in times:
            for coin, (bars, a, idx) in per.items():
                k = idx.get(ts)
                if k is None:
                    continue
                x = bars[k]
                if coin in bs["positions"] and x["ts"] > bs["positions"][coin]["entry_ts"]:
                    if not bot.check_hit(None, pb, bs, coin, x):
                        bot.manage_on_close(None, pb, bs, coin, a, k, x, k - entry_k[coin])
                if (coin not in bs["positions"] and a["signal"][k] and pb.get("new_trades", True)
                        and not bot.fear_blocks(pb, x)):
                    bot.open_position(None, pb, bs, coin, x, a["info"][k], bot.entry_extra(pb, x, a["info"][k]))
                    entry_k[coin] = k
            mtm = bs["equity"]
            for coin, p in bs["positions"].items():
                bars, _, idx = per[coin]
                k = idx.get(ts)
                if k is not None:
                    mtm += p["qty"] * bars[k]["c"] * (1 - bot.FEE) - p["cost"]
            curve.append((ts + {"1H": 3600000, "4H": bot.H4_MS, "1D": 86400000}[bot.bot_tf(pb)], mtm))
    finally:
        bot.log_trade, bot.log, bot.SWEEP["on"] = o_lt, o_log, o_sweep
    return [(t0, b["equity"])] + curve, pnls


def stats(pnls, curve):
    won, lost = sum(p for p in pnls if p > 0), -sum(p for p in pnls if p < 0)
    peak, dd = None, 0.0
    for _, v in curve:
        peak = v if peak is None else max(peak, v)
        dd = min(dd, v / peak - 1)
    return {"n": len(pnls), "win": (sum(p > 0 for p in pnls) / len(pnls) * 100) if pnls else None,
            "pf": (won / lost if lost else (float("inf") if won else None)), "dd": dd * 100}


def chart(live, back, path, labels=("live", "backtest replay")):
    pts = live + back
    t0, t1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lo, hi = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = max((hi - lo) * 0.15, 2.0)
    lo, hi = lo - pad, hi + pad
    t1 = t1 if t1 > t0 else t0 + 1

    def xy(t, v):
        return (PADL + (t - t0) / (t1 - t0) * (W - PADL - PADR), PADT + (hi - v) / (hi - lo) * (H - PADT - PADB))

    def line(series, style):
        if len(series) == 1:
            series = series + [(t1, series[0][1])]
        return f'<polyline fill="none" {style} points="' + " ".join("%.1f,%.1f" % xy(t, v) for t, v in series) + '"/>'
    el = [f'<rect width="{W}" height="{H}" fill="#ffffff" rx="6"/>',
          f'<line x1="{PADL}" y1="{H - PADB}" x2="{W - PADR}" y2="{H - PADB}" stroke="#dee2e6"/>']
    for v in (lo + pad, hi - pad):
        y = xy(t0, v)[1]
        el.append(f'<text x="{PADL - 4}" y="{y + 3}" text-anchor="end" font-size="9" fill="#868e96">{v:,.0f}</text>')
        el.append(f'<line x1="{PADL}" y1="{y}" x2="{W - PADR}" y2="{y}" stroke="#f1f3f5"/>')
    el.append(line(back, 'stroke="#adb5bd" stroke-width="2" stroke-dasharray="5,4"'))
    el.append(line(live, 'stroke="#1971c2" stroke-width="2.5"'))
    d0 = dt.datetime.fromtimestamp(t0 / 1000, dt.timezone.utc).strftime("%b %d")
    d1 = dt.datetime.fromtimestamp(t1 / 1000, dt.timezone.utc).strftime("%b %d")
    el.append(f'<text x="{PADL}" y="{H - 7}" font-size="9" fill="#868e96">{d0}</text>')
    el.append(f'<text x="{W - PADR}" y="{H - 7}" font-size="9" fill="#868e96" text-anchor="end">{d1}</text>')
    el.append(f'<text x="{W - PADR}" y="{PADT + 2}" font-size="9" text-anchor="end"><tspan fill="#1971c2">━ {labels[0]}</tspan>'
              f'<tspan fill="#868e96">  ┅ {labels[1]}</tspan></text>')
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
                f'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">' + "".join(el) + "</svg>")


def fmt(x, f):
    if x is None:
        return "-"
    return "inf" if x == float("inf") else f.format(x)


def summed(curves):
    """Add step curves (each held flat between its points) on the union of their times."""
    times = sorted({t for c in curves for t, _ in c})
    out = []
    for t in times:
        tot = 0.0
        for c in curves:
            v = c[0][1]
            for tt, vv in c:
                if tt <= t:
                    v = vv
                else:
                    break
            tot += v
        out.append((t, tot))
    return out


def hold_pile_lines(state, api):
    hp = state.get("hold") or {}
    paid = sum(hp.get("spent", {}).values())
    val = 0.0
    for coin, units in hp.get("units", {}).items():
        try:
            val += units * bot.get_data(api, "okx", coin, "1D")[0][-1]["c"]
        except Exception:
            pass
    return (f"HOLD (long-term, PAPER): weekly dip-DCA buyer, ${bot.DCA['weekly_usd']:g}/week into "
            f"{' + '.join(c.split('-')[0] for c in bot.DCA['coins'])}, double when 20%+ below the 200-day average. "
            f"Paid ${paid:,.2f}, worth ${val:,.2f}. Profit sweeper (25% of wins into this pile): "
            f"{'ON' if bot.SWEEP['on'] else 'OFF until real money'}. Buys: hold_pile.csv.")


def build(api, rows):
    """Markdown lines for the cards section (and the SVG charts)."""
    os.makedirs(OUT, exist_ok=True)
    exp = expected()
    try:  # full Fear & Greed history, so the replay never sees "unknown" for older days
        import urllib.request
        raw = json.loads(urllib.request.urlopen(bot.FNG_URL.replace("limit=10", "limit=0"), timeout=30).read())
        bot._fng["v"] = {bot.day_of(int(x["timestamp"]) * 1000): int(x["value"]) for x in raw["data"]}
    except Exception:
        pass
    try:
        with open(os.path.join(HERE, "journal", "trades.json")) as f:
            jtrades = json.load(f)
    except Exception:
        jtrades = []
    try:
        state = bot.load_state()
    except Exception:
        state = {"bots": {}}
    names = {b["id"]: b["name"] for b in bot.BOTS}
    piles = ["## The three piles", "", "- " + hold_pile_lines(state, api)]
    for title, ids in PILES:
        piles.append(f"- {title}: " + (", ".join(names[i] for i in ids if i in names) if ids else
                                       "none yet. No range bot has passed a test (research/N1_RANGE.md, B2), so this pile stays "
                                       "empty until one does."))
    piles.append("")
    out = ["## Strategy cards", "", "One card per bot. Chart: blue = the bot's real balance (demo or paper fills, open trades "
           "valued now); dashed grey = the same bot.py code replayed on the same candles since the start (the backtest "
           "engine). A gap between them = fills, timing, or a settings change during the period (see journal/changes.json). "
           "'Backtest' stats are the long-run research numbers (2022-now).", ""]
    demo_curves, paper_curves = [], []
    numbers = {}  # live vs replay per bot, saved for watcher.py
    for b in bot.BOTS:
        st = status(b)
        tf = {"1H": "1-hour", "4H": "4-hour", "1D": "daily"}[bot.bot_tf(b)]
        venue = "Kraken" if b["venue"] == "kraken" else "OKX"
        bs = state.get("bots", {}).get(b["id"], {"equity": b["equity"], "positions": {}})
        mtm, back, bpn, err = bs.get("equity", b["equity"]), None, [], None
        try:
            for coin, p in bs.get("positions", {}).items():
                px = bot.get_data(api, b["venue"], coin, bot.bot_tf(b))[0][-1]["c"]
                mtm += (p["qty"] * px * (1 - bot.FEE) - p["cost"]) * p.get("pnl_scale", 1.0)
            back, bpn = replay(api, b, start_ms(b))
        except Exception as ex:
            err = str(ex)[:120]
        live = live_curve(b, rows, mtm)
        if b.get("new_trades") is not False:
            (demo_curves if b["mode"] == "demo" else paper_curves).append(live)
        if back:
            chart(live, back, os.path.join(OUT, f"{b['id']}.svg"))
        closed = [t for t in jtrades if t.get("bot_id") == b["id"] and t.get("status") == "closed"]
        ls = stats([t.get("pnl") or 0.0 for t in closed], live)
        rs = stats(bpn, back or live)
        numbers[b["id"]] = {"live_now": mtm, "replay_now": back[-1][1] if back else None, "live": ls,
                            "replay": rs if back else None, "error": err}
        e = exp.get(b["id"])
        out += [f"### {b['name']}  ·  {st}", "",
                f"{venue} · {' '.join(c.split('-')[0] for c in b['coins'])} · {tf} candles · started {START.get(b['id'], '-')}"
                f" · balance now {mtm:,.2f}", ""]
        if back:
            out += [f"![{b['name']} live vs backtest](calendars/cards/{b['id']}.svg)", ""]
        elif err:
            out += [f"(chart unavailable this hour: {err})", ""]
        out += ["| | Trades | Win % | PF | Max DD |", "|---|---|---|---|---|",
                f"| Backtest, long run (research, 2022-now) | - | {fmt(e and e['win'], '{:.0f}%')} | "
                f"{fmt(e and e['pf'], '{:.2f}')} | {fmt(e and e['dd'], '{:.1f}%')} |",
                f"| Backtest replay since start | {rs['n']} | {fmt(rs['win'], '{:.0f}%')} | {fmt(rs['pf'], '{:.2f}')} | "
                f"{rs['dd']:.1f}% |",
                f"| Live ({st.lower()}) since start | {ls['n']} | {fmt(ls['win'], '{:.0f}%')} | {fmt(ls['pf'], '{:.2f}')} | "
                f"{ls['dd']:.1f}% |", ""]
    with open(os.path.join(OUT, "numbers.json"), "w") as f:
        json.dump({"updated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"), "bots": numbers}, f,
                  indent=1)
    growth = []
    if demo_curves and paper_curves:
        d = [(t, v / len(demo_curves)) for t, v in summed(demo_curves)]
        p = [(t, v / len(paper_curves)) for t, v in summed(paper_curves)]
        chart(d, p, os.path.join(OUT, "growth.svg"), labels=("demo (active)", "paper (incubating)"))
        growth = ["## Growth: demo vs paper", "", f"Average balance per bot, each bot starting at $1,000: the active demo bots "
                  f"({len(demo_curves)}, solid) vs the paper bots ({len(paper_curves)}, dashed). Demo now ${d[-1][1]:,.2f} "
                  f"({(d[-1][1] / 1000 - 1) * 100:+.2f}%), paper now ${p[-1][1]:,.2f} ({(p[-1][1] / 1000 - 1) * 100:+.2f}%).",
                  "", "![Demo vs paper growth](calendars/cards/growth.svg)", ""]
    return piles + growth + out
