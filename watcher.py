"""
Trade watcher: reads what the bots did this hour and writes short factual notes to BOT_NOTES.md for the Chrome
Claude. Runs every hour after bot.py, journal.py and pl_calendar.py. NEVER trades and never changes a bot.

BOT_NOTES.md:
  - line 1: "STATUS: all normal" or "ATTENTION: ...", rewritten every run
  - below it, one line per event, newest at the top, Eastern time

Notes are added for: buys and sells (incl. half profit), a bot reaching 8%+ drawdown, losing streaks of 5+,
live vs backtest-replay drift, failed bot runs, and unexpected open positions.
ATTENTION while any of these is true: 8%+ drawdown, a losing streak longer than the backtest's worst
(research/scout.py EXPECTED), live vs replay gap of 2%+ of the starting balance, errors in this hour's bot run,
an unexpected open position.

Inputs: state.json, trades.csv, calendars/cards/numbers.json (live vs replay, from cards.py), bot_run.log and
BOT_OUTCOME (this hour's bot step). Memory between runs: journal/watcher.json.
Run:  python watcher.py   (writes GITHUB_OUTPUT "new" and "attention_new" when run in GitHub Actions)
"""
import csv
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

import bot

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "research"))
NOTES = os.path.join(HERE, "BOT_NOTES.md")
MEMORY = os.path.join(HERE, "journal", "watcher.json")
NUMBERS = os.path.join(HERE, "calendars", "cards", "numbers.json")
RUN_LOG = os.path.join(HERE, "bot_run.log")
NEW_FILE = os.path.join(HERE, "bot_notes_new.md")  # this run's new lines, for the GitHub comment (not saved)
ET = ZoneInfo("America/New_York")
DD_ATTN = 8.0         # % below the bot's best balance
STREAK_NOTE = 5       # note every loss once a streak reaches this
DRIFT_ATTN = 2.0      # live vs replay gap, % of the starting balance
NUMBERS_MAX_AGE = 3   # hours; older replay numbers are not used
HALF = "half profit +2R"


def expected():
    try:
        import scout
        return scout.EXPECTED
    except Exception:
        return {}


def et(t):
    return t.astimezone(ET).strftime("%Y-%m-%d %I:%M %p ET").replace(" 0", " ")


def csv_time(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)


def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def short(coin):
    return coin.replace("-USDT", "").replace("XBTUSD", "BTC").replace("USD", "") if coin else coin


def num(x):
    return f"{x:.6g}" if isinstance(x, (int, float)) else "-"


def closed_trades(rows, name):
    """Full trades (buy -> final sell) for one bot, P/L summed over half and final sells, oldest first."""
    out, cur = [], {}
    for r in rows:
        if r["bot"] != name:
            continue
        if r["side"] == "buy":
            cur[r["coin"]] = 0.0
        elif r["coin"] in cur:
            cur[r["coin"]] += float(r["pnl_usdt"] or 0)
            if r["reason"] != HALF:
                out.append(cur.pop(r["coin"]))
    return out, set(cur)  # set: coins still open according to trades.csv


def losing_streak(pnls):
    n = 0
    for p in reversed(pnls):
        if p > 0:
            break
        n += 1
    return n


