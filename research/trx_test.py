"""
TRX (Scout flag): job-2d-style pick (data to 2021) + check (2022-now) for v4 and Trend Rider.
Rules fixed beforehand in research/COINS_PLAN.md (TRX section).

Run:
  python research/trx_test.py        # writes research/TRX.md
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

UTC = dt.timezone.utc


def fmt(r):
    pf = "inf" if r["pf"] == float("inf") else f"{r['pf']:.2f}"
    return f"{r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}% | {pf}"


def main():
    data = e.load(["TRX"])
    first = dt.datetime.fromtimestamp(data["TRX"][0][0]["ts"] / 1000, UTC)
    lines = ["# TRX for v4 and Trend Rider (Scout flag)", "", f"Rules fixed beforehand in research/COINS_PLAN.md. Binance "
             f"TRXUSDT 4H from {first:%Y-%m-%d}. TRX alone, own $1,000, 0.5% risk. Script: research/trx_test.py.", "",
             "| Bot | Pick (to 2021): trades | Win % | Return | Max DD | PF | Picked? | Check (2022-now): trades | Win % | "
             "Return | Max DD | PF | Passed? |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    passed = []
    for name, sim, bid in (("v4", e.v4_sim, "v4-okx"), ("Trend Rider", e.tr_sim, "tr-okx")):
        r1 = sim(data, dt.datetime(2013, 1, 1, tzinfo=UTC), e.CUT, coins=["TRX"])
        picked = r1["trades"] >= 30 and r1["pf"] >= 1.30 and r1["ret"] > 0 and r1["dd"] >= -10
        r2 = sim(data, e.CUT, None, coins=["TRX"])
        ok = picked and r2["pf"] > 1.0 and r2["ret"] > 0 and r2["dd"] >= -10
        if ok:
            passed.append((name, sim, bid))
        lines.append(f"| {name} | {fmt(r1)} | {'yes' if picked else 'no'} | {fmt(r2)} | "
                     f"{'yes' if ok else ('no' if picked else '- (not picked; shown for information)')} |")
    lines.append("")
    for name, sim, bid in passed:
        coins = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == bid)["coins"]]
        d = e.load(coins + ["TRX"])
        lines += [f"### {name} as it trades, with and without TRX", "", "| Coins | Period | Trades | Win % | Return | Max DD | PF |",
                  "|---|---|---|---|---|---|---|"]
        for cs in (coins, coins + ["TRX"]):
            for pname, t0 in (("2022-now", e.CUT), (f"{first:%Y-%m}-now", max(first, e.START))):
                lines.append(f"| {' '.join(cs)} | {pname} | {fmt(sim(d, t0, None, coins=cs))} |")
        lines.append("")
    lines.append(f"Result: {'TRX passes for ' + ', '.join(p[0] for p in passed) if passed else 'TRX passes for neither bot'}")
    with open(os.path.join(HERE, "TRX.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
