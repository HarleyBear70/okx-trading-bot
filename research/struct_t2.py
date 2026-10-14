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
  Show      every zone that is fresh and INSIDE the right half of the current fib (Jeff "Way 2": demand between STRONG
            and the 50%, supply between the 50% and STRONG; the box's 50% line decides); switch "only WITH the trend" (demand in an uptrend, supply in a downtrend). Letters per side (Jeff,
            Oct 13 #9): A = the extreme zone (farthest from price), then B, C, ... toward price. No cap (Jeff).
  python3 research/struct_t2.py sol15 FILE   SOL 15m (OKX json) lettered zones every 3 hours on Oct 12
  python3 research/struct_t2.py   BTCUSD 1H Binance.US: every OB made in the last 7 days + when it was used, and what shows now
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import struct_t1 as T  # noqa: E402


def zones(rows, snaps=()):
    """returns (zones, engine, times); zone = dict(side, made, ob, top, bot, used)"""
    tm = [T.et(int(r[0])) for r in rows]
    o, h, l, c = ([float(r[i]) for r in rows] for i in (1, 2, 3, 4))
    s = T.Tier1(h, l, c)
    out, snap = [], {}
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
        if k in snaps:
            snap[k] = (s.trend, s.strong, s.weak, c[k], [dict(z) for z in out if z["used"] is None])
    return out, s, tm, c, snap


def lettered(trend, strong, weak, fresh, with_trend=True):
    """the zones the chart shows, per side, lettered A (farthest from price) -> B, C ... (nearest)"""
    mid = (strong + weak) / 2
    out = {}
    for side, sgn in (("demand", 1), ("supply", -1)):
        if with_trend and sgn != trend:
            continue
        lo, hi = (min(strong, mid), mid) if sgn == 1 else (mid, max(strong, mid))  # Way 2: inside the fib, STRONG to 50%
        zs = [z for z in fresh if z["side"] == side and lo <= (z["top"] + z["bot"]) / 2 <= hi]
        zs.sort(key=lambda z: z["bot"] if sgn == 1 else -z["top"])  # farthest from price first
        out[side] = [(chr(65 + i) if i < 26 else str(i + 1), z) for i, z in enumerate(zs)]
    return out


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "sol15":  # Chrome's check: SOL 15m OKX, Oct 12, both sides (switch off on Jeff's chart)
        import json
        rows = json.load(open(sys.argv[2]))
        tm = [T.et(int(r[0])) for r in rows]
        snaps = [k for k, t in enumerate(tm) if t.month == 10 and t.day == 12 and t.minute == 0 and t.hour in (0, 3, 6, 9, 12, 15, 18, 21)]
        zs, s, tm, c, snap = zones(rows, snaps)
        print("SOL-USDT 15m OKX, history from", f"{tm[0]:%b %d}", f"({len(rows)} candles). Times ET. Both sides shown (switch off).")
        for k in snaps:
            tr, st, wk, cl, fresh = snap[k]
            print(f"\n{tm[k]:%a %b %d %I:%M %p} close {cl:g}: trend {'UP' if tr == 1 else 'DOWN'}, STRONG {st:g}, WEAK {wk:g}, 50% {(st + wk) / 2:g}")
            for side, lst in lettered(tr, st, wk, fresh, with_trend=False).items():
                for L, z in lst:
                    print(f"   {side:7} {L}: {z['bot']:g} - {z['top']:g}   (OB candle {tm[z['ob']]:%b %d %I:%M %p}, made by {z['ev']} {tm[z['made']]:%b %d %I:%M %p})")
                if not lst:
                    print(f"   {side:7} none")
        return
    sym = sys.argv[1] if len(sys.argv) > 1 else "BTCUSD"
    rows = T.binance_us(sym)
    zs, s, tm, c, _ = zones(rows)
    cut = tm[-1] - dt.timedelta(days=7)
    print(f"{sym} 1H Binance.US ({len(rows)} candles), times ET (candle open). Order blocks made in the last 7 days:")
    print("made by              OB candle          side     box (bottom - top)       used (price back to its 50%)")
    for z in zs:
        if tm[z["made"]] >= cut:
            u = f"{tm[z['used']]:%a %b %d %I %p}" if z["used"] is not None else "FRESH"
            print(f"{z['ev']:8} {tm[z['made']]:%a %d %I %p}  {tm[z['ob']]:%a %b %d %I %p}  {z['side']:7}  {z['bot']:<10g} - {z['top']:<10g}  {u}")
    tr = "UP" if s.trend == 1 else "DOWN"
    print(f"\nNow ({tm[-1]:%a %b %d %I %p}): trend {tr}, fib STRONG {s.strong:g} / WEAK {s.weak:g}, 50% {(s.strong + s.weak) / 2:g}, close {c[-1]:g}")
    for wt in (True, False):
        print("Chart shows" + (" (only WITH the trend):" if wt else " (switch off, both sides):"))
        for side, lst in lettered(s.trend, s.strong, s.weak, [z for z in zs if z["used"] is None], wt).items():
            print(f"   {side:7}", ", ".join(f"{L} {z['bot']:g}-{z['top']:g}" for L, z in lst) or "none")


if __name__ == "__main__":
    main()
