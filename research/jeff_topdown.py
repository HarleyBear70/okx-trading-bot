"""
JT: Jeff's top-down SMC process as a bot (Oct 8 2026), built on the Smoke Detector's structure engine
(pine/smoke detector: swings of 5, BOS, market shift = body close through the strong level, traps = sweeps).

  1. Bias: daily trend and 4H trend (Smoke Detector engine on each) agree.
  2. Entry chart (15m or 1H): wait for the turnaround = a market shift back in the bias direction.
     A  shift only
     B  shift after a liquidity sweep (trap candle) in the last 12 candles
     C  shift while price is in the 4H discount (longs) / premium (shorts)
     BC both: in the 4H discount, liquidity sweep (fuel), then the shift (Jeff's full recipe, Brad Guan style)
  3. Stop just past where it went: the new strong level (the pullback's extreme) -/+ 0.15 ATR.
     Jeff's rule variant: skip if that stop is more than 1.35% away.
  4. Trail: the stop follows the entry chart's strong level after each BOS.
  5. Exit: market shift against the trade (body close through the strong level), at the next open.
Next-open fills, 0.5% risk, one trade per instrument, costs and data as research/battery.py.

  python3 research/jeff_topdown.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402

L, CUSH, SWEEP_WIN = 5, 0.15, 12
H4, D1 = 4 * 3600000, 86400000


def structure(b, leg=None):
    """Smoke Detector engine per bar: trend, strong, shift, bos, trap, and the 50% of the strong-ext range.
    leg=1 (Oct 9 2026 Pine fix): each close beyond the last small (leg-candle) swing in the trend direction moves the
    strong level to where that leg started, so the shift fires on a close back through the leg's lower high/higher low."""
    n = len(b)
    h, l, c = [x["h"] for x in b], [x["l"] for x in b], [x["c"] for x in b]
    swH = swL = None
    hDone = lDone = True
    trend, strong, ext = 0, None, None
    out_t, out_s, out_shift, out_trap, out_mid = [0] * n, [None] * n, [False] * n, [False] * n, [None] * n
    out_tdir = [0] * n  # +1 swept a high (bearish fuel), -1 swept a low (bullish fuel)
    legH = legL = None
    legHd = legLd = True
    for i in range(n):
        if leg:
            j = i - leg
            if j >= leg:
                if h[j] == max(h[j - leg:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                    legH, legHd = h[j], False
                if l[j] == min(l[j - leg:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                    legL, legLd = l[j], False
            if trend == -1 and not legLd and c[i] < legL:
                legLd = True
                if legH is not None and strong is not None and legH < strong:
                    strong = legH
            if trend == 1 and not legHd and c[i] > legH:
                legHd = True
                if legL is not None and strong is not None and legL > strong:
                    strong = legL
        j = i - L  # pivot candidate, confirmed L bars later (no look-ahead)
        if j >= L:
            if h[j] == max(h[j - L:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                swH, hDone = h[j], False
            if l[j] == min(l[j - L:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                swL, lDone = l[j], False
        shift = False
        up_trap = swH is not None and not hDone and h[i] > swH and c[i] <= swH
        dn_trap = swL is not None and not lDone and l[i] < swL and c[i] >= swL
        trap = up_trap or dn_trap
        if trend == 1:
            ext = max(ext if ext is not None else h[i], h[i])
            if strong is not None and c[i] < strong:
                shift, trend, strong, ext, lDone, legLd = True, -1, ext, l[i], True, True
            elif not hDone and swH is not None and c[i] > swH:
                hDone, strong = True, (max(strong, swL) if leg and strong is not None and swL is not None else swL)
            elif not lDone and swL is not None and c[i] < swL:
                lDone = True
        elif trend == -1:
            ext = min(ext if ext is not None else l[i], l[i])
            if strong is not None and c[i] > strong:
                shift, trend, strong, ext, hDone, legHd = True, 1, ext, h[i], True, True
            elif not lDone and swL is not None and c[i] < swL:
                lDone, strong = True, (min(strong, swH) if leg and strong is not None and swH is not None else swH)
            elif not hDone and swH is not None and c[i] > swH:
                hDone = True
        else:
            if not hDone and swH is not None and c[i] > swH:
                trend, hDone, strong, ext = 1, True, swL, h[i]
            elif not lDone and swL is not None and c[i] < swL:
                trend, lDone, strong, ext = -1, True, swH, l[i]
        out_t[i], out_s[i], out_shift[i], out_trap[i] = trend, strong, shift, trap
        out_tdir[i] = -1 if dn_trap else (1 if up_trap else 0)
        if strong is not None and ext is not None and strong != ext:
            out_mid[i] = (strong + ext) / 2
    return {"trend": out_t, "strong": out_s, "shift": out_shift, "trap": out_trap, "mid": out_mid, "tdir": out_tdir}


def resample(b, span):
    out = {}
    for x in b:
        k = x["ts"] - x["ts"] % span
        if k not in out:
            out[k] = {"ts": k, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"], "sp": x["sp"]}
        else:
            y = out[k]
            y["h"], y["l"], y["c"], y["sp"] = max(y["h"], x["h"]), min(y["l"], x["l"]), x["c"], x["sp"]
    return [out[k] for k in sorted(out)]


def htf_view(b, span, tf_ms):
    """per entry bar: (trend, mid) of the higher timeframe as of its last COMPLETED candle"""
    hb = resample(b, span)
    s = structure(hb)
    known = {x["ts"] + span: (s["trend"][i], s["mid"][i]) for i, x in enumerate(hb)}
    out, cur, prev = [], (0, None), None
    for x in b:
        key = x["ts"] - x["ts"] % span
        if prev is not None and key != prev:
            cur = known.get(prev + span, cur)
        if (x["ts"] + tf_ms) % span == 0:
            cur = known.get(x["ts"] + tf_ms, cur)
        out.append(cur)
        prev = key
    return out


def run(market, b, tf, variant, max_stop, lev, longs_only=False):
    tf_ms = B.MS[tf]
    s = structure(b)
    d1, h4 = htf_view(b, D1, tf_ms), htf_view(b, H4, tf_ms)
    a = B.atr(b)
    t0 = B.ms(B.START)
    eq, pos, pend, pend_exit, trades, curve = 1000.0, None, None, False, [], []
    last_trap = -999
    dayb = 86400000 // tf_ms
    for k, x in enumerate(b):
        if s["trap"][k]:
            last_trap = k
        if x["ts"] < t0:
            continue
        if pos and pend_exit:
            px = x["o"]
            pnl = pos["side"] * (px - pos["entry"]) * pos["u"] - (pos["ec"] + B.cost(market, x, px)) * pos["u"]
            eq += pnl
            trades.append((pos["side"], pnl, pos["ts"]))
            pos, pend_exit = None, False
        if pend and not pos:
            side, stop = pend
            px = x["o"]
            dist = (px - stop) * side
            if dist > 0 and (max_stop is None or dist / px <= max_stop):
                u = min(eq * B.RISK / dist, eq * lev / px)
                pos = {"side": side, "entry": px, "stop": stop, "u": u, "ts": x["ts"], "ec": B.cost(market, x, px)}
        pend = None
        if pos:
            sd = pos["side"]
            if (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"]):
                px = min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"])
                pnl = sd * (px - pos["entry"]) * pos["u"] - (pos["ec"] + B.cost(market, x, px)) * pos["u"]
                eq += pnl
                trades.append((sd, pnl, pos["ts"]))
                pos, pend_exit = None, False
        if pos:
            sd = pos["side"]
            if s["trend"][k] == -sd:  # market shift against the trade
                pend_exit = True
            elif s["strong"][k] is not None and a[k]:
                t = s["strong"][k] - sd * CUSH * a[k]
                pos["stop"] = max(pos["stop"], t) if sd == 1 else min(pos["stop"], t)
        elif s["shift"][k] and a[k] and s["strong"][k] is not None:
            side = s["trend"][k]
            bias_ok = d1[k][0] == side and h4[k][0] == side
            if variant in ("B", "BC"):
                bias_ok = bias_ok and k - last_trap <= SWEEP_WIN
            if variant in ("C", "BC"):
                mid = h4[k][1]
                bias_ok = bias_ok and mid is not None and ((x["c"] <= mid) if side == 1 else (x["c"] >= mid))
            if longs_only and side == -1:
                bias_ok = False
            if bias_ok:
                pend = (side, s["strong"][k] - side * CUSH * a[k])
        if k % dayb == 0:
            op = pos["side"] * (x["c"] - pos["entry"]) * pos["u"] if pos else 0
            curve.append((x["ts"], eq + op))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


def main():
    sets = [("crypto", B.CRYPTO, 1.0)]
    if os.path.isdir(B.FXDIR):
        sets.append(("forex", B.FOREX, 20.0))
    print("| Market | Chart | Version | 2019-now (return / drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for market, insts, lev in sets:
        for tf in ("1H", "15m"):
            B.MS_CUR[0] = B.MS[tf]
            data = {i: B.load(market, i, tf) for i in insts}
            for variant in ("A", "B", "C"):
                for ms_ in ((None, 0.0135) if market == "crypto" else (None,)):
                    all_tr, curves = [], []
                    for i in insts:
                        tr, cv = run(market, data[i], tf, variant, ms_, lev)
                        all_tr += tr
                        curves.append(cv)
                    port = B.mix(curves)
                    f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in
                                 ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
                    lp = "-" if f["long_pf"] is None else f"{f['long_pf']:.2f}"
                    sp = "-" if f["short_pf"] is None else f"{f['short_pf']:.2f}"
                    name = variant + (" + max stop 1.35%" if ms_ else "")
                    print(f"| {market} | {tf} | {name} | {B.cell(f)} | {B.cell(h1)} | {B.cell(h2)} | {f['win']:.0f}% | "
                          f"{f['tpw']:.1f} | {lp} | {sp} |", flush=True)


if __name__ == "__main__":
    main()
