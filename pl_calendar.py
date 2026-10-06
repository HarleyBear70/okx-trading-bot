"""
P/L calendar for Jeff's bots. GitHub runs it after bot.py and journal.py, every hour.

It NEVER trades. It reads trades.csv and writes:
  calendars/combined.svg   the OKX demo account (every demo bot added together)
  calendars/<bot id>.svg   one per active bot (paused bots hidden), labelled DEMO or PAPER
  CALENDAR.md              shows all of them (GitHub renders the SVGs on the repo page, private repos too)

One square per day (Eastern time): green = closed profit that day, red = closed loss, grey = no closed trades.
The stronger the colour, the bigger the day (full colour at 2% of the balance). Each square shows the day's %
change of the balance and the $ amount. Under each month: the month's total and win days vs loss days.
Newest month first; every month since the first trade is kept.
"""

import calendar as cal
import csv
import datetime as dt
import json
import os
from collections import defaultdict
from zoneinfo import ZoneInfo

import bot

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "calendars")
ET = ZoneInfo("America/New_York")
FULL_AT = 2.0  # % of balance that gets the strongest colour

CELL, GAP, PAD = 44, 3, 12
WIDTH = PAD * 2 + 7 * CELL + 6 * GAP  # 344 px: fits a phone screen


def read_rows():
    try:
        with open(bot.TRADES_FILE, newline="") as f:
            return list(csv.DictReader(f))
    except FileNotFoundError:
        return []


def et_day(time_utc):
    t = dt.datetime.strptime(time_utc, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc)
    return t.astimezone(ET).date()


def daily_pl(rows, names, start_balance):
    """{date: (pnl $, pnl % of the balance at the start of that day)} for the bots in `names` added together.
    Closed P/L only (sells, including half-profit sells)."""
    bal = {n: start_balance[n] for n in names}  # balance after each bot's latest sale
    by_day = defaultdict(float)
    start_of_day = {}
    for r in rows:
        if r["bot"] not in names or r["side"] != "sell" or not r.get("pnl_usdt"):
            continue
        day = et_day(r["time_utc"])
        if day not in start_of_day:
            start_of_day[day] = sum(bal.values())
        by_day[day] += float(r["pnl_usdt"])
        if r.get("bot_balance"):
            bal[r["bot"]] = float(r["bot_balance"])
    return {d: (p, p / start_of_day[d] * 100 if start_of_day[d] else 0.0) for d, p in by_day.items()}


def colour(pct):
    """Light to strong green / red by size of the day."""
    if pct is None:
        return "#e9ecef", "#868e96"
    k = min(abs(pct) / FULL_AT, 1.0)
    lo, hi = ((216, 243, 220), (26, 127, 55)) if pct >= 0 else ((255, 222, 222), (201, 42, 42))
    rgb = tuple(round(a + (b - a) * (0.15 + 0.85 * k)) for a, b in zip(lo, hi))
    text = "#ffffff" if k > 0.45 else "#212529"
    return "#%02x%02x%02x" % rgb, text


def plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def money(x):
    s = f"{abs(x):,.2f}" if abs(x) < 1000 else f"{abs(x):,.0f}"
    return ("+" if x >= 0 else "-") + "$" + s


