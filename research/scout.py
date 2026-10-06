"""
Scout (N5): weekly, read-only. Writes reports/weekly-YYYY-MM-DD.md with
  1. a demo performance review of every bot (from the journal), with warnings,
  2. a battery: v4 and Trend Rider on top-20 coins OKX US lists that they don't trade yet (last 2 years),
  3. the output of every research/ideas/*.py that defines run(),
  4. the research queue: the next 2-3 pre-written spec files queued in research/ideas/IDEAS.md (research/spec_runner.py).
It NEVER edits bot.py, places orders or changes settings. Plan: research/NEWBOTS_PLAN.md (N5).

Run:
  python research/scout.py
"""
import csv
import datetime as dt
import importlib.util
import json
import os
import re
import sys
import traceback
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

UTC = dt.timezone.utc
STABLE = {"USDT", "USDC", "BUSD", "DAI", "TUSD", "UST", "USDe", "USD1", "WBTC", "FDUSD", "PYUSD"}

# What the backtests say each bot should look like (2022 to now, bot.py as it is; research/*.md)
EXPECTED = {
    # v4, Kraken copy, Trend Rider: no half sell at +2R (v4 0.4% risk) since Oct 5 2026 (reports/upside-2026-10-05)
    "v4-okx": {"win": 34, "pf": 1.40, "dd": -9.6, "streak": 12, "src": "no half sell, 0.4% risk, 2022-now"},
    "v4-kraken": {"win": 33, "pf": 1.46, "dd": -9.5, "streak": 14, "src": "no half sell, 0.4% risk, 2022-now"},
    "tr-okx": {"win": 33, "pf": 1.66, "dd": -9.6, "streak": 10, "src": "0.4% risk, real 0.35% fee, no fear filter, 2022-now (research/FEES.md)"},
    "b3-paper": {"win": 44, "pf": 1.52, "dd": -5.1, "streak": 10, "src": "research/B3_PAIRS.md (P3)"},
    "nnfx-okx": {"win": 59, "pf": 1.89, "dd": -6.1, "streak": None, "src": "real 0.35% fee, 2022-now (research/FEES.md)"},
    "nnfx-paper": {"win": 61, "pf": 2.20, "dd": -5.4, "streak": None, "src": "research/NNFX.md (2022-now)"},
    "b1-paper": {"win": 46, "pf": 1.17, "dd": -5.8, "streak": None, "src": "research/B_BOXES.md"},
}


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


# ───────── 1. demo performance review ─────────
def stats(closed):
    pnl = [t.get("pnl") or 0.0 for t in closed]
    won, lost = sum(p for p in pnl if p > 0), -sum(p for p in pnl if p < 0)
    rs = [t["r_multiple"] for t in closed if t.get("r_multiple") is not None]
    streak = run = 0
    for p in pnl:
        run = run + 1 if p <= 0 else 0
        streak = max(streak, run)
    return {"n": len(closed), "win": sum(p > 0 for p in pnl) / len(pnl) * 100 if pnl else None,
            "pnl": sum(pnl), "pf": won / lost if lost else (float("inf") if won else None),
            "avg_r": sum(rs) / len(rs) if rs else None, "streak": streak}


def balance_dd(bot_name, start):
    """Worst drop of the bot's balance from its best, using the balance after every sale in trades.csv."""
    peak, dd, bal = start, 0.0, start
    try:
        with open(os.path.join(ROOT, "trades.csv")) as f:
            for row in csv.DictReader(f):
                if row["bot"] == bot_name and row["side"] == "sell" and row.get("bot_balance"):
                    bal = float(row["bot_balance"])
                    peak = max(peak, bal)
                    dd = min(dd, bal / peak - 1)
    except FileNotFoundError:
        pass
    return dd * 100


def fmt(x, f="{:.2f}", none="-"):
    if x is None:
        return none
    return "inf" if x == float("inf") else (">100" if x > 100 and f == "{:.2f}" else f.format(x))


