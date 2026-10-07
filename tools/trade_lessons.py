"""
Trade lessons (Jeff, Oct 7 2026: "journal what happens in the trade and learn, don't do that again" - from the bots'
own trades only, not from Chrome Claude). Read-only: never trades, never changes a bot.

Reads journal/trades.json (journal.py: what each bot saw when it bought, best/worst price during the trade, how it
ended) and writes LESSONS.md:
  1. every closed trade in plain English, with the mistakes it shows (tags below)
  2. a tally per mistake: how often it showed up on losers vs winners, and the money involved
  3. CANDIDATE RULES: a mistake seen on 3+ losers and at least 2x more often on losers than winners. Claude backtests
     each candidate (8 years, real fees, never-seen coins) and asks Jeff before any bot changes. One week of trades
     can't tell broken from unlucky, so nothing changes from this file alone.

  python tools/trade_lessons.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES = os.path.join(ROOT, "journal", "trades.json")
OUT = os.path.join(ROOT, "LESSONS.md")

# tag: (plain meaning, the "don't do that again" rule to test, check on a closed trade)
TAGS = {
    "never_worked": ("went wrong almost right away (never up even 0.3R)",
                     "skip breakouts that don't follow through: wait for a close above the breakout candle",
                     lambda t, m, k: t["result"] == "loss" and (t.get("best_r") is not None and t["best_r"] < 0.3)),
    "gave_back": ("was up 1R or more, then ended as a loss",
                  "move the stop to breakeven at +1R",
                  lambda t, m, k: t["result"] == "loss" and (t.get("best_r") or 0) >= 1),
    "stretched": ("bought more than 6% above the 50 EMA (chasing)",
                  "don't buy when price is over 6% above the 50 EMA",
                  lambda t, m, k: (m.get("pct_from_ema50") or 0) > 6),
    "wide_stop": ("stop was more than 8% away",
                  "skip trades whose stop is over 8% away",
                  lambda t, m, k: (k.get("stop_distance_pct") or 0) > 8),
    "supertrend_down": ("the 4H Supertrend was still pointing down",
                        "only buy when the 4H Supertrend is up",
                        lambda t, m, k: "down" in str(m.get("supertrend") or "")),
    "weak_volume": ("breakout candle had below-average volume",
                    "need volume at least equal to the 20-candle average",
                    lambda t, m, k: m.get("volume_vs_20avg") is not None and m["volume_vs_20avg"] < 0.8),
    "overbought_daily": ("daily RSI was over 70 (overbought)",
                         "don't buy when the daily RSI is over 70",
                         lambda t, m, k: (m.get("daily_rsi14") or 0) > 70),
}
MIN_LOSERS, RATIO = 3, 2.0


def tags_for(t):
    d = t.get("entry_decision") or {}
    m, k = d.get("market") or {}, d.get("risk") or {}
    return [name for name, (_, _, test) in TAGS.items() if test(t, m, k)]


def story(t, tags):
    sign = "WIN" if t["result"] == "win" else "LOSS"
    lines = [f"### {sign} {t['pnl']:+.2f} - {t['bot']} {t['coin'].split('-')[0]} ({t['entry_time']} -> {t['exit_time']} UTC)",
             f"- **Why it bought:** {t.get('why_entry') or t.get('entry_note') or '-'}",
             f"- **What happened:** best {t.get('best_pct', 0):+.2f}% ({t.get('best_r', '-')}R), worst "
             f"{t.get('worst_pct', 0):+.2f}%, held {t.get('candles_held', '-')} candles, sold by {t.get('exit_plain')} "
             f"at {t.get('exit_px')} ({t.get('pnl_pct', 0):+.2f}%, {t.get('r_multiple', '-')}R)."]
    if tags:
        lines.append("- **Lessons:** " + "; ".join(TAGS[x][0] for x in tags) + ".")
    else:
        lines.append("- **Lessons:** none - the trade followed the plan" + (" (a normal loss)." if sign == "LOSS" else "."))
    return "\n".join(lines)


def main():
    trades = json.load(open(TRADES)) if os.path.exists(TRADES) else []
    closed = [t for t in trades if t.get("status") == "closed" and t.get("result")]
    closed.sort(key=lambda t: t.get("exit_ms") or 0, reverse=True)
    tagged = [(t, tags_for(t)) for t in closed]
    tally = {name: {"loss": 0, "win": 0, "pnl": 0.0} for name in TAGS}
    for t, tags in tagged:
        for x in tags:
            tally[x][t["result"]] += 1
            tally[x]["pnl"] += t.get("pnl") or 0
    cands = [x for x, c in tally.items() if c["loss"] >= MIN_LOSERS and c["loss"] >= RATIO * max(c["win"], 0.5)]

    out = ["# Trade lessons",
           "",
           "What each closed trade teaches, from the bots' own trades only. Written every hour by tools/trade_lessons.py "
           "(read-only). A mistake becomes a **candidate rule** after it shows up on 3+ losers. Claude backtests it, and "
           "a bot changes only with Jeff's OK.",
           "",
           f"## Candidate rules ({len(cands)})",
           ""]
    out += [f"- **{TAGS[x][1]}** - seen on {tally[x]['loss']} losers vs {tally[x]['win']} winners "
            f"(P/L {tally[x]['pnl']:+.2f}). Status: needs a backtest." for x in cands] or \
        [f"- none yet ({len(closed)} closed trades; need a mistake on {MIN_LOSERS}+ losers)"]
    out += ["", "## Mistake tally", "", "| Mistake | On losers | On winners | P/L of those trades |", "|---|---|---|---|"]
    out += [f"| {TAGS[x][0]} | {c['loss']} | {c['win']} | {c['pnl']:+.2f} |" for x, c in tally.items()]
    out += ["", f"## Every closed trade, newest first ({len(closed)})", ""]
    out += [story(t, tags) + "\n" for t, tags in tagged]
    with open(OUT, "w") as f:
        f.write("\n".join(out).rstrip() + "\n")
    print(f"LESSONS.md: {len(closed)} closed trades, {len(cands)} candidate rules")


if __name__ == "__main__":
    main()
