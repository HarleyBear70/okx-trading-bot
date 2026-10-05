"""
Ways to get more out of the bots (Jeff, Oct 5 2026), on the scoreboard footing (research/scoreboard.py):
$1,000 per bot, 0.1% fee each side, max 3 open, step-ups off, 2018-05 to now plus the two halves.

  A. Sell half at +2R vs keep the whole position: SP-12 v4, Trend Rider, SP-12 v2 (paused, used as a test run)
  B. v4 + Trend Rider together (each bot its own balance), at 0.5%, 0.75% and 1% risk per trade
  C. Same pair, more money behind Trend Rider: 50/50 vs 30/70

Run:
  python research/upside_test.py OUT.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import scoreboard as sb  # noqa: E402

RISKS = [0.005, 0.0075, 0.01]
SPLITS = [(0.5, 0.5), (0.3, 0.7)]  # (v4, Trend Rider)


def years(curve):
    return (curve[-1][0] - curve[0][0]) / (365.25 * 86400000)


def row(curve, extra=""):
    ret, dd, rd = e.ret_dd(curve)
    yrs = years(curve)
    cagr = ((curve[-1][1] / curve[0][1]) ** (1 / yrs) - 1) * 100 if yrs > 0 else 0
    return f"{ret:+.0f}% | {cagr:+.1f}% | {dd:.1f}% | {rd:.2f}{extra}"


def main(out):
    bot.RISK_STEPS_ON = False
    base_risk = bot.RISK_PCT
    v4c, trc, v2c = sb.bot_coins("v4-okx"), sb.bot_coins("tr-okx"), sb.bot_coins("v2-okx")
    d4, dtr, dv2 = e.load(v4c), e.load(trc), e.load(v2c)
    sp = lambda cfg: (lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS[cfg]))  # noqa: E731
    tr = lambda b, d: bot.analyse_tr(b, d, 5)  # noqa: E731

    def run(name, half, t0, t1):
        nh = {} if half else {"no_half": True}
        if name == "v4":
            return e.bot_sim("v4", v4c, d4, sp("v4"), t0, t1, extra=lambda x: dict(nh))
        if name == "v2":
            return e.bot_sim("v2", v2c, dv2, sp("v2"), t0, t1, extra=lambda x: dict(nh))
        return e.bot_sim("tr", trc, dtr, tr, t0, t1, extra=lambda x: {"hi": x["c"], **nh})

    names = {"v4": f"SP-12 v4 ({' '.join(v4c)})", "tr": f"Trend Rider ({' '.join(trc)})",
             "v2": f"SP-12 v2, paused, test run ({' '.join(v2c)})"}
    curves = {}  # (bot, half, risk, period) -> result
    lines = ["## A. Sell half at +2R vs keep the whole position (0.5% risk)", "",
             "| Bot | Period | Half at +2R: return / per year / worst drop / return÷drop / PF | "
             "No half sell: return / per year / worst drop / return÷drop / PF |", "|---|---|---|---|"]
    for name in ("v4", "tr", "v2"):
        for p, t0, t1 in sb.PERIODS:
            cells = []
            for half in (True, False):
                bot.RISK_PCT = base_risk
                r = run(name, half, t0, t1)
                curves[(name, half, base_risk, p)] = r
                cells.append(row(r["curve"], f" | {r['pf']:.2f}"))
            lines.append(f"| {names[name]} | {p} | {cells[0].replace(' | ', ' / ')} | {cells[1].replace(' | ', ' / ')} |")
        print(f"done A {name}", flush=True)

    lines += ["", "## B and C. v4 + Trend Rider together, by risk per trade and money split", "",
              "Each bot keeps its own balance (like live); the pair's value is the two added up. "
              "Columns: return / per year / worst drop / return÷drop.", "",
              "| Half sell | Risk per trade | Split v4 / TR | Full 2018-now | 2018-2021 | 2022-now |",
              "|---|---|---|---|---|---|"]
    for half in (True, False):
        for risk in RISKS:
            for name in ("v4", "tr"):
                for p, t0, t1 in sb.PERIODS:
                    if (name, half, risk, p) not in curves:
                        bot.RISK_PCT = risk
                        curves[(name, half, risk, p)] = run(name, half, t0, t1)
            for w in SPLITS:
                cells = [row(e.combine([curves[("v4", half, risk, p)]["curve"], curves[("tr", half, risk, p)]["curve"]],
                                       list(w))).replace(" | ", " / ") for p, _, _ in sb.PERIODS]
                lines.append(f"| {'yes' if half else 'no'} | {risk * 100:g}% | {w[0] * 100:.0f} / {w[1] * 100:.0f} | "
                             + " | ".join(cells) + " |")
            print(f"done B half={half} risk={risk}", flush=True)
    bot.RISK_PCT = base_risk
    with open(out, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1])
