"""
Fixed % exits (Jeff, Oct 5 2026): the same SP-12 v4 and Trend Rider entries, but a fixed stop of 1-1.5% below
entry and a fixed take profit 1.5-3% above, nothing else. Same footing as the scoreboard: $1,000, 0.5% risk per
trade (from the stop), 0.1% fee each side, max 3 open, 2018-05 to now plus both halves.

Run:
  python research/fixed_exits_test.py OUT.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import scoreboard as sb  # noqa: E402

STOPS = [1.0, 1.25, 1.5]
TPS = [1.5, 2.0, 2.5, 3.0]


def entries(analyse, stop, tp):
    def fn(coin, bars, daily):
        a = analyse(bars, daily)
        return [{"stop": x["c"] * (1 - stop / 100), "target": x["c"] * (1 + tp / 100)} if a["signal"][k] else None
                for k, x in enumerate(bars)]
    return fn


def cell(r):
    ret, dd, _ = e.ret_dd(r["curve"])
    return f"{ret:+.0f}% / {dd:.1f}%"


def main(out):
    v4c, trc = sb.bot_coins("v4-okx"), sb.bot_coins("tr-okx")
    d4, dtr = e.load(v4c), e.load(trc)
    bots = [("SP-12 v4", v4c, d4, lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), lambda t0, t1: e.v4_sim(d4, t0, t1, coins=v4c)),
            ("Trend Rider", trc, dtr, lambda b, d: bot.analyse_tr(b, d, 5), lambda t0, t1: e.tr_sim(dtr, t0, t1, coins=trc))]
    lines = []
    for name, coins, data, analyse, current in bots:
        lines += [f"## {name} ({' '.join(coins)})", "",
                  "Each cell: return / worst drop. Win % and PF are for the full period.", "",
                  "| Exits | Full 2018-now | 2018-2021 | 2022-now | Win % | PF | Trades |", "|---|---|---|---|---|---|---|"]
        res = [current(t0, t1) for _, t0, t1 in sb.PERIODS]
        f = res[0]
        lines.append(f"| **Current exits (swing-low stop, trailing)** | {' | '.join(cell(r) for r in res)} | "
                     f"{f['win']:.0f}% | {f['pf']:.2f} | {f['trades']} |")
        for stop in STOPS:
            for tp in TPS:
                fn = entries(analyse, stop, tp)
                res = [e.trade_sim(coins, data, fn, t0, t1) for _, t0, t1 in sb.PERIODS]
                f = res[0]
                lines.append(f"| stop {stop:g}%, TP {tp:g}% | {' | '.join(cell(r) for r in res)} | "
                             f"{f['win']:.0f}% | {f['pf']:.2f} | {f['trades']} |")
            print(f"done {name} stop {stop}", flush=True)
        lines.append("")
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
