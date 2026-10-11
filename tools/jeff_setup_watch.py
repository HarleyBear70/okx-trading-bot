"""
Watches a setup Jeff described but couldn't wait for (Oct 11 2026, LINK: "i was waiting on it to break the 4hr high and
do a ms to set a short"). Paper only, never trades. Runs every 15 min in jeff-bot.yml.

  1) a 15m candle trades above the level (the 4H high)              -> the fuel grab Jeff expects
  2) then the 15m heartbeat makes an MS DOWN (research/jeff_struct.py) -> proof that sellers took over
  3) a paper sell limit goes into journal/jeff_paper_trades.csv; tools/jeff_paper_check.py fills and scores it
       [NOT JEFF, Claude's fill-ins since he had to leave]: entry = 50% of the new 15m down leg (premium),
       stop = the highest high since the break + 0.05%, target = 2R. Cancelled if price hits the target before
       filling or 8 h pass unfilled. Setup expires 24 h after it was set if steps 1-2 never happen.
State: journal/jeff_setups.json
"""
import csv
import datetime as dt
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "research"))
sys.path.insert(0, os.path.join(HERE, "tools"))
from heartbeat_watch import ET, fetch  # noqa: E402
from jeff_struct import Heart  # noqa: E402

SETUPS = os.path.join(HERE, "journal", "jeff_setups.json")
CSV = os.path.join(HERE, "journal", "jeff_paper_trades.csv")
M15, GAP = 900000, 0.0005


def et(ms):
    return dt.datetime.fromtimestamp(ms / 1000, ET).strftime("%Y-%m-%d %H:%M")


def note(msg):
    print(msg)
    if os.environ.get("GH_TOKEN"):
        subprocess.run(["gh", "issue", "comment", "4", "--body", "From terminal Claude (Jeff's setup watch): " + msg], check=False)


def set_row(key, **kv):
    with open(CSV, newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    if not any(r["date_et"] == key for r in rows):
        rows.append({k: "" for k in fields} | {"date_et": key})
    for r in rows:
        if r["date_et"] == key:
            r.update(kv)
    with open(CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def run(s):
    d = fetch(f"{s['coin']}-USDT", "15m")
    h, l, c = ([float(r[i]) for r in d] for i in (2, 3, 4))
    hb = Heart(h, l, c, 1)
    for k in range(len(d)):
        ev = hb.step(k)
        t = int(d[k][0]) + M15
        if t <= s["last"]:
            continue
        s["last"] = t
        if s["stage"] == "wait_break":
            if h[k] > s["level"]:
                s["stage"], s["top"] = "wait_ms", h[k]
                note(f"{s['coin']} 15m traded above the 4H high {s['level']} (high {h[k]}) at {et(t)} ET. Waiting for a 15m MS down.")
            elif t > s["expires"]:
                s["stage"] = "expired"
                note(f"{s['coin']} setup expired: price never broke {s['level']}.")
        elif s["stage"] == "wait_ms":
            s["top"] = max(s["top"], h[k])
            if ev == "MS DOWN":
                lo, hi = hb.rng
                entry = round((lo + hi) / 2, 6)
                stop = round(s["top"] * (1 + GAP), 6)
                risk = stop - entry
                if risk <= 0:
                    continue
                tgt = round(entry - 2 * risk, 6)
                s.update(stage="order", key=et(t), entry=entry, stop=stop, target=tgt, placed=t)
                set_row(s["key"], coin=f"{s['coin']}-USDT", venue="paper (set by Claude for Jeff)", tf="15m", side="short",
                        entry=entry, stop=stop, target=tgt, risk_pts=round(risk, 6), rr_planned="2.00",
                        status="sell limit (Claude, for Jeff)",
                        lesson=f"Jeff's setup while he was away: broke the 4H high {s['level']} (top {s['top']}), then 15m MS DOWN. "
                               "Entry 50% of the new 15m leg, stop above the top +0.05%, target 2R = Claude's fill-ins.")
                note(f"{s['coin']} 15m MS DOWN at {et(t)} ET after the break. Paper sell limit {entry}, stop {stop}, target {tgt} (2R).")
            elif t > s["expires"]:
                s["stage"] = "expired"
                note(f"{s['coin']} setup expired: broke {s['level']} but no 15m MS down within the time limit.")
        elif s["stage"] == "order":
            if h[k] >= s["entry"]:
                s["stage"] = "filled"  # jeff_paper_check.py takes it from here
            elif l[k] <= s["target"] or t - s["placed"] > 8 * 3600000:
                s["stage"] = "cancelled"
                why = "price reached the target before filling" if l[k] <= s["target"] else "8 h without a fill"
                set_row(s["key"], status=f"cancelled ({why})")
                note(f"{s['coin']} paper short cancelled: {why}.")


def main():
    try:
        with open(SETUPS) as f:
            setups = json.load(f)
    except (OSError, ValueError):
        return
    for s in setups:
        if s["stage"] in ("wait_break", "wait_ms", "order"):
            try:
                run(s)
            except Exception as ex:
                print(f"setup watch failed: {ex}")
    with open(SETUPS, "w") as f:
        json.dump(setups, f, indent=1)


if __name__ == "__main__":
    main()