def month_svg(y, m, days, y0):
    """SVG elements for one month starting at height y0. Returns (elements, height)."""
    el = []
    weeks = cal.Calendar(firstweekday=6).monthdayscalendar(y, m)  # weeks start on Sunday (US)
    el.append(f'<text x="{PAD}" y="{y0 + 18}" class="mt">{cal.month_name[m]} {y}</text>')
    yh = y0 + 30
    for i, name in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        el.append(f'<text x="{PAD + i * (CELL + GAP) + CELL / 2}" y="{yh + 10}" class="wd">{name}</text>')
    yg = yh + 16
    tot, wins, losses, start_pct = 0.0, 0, 0, []
    for r, week in enumerate(weeks):
        for c, d in enumerate(week):
            if not d:
                continue
            x, yy = PAD + c * (CELL + GAP), yg + r * (CELL + GAP)
            v = days.get(dt.date(y, m, d))
            fill, txt = colour(v[1] if v else None)
            el.append(f'<rect x="{x}" y="{yy}" width="{CELL}" height="{CELL}" rx="5" fill="{fill}"/>')
            el.append(f'<text x="{x + 4}" y="{yy + 11}" class="dn" fill="{txt}">{d}</text>')
            if v:
                tot += v[0]
                wins += v[0] > 0
                losses += v[0] < 0
                el.append(f'<text x="{x + CELL / 2}" y="{yy + 26}" class="pc" fill="{txt}">{v[1]:+.2f}%</text>')
                el.append(f'<text x="{x + CELL / 2}" y="{yy + 38}" class="usd" fill="{txt}">{money(v[0])}</text>')
    yb = yg + len(weeks) * (CELL + GAP) + 14
    tone = "#1a7f37" if tot > 0 else ("#c92a2a" if tot < 0 else "#495057")
    el.append(f'<text x="{PAD}" y="{yb}" class="sum" fill="{tone}">Month: {money(tot)}  ·  '
              f'{plural(wins, "win day")}  ·  {plural(losses, "loss day")}</text>')
    return el, yb - y0 + 16


def build_svg(title, subtitle, days, months):
    el, y = [], 0
    el.append(f'<text x="{PAD}" y="22" class="tt">{title}</text>')
    el.append(f'<text x="{PAD}" y="40" class="st">{subtitle}</text>')
    y = 50
    for (yy, mm) in months:
        part, h = month_svg(yy, mm, days, y)
        el += part
        y += h + 6
    style = ("<style>text{font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif}"
             ".tt{font-size:16px;font-weight:700;fill:#212529}.st{font-size:11px;fill:#6c757d}"
             ".mt{font-size:14px;font-weight:700;fill:#212529}.wd{font-size:9px;fill:#868e96;text-anchor:middle}"
             ".dn{font-size:9px}.pc{font-size:10px;font-weight:700;text-anchor:middle}"
             ".usd{font-size:8.5px;text-anchor:middle}.sum{font-size:11px;font-weight:600}</style>")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{y + 4}" viewBox="0 0 {WIDTH} {y + 4}">'
            f'<rect width="100%" height="100%" fill="#ffffff" rx="8"/>{style}' + "".join(el) + "</svg>")


def months_between(first, last):
    out, y, m = [], last.year, last.month
    while (y, m) >= (first.year, first.month):
        out.append((y, m))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return out


def build_cards(rows):
    """Strategy cards (cards.py); never breaks the calendar if it fails."""
    try:
        import cards
        return cards.build(bot.OKX("", "", ""), rows)
    except Exception as ex:
        return ["## Strategy cards", "", f"(cards unavailable this hour: {str(ex)[:150]})", ""]


