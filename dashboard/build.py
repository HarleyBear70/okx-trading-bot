"""
One-page bot dashboard: every bot, balance, wins / losses, P/L, coins, open trades, full trade history, and an
equity chart per bot that shows the backtest years first and the demo (and later real-money) results after it.

Reads the files the hourly run already writes (journal/*.json, trades.csv, state.json, calendars/cards/numbers.json,
hold_pile.csv) plus dashboard/backtest.json, and writes one self-contained page: dashboard/index.html.
Read-only: it never trades and never changes a bot.

Run:
  python dashboard/build.py
"""
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import cards  # noqa: E402

PILE = {bid: name.split(" ")[0] for name, ids in cards.PILES for bid in ids}  # ACTIVE / HOLD / INCUBATING / RETIRED
REAL_FEE = 0.0035  # what OKX really charges per buy / sell (spot Lv1 market orders); paper bots log bot.FEE
STOP_DD = 10.0  # scoreboard rule 3: stop any bot 10% below its best balance
VERDICT_AT = 30  # scoreboard rule 1: no verdict before about 30 closed trades


def load(path, default):
    try:
        with open(os.path.join(ROOT, path)) as f:
            return json.load(f)
    except Exception:
        return default


def rows(path):
    try:
        with open(os.path.join(ROOT, path), newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def clean(x):
    """JSON-safe numbers (Infinity / NaN become None)."""
    if isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))):
        return None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [clean(v) for v in x]
    return x


def max_dd(points):
    peak, dd = None, 0.0
    for _, v in points:
        peak = v if peak is None else max(peak, v)
        dd = min(dd, (v / peak - 1) * 100)
    return dd


def real_fees(trades, fee_for):
    """Paper trades are logged with bot.FEE (0.1%). Re-price them at REAL_FEE so every bot is on the user's real cost.
    Demo trades already carry OKX's real fee (proceeds come back net of it). Returns {bot_id: [(ms, extra_cost)]}."""
    extra = {}
    for t in trades:
        d = fee_for(t["bot_id"]) - bot.FEE
        if t.get("mode") != "paper" or d <= 0:
            continue
        q, cost_in = t["qty"], t["qty"] * t["entry_px"] * d
        ev = extra.setdefault(t["bot_id"], [])
        ev.append((t["entry_ms"], cost_in))
        out = 0.0
        if t.get("half_px"):
            out += q / 2 * t["half_px"] * d
        if t["status"] != "open":
            out += (q / 2 if t.get("half_px") else q) * t["exit_px"] * d
            t["pnl_logged"] = t["pnl"]
            t["pnl"] = round(t["pnl"] - cost_in - out, 2)
            ev.append((t["exit_ms"], out))
        t["fee_adjusted"] = True
    return extra


def stats(ts):
    """Same fields as journal/summary.json, from the (fee-corrected) trades."""
    cl = [t for t in ts if t["status"] != "open"]
    w = [t["pnl"] for t in cl if t["pnl"] > 0]
    lo = [t["pnl"] for t in cl if t["pnl"] <= 0]
    rs = [t["r_multiple"] for t in cl if t.get("r_multiple") is not None]
    return {"trades": len(ts), "closed": len(cl), "open": len(ts) - len(cl), "wins": len(w), "losses": len(lo),
            "win_rate_pct": round(len(w) / len(cl) * 100, 1) if cl else None,
            "profit_factor": round(sum(w) / -sum(lo), 2) if lo and sum(lo) < 0 else (None if not w else float("inf")),
            "total_pnl": round(sum(t["pnl"] for t in cl), 2), "avg_r": round(sum(rs) / len(rs), 2) if rs else None}


