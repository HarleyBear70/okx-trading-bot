"""
STRUCT_T2 (Tier 2a): order blocks on top of Tier 1 (research/struct_t1.py). Issue #6/#9, Jeff + Chrome Claude, Oct 13 2026.
Rules (Brad Ep 7, 9, 10, 25; Jeff's answers on #9):
  OB        every Tier 1 BOS / MS makes a candidate. The move = from its launch candle (Tier 1 STRONG candle) to the break.
            It must leave a fair value gap inside that move (bull: candle 1 high < candle 3 low; bear = mirror). No gap = no OB.
            "Sharp" = the gap itself; no size number (Jeff, Q2).
            Box = ONE candle, wick to wick (Jeff, Q1): the last opposite-colour candle (red for a bull OB) from the launch
            candle up to the gap's candle 1; if there is none, the launch candle itself.
            [CLAUDE: which candle when the move has several red candles = the last one before the gap]
  Fresh     price has not come back to the box's 50% line since the break. Used = removed.
  Show      only on the latest candle, only zones that are: fresh, WITH the current Tier 1 trend (demand in an uptrend,
            supply in a downtrend), in the right half of the current fib STRONG-WEAK (demand in discount, supply in premium),
            and the NEAREST one to price on each side (Jeff, Q3: 1 buy below, 1 sell above).
            [CLAUDE: "in discount" = the box's 50% line is below the fib 50%]
  python3 research/struct_t2.py   BTCUSD 1H Binance.US: every OB made in the last 7 days + when it was used, and what shows now
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import struct_t1 as T  # noqa: E402


def zones(rows):
    """returns (zones, engine, times); zone = dict(side, made, ob, top, bot, used)"""
    tm = [T.et(int(r[0])) for r in rows]
    o, h, l, c = ([float(r[i]) for r in rows] for i in (1, 2, 3, 4))
    s = T.Tier1(h, l, c)
    out = []
    for k in range(len(rows)):
        for b, ev, _ in s.step(k):
            if not (ev.startswith("BOS") or ev.startswith("MS")):
                continue
            up = s.trend == 1
            a = s.sb  # launch candle of this break
            gap = next((j for j in range(a + 1, b) if (h[j - 1] < l[j + 1] if up else l[j - 1] > h[j + 1])), None)
            if gap is None:
                continue
            red = [x for x in range(a, gap) if (c[x] < o[x] if up else c[x] > o[x])]
            ob = red[-1] if red else a
            out.append(dict(side="demand" if up else "supply", made=b, ob=ob, top=h[ob], bot=l[ob], used=None, ev=ev))
        for z in out:  # fresh until price trades back to the 50% line (candles after the break)
            if z["used"] is None and k > z["made"]:
                mid = (z["top"] + z["bot"]) / 2
                if (l[k] <= mid) if z["side"] == "demand" else (h[k] >= mid):
                    z["used"] = k
    return out, s, tm, c


def shown(zs, s, close):
    """what the chart shows on the latest candle"""
    mid = (s.strong + s.weak) / 2
    up = s.trend == 1
    best = None
    for z in zs:
        zm = (z["top"] + z["bot"]) / 2
        if z["used"] is not None or (z["side"] == "demand") != up:
            continue
        if up and zm < mid and z["top"] < close and (best is None or z["top"] > best["top"]):
            best = z
        if not up and zm > mid and z["bot"] > close and (best is None or z["bot"] < best["bot"]):
            best = z
    return best


def main():
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSD"
    rows = T.binance_us(sym)
    zs, s, tm, c = zones(rows)
    cut = tm[-1] - dt.timedelta(days=7)
    print(f"{sym} 1H Binance.US, times ET (candle open). Order blocks made in the last 7 days:")
    print("made by              OB candle          side     box (bottom - top)       used (price back to its 50%)")
    for z in zs:
        if tm[z["made"]] >= cut:
            u = f"{tm[z['used']]:%a %b %d %I %p}" if z["used"] is not None else "FRESH"
            print(f"{z['ev']:8} {tm[z['made']]:%a %d %I %p}  {tm[z['ob']]:%a %b %d %I %p}  {z['side']:7}  {z['bot']:<10g} - {z['top']:<10g}  {u}")
    b = shown(zs, s, c[-1])
    tr = "UP" if s.trend == 1 else "DOWN"
    print(f"\nNow ({tm[-1]:%a %b %d %I %p}): trend {tr}, fib STRONG {s.strong:g} / WEAK {s.weak:g}, 50% {(s.strong + s.weak) / 2:g}, close {c[-1]:g}")
    print("Chart shows:", f"{b['side']} {b['bot']:g} - {b['top']:g} (OB candle {tm[b['ob']]:%a %b %d %I %p})" if b else
          "no zone (none fresh, with the trend, in the right half)")


if __name__ == "__main__":
    main()
