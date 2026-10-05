"""
Job 2d: more coins for SP-12 v4. Applies the rules fixed in research/COINS_PLAN.md (committed first).

Step 1 picks coins using data up to 2021-12-31 only, step 2 checks them on 2022-now, step 3 runs the
v4 bot as it trades (one shared $1,000, max 3 open) with and without the coins that passed.

Run:
  python research/coins_test.py        # writes research/COINS.md
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import long_history as lh  # noqa: E402
import score_test as st  # noqa: E402

UTC = dt.timezone.utc
CUT = dt.datetime(2022, 1, 1, tzinfo=UTC)
CANDIDATES = ["LTC", "DOGE", "XLM", "ADA", "BNB", "LINK", "BCH", "AVAX", "SUI", "LUNA", "FTT"]
BASE = ["BTC", "ETH", "XRP"]


def single(coin, t0, t1):
    bars, daily = lh.load(coin)
    a = bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v4"])
    t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC))
    if t0 >= t1 or bars[-1]["ts"] < lh.ms(t0):
        return None
    return lh.simulate("v4", bars, a, t0, t1)


def portfolio(coins, t0, t1):
    """The v4 bot as it trades: research/score_test.py's simulator on these coins."""
    st.COINS = coins
    data = {c: lh.load(c) for c in coins}
    return st.simulate(data, st.make_analyse(st.SCORE_NOW), t0, t1)


def fmt(r):
    if r is None:
        return "no data | | | | "
    pf = "inf" if r["pf"] == float("inf") else f"{r['pf']:.2f}"
    return f"{r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}% | {pf}"


def main():
    now = dt.datetime.now(UTC)
    lines = ["# More coins for SP-12 v4 (job 2d)", "",
             f"Run {now:%Y-%m-%d}. Rules fixed beforehand in research/COINS_PLAN.md. bot.py as it is now "
             f"({bot.RISK_PCT * 100:g}% risk, 0.1% fee each side). Script: research/coins_test.py.", "",
             "## Step 1 (pick, data to end of 2021) and step 2 (check, 2022-now)", "",
             "| Coin | Pick: trades | Win % | Return | Max DD | PF | Picked? | Check: trades | Win % | Return | "
             "Max DD | PF | Passed? |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    passed = []
    for c in CANDIDATES:
        r1 = single(c, dt.datetime(2013, 1, 1, tzinfo=UTC), CUT)
        picked = bool(r1 and r1["trades"] >= 30 and r1["pf"] >= 1.30 and r1["ret"] > 0 and r1["dd"] >= -10)
        r2 = single(c, CUT, now) if picked else None
        ok = bool(picked and r2 and r2["pf"] > 1.0 and r2["ret"] > 0 and r2["dd"] >= -10)
        if ok:
            passed.append(c)
        lines.append(f"| {c} | {fmt(r1)} | {'yes' if picked else 'no'} | "
                     f"{fmt(r2) if picked else '- | | | | '} | {'yes' if ok else ('no' if picked else '-')} |")
        print(f"done {c}", flush=True)

    lines += ["", f"Passed both steps: {', '.join(passed) or 'none'}", "",
              "## Step 3: the v4 bot as it trades (one shared $1,000, max 3 open)", "",
              "| Coins | Period | Trades | Win % | Return | Max DD | PF |", "|---|---|---|---|---|---|---|"]
    if passed:
        start = max(lh.load(c)[0][0]["ts"] for c in BASE + passed) / 1000
        full0 = max(dt.datetime.fromtimestamp(start, UTC) + dt.timedelta(days=30), dt.datetime(2013, 1, 1, tzinfo=UTC))
        for coins in (BASE, BASE + passed):
            for pname, t0 in ((f"Full ({full0:%Y-%m}-now)", full0), ("2022-now (out-of-sample)", CUT)):
                r = portfolio(coins, t0, now)
                lines.append(f"| {' '.join(coins)} | {pname} | {fmt(r)} |")
    else:
        lines.append("| - | - | nothing to add | | | | |")
    with open(os.path.join(HERE, "COINS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