def review():
    trades = load_json(os.path.join(ROOT, "journal", "trades.json"), [])
    summary = load_json(os.path.join(ROOT, "journal", "summary.json"), {}).get("bots", {})
    lines = ["## 1. Demo performance review", "",
             "| Bot | Mode | Status | Balance | Closed trades | Win % | P/L | PF | Avg R | Longest losing streak | "
             "Balance DD | Backtest (win % / PF / DD) |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    warnings, coin_lines = [], []
    for b in bot.BOTS:
        closed = [t for t in trades if t["bot_id"] == b["id"] and t["status"] == "closed"]
        open_n = sum(1 for t in trades if t["bot_id"] == b["id"] and t["status"] == "open")
        s = stats(closed)
        bal = summary.get(b["id"], {}).get("balance", b["equity"])
        dd = balance_dd(b["name"], b["equity"])
        exp = EXPECTED.get(b["id"])
        status = "paused" if b.get("new_trades") is False else "active"
        lines.append(f"| {b['name']} | {b['mode']} | {status} | {bal:,.2f} | {s['n']} (+{open_n} open) | "
                     f"{fmt(s['win'], '{:.0f}%')} | {s['pnl']:+.2f} | {fmt(s['pf'])} | {fmt(s['avg_r'])} | {s['streak']} | "
                     f"{dd:.1f}% | {('%d%% / %.2f / %.1f%%' % (exp['win'], exp['pf'], exp['dd'])) if exp else '-'} |")
        if status == "paused":
            continue
        if dd <= -8:
            warnings.append(f"{b['name']}: balance drawdown {dd:.1f}% (limit 10%)")
        if s["streak"] >= 8:
            norm = f"; the backtest's longest was {exp['streak']}" if exp and exp.get("streak") else ""
            warnings.append(f"{b['name']}: {s['streak']} losses in a row{norm}")
        if s["n"] >= 20 and s["pf"] is not None and s["pf"] < 1:
            warnings.append(f"{b['name']}: PF {s['pf']:.2f} after {s['n']} trades")
        if s["n"] >= 20 and exp and s["win"] is not None and s["win"] < exp["win"] - 15:
            warnings.append(f"{b['name']}: win {s['win']:.0f}% vs {exp['win']}% in the backtest after {s['n']} trades")
        for coin in b["coins"]:
            cs = stats([t for t in closed if t["coin"] == coin])
            if cs["n"]:
                coin_lines.append(f"| {b['name']} | {coin} | {cs['n']} | {fmt(cs['win'], '{:.0f}%')} | {cs['pnl']:+.2f} | "
                                  f"{fmt(cs['pf'])} | {fmt(cs['avg_r'])} |")
            if cs["n"] >= 5 and cs["pnl"] < 0:
                warnings.append(f"{b['name']} {coin}: losing {cs['pnl']:+.2f} after {cs['n']} trades")
    lines += ["", "Per coin (closed trades):", "", "| Bot | Coin | Trades | Win % | P/L | PF | Avg R |",
              "|---|---|---|---|---|---|---|"] + (coin_lines or ["| - | no closed trades yet | | | | | |"])
    lines += ["", "**Warnings:** " + ("none" if not warnings else ""), ""] + [f"- {w}" for w in warnings]
    lines += ["", "Small samples: with fewer than about 30 closed trades a bot's win % and PF are mostly noise.", ""]
    return lines


# ───────── 1b. hold pile and Trend Rider's fear filter ─────────
FEAR_SINCE = dt.datetime(2026, 10, 5, tzinfo=UTC)  # filter switched on (journal/changes.json)


def hold_pile():
    lines = ["## 1b. Hold pile (paper dip-DCA buyer)", ""]
    hp = load_json(os.path.join(ROOT, "state.json"), {}).get("hold")
    if not hp or not hp.get("units"):
        return lines + ["No hold-pile buys yet.", ""]
    api = bot.OKX("", "", "")
    lines += ["| Coin | Units | Paid | Avg price | Price now | Value | Gain |", "|---|---|---|---|---|---|---|"]
    tot_paid = tot_val = 0.0
    for coin, units in hp["units"].items():
        paid = hp["spent"].get(coin, 0.0)
        try:
            px = float(api.get("/api/v5/market/ticker", {"instId": coin})[0]["last"])
        except Exception:
            px = None
        val = units * px if px else None
        tot_paid += paid
        tot_val += val or 0.0
        lines.append(f"| {coin} | {units:.8g} | ${paid:,.2f} | {fmt(paid / units if units else None, '{:.6g}')} | "
                     f"{fmt(px, '{:.6g}')} | {fmt(val, '${:,.2f}')} | {fmt((val / paid - 1) * 100 if val and paid else None, '{:+.1f}%')} |")
    dips = 0
    try:
        with open(os.path.join(ROOT, "hold_pile.csv")) as f:
            dips = sum(1 for r in csv.DictReader(f) if r.get("dip") == "True")
    except FileNotFoundError:
        pass
    lines += ["", f"Total paid ${tot_paid:,.2f}, worth ${tot_val:,.2f}. Double (dip) buys so far: {dips}. "
              f"Last buy week: {hp.get('last_week')}.", ""]
    return lines


def fear_compare():
    """Trend Rider since the fear filter went on, simulated both ways on the real OKX candles."""
    lines = ["## 1c. Trend Rider with vs without the fear filter (since 2026-10-05)", ""]
    api = bot.OKX("", "", "")
    trb = next(b for b in bot.BOTS if b["id"] == "tr-okx")
    days = (dt.datetime.now(UTC) - FEAR_SINCE).days + 1
    data = {}
    for inst in trb["coins"]:
        c = inst.split("-")[0]
        raw4 = api.candles(inst, "4H", (days + 90) * 6)
        rawd = api.candles(inst, "1Dutc", days + 120)
        data[c] = ([x for x in raw4 if x["confirm"]], [x for x in rawd if x["confirm"]])
    raw = json.loads(urllib.request.urlopen("https://api.alternative.me/fng/?limit=0&format=json", timeout=60).read())
    bot._fng["v"] = {bot.day_of(int(x["timestamp"]) * 1000): int(x["value"]) for x in raw["data"]}
    coins = list(data)

    def with_filter(bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        return {**a, "signal": [s and not bot.fear_blocks(trb, b) for s, b in zip(a["signal"], bars)]}
    res = {"with filter (live setting)": e.bot_sim("tr", coins, data, with_filter, FEAR_SINCE, extra=lambda x: {"hi": x["c"]}),
           "without filter": e.bot_sim("tr", coins, data, lambda b, d: bot.analyse_tr(b, d, 5), FEAR_SINCE,
                                       extra=lambda x: {"hi": x["c"]})}
    lines += ["| Version | Trades | Win % | Return | Max DD | PF |", "|---|---|---|---|---|---|"]
    for name, r in res.items():
        lines.append(f"| {name} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.2f}% | {r['dd']:.1f}% | {fmt(r['pf'])} |")
    blocked = sum(1 for d, v in bot._fng["v"].items() if v <= 25 and d >= bot.day_of(e.ms(FEAR_SINCE)))
    lines += ["", f"Days at or below 25 (extreme fear) since the change: {blocked}. Simulated on the real candles, "
              "same code the demo bot runs.", ""]
    return lines


# ───────── 2. battery: existing bots on new coins ─────────
def latest_top20():
    day = dt.datetime.now(UTC).date()
    for back in range(0, 21):
        d = day - dt.timedelta(days=back)
        if d.weekday() != 6:
            continue
        try:
            req = urllib.request.Request(f"https://coinmarketcap.com/historical/{d:%Y%m%d}/",
                                         headers={"User-Agent": "Mozilla/5.0"})
            t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            syms = re.findall(r'cmc-table__column-name--symbol[^>]*>([A-Za-z0-9.$-]+)<', t)
            if syms:
                return str(d), [s for s in syms if s not in STABLE][:20]
        except Exception:
            continue
    return None, []


def battery():
    lines = ["## 2. Battery: v4 and Trend Rider on top-20 coins they don't trade (last 2 years, OKX 4H)", ""]
    api = bot.OKX("", "", "")
    snap, top = latest_top20()
    try:
        listed = {x["instId"] for x in api.get("/api/v5/public/instruments", {"instType": "SPOT"})}
    except Exception as ex:
        return lines + [f"Could not read OKX US instruments: {ex}", ""]
    t0 = dt.datetime.now(UTC) - dt.timedelta(days=730)
    rows, flags = [], []
    traded = {b["id"]: {c.split("-")[0] for c in b["coins"]} for b in bot.BOTS}
    for sym in top:
        inst = f"{sym}-USDT"
        if inst not in listed:
            continue
        try:
            raw4 = api.candles(inst, "4H", 730 * 6 + 400)
            rawd = api.candles(inst, "1Dutc", 730 + 120)
        except Exception as ex:
            rows.append(f"| {sym} | data error: {str(ex)[:60]} | | | | | |")
            continue
        data = {sym: ([x for x in raw4 if x["confirm"]], [x for x in rawd if x["confirm"]])}
        for bid, name, sim in (("v4-okx", "v4", e.v4_sim), ("tr-okx", "Trend Rider", e.tr_sim)):
            if sym in traded[bid]:
                continue
            r = sim(data, t0, None, coins=[sym])
            flag = r["pf"] >= 1.3 and r["trades"] >= 30 and r["dd"] > -10
            if flag:
                flags.append(f"{name} on {sym}")
            rows.append(f"| {sym} | {name} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}% | "
                        f"{fmt(r['pf'])} | {'FLAG' if flag else ''} |")
    lines += [f"CoinMarketCap snapshot: {snap or 'unavailable'}. Each coin alone, own $1,000, 0.5% risk, 0.1% fee.", "",
              "| Coin | Bot | Trades | Win % | Return | Max DD | PF | |", "|---|---|---|---|---|---|---|---|"]
    lines += rows or ["| - | nothing to test | | | | | | |"]
    lines += ["", "Flagged (worth a full plan-first test, NOT an add): " + (", ".join(flags) or "none"), ""]
    return lines


# ───────── 3. ideas ─────────
def ideas():
    lines = ["## 3. Ideas folder (research/ideas/*.py)", ""]
    folder = os.path.join(HERE, "ideas")
    found = False
    for fn in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not fn.endswith(".py"):
            continue
        found = True
        try:
            spec = importlib.util.spec_from_file_location(fn[:-3], os.path.join(folder, fn))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            lines += [f"### {fn}", ""] + list(mod.run()) + [""]
        except Exception:
            lines += [f"### {fn}", "", "Error:", "```", traceback.format_exc()[-1500:], "```", ""]
    return lines + ([] if found else ["No idea scripts this week (the idea list is research/ideas/IDEAS.md).", ""])


def main():
    today = dt.datetime.now(UTC).date()
    lines = [f"# Weekly Scout report {today}", "",
             "Read-only: this report never changes a bot. Chrome reads it and brings proposals to Jeff; anything new "
             "still goes through a plan-first backtest.", ""]
    def research_queue():
        import spec_runner
        return spec_runner.run_queue(3)
    for part in (review, hold_pile, fear_compare, battery, ideas, research_queue):
        try:
            lines += part()
        except Exception:
            lines += [f"## {part.__name__} failed", "", "```", traceback.format_exc()[-1500:], "```", ""]
    os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True)
    path = os.path.join(ROOT, "reports", f"weekly-{today}.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
