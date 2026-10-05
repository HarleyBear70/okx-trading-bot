"""
Look-ahead audit (Chrome / Jeff). Two empirical tests for every live / paper bot's analysis:

T1 look-ahead: at many past decision times, rerun the analysis on ONLY the data that existed then (candles that
   had closed; daily candles only if their day had ended) and compare the decision at that candle with the
   full-history run. Any difference = the full-history backtest used information from the future.
T2 warm-up: rerun with exactly the history the live bot downloads (4H: 500 candles, daily: 120, 1H: 400,
   daily bots: 220) and compare with the long-history backtest at the same candle. Differences = live
   indicators haven't warmed up the same way (not look-ahead, but live would not match the backtest).

Run:
  python research/audit_lookahead.py        # writes research/AUDIT.md
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import hourly as hr  # noqa: E402
import long_history as lh  # noqa: E402

DAY, H4 = 86400000, bot.H4_MS
random.seed(7)


def daily_known(daily, t):
    """Daily candles whose day had ended by time t."""
    return [d for d in daily if d["ts"] + DAY <= t]


def same(a, b, tol=1e-9):
    """Same decision: same stop / target (relative tolerance) and same pair tag."""
    if a is None or b is None:
        return a is b
    return all(abs(a[k] - b[k]) <= tol * max(1e-12, abs(a[k])) for k in ("sl", "tp") if a.get(k) is not None) \
        and a.get("tag") == b.get("tag")


def check(name, bars, full, rerun, n_cuts, live_len=None, live_rerun=None, start=300):
    """full: analysis on all bars; rerun(k) -> analysis using only data known at bar k's close."""
    cuts = sorted(random.sample(range(start, len(bars)), min(n_cuts, len(bars) - start)))
    t1_bad, t2_bad, t2_sig = 0, 0, 0
    for k in cuts:
        a = rerun(k)
        if a["signal"][k] != full["signal"][k] or (full["signal"][k] and not same(a["info"][k], full["info"][k])):
            t1_bad += 1
        if live_rerun:
            b = live_rerun(k)
            j = len(b["signal"]) - 1
            if b["signal"][j] != full["signal"][k] or (full["signal"][k] and not same(b["info"][j], full["info"][k], 1e-3)):
                t2_bad += 1
    # T2 on signal candles specifically (where it matters)
    sig_cuts = [k for k in range(start, len(bars)) if full["signal"][k]]
    sig_cuts = random.sample(sig_cuts, min(60, len(sig_cuts)))
    for k in sig_cuts:
        if live_rerun:
            b = live_rerun(k)
            j = len(b["signal"]) - 1
            if not b["signal"][j] or not same(b["info"][j], full["info"][k], 1e-3):
                t2_sig += 1
    return name, len(cuts), t1_bad, t2_bad, len(sig_cuts), t2_sig


def main():
    rows = []
    for coin in ("BTC", "ETH", "XRP"):
        bars, daily = lh.load(coin)
        bars = bars[-6000:]  # last ~2.7 years keeps the test fast; plenty of signals
        for strat, fn, live_daily in (
            ("v4", lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), 120),
            ("Trend Rider", lambda b, d: bot.analyse_tr(b, d, 5), 120),
        ):
            full = fn(bars, daily)
            rows.append(check(
                f"{strat} {coin}", bars, full,
                lambda k: fn(bars[:k + 1], daily_known(daily, bars[k]["ts"] + H4)), 40,
                live_rerun=lambda k: fn(bars[max(0, k - 498):k + 1],
                                        daily_known(daily, bars[k]["ts"] + H4)[-live_daily:])))
            print("done", rows[-1][0], flush=True)
        b1 = hr.hourly(coin)[-20000:]
        full = bot.analyse_b1(b1)
        rows.append(check(f"B1c {coin}", b1, full, lambda k: bot.analyse_b1(b1[:k + 1]), 40,
                          live_rerun=lambda k: bot.analyse_b1(b1[max(0, k - 399):k + 1]), start=400))
        print("done", rows[-1][0], flush=True)
    # B3 pairs on daily candles (decision at the daily close)
    dd = {c: lh.load(c)[1] for c in ("BTC", "ETH", "XRP")}
    for coin in ("ETH", "XRP", "BTC"):
        bars = dd[coin]
        alts = {a: dd[a] for a in ("ETH", "XRP")}
        full = bot.analyse_pairs(coin, bars, dd["BTC"], alts)

        def rerun(k, bars=bars, coin=coin):
            t = bars[k]["ts"]
            return bot.analyse_pairs(coin, bars[:k + 1], [d for d in dd["BTC"] if d["ts"] <= t],
                                     {a: [d for d in v if d["ts"] <= t] for a, v in alts.items()})

        def live(k, bars=bars, coin=coin):
            t = bars[k]["ts"]
            return bot.analyse_pairs(coin, bars[max(0, k - 219):k + 1], [d for d in dd["BTC"] if d["ts"] <= t][-220:],
                                     {a: [d for d in v if d["ts"] <= t][-220:] for a, v in alts.items()})
        rows.append(check(f"B3 pairs {coin}", bars, full, rerun, 40, live_rerun=live, start=200))
        print("done", rows[-1][0], flush=True)
    lines = ["# Look-ahead audit", "", "T1 = decision at a past candle recomputed with only the data that existed then, vs "
             "the full-history backtest (any mismatch = look-ahead). T2 = recomputed with exactly the history the live "
             "bot downloads (mismatch = signal flips or stop / target more than 0.1% off: a warm-up difference). Script: research/audit_lookahead.py.", "",
             "| Bot / coin | T1 cuts | T1 mismatches | T2 random cuts mismatched | T2 signal candles | T2 signals lost / changed |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5]} |")
    with open(os.path.join(HERE, "AUDIT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
