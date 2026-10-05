"""Write results/SUMMARY.md: each strategy with risk step-ups off and on, side by side.

Reads results/<name>.txt (step-ups off) and results/<name>_steps.txt (step-ups on). If
results/SP12v4_nohalf.txt exists, SP12v4 with and without selling half at +2R comes first.
results/EXTRA_TESTS.md (hand-kept results from other tests) is added at the end.
Usage: python3 freqtrade/summary.py SP12v4 SP12v2 TrendRider
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

RESULTS = Path(__file__).resolve().parent / "results"
ANSI = re.compile(r"\x1b\[[0-9;]*m")
ROWS = [
    ("Trades", "Total/Daily Avg Trades"),
    ("Final balance", "Final balance"),
    ("Total profit %", "Total profit %"),
    ("CAGR %", "CAGR %"),
    ("Win / draw / loss, win %", None),
    ("Profit factor", "Profit factor"),
    ("Max % of account underwater", "Max % of account underwater"),
    ("Absolute drawdown", "Absolute drawdown"),
    ("Best trade", "Best trade"),
    ("Worst trade", "Worst trade"),
]


def read(name):
    f = RESULTS / f"{name}.txt"
    return ANSI.sub("", f.read_text(errors="replace")) if f.exists() else ""


def metrics(text, name):
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("│").split("│")]
        if len(cells) == 2 and cells[0] and cells[0] not in out:
            out[cells[0]] = cells[1]
        if len(cells) >= 8 and cells[0] == name:  # STRATEGY SUMMARY row
            w = cells[6].split()
            out["_wdl"] = f"{w[0]} / {w[1]} / {w[2]}, {w[3]}%" if len(w) == 4 else cells[6]
    return out


def block(text):
    keep, on = [], False
    for line in text.splitlines():
        if "STRATEGY SUMMARY" in line or "SUMMARY METRICS" in line:
            on = True
        if on:
            if not line.strip():
                on = False
                keep.append("")
                continue
            keep.append(line)
    return "\n".join(keep).strip("\n") or "(no result - check the workflow log)"


def section(title, name, cols):
    """cols: [(column label, results file name), (column label, results file name)]"""
    texts = [read(f) for _, f in cols]
    ms = [metrics(t, name) for t in texts]
    lines = ["", f"## {title}", "", f"| | {cols[0][0]} | {cols[1][0]} |", "|---|---|---|"]
    for label, key in ROWS:
        k = key or "_wdl"
        lines.append(f"| {label} | {ms[0].get(k, '-')} | {ms[1].get(k, '-')} |")
    for (label, _), txt in zip(cols, texts):
        lines += ["", f"<details><summary>{title}: full report, {label}</summary>", "", "```",
                  block(txt), "```", "", "</details>"]
    return lines


def main(names):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Freqtrade backtest results",
        "",
        f"Updated {now} UTC. OKX prices from March 2024, 1,000 USDT start, 0.1% fee. Exits match the live bots, "
        "including selling half at +2R. Risk per trade comes from `risk_pct()` in bot.py: "
        "**Step-ups off** risks RISK_PCT every trade; **Step-ups on** raises it by RISK_STEPS as the balance grows "
        "(back to RISK_PCT if the balance falls 5% from its best).",
    ]
    if (RESULTS / "SP12v4_nohalf.txt").exists():
        lines += section("SP12v4: selling half at +2R vs not", "SP12v4",
                         [("Sell half at +2R", "SP12v4"), ("No half sell", "SP12v4_nohalf")])
        lines += ["", "Both risk 0.5% per trade (RISK_PCT) with step-ups off. Without the half sell, the whole position runs "
                  "to the stop, trailing stop, target or time exit."]
    for name in names:
        lines += section(name, name, [("Step-ups off", name), ("Step-ups on", f"{name}_steps")])
    extra = RESULTS / "EXTRA_TESTS.md"  # hand-kept tests from other tools, kept on every rebuild
    if extra.exists():
        lines += ["", extra.read_text().rstrip()]
    (RESULTS / "SUMMARY.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])
