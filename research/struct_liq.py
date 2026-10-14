"""
STRUCT_LIQ (Tier 2b, liquidity "$$$"): on top of Tier 1 + zones. Jeff, Oct 14 2026 (#9). Same logic as the liquidity
part of pine/structure_sd.pine.
  $$$ sits above wicks (Jeff). When a group of tops lines up at about the same level, the $$$ sits above them (supply
  side) / below a group of bottoms (demand side). A wick reaches out to grab it, then price pulls back: once a wick
  takes it, it is gone ("the fuel station is empty").
  Day      yesterday's daily candle high and low (TradingView's own day = 00:00 UTC for crypto). Gone once today's
           wick goes past it. [CLAUDE: Jeff unsure which day method; the standard one, Jeff OK'd the proposal]
  Equal    a top = a green candle followed by a red candle (same as the supply zones); its wick = the higher of the
           two candles' highs, its upper wick runs down to that candle's body top. Two tops are "equal highs" when the
           later top's high reaches into the earlier top's upper wick (between its body top and its high) and no
           wick in between went past the earlier high. $$$ = the earlier (highest) high. Bottoms = mirror.
           Only tops made since the start of the current fib leg (here and now). One line per group: a level inside
           another level's wick is dropped. [CLAUDE's rules, no number]
  python3 research/struct_liq.py FILE "10-14 13:00"   (rows: OKX layout [ts, o, h, l, c], times ET)
"""
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import struct_t1 as T  # noqa: E402


def run(rows, at):
    tm = [T.et(int(r[0])) for r in rows]
    o, h, l, c = ([float(r[i]) for r in rows] for i in (1, 2, 3, 4))
    s = T.Tier1(h, l, c)
    tops, bots = [], []  # [bar, wick, body edge, is_equal]
    day, dhi, dlo, pdh, pdl = None, None, None, None, None
    for k in range(len(rows)):
        s.step(k)
        d = int(rows[k][0]) // 86400000
        if d != day:
            pdh, pdl = dhi, dlo
            day, dhi, dlo = d, h[k], l[k]
        else:
            dhi, dlo = max(dhi, h[k]), min(dlo, l[k])
        # a wick past a top / bottom takes it
        tops = [t for t in tops if h[k] <= t[1]]
        bots = [b for b in bots if l[k] >= b[1]]
        if k >= 1 and c[k - 1] > o[k - 1] and c[k] < o[k]:
            j = k - 1 if h[k - 1] >= h[k] else k
            w, edge = h[j], max(o[j], c[j])
            for t in tops:
                if t[2] <= w <= t[1]:
                    t[3] = True
            tops.append([j, w, edge, False])
        if k >= 1 and c[k - 1] < o[k - 1] and c[k] > o[k]:
            j = k - 1 if l[k - 1] <= l[k] else k
            w, edge = l[j], min(o[j], c[j])
            for b in bots:
                if b[1] <= w <= b[2]:
                    b[3] = True
            bots.append([j, w, edge, False])
        if f"{tm[k]:%m-%d %H:%M}" == at:
            start = min(s.sb, s.wb)
            print(f"{tm[k]:%a %b %d %H:%M} ET  close {c[k]}  trend {'UP' if s.trend == 1 else 'DOWN'}  STRONG {s.strong}  WEAK {s.weak}")
            print(f"  yesterday high {pdh}{'' if dhi <= pdh else '  (taken today)'}   yesterday low {pdl}{'' if dlo >= pdl else '  (taken today)'}")
            for name, xs in (("equal highs $$$", tops), ("equal lows $$$", bots)):
                lv = [x for x in xs if x[3] and x[0] >= start]
                # one line per group: drop a level that sits inside another level's wick
                lv = [x for x in lv if not any(y is not x and min(y[1], y[2]) <= x[1] <= max(y[1], y[2]) and y[1] != x[1] for y in lv)]
                print(f"  {name}: " + (", ".join(f"{x[1]} ({tm[x[0]]:%m-%d %H:%M})" for x in lv) or "none"))


if __name__ == "__main__":
    run(json.load(open(sys.argv[1])), sys.argv[2])
