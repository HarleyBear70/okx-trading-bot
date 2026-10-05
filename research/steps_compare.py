"""
Risk step-ups off vs on, on the equal-terms scoreboard footing (research/scoreboard.py).

Only the bots that size trades through bot.risk_pct() can step up (bot.py's own strategies run by
engine.bot_sim). B1c, B3 and the research bots use fixed 0.5% sims, so they are left out.

Run:
  python research/steps_compare.py OUT.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import scoreboard as sb  # noqa: E402

STEP_BOTS = ["SP-12 v4", "SP-12 v4 (Kraken paper)", "Trend Rider", "NNFX Aroon", "SP-12 v2",
             "Trend Rider gold (pivot 3)"]


def cell(r):
    ret, dd, rd = e.ret_dd(r["curve"])
    return f"{ret:+.0f}% / {dd:.1f}% / {rd:.2f}"


def main(out):
    lines = ["| Bot | Period | Step-ups off: return / max DD / return÷DD | Step-ups on: return / max DD / return÷DD |",
             "|---|---|---|---|"]
    for name, _status, run, coins in sb.rows():
        if name not in STEP_BOTS:
            continue
        for p, t0, t1 in sb.PERIODS:
            res = {}
            for on in (False, True):
                bot.RISK_STEPS_ON = on
                res[on] = run(t0, t1)
            lines.append(f"| {name} ({coins}) | {p} | {cell(res[False])} | {cell(res[True])} |")
        print(f"done {name}", flush=True)
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
