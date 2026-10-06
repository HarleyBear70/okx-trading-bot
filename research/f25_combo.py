"""F25 follow-up: Donchian + Trend Analysis (C1 / C2), same account, P/L adds up. Plus a C2 diagnostic by coin."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as e  # noqa: E402
import f24_jeff2 as f24  # noqa: E402
import f25_tas as f25  # noqa: E402


def add(*cvs):
    ds, last, out = [dict(c) for c in cvs], [1000.0] * len(cvs), []
    for ts in sorted({t for c in cvs for t, _ in c}):
        for j, d in enumerate(ds):
            last[j] = d.get(ts, last[j])
        out.append((ts, 1000 + sum(v - 1000 for v in last)))
    return out


cs = f24.DESIGN
raw = e.load(cs)
data = {c: (d, d) for c, (b, d) in raw.items() if d}
for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
    dc = e.trade_sim(cs, data, f24.dc_entries, t0, t1, risk=0.0035, max_open=5, fee=0.0035, manage=f24.dc_manage)["curve"]
    rows = [("DC alone", dc)]
    for v in ("C1", "C2"):
        rows.append((f"DC + {v}", add(dc, f25.run(v, False, [(lab, t0, t1)])["_curve"])))
    for name, cv in rows:
        r, dd, ratio = e.ret_dd(cv)
        print(f"{lab:9} {name:10} ret {r:7.1f}%  dd {dd:6.1f}%  ret/dd {ratio:5.1f}", flush=True)

print("C2 on never-seen coins, one coin at a time (full period):")
for c in [c for c in e.UNSEEN if c not in f24.DESIGN]:
    r = f25.run("C2", True, [("full", e.START, None)], [c])
    if "full" in r:
        print(f"  {c:5} ret {r['full']['ret']:7.1f}%  dd {r['full']['dd']:6.1f}%  pf {r['full']['pf']}", flush=True)
