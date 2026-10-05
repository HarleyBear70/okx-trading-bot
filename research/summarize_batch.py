"""Turn the research batch logs into one plain-English scoreboard (research/BATCH1.md)."""
import re
import sys
from datetime import datetime, timezone

tests_file, log_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return re.sub(r"\x1b\[[0-9;]*m", "", f.read())
    except FileNotFoundError:
        return ""


def metric(txt, label):
    m = re.search(r"│ " + re.escape(label) + r"\s*│\s*([-\d.]+)", txt)
    return float(m.group(1)) if m else None


def row(txt, strat):
    for line in txt.splitlines():
        if f"│ {strat} │" in line and "TOTAL" not in line:
            cells = [c.strip() for c in line.split("│")[1:-1]]
            if len(cells) >= 5:
                try:
                    return int(cells[1]), float(cells[4])
                except ValueError:
                    pass
    return None


lines = ["# Research batch 1: what works and what doesn't", "",
         f"Updated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. OKX prices, Mar 2024 to now, "
         "1,000 USDT start, 0.1% fee, max 3 trades open. "
         "Pass = profit factor 1.3+, worst drop under 10%, beats just holding the coins, and makes money in both halves.",
         "", "| Test | Trades | Profit | Profit factor | Worst drop | Just holding | 1st half | 2nd half | Verdict |",
         "|---|---|---|---|---|---|---|---|---|"]
for i, spec in enumerate(open(tests_file).read().strip().splitlines()):
    name, strat, tf, pairs = spec.split("|")
    full, h1, h2 = (read(f"{log_dir}/{i}_{part}.txt") for part in ("full", "h1", "h2"))
    r, r1, r2 = row(full, strat), row(h1, strat), row(h2, strat)
    pf = metric(full, "Profit factor")
    dd = metric(full, "Max % of account underwater")
    mk = metric(full, "Market change")
    if r is None:
        lines.append(f"| {name} | - | - | - | - | - | - | - | Error (see logs) |")
        continue
    trades, prof = r
    p1 = r1[1] if r1 else None
    p2 = r2[1] if r2 else None
    both = p1 is not None and p2 is not None and p1 > 0 and p2 > 0
    if both and pf and pf >= 1.3 and dd is not None and dd < 10 and mk is not None and prof > mk:
        verdict = "**Pass**"
    elif both and prof > 0:
        verdict = "Watch"
    else:
        verdict = "Fail"
    f = lambda x, s="%": "-" if x is None else f"{x:+.1f}{s}"
    lines.append(f"| {name} | {trades} | {f(prof)} | {'-' if pf is None else f'{pf:.2f}'} | "
                 f"{'-' if dd is None else f'{dd:.1f}%'} | {f(mk)} | {f(p1)} | {f(p2)} | {verdict} |")
lines += ["", "Full logs: research/batch_logs/. Just holding = average change of the same coins over the same time.", ""]
open(out, "w").write("\n".join(lines))
print("\n".join(lines))
