"""F18c: Donchian as live (pyramid + BTC leash) with fixed-% sizing. python research/f18c.py <risk|0.03|...> [u]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402
arg, unseen = sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "u"
cs, per, _, mo = f10.prepare("DC", 3.0, unseen=unseen, leash=True)
opts = {} if arg == "risk" else {"sizing": "pct", "size_arg": float(arg)}
out = {"size": arg, "unseen": unseen}
for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
    r = f10.sim(cs, per, 0.0032, mo, True, t0, t1, **opts)
    out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"]}
print(json.dumps(out), flush=True)
