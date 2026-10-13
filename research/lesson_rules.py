"""Lesson candidate rules on Trend Rider (design coins + never-seen coins). python research/lesson_rules.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f10_exits as f10  # noqa: E402


def ok_for(v, bars):
    h, l, c, vol = ([x[f] for x in bars] for f in "hlcv")
    n = len(bars)
    if v == "follow":  # entry moves to the next candle, only if it closes above the breakout candle's high
        return None
    if v == "st4h":
        d = bot.supertrend(h, l, c, 3, 10)
        return [d[k] == -1 for k in range(n)]
    if v == "vol":
        return [k >= 20 and vol[k] >= sum(vol[k - 20:k]) / 20 for k in range(n)]
    return [True] * n


def run(v, unseen):
    cs, per, risk, mo = f10.prepare("TR", 3.0, unseen=unseen)
    if v != "base":
        for c in cs:
            bars, ent, trail = per[c]
            if v == "follow":
                new = {}
                for k, sl in ent.items():
                    if k + 1 < len(bars) and bars[k + 1]["c"] > bars[k]["h"]:
                        new[k + 1] = min(sl, bars[k + 1]["c"] * 0.995)
                per[c] = (bars, new, trail)
            else:
                ok = ok_for(v, bars)
                per[c] = (bars, {k: s for k, s in ent.items() if ok[k]}, trail)
    out = {}
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        r = f10.sim(cs, per, risk, mo, False, t0, t1)
        out[lab] = f"{r['ret']:+.0f}% / DD {r['dd']:.1f}% / PF {r['pf']:.2f} / {r['trades']} trades"
    return out


if __name__ == "__main__":
    lines = ["| Rule | Coins | Full | 1st half | 2nd half |", "|---|---|---|---|---|"]
    for v in ["base", "follow", "st4h", "vol"]:
        for u in (False, True):
            o = run(v, u)
            lines.append(f"| {v} | {'never-seen' if u else 'design'} | {o['full']} | {o['1st half']} | {o['2nd half']} |")
            print(lines[-1], flush=True)
    open(os.path.join(HERE, "lesson_rules_out.md"), "w").write("\n".join(lines) + "\n")
