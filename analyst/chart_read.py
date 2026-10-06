"""
Chart reader: the Smoke Detector's logic (pine/smoke detector) in plain English, for any coin on the daily and 4H.
Answers Jeff's questions: who is in control, is price expanding / pulling back / sideways, what level must hold,
where is the liquidity (where price may be drawing), premium or discount, and what just happened (BOS, market
shift on a body close, trap, failed breakout). Reads public OKX candles; never trades.

  python analyst/chart_read.py BTC SOL LINK BNB
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402

SWING = 5


def read(bars):
    """Walk the closed candles like the Pine script does; returns the final state and the last events."""
    h, l, c, o = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars], [b["o"] for b in bars]
    n = len(bars)
    atr = bot.atr(h, l, c, 14)
    swH = swL = None
    hDone = lDone = True
    trend, strong, ext = 0, None, None
    highs, lows, events = [], [], []
    bos_level, bos_bar, bos_dir = None, None, 0
    for i in range(n):
        j = i - SWING  # a swing point is confirmed SWING candles later
        if j >= SWING:
            if h[j] == max(h[j - SWING:i + 1]):
                swH, hDone = h[j], False
                highs.append(h[j])
            if l[j] == min(l[j - SWING:i + 1]):
                swL, lDone = l[j], False
                lows.append(l[j])
        ev = None
        if trend == 1:
            ext = max(ext or h[i], h[i])
            if strong is not None and c[i] < strong:
                ev, trend, strong, ext, lDone = "MARKET SHIFT down (body closed below the strong low)", -1, ext, l[i], True
            elif not hDone and c[i] > swH:
                ev, hDone, strong = "BOS up (trend continues)", True, swL
            elif not lDone and c[i] < swL:
                ev, lDone = "a pullback low broke, strong low still holds", True
        elif trend == -1:
            ext = min(ext or l[i], l[i])
            if strong is not None and c[i] > strong:
                ev, trend, strong, ext, hDone = "MARKET SHIFT up (body closed above the strong high)", 1, ext, h[i], True
            elif not lDone and c[i] < swL:
                ev, lDone, strong = "BOS down (trend continues)", True, swH
            elif not hDone and c[i] > swH:
                ev, hDone = "a pullback high broke, strong high still holds", True
        else:
            if not hDone and swH is not None and c[i] > swH:
                ev, trend, hDone, strong, ext = "BOS up (first trend)", 1, True, swL, h[i]
            elif not lDone and swL is not None and c[i] < swL:
                ev, trend, lDone, strong, ext = "BOS down (first trend)", -1, True, swH, l[i]
        if ev and ev.startswith("BOS"):
            bos_level, bos_bar, bos_dir = (swH if trend == 1 else swL), i, trend
        elif bos_level is not None and i - bos_bar <= 3 and ((bos_dir == 1 and c[i] < bos_level) or (bos_dir == -1 and c[i] > bos_level)):
            ev, bos_level = "FAILED BREAKOUT (trap: the broken level was lost again)", None
        if not ev and swH is not None and not hDone and h[i] > swH and c[i] <= swH:
            ev = "TRAP at the highs (wick swept the swing high, body closed back inside)"
        if not ev and swL is not None and not lDone and l[i] < swL and c[i] >= swL:
            ev = "TRAP at the lows (wick swept the swing low, body closed back inside)"
        if ev:
            events.append((bars[i]["ts"], ev))
    px, a = c[-1], atr[-1] or 0
    above = sorted(x for x in set(highs) if x > px)
    below = sorted((x for x in set(lows) if x < px), reverse=True)
    weak = (swH if not hDone else None) if trend == 1 else (swL if not lDone else None) if trend == -1 else None
    width = [4 * (sum((x - sum(c[k - 19:k + 1]) / 20) ** 2 for x in c[k - 19:k + 1]) / 20) ** 0.5 / (sum(c[k - 19:k + 1]) / 20)
             for k in range(19, n)]
    squeeze = len(width) > 100 and width[-1] <= min(width[-100:]) * 1.10
    expanding = (trend == 1 and px > max(c[-11:-1])) or (trend == -1 and px < min(c[-11:-1]))
    phase = ("sideways, squeezing (a breakout is building)" if squeeze else "expanding" if expanding else
             "pulling back / loading orders" if trend and strong and ((trend == 1 and px > strong) or (trend == -1 and px < strong))
             else "testing the strong level" if trend else "no clear structure")
    lo_, hi_ = (strong, ext) if trend == 1 else (ext, strong) if trend == -1 else (min(l[-50:]), max(h[-50:]))
    eq = (lo_ + hi_) / 2 if lo_ and hi_ else None
    zone = None if eq is None else ("premium (expensive half)" if px > eq else "discount (cheap half)")
    body = abs(c[-1] - o[-1]); rng = h[-1] - l[-1]
    candle = ("doji (indecision)" if rng and body <= 0.1 * rng else
              "big-body momentum candle" if a and body >= 1.2 * a else "normal candle")
    return {"px": px, "trend": trend, "strong": strong, "weak": weak, "phase": phase, "eq": eq, "zone": zone,
            "above": above[:2], "below": below[:2], "events": events[-3:], "candle": candle, "atr_pct": a / px * 100}


def fmt(x):
    return "-" if x is None else f"{x:,.6g}"


def report(coin):
    api = bot.OKX("", "", "")
    out = [f"## {coin}"]
    for tf, label in (("1Dutc", "Daily"), ("4H", "4-hour")):
        bars = [b for b in api.candles(f"{coin}-USDT", tf, 300) if b["confirm"]]
        r = read(bars)
        who = {1: "UP: buyers in control", -1: "DOWN: sellers in control", 0: "no clear trend"}[r["trend"]]
        hold = "" if r["strong"] is None else f"; must hold {'above' if r['trend'] == 1 else 'below'} {fmt(r['strong'])}"
        out.append(f"**{label}:** {who}, {r['phase']}{hold}. Price {fmt(r['px'])} is in the {r['zone'] or '-'} "
                   f"(equilibrium {fmt(r['eq'])}). Last candle: {r['candle']}.")
        out.append(f"  Liquidity above (old highs): {', '.join(fmt(x) for x in r['above']) or 'none (new highs)'} | "
                   f"below (old lows): {', '.join(fmt(x) for x in r['below']) or 'none'}"
                   + (f" | target (weak level): {fmt(r['weak'])}" if r["weak"] else ""))
        if r["events"]:
            import datetime as dt
            out.append("  Recent: " + "; ".join(f"{dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc):%b %d %H:%M} {e}"
                                                 for t, e in r["events"]))
    return "\n".join(out)


if __name__ == "__main__":
    for coin in [x.upper() for x in sys.argv[1:]] or ["BTC"]:
        print(report(coin) + "\n")