def claude_bots():
    """The two Claudes' paper accounts (analyst/ledger.py), shaped like a bot so the page shows them the same way."""
    out = []
    for bid, name, sub in (("claude", "Claude (Analyst)", ""), ("chrome", "Chrome Claude", "chrome")):
        led = load(os.path.join("analyst", sub, "ledger.json"), None)
        if not led:
            continue
        start_ms = int(dt.datetime(2026, 10, 6, 13, 30, tzinfo=dt.timezone.utc).timestamp() * 1000)
        curve, ts, open_buy = [(start_ms, 1000.0)], [], {}
        for r in rows(os.path.join("analyst", sub, "trades.csv")):
            ms = int(dt.datetime.strptime(r["time_utc"], "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            if r["side"] == "buy":
                open_buy[r["coin"]] = ms
            else:
                open_buy.pop(r["coin"], None)
                ts.append({"coin": r["coin"], "status": "closed", "pnl": float(r["pnl_usdt"]),
                           "r_multiple": float(r["r_multiple"]) if r["r_multiple"] else None})
                curve.append((ms, float(r["balance"])))
        ts += [{"coin": c, "status": "open", "pnl": 0.0, "r_multiple": None} for c in led["positions"]]
        now_bal = led["equity"]
        curve.append((int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000), now_bal))
        peak = max(v for _, v in curve)
        out.append({
            "id": bid, "name": name, "strat": "judgment", "mode": "paper", "venue": "okx", "prefix": None,
            "status": "halted" if led.get("halted") else "running", "pile": "CLAUDE",
            "coins": ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK"], "risk_pct": 0.5,
            "start": "2026-10-06", "start_balance": 1000.0, "balance": round(now_bal, 2), "peak": round(peak, 2),
            "dd_now": round((now_bal / peak - 1) * 100, 2), "dd_max": round(max_dd(curve), 2),
            "stats": stats(ts), "by_coin": {c: stats([t for t in ts if t["coin"] == c]) for c in sorted({t["coin"] for t in ts})},
            "expected": None, "live_curve": [[t, round(v, 2)] for t, v in curve], "backtest": None,
            "odd": "; ".join([f"waiting: {c} {o['side']} {o['trigger']:g}" for c, o in led.get("orders", {}).items()]
                             + [f"open: {c} from {p['entry']:g}, stop {p['stop']:g}" for c, p in led["positions"].items()]),
        })
    return out


def main():
    summary = load("journal/summary.json", {"bots": {}, "totals": {}})
    trades = load("journal/trades.json", [])
    watcher = load("journal/watcher.json", {"bots": {}, "attention": []})
    numbers = load("calendars/cards/numbers.json", {"bots": {}})
    backtest = load("dashboard/backtest.json", {"bots": {}})
    state = load("state.json", {"bots": {}})
    csv_rows = rows("trades.csv")
    exp = {**cards.expected(), **load("dashboard/expected_real.json", {})}
    kraken = load("journal/kraken.json", None)
    k_taker = (kraken or {}).get("fees", {}).get("taker", {})
    k_fee = max(k_taker.values()) / 100 if k_taker else None  # Kraken reports % (e.g. 0.40)
    venue = {b["id"]: b["venue"] for b in bot.BOTS}
    fee_for = lambda bid: k_fee if venue.get(bid) == "kraken" and k_fee else REAL_FEE  # noqa: E731
    extra = real_fees(trades, fee_for)
    for t in trades:  # R for re-priced paper trades: P/L over the money at risk
        if t.get("fee_adjusted") and t["status"] != "open" and t.get("planned_stop") and t["entry_px"] > t["planned_stop"]:
            t["r_multiple"] = round(t["pnl"] / (t["qty"] * (t["entry_px"] - t["planned_stop"])), 2)

    bots = []
    for b in bot.BOTS:
        bid = b["id"]
        s = summary["bots"].get(bid, {})
        num = numbers["bots"].get(bid, {})
        now_bal = num.get("live_now") or state["bots"].get(bid, {}).get("equity", b["equity"])
        live = cards.live_curve(b, csv_rows, now_bal)
        ev = sorted(extra.get(bid, []))
        if ev:  # take the extra (real) fees off the paper balance from the moment each was paid
            live = [(t, v - sum(x for ms, x in ev if ms <= t)) for t, v in live]
            now_bal = live[-1][1]
        mine = [t for t in trades if t.get("bot_id") == bid]
        peak = max([v for _, v in live] + [watcher["bots"].get(bid, {}).get("peak") or 0])
        bt = backtest["bots"].get(bid)
        st = stats(mine)
        by_coin = {c: stats([t for t in mine if t["coin"] == c]) for c in sorted({t["coin"] for t in mine})}
        bots.append({
            "id": bid, "name": b["name"], "strat": b["strat"], "mode": b["mode"], "venue": b["venue"], "prefix": b.get("prefix"),
            "status": "retired" if b.get("retired") else "paused" if b.get("new_trades") is False else "running",
            "pile": PILE.get(bid, ""),
            "coins": [c.replace("-USDT", "").replace("USD", "").replace("XBT", "BTC") for c in b["coins"]],
            "risk_pct": round(b.get("risk", bot.RISK_PCT) * 100, 2),
            "start": cards.START.get(bid), "start_balance": b["equity"],
            "balance": round(now_bal, 2), "peak": round(peak, 2),
            "dd_now": round((now_bal / peak - 1) * 100, 2) if peak else 0.0,
            "dd_max": round(max_dd(live), 2),
            "stats": st, "by_coin": by_coin,
            "expected": exp.get(bid),
            "live_curve": [[t, round(v, 2)] for t, v in live],
            "backtest": bt,
            "odd": watcher["bots"].get(bid, {}).get("odd", ""),
        })

    bots = claude_bots() + bots

    for t in trades:
        d = t.pop("entry_decision", None) or {}
        t["checks"] = [{"plain": c["plain"], "passed": c["passed"], "points": c.get("points")}
                       for c in d.get("checks", [])]

    hold = state.get("hold", {})
    data = {
        "updated_utc": summary.get("updated_utc"),
        "built_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "attention": watcher.get("attention", []),
        "btc": summary.get("btc", {}),
        "totals": summary.get("totals", {}),
        "rules": {"stop_dd": STOP_DD, "verdict_at": VERDICT_AT, "pf_shortlist": 1.3},
        "bots": bots, "trades": trades, "kraken": kraken, "kraken_fee_pct": round(k_fee * 100, 2) if k_fee else None,
        "hold": {"spent": hold.get("spent", {}), "units": hold.get("units", {}), "buys": rows("hold_pile.csv")},
        "changes": load("journal/changes.json", []),
        "backtest_made": backtest.get("made_utc"),
        "fee_pct": round(REAL_FEE * 100, 2), "paper_fee_pct": round(bot.FEE * 100, 2),
    }
    with open(os.path.join(HERE, "template.html")) as f:
        page = f.read()
    blob = json.dumps(clean(data), separators=(",", ":")).replace("</", "<\\/")
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(page.replace("/*DATA*/null", blob))
    print("wrote dashboard/index.html", len(blob) // 1024, "KB of data")


if __name__ == "__main__":
    main()