def build_analyst():
    """The two Claudes trading on judgment (analyst/ledger.py, paper), scored against the active bots."""
    try:
        with open(os.path.join(HERE, "state.json")) as f:
            st = json.load(f)["bots"]
        md = ["## The Claudes vs the bots", "",
              "Both Claudes trade on judgment, on paper, since Oct 6 2026: same $1,000 start, same 0.35% fee, same risk "
              "rules enforced in code (0.5% per trade, stop on every trade, max 3 open, 12% guard). Claude (terminal) "
              "writes briefs, journal and lessons in [analyst/](analyst/); Chrome Claude trades through "
              "[analyst/chrome/requests.md](analyst/chrome/requests.md).", "",
              "| | Balance | Change | Closed trades |", "|---|---|---|---|"]
        notes = []
        for label, sub in (("Claude (Analyst)", ""), ("Chrome Claude", "chrome")):
            folder = os.path.join(HERE, "analyst", sub)
            path = os.path.join(folder, "ledger.json")
            if not os.path.exists(path):
                continue
            with open(path) as f:
                led = json.load(f)
            trades = []
            tpath = os.path.join(folder, "trades.csv")
            if os.path.exists(tpath):
                with open(tpath) as f:
                    trades = [r for r in csv.DictReader(f) if r["side"] == "sell"]
            eq = led["equity"]
            wins = sum(1 for r in trades if float(r["pnl_usdt"]) > 0)
            md.append(f"| **{label}** | **{eq:,.2f}** | **{eq / 10 - 100:+.2f}%** | {len(trades)}"
                      f"{f' ({wins} won)' if trades else ''} |")
            for c, p in led["positions"].items():
                notes.append(f"- **{label}, open {c}:** bought {p['entry']:g} on {p['opened']} UTC, stop {p['stop']:g}. "
                             f"Why: {p['why']}")
            for c, o in led.get("orders", {}).items():
                word = "above" if o["side"] == "above" else "down to"
                notes.append(f"- **{label}, waiting {c}:** buy if price goes {word} {o['trigger']:g}, stop {o['stop']:g}. "
                             f"Why: {o['why']}")
            if led.get("halted"):
                notes.append(f"- **{label} HALTED:** {led['halted']}")
        for bid in ("tr-okx", "dc-okx", "nnfx-okx"):
            b = next((x for x in bot.BOTS if x["id"] == bid), None)
            if b:
                e = st.get(bid, {}).get("equity", b["equity"])
                md.append(f"| {b['name']} | {e:,.2f} | {e / b['equity'] * 100 - 100:+.2f}% | |")
        return md + ["", "Closed P/L only; open trades count when they close.", ""] + notes + [""]
    except Exception as ex:
        return ["## The Claudes vs the bots", "", f"(unavailable this hour: {str(ex)[:150]})", ""]


def main():
    rows = read_rows()
    os.makedirs(OUT_DIR, exist_ok=True)
    today = dt.datetime.now(ET).date()
    first = min((et_day(r["time_utc"]) for r in rows), default=today)
    months = months_between(first, today)
    start = {b["name"]: b["equity"] for b in bot.BOTS}
    stamp = dt.datetime.now(ET).strftime("%Y-%m-%d %H:%M %Z")
    views = []
    demo = [b["name"] for b in bot.BOTS if b["mode"] == "demo"]
    views.append(("combined", "Combined OKX demo account", f"DEMO · {', '.join(demo)} · updated {stamp}", demo))
    for b in bot.BOTS:
        if b.get("new_trades") is False:
            continue  # paused bots hidden
        views.append((b["id"], b["name"], f"{b['mode'].upper()} · {' '.join(c.split('-')[0] for c in b['coins'])}",
                      [b["name"]]))
    cards_done = False
    md = ["# P/L calendar and strategy cards", "", f"Updated automatically every hour ({stamp}). Days are Eastern time. Green = closed "
          "profit that day, red = closed loss, grey = no closed trades; stronger colour = bigger day (full colour at "
          f"{FULL_AT:g}% of the balance). Each square: the day's % change of the balance and the $ amount. "
          "DEMO = OKX demo account orders, PAPER = simulated, no orders. Made by pl_calendar.py.", ""]
    for vid, title, sub, names in views:
        if vid != "combined" and not cards_done:
            md += build_cards(rows)
            md += ["## Per-bot P/L calendars", ""]
            cards_done = True
        days = daily_pl(rows, names, start)
        with open(os.path.join(OUT_DIR, f"{vid}.svg"), "w") as f:
            f.write(build_svg(title, sub, days, months))
        tot = sum(p for p, _ in days.values())
        md += [f"## {title}" if vid == "combined" else f"### {title}", "",
               f"Closed P/L so far: {money(tot)} · {plural(sum(1 for p, _ in days.values() if p > 0), 'win day')} · "
               f"{plural(sum(1 for p, _ in days.values() if p < 0), 'loss day')}", "", f"![{title}](calendars/{vid}.svg)", ""]
        if vid == "combined":
            md += build_analyst()
    with open(os.path.join(HERE, "CALENDAR.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    bot.log(f"[calendar] {len(views)} calendars, {len(months)} months")


if __name__ == "__main__":
    main()
