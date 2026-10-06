"""
F18: entries and position sizing (research/F18_PLAN.md). Research only.

  python research/f18_sizing.py <TR|DC> <Z0|Z1|Z2|AD>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402

kind, v = sys.argv[1], sys.argv[2]
cs, per, risk, mo = f10.prepare(kind, 3.0)
if kind == "DC":
    risk = 0.0032
small = {"TR": (100, 0.06), "DC": (80, 0.06)}[kind]  # F18b
opts = {"Z1s": {"sizing": "usd", "size_arg": small[0]}, "Z2s": {"sizing": "pct", "size_arg": small[1]}, "Z0": {}, "Z1": {"sizing": "usd", "size_arg": 250 if kind == "TR" else 200},
        "Z2": {"sizing": "pct", "size_arg": 0.25 if kind == "TR" else 0.20}, "AD": {"avg_down": True}}[v]
out = {"bot": kind, "variant": v}
for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
    r = f10.sim(cs, per, risk, mo, False, t0, t1, **opts)
    out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                "win": round(r["win"])}
print(json.dumps(out), flush=True)