def main():
    now = dt.datetime.now(dt.timezone.utc)
    mem = load_json(MEMORY, {})
    first_run = not mem
    state = load_json(os.path.join(HERE, "state.json"), {"bots": {}})
    with open(os.path.join(HERE, "trades.csv")) as f:
        rows = list(csv.DictReader(f))
    numbers = load_json(NUMBERS, {})
    fresh = False
    if numbers.get("updated_utc"):
        fresh = now - csv_time(numbers["updated_utc"]) <= dt.timedelta(hours=NUMBERS_MAX_AGE)
    exp = expected()
    events, attention = [], []  # events: (time, text)

    # ---- 1. buys and sells since the last run ----
    seen = mem.get("rows_seen", 0)
    if first_run:
        seen = len(rows)
    for r in rows[seen:]:
        b = next((x for x in bot.BOTS if x["name"] == r["bot"]), None)
        t = csv_time(r["time_utc"])
        coin = short(r["coin"])
        if r["side"] == "buy":
            pos = state["bots"].get(b["id"], {}).get("positions", {}).get(r["coin"], {}) if b else {}
            txt = (f"{r['bot']} bought {coin} {num(float(r['qty']))} at {num(float(r['price']))} "
                   f"({float(r['usdt']):.2f} USDT), stop {num(pos.get('sl'))}, target {num(pos.get('tp'))}")
            if b and b.get("new_trades") is False:
                txt += ". UNEXPECTED: this bot is paused"
                mem.setdefault("paused_buys", {}).setdefault(b["id"], []).append(r["coin"])
        else:
            what = "sold half of" if r["reason"] == HALF else "sold"
            txt = (f"{r['bot']} {what} {coin} at {num(float(r['price']))} ({r['reason']}), "
                   f"P/L {float(r['pnl_usdt'] or 0):+.2f} ({float(r['pnl_pct'] or 0):+.2f}%), "
                   f"balance {float(r['bot_balance']):.2f}")
        events.append((t, txt))
    mem["rows_seen"] = len(rows)

    bots_mem = mem.setdefault("bots", {})
    live_numbers = numbers.get("bots", {}) if fresh else {}
    for b in bot.BOTS:
        bid, name = b["id"], b["name"]
        bs = state["bots"].get(bid, {"equity": b["equity"], "positions": {}})
        bm = bots_mem.setdefault(bid, {})
        start = b["equity"]

        # ---- 2. drawdown from the best balance (open trades valued at the last price when cards.py ran) ----
        sells = [float(r["bot_balance"]) for r in rows if r["bot"] == name and r["side"] == "sell" and r["bot_balance"]]
        now_bal = live_numbers.get(bid, {}).get("live_now") or bs.get("equity", start)
        peak = max([start, bm.get("peak", start), now_bal] + sells)
        bm["peak"] = peak
        dd = (1 - now_bal / peak) * 100
        if dd >= DD_ATTN:
            attention.append((f"dd:{bid}", f"{name} {dd:.1f}% below its best balance"))
            if not bm.get("dd_flag"):
                events.append((now, f"{name} is {dd:.1f}% below its best balance ({now_bal:.2f} vs {peak:.2f}). "
                                    f"The guard halts new buys at {bot.GUARD['max_dd'] * 100:.0f}%"))
            bm["dd_flag"] = True
        elif bm.get("dd_flag"):
            events.append((now, f"{name} back above 8% drawdown line: {dd:.1f}% below its best"))
            bm["dd_flag"] = False
        if bs.get("halted"):
            attention.append((f"halted:{bid}", f"{name} HALTED by the guard, no new buys until Jeff says resume"))
            if not bm.get("halt_flag"):
                events.append((now, f"{name} halted by the guard: {bs['halted']}"))
            bm["halt_flag"] = True
        else:
            bm["halt_flag"] = False

        # ---- 3. losing streak ----
        pnls, open_csv = closed_trades(rows, name)
        streak = losing_streak(pnls)
        worst = (exp.get(bid) or {}).get("streak")
        if worst and streak > worst:
            attention.append((f"streak:{bid}", f"{name} {streak} losses in a row (backtest worst {worst})"))
        if streak >= STREAK_NOTE and streak != bm.get("streak_noted"):
            norm = (f"backtest's worst was {worst}, " + ("BEYOND it" if streak > worst else "still normal")) if worst \
                else "no backtest figure for this bot"
            events.append((now, f"{name} has lost {streak} in a row; {norm}"))
            bm["streak_noted"] = streak
        elif streak < STREAK_NOTE:
            bm.pop("streak_noted", None)

        # ---- 4. live vs backtest replay ----
        n = live_numbers.get(bid)
        if n and n.get("replay_now") is not None:
            gap = (n["live_now"] - n["replay_now"]) / start * 100
            if abs(gap) >= DRIFT_ATTN:
                attention.append((f"drift:{bid}", f"{name} live vs replay gap {gap:+.1f}%"))
                if not bm.get("drift_flag"):
                    events.append((now, f"{name} live balance {n['live_now']:.2f} vs backtest replay {n['replay_now']:.2f} "
                                        f"({gap:+.1f}% of start). Live trades {n['live']['n']}, replay trades "
                                        f"{n['replay']['n']}"))
                bm["drift_flag"] = True
            elif bm.get("drift_flag"):
                events.append((now, f"{name} live vs replay back in line ({gap:+.1f}% of start)"))
                bm["drift_flag"] = False

        # ---- 5. unexpected open positions ----
        odd = []
        held = set(bs.get("positions", {}))
        for coin in sorted(held - set(b["coins"])):
            odd.append(f"{short(coin)} is not one of its coins")
        for coin in sorted(held - open_csv):
            odd.append(f"{short(coin)} open in state.json but no open buy in trades.csv")
        for coin in sorted(open_csv - held):
            odd.append(f"{short(coin)} bought in trades.csv but not open in state.json")
        for coin in mem.get("paused_buys", {}).get(bid, []):
            if coin in held:
                odd.append(f"{short(coin)} bought while the bot is paused")
        mem.get("paused_buys", {})[bid] = [c for c in mem.get("paused_buys", {}).get(bid, []) if c in held]
        max_open = b.get("max_open", bot.MAX_OPEN)
        if len(held) > max_open:
            odd.append(f"{len(held)} trades open (max {max_open})")
        for o in odd:
            attention.append((f"odd:{bid}:{o}", f"{name}: {o}"))
        sig = "; ".join(odd)
        if sig and sig != bm.get("odd"):
            events.append((now, f"{name} unexpected position: {sig}"))
        bm["odd"] = sig

    # ---- 6. this hour's bot run ----
    outcome = os.environ.get("BOT_OUTCOME", "")
    errs = []
    try:
        with open(RUN_LOG) as f:
            errs = [ln.strip() for ln in f if "ERROR" in ln or "waiting for OKX API key" in ln]
    except FileNotFoundError:
        pass
    if outcome and outcome != "success":
        errs.insert(0, f"bot step {outcome}")
    if errs:
        attention.append(("run", f"bot run had {len(errs)} error(s)"))
        sig = " | ".join(errs)[:400]
        if sig != mem.get("run_errors"):
            events.append((now, f"Bot run problem: {sig}"))
        mem["run_errors"] = sig
    elif mem.get("run_errors"):
        events.append((now, "Bot run OK again"))
        mem["run_errors"] = ""

    if first_run:
        opens = [f"{b['name']} {short(c)}" for b in bot.BOTS
                 for c in state["bots"].get(b["id"], {}).get("positions", {})]
        events.append((now, "Watcher started. Open now: " + (", ".join(opens) or "none")))

    # ---- write BOT_NOTES.md ----
    status = ("ATTENTION: " + "; ".join(txt for _, txt in attention)) if attention else "STATUS: all normal"
    status += f" (checked {et(now)})"
    old = []
    try:
        with open(NOTES) as f:
            old = [ln.rstrip("\n") for ln in f if ln.startswith("- ")]
    except FileNotFoundError:
        pass
    events.sort(key=lambda e: e[0], reverse=True)
    new = [f"- {et(t)} · {txt}" for t, txt in events]
    head = [status, "", "# Bot notes", "",
            "Written every hour by watcher.py after the bots run. Read-only: it never trades. Newest first, Eastern "
            "time. ATTENTION means: a bot 8%+ below its best balance, a losing streak longer than the backtest's "
            "worst, live vs backtest replay 2%+ apart, a failed bot run, or an unexpected open position."]
    if not fresh:
        head += ["", "Note: live vs replay was not checked this hour (cards.py numbers missing or more than "
                 f"{NUMBERS_MAX_AGE} hours old)."]
    with open(NOTES, "w") as f:
        f.write("\n".join(head + [""] + new + old) + "\n")
    with open(NEW_FILE, "w") as f:
        f.write("\n".join([status, ""] + new) + "\n")
    keys = sorted({k for k, _ in attention})
    raised = [k for k in keys if k not in mem.get("attention", [])]  # new ATTENTION reasons -> mention Jeff
    mem["attention"] = keys
    os.makedirs(os.path.dirname(MEMORY), exist_ok=True)
    with open(MEMORY, "w") as f:
        json.dump(mem, f, indent=1)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"new={len(new)}\nattention_new={'true' if raised else 'false'}\n")
    print(status)
    print("\n".join(new))


if __name__ == "__main__":
    main()
