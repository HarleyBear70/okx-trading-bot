"""Write results/COMMUNITY.md from results/community/<Strategy>_<fee>.txt (freqtrade backtesting output).

Each strategy from github.com/freqtrade/freqtrade-strategies, its own timeframe, BTC ETH SOL XRP on OKX, 2022-01 to now,
at Jeff's real fee (0.35%) and at the 0.1% these scripts are usually shown with. Usage: python3 freqtrade/community_summary.py
"""
import re
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results" / "community"
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def metrics(text):
    out = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("│").split("│")]
        if len(cells) == 2 and cells[0] and cells[0] not in out:
            out[cells[0]] = cells[1]
    m = re.search(r"Timeframe:?\s*│?\s*(\w+)", text) or re.search(r"timeframe[\"': ]+(\w+)", text)
    out["_tf"] = out.get("Timeframe", m.group(1) if m else "?")
    return out


def num(s):
    m = re.search(r"-?[\d.]+", s or "")
    return float(m.group()) if m else None


rows = []
for f in sorted(RES.glob("*_0.0035.txt")):
    name = f.name[: -len("_0.0035.txt")]
    real = metrics(ANSI.sub("", f.read_text(errors="replace")))
    low_f = RES / f"{name}_0.001.txt"
    low = metrics(ANSI.sub("", low_f.read_text(errors="replace"))) if low_f.exists() else {}
    if "Total profit %" not in real:
        rows.append((None, f"| {name} | - | - | - | - | - | - | - | did not run (see results/community/{f.name}) |"))
        continue
    p = num(real.get("Total profit %"))
    rows.append((p, f"| {name} | {real.get('_tf')} | {real.get('Total/Daily Avg Trades', '-')} | {real.get('Total profit %')} | "
                    f"{real.get('Max % of account underwater', '-')} | {real.get('Profit factor', '-')} | "
                    f"{low.get('Total profit %', '-')} | {low.get('Max % of account underwater', '-')} | |"))
rows.sort(key=lambda r: (r[0] is None, -(r[0] or 0)))
md = ["# Freqtrade community strategies at Jeff's real fee", "",
      f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC by .github/workflows/freqtrade-community.yml. Every strategy in "
      "github.com/freqtrade/freqtrade-strategies (user_data/strategies and berlinguyinca), unchanged, each on its own timeframe, "
      "BTC ETH SOL XRP (OKX), 2022-01-01 to now, max 3 open, all-in stake as the scripts expect. Sorted by profit at 0.35%. "
      "These are the community's own settings (no tuning); most were written for Binance with lower fees.", "",
      "| Strategy | Timeframe | Trades | Profit at 0.35% fee | Max underwater | PF | Profit at 0.1% fee | Max underwater (0.1%) | Note |",
      "|---|---|---|---|---|---|---|---|---|"] + [r for _, r in rows]
(HERE / "results" / "COMMUNITY.md").write_text("\n".join(md) + "\n")
print(f"{len(rows)} strategies summarised")
