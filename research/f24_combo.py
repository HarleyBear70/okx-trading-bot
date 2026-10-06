import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine as e, f24_jeff2 as f
cs = f.DESIGN
raw = e.load(cs)
data = {c: (d, d) for c, (b, d) in raw.items() if d}
def curve(ent, man, risk, t0=e.START, t1=None):
    return e.trade_sim(cs, data, ent, t0, t1, risk=risk, max_open=5, fee=f.FEE, manage=man)["curve"]
for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
    dc = curve(f.dc_entries, f.dc_manage, 0.0035, t0, t1)
    a3 = curve(*f.tlb_entries(False), 0.004, t0, t1)
    b1 = curve(*f.crts_entries(85), 0.004, t0, t1)
    def add(*cvs):  # all bots on the same account, each risking its own % (pnl adds up)
        ds = [dict(c) for c in cvs]; out, last = [], [1000.0] * len(cvs)
        for ts in sorted({t for c in cvs for t, _ in c}):
            for j, d in enumerate(ds):
                last[j] = d.get(ts, last[j])
            out.append((ts, 1000 + sum(v - 1000 for v in last)))
        return out
    for name, cv in [("DC alone", dc), ("DC + A3", add(dc, a3)), ("DC + B1", add(dc, b1)), ("DC + A3 + B1", add(dc, a3, b1))]:
        r, dd, ratio = e.ret_dd(cv)
        print(f"{lab:9} {name:14} ret {r:7.1f}%  dd {dd:6.1f}%  ret/dd {ratio:5.1f}")
