"""
STRUCT_SD (Tier 2, supply / demand zones): on top of Tier 1 (research/struct_t1.py). Replaces the Tier 2a order blocks on
the chart (Jeff, Oct 14 2026, #9: "i like seeing the supplies and demands as talked about"; OB "not sure yet").
Same logic as pine/structure_sd.pine. Rules from Jeff's SOL 15m Oct 13 drawing (A 4:00 AM, B 10:15 AM, C 3:00 PM, D 11:30 PM):
  Zone      ONE candle, wick to wick (Jeff).
  Supply A  where the current bearish move started (Jeff), at the top of the run: from the top candle (Tier 1's new STRONG
            after an MS DOWN), the last GREEN candle before the first body close below the top candle's low (Oct 13: 4:00 AM,
            Oct 12: 1:00 AM 113.02-113.39, Chrome). If none, the last green candle before the top candle. [CLAUDE's wording]
            Nothing older than A. A body close above A = the bearish move is over (Jeff: "ceiling = A"). A stays on its own.
  Supply B, C, D ...  every later top: a green candle followed by a red candle (Jeff: "a place to stop and pull back to
            to get fuel"). Overlapping zones all show (Jeff).
  Removed   only when a candle BODY closes past its far edge (above the top for supply). A wick past = sweep, it stays (Jeff).
  Demand    mirror: A = the last RED candle before the latest MS UP candle; then every red candle followed by a green one.
  Shown     supply whose 50% is in premium (above the fib 50%), demand whose 50% is in discount. Both sides (Jeff).
  Letters   per side, A = farthest from price, then B, C ... by the box's 50%. [CLAUDE: order by the box's 50%]
  Groups    "same area" boxes = one box, one letter (Jeff, demand Oct 13: A alone | 7:45+8:30+9:00 | 9:45+7PM+7:45PM).
            Going from A toward price, a box joins the group when its 50% is inside the group's first box. [CLAUDE's rule]
  python3 research/struct_sd.py FILE "10-13 23:45"   zones at that candle (OKX 15m json, times ET)
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import struct_t1 as T  # noqa: E402


def opp(o, c, x, sd):
    return c[x] < o[x] if sd == 1 else c[x] > o[x]


def anchor(o, h, l, c, top, b, sd):
    """A: from the top candle of the run (Tier 1's new STRONG candle), the last green (demand: red) candle before the
    first body close below the top candle's low (demand: above its high). If none, the last one before the top candle."""
    j = top + 1
    while j <= b and not (c[j] > h[top] if sd == 1 else c[j] < l[top]):
        j += 1
    xs = [x for x in range(top, j) if opp(o, c, x, sd)]
    if xs:
        return xs[-1]
    return next((x for x in range(top - 1, -1, -1) if opp(o, c, x, sd)), None)


def groups(z, h, l, a):
    """A alone; the rest, farthest from price first: a box joins the group when its 50% is inside the group's first box"""
    out = []
    for j in z:
        m = (h[j] + l[j]) / 2
        if out and out[-1][0] != a and l[out[-1][0]] <= m <= h[out[-1][0]]:
            out[-1].append(j)
        else:
            out.append([j])
    return out


def run(rows, at):
    tm = [T.et(int(r[0])) for r in rows]
    o, h, l, c = ([float(r[i]) for r in rows] for i in (1, 2, 3, 4))
    s = T.Tier1(h, l, c)
    anc = {1: None, -1: None}  # demand A, supply A (candle index)
    z = {1: [], -1: []}
    for k in range(len(rows)):
        for b, ev, _ in s.step(k):
            if ev in ("MS UP", "MS DOWN"):
                sd = 1 if ev == "MS UP" else -1
                j = anchor(o, h, l, c, s.sb, b, sd)
                if j is not None:
                    anc[sd], z[sd] = j, [j]
        for sd in (1, -1):
            a = anc[sd]
            if a is not None and k - 1 > a:
                if (c[k - 1] < o[k - 1] and c[k] > o[k]) if sd == 1 else (c[k - 1] > o[k - 1] and c[k] < o[k]):
                    z[sd].append(k - 1)
            z[sd] = [j for j in z[sd] if not (c[k] < l[j] if sd == 1 else c[k] > h[j])]
        if f"{tm[k]:%m-%d %H:%M}" == at:
            mid = (s.strong + s.weak) / 2
            print(f"{tm[k]:%a %b %d %H:%M} ET  close {c[k]}  trend {'UP' if s.trend == 1 else 'DOWN'}  STRONG {s.strong}  WEAK {s.weak}  fib 50% {mid:.3f}")
            for sd, name in ((-1, "SUPPLY (premium)"), (1, "DEMAND (discount)")):
                show = [j for j in z[sd] if ((h[j] + l[j]) / 2 > mid if sd == -1 else (h[j] + l[j]) / 2 < mid)]
                show.sort(key=lambda j: (-(h[j] + l[j]) if sd == -1 else (h[j] + l[j]), l[j] - h[j]))  # tie: bigger box first (Chrome)
                if anc[sd] in show:  # A first, on its own
                    show.remove(anc[sd])
                    show.insert(0, anc[sd])
                print(" ", name)
                for n, g in enumerate(groups(show, h, l, anc[sd])):
                    print(f"    {'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[n] if n < 26 else n + 1}  {min(l[j] for j in g)} - {max(h[j] for j in g)}   (" + ", ".join(f"{tm[j]:%m-%d %H:%M}" for j in g) + ")")


if __name__ == "__main__":
    run(json.load(open(sys.argv[1])), sys.argv[2])
