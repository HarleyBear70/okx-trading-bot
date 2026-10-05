"""
H1 safety switch (halve risk when the combined balance is X% below its best) and volatility sizing.
Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md.

Run:
  python research/h1_safety.py        # writes research/H1_SAFETY.md
"""
import bisect
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402


def switch(x, back_to):
    """back_to: 'half' (halfway back to the best) or 'peak'."""
    st = {"peak": None, "low": None, "on": False}

    def on_bar(ctx):
        v = ctx["combined"]
        st["peak"] = v if st["peak"] is None else max(st["peak"], v)
        if not st["on"] and v <= st["peak"] * (1 - x):
            st["on"], st["low"] = True, v
        if st["on"]:
            st["low"] = min(st["low"], v)
            level = st["peak"] if back_to == "peak" else st["low"] + 0.5 * (st["peak"] - st["low"])
            if v >= level:
                st["on"] = False

    return on_bar, (lambda ctx, name, coin, bars, k: 0.5 if st["on"] else 1.0)


def vol_sizing():
    cache = {}

    def atr_pct_rank(bars):
        key = id(bars)
        if key not in cache:
            h, l, c = ([b[x] for b in bars] for x in "hlc")
            a = bot.atr(h, l, c, 14)
            val = [a[i] / c[i] if a[i] else None for i in range(len(bars))]
            med, q, ordered = [None] * len(bars), deque(), []
            for i, v in enumerate(val):
                if len(ordered) >= 100:
                    med[i] = ordered[len(ordered) // 2]
                if v is not None:
                    q.append(v)
                    bisect.insort(ordered, v)
                    if len(q) > 540:
                        ordered.pop(bisect.bisect_left(ordered, q.popleft()))
            cache[key] = (val, med)
        return cache[key]

    def mult(ctx, name, coin, bars, k):
        val, med = atr_pct_rank(bars)
        if val[k] is None or med[k] is None or val[k] <= 0:
            return 1.0
        return min(max(med[k] / val[k], 0.5), 1.5)  # 0.25%-0.75% around the 0.5% base

    return None, mult


def main():
    specs = e.demo_specs()
    versions = {"current (no switch)": (None, None), "W1: 5%, back halfway": switch(0.05, "half"),
                "W2: 6%, back to the best": switch(0.06, "peak"), "W3: 8%, back to the best": switch(0.08, "peak"),
                "V1: volatility sizing": vol_sizing()}
    res = {}
    for name, (on_bar, mult) in versions.items():
        res[name] = {}
        for h, t0, t1 in e.HALVES:
            if name.startswith("W"):  # fresh switch state per half
                on_bar, mult = {"W1": switch(0.05, "half"), "W2": switch(0.06, "peak"),
                                "W3": switch(0.08, "peak")}[name[:2]]
            r = e.multi_sim(specs, t0, t1, on_bar=on_bar, risk_mult=mult)
            ret, dd, rd = e.ret_dd(r["combined"])
            res[name][h] = {"ret": ret, "dd": dd, "rd": rd, "v4": r["bots"]["v4"], "tr": r["bots"]["tr"]}
        print(f"done {name}", flush=True)
    base = res["current (no switch)"]
    lines = ["# H1 safety switch and volatility sizing", "",
             "Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider as they trade, "
             "$1,000 each; combined = the sum. Script: research/h1_safety.py.", "",
             "| Version | Half | Combined return | Combined max DD | Return/DD | v4 return / DD | TR return / DD | Pass? |",
             "|---|---|---|---|---|---|---|---|"]
    verdicts = []
    for name in versions:
        ok = name != "current (no switch)" and all(
            res[name][h]["dd"] > base[h]["dd"] and res[name][h]["ret"] >= 0.9 * base[h]["ret"] for h in base)
        for h, _, _ in e.HALVES:
            r = res[name][h]
            lines.append(f"| {name} | {h} | {r['ret']:+.1f}% | {r['dd']:.1f}% | {r['rd']:.2f} | "
                         f"{r['v4']['ret']:+.1f}% / {r['v4']['dd']:.1f}% | {r['tr']['ret']:+.1f}% / {r['tr']['dd']:.1f}% | "
                         f"{'-' if name.startswith('current') else ('PASS' if ok else 'fail')} |")
        if not name.startswith("current"):
            verdicts.append(f"- {name}: {'PASS' if ok else 'fail'}")
    lines += [""] + verdicts
    with open(os.path.join(HERE, "H1_SAFETY.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
