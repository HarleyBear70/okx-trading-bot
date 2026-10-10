"""
PURE15: Jeff's pure 15m method (Oct 9 2026), from his answers in "To Claude/ideas/looking for answers.txt" and his
worked BTC example (MS over 82,595, fib 82,502 -> 82,680, buy ~82,615, stop 82,502, target 83,028 under 83,060).
15m only - no daily/4H/1H filter. Both directions; shorts = exact mirror (run on upside-down prices).

  Swings      a swing high/low = N candles each side (Jeff: test N = 3 and 5).
  Structure   bearish -> bullish (market shift) when a candle BODY closes above the last swing high (the last
              lower high); bullish -> bearish when a body closes below the last swing low. Wicks don't count.
  Fib         in a bullish trend: 100% = the newest swing low (higher low), 0% = the highest high since it.
              A newer swing low = the fib is redrawn to it. Below 50% = discount.
  Entry       Jeff: test both - (touch) buy when price touches the 50% line; (green) buy at the next open after a
              green candle closes below the 50% line. One trade per fib leg [Claude: assumed, see JEFF note].
  Stop        under the 100% (the newest higher low). Cushion: Jeff: test 0 and 0.05%.
              Skip if the stop is more than 1.35% away (Jeff's max stop).
  Target      just under a swing high above entry [Claude: "just under" = the same cushion].
              Jeff's example skipped the nearer 82,750 high, so both are tested:
              (near) the nearest swing high above entry that price hasn't taken out,
              (2R)   the nearest such high that gives 2:1 or better.
  Min R:R     2:1 (Jeff). Skip trades under 2:1.
  Trail       Jeff's example: "as price makes a new high above the 0%, trail the stop up to breakeven". Tested
              (none) and (BE): stop moves to the entry price once price makes a new high above the fib's 0%.
  Fees        Jeff: taker 0.02% + 0.02% slippage on entries and stops; maker 0% on targets.
  Coins       BTC ETH SOL XRP (Jeff). Results in R after fees; 2019-now; halves 2019-22 / 2023-now.

  python3 research/pure15.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import m15  # noqa: E402

TAKER, MAXSTOP, MINRR = 0.0004, 0.0135, 2.0
COINS = ["BTC", "ETH", "SOL", "XRP"]


def run(o, h, l, c, ts, N, cush, trig, tgtm, trail, spr=None, taker=TAKER, log=None, flat=None, fib=0.5, mslog=None):
    """flat = no new trades when the last BOS or market shift is more than this many candles old (Jeff rule 1, Oct 9).
    fib = entry level on the fib (0.5 = the 50% line; deeper levels sit nearer the 100%, Jeff rule 4)."""
    """long side only (shorts: upside-down prices). Returns (entry ts, exit ts, R)."""
    n, t0 = len(ts), B.ms(B.START)
    # cost per side in price: crypto = taker+slippage on entries/stops, 0 on targets; forex = half the OANDA spread
    mkt = (lambda i, px: spr[i] / 2) if spr else (lambda i, px: taker * abs(px))
    lim = (lambda i, px: spr[i] / 2) if spr else (lambda i, px: 0.0)
    trend, lsh, lsl, lsl_i = 0, None, None, 0
    hi_hit = lo_hit = True
    last_ev = -10 ** 9
    ms_ts = ms_lvl = None  # last swing high / low
    highs = []  # swing highs not yet taken out
    leg_lo = leg_hi = None
    leg_used = False
    green_go = False
    pos, out = None, []
    for i in range(n):
        # 1) a pending "green candle" entry fills at this open
        if green_go and not pos:
            green_go = False
            enter_px = o[i]
            pos = open_pos(enter_px, leg_lo, cush, highs, tgtm, ts[i], leg_hi)
            if pos:
                pos["ec"] = mkt(i, enter_px)
                pos["info"] = (ms_ts, ms_lvl, leg_lo, leg_hi)
                leg_used = True
        # 2) manage the open trade on this candle
        if pos:
            px = None
            if l[i] <= pos["stop"]:
                px = min(pos["stop"], o[i])
                fee = mkt(i, px)
            elif h[i] >= pos["tgt"]:
                px = max(pos["tgt"], o[i])
                fee = lim(i, px)
            if px is not None:
                r = (px - pos["e"] - pos["ec"] - fee) / pos["r"]
                out.append((pos["ts"], ts[i], r))
                if log is not None:
                    log.append(dict(pos, x_ts=ts[i], x=px, R=r))
                pos = None
            elif trail and h[i] > pos["hi0"]:
                pos["stop"] = max(pos["stop"], pos["e"])
        # 3) touch entry at the 50% line during this candle
        if (not pos and trig == "touch" and trend == 1 and leg_lo is not None and not leg_used
                and ts[i] >= t0 and leg_hi > leg_lo):
            mid = leg_hi - fib * (leg_hi - leg_lo)
            if l[i] <= mid and (flat is None or i - last_ev <= flat):
                e = min(o[i], mid)
                p = open_pos(e, leg_lo, cush, highs, tgtm, ts[i], leg_hi)
                leg_used = True  # one try per fib leg, taken or skipped
                if p:
                    pos = p
                    p["ec"] = mkt(i, e)
                    p["info"] = (ms_ts, ms_lvl, leg_lo, leg_hi)
                    if l[i] <= p["stop"]:  # same candle stop (worst case)
                        r = (p["stop"] - e - p["ec"] - mkt(i, p["stop"])) / p["r"]
                        out.append((ts[i], ts[i], r))
                        if log is not None:
                            log.append(dict(p, x_ts=ts[i], x=p["stop"], R=r))
                        pos = None
        # 4) green candle close in the discount -> buy next open
        if (not pos and trig == "green" and trend == 1 and leg_lo is not None and not leg_used
                and ts[i] >= t0 and leg_hi > leg_lo):
            mid = leg_hi - fib * (leg_hi - leg_lo)
            if c[i] > o[i] and c[i] < mid and l[i] > leg_lo and (flat is None or i - last_ev <= flat):
                green_go = True
                leg_used = True
        # 5) structure: body closes through the last swing (BOS or market shift = the market is moving)
        if lsh is not None and not hi_hit and c[i] > lsh:
            hi_hit, last_ev = True, i
        if lsl is not None and not lo_hit and c[i] < lsl:
            lo_hit, last_ev = True, i
        if trend != 1 and lsh is not None and c[i] > lsh:
            trend = 1
            ms_ts, ms_lvl = ts[i], lsh
            if mslog is not None:
                mslog.append((ts[i], 1, lsh))
            leg_lo, leg_hi, leg_used = lsl, (max(h[lsl_i:i + 1]) if lsl is not None else None), False
        elif trend != -1 and lsl is not None and c[i] < lsl:
            trend = -1
            if mslog is not None:
                mslog.append((ts[i], -1, lsl))
            leg_lo = leg_hi = None
            green_go = False
        # 5b) Jeff Oct 9: decide only on a CLOSED candle - buy at the close of a candle that closes at/below the fib
        #     level (above the 100%), with the trend still bullish after that close
        if (not pos and trig == "close" and trend == 1 and leg_lo is not None and not leg_used and ts[i] >= t0
                and leg_hi > leg_lo and (flat is None or i - last_ev <= flat)):
            mid = leg_hi - fib * (leg_hi - leg_lo)
            if leg_lo < c[i] <= mid:
                leg_used = True
                p = open_pos(c[i], leg_lo, cush, highs, tgtm, ts[i], leg_hi)
                if p:
                    pos = p
                    p["ec"] = mkt(i, c[i])
                    p["info"] = (ms_ts, ms_lvl, leg_lo, leg_hi)
        if trend == 1 and leg_hi is not None:
            leg_hi = max(leg_hi, h[i])
        # 6) swings confirmed N candles later (no look-ahead)
        j = i - N
        if j >= N:
            if h[j] == max(h[j - N:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                lsh, hi_hit = h[j], False
                highs.append(h[j])
            if l[j] == min(l[j - N:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                lsl, lsl_i, lo_hit = l[j], j, False
                if trend == 1:  # newer higher low: redraw the fib to it
                    leg_lo, leg_hi, leg_used = l[j], max(h[j:i + 1]), False
                    green_go = False
        highs = [v for v in highs if v > h[i]][-200:]
    return out


def open_pos(e, leg_lo, cush, highs, tgtm, t, leg_hi):
    if leg_lo is None:
        return None
    stop = leg_lo - cush * abs(leg_lo)
    r = e - stop
    if r <= 0 or r > MAXSTOP * abs(e):
        return None
    above = sorted(t for t in (v - cush * abs(v) for v in highs) if t > e)
    if tgtm == "2R":
        above = [v for v in above if v - e >= MINRR * r]
    if not above:
        return None
    tgt = above[0]
    if tgt - e < MINRR * r:  # Jeff: skip trades under 2:1
        return None
    return {"e": e, "stop": stop, "tgt": tgt, "r": r, "ts": t, "hi0": leg_hi}


def stats(rs):
    if not rs:
        return None
    win, loss = sum(r for r in rs if r > 0), -sum(r for r in rs if r < 0)
    eq = peak = dd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    return {"n": len(rs), "win": 100 * sum(r > 0 for r in rs) / len(rs), "pf": win / loss if loss else 99,
            "avg": sum(rs) / len(rs), "dd": dd}


def row(name, tr, years):
    tr.sort()
    cut = B.ms(B.CUT)
    f = stats([t[2] for t in tr])
    if not f:
        return f"| {name} | 0 |"
    h1, h2 = stats([t[2] for t in tr if t[0] < cut]), stats([t[2] for t in tr if t[0] >= cut])
    lo, sh = stats([t[2] for t in tr if t[3] == 1]), stats([t[2] for t in tr if t[3] == -1])
    w, ls = [t[2] for t in tr if t[2] > 0], [t[2] for t in tr if t[2] <= 0]
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    aw = f"{sum(w) / len(w):+.2f}R" if w else "-"
    al = f"{sum(ls) / len(ls):+.2f}R" if ls else "-"
    return (f"| {name} | {f['n'] / years:.0f} | {f['win']:.0f}% | {aw} | {al} | {f['pf']:.2f} | {f['avg']:+.2f}R | "
            f"{f['dd']:.0f}R | {p(h1)} | {p(h2)} | {p(lo)} | {p(sh)} |")


FOREX = ["EUR_USD", "GBP_USD", "AUD_USD", "USD_JPY", "XAU_USD"]


def load(cn):
    if "_" in cn:
        b = B.load("forex", cn, "15m")
        return b, [x["sp"] for x in b]
    return [x for x in m15.m15(cn) if x["ts"] >= B.ms(B.START) - 30 * 86400000], None


def main_v2():
    """Oct 9 round 2 (Jeff's rules 1-4): swing 1/3/5 x flat filter x fib entry level; 0.05% cushion, enter on a candle close, 2:1."""
    years = (dt.datetime.now(dt.timezone.utc) - B.START).days / 365.25
    vers = [(f"swing {N}, flat {'off' if fl is None else f'after {fl} candles'}, entry at {fb * 100:.1f}%", N, fl, fb)
            for N in (1, 3, 5) for fl in (None, 8, 16, 32) for fb in (0.5, 0.618, 0.705, 0.786)]
    res = {v[0]: [] for v in vers}
    for cn in COINS:
        raw, _ = load(cn)
        ts = [x["ts"] for x in raw]
        o, h, l, c = ([x[k] for x in raw] for k in "ohlc")
        del raw
        gc.collect()
        no, nh, nl, nc = [-v for v in o], [-v for v in l], [-v for v in h], [-v for v in c]
        for name, N, fl, fb in vers:
            kw = dict(flat=fl, fib=fb)
            lo = [t + (1,) for t in run(o, h, l, c, ts, N, 0.0005, "close", "2R", False, **kw)]
            sh = [t + (-1,) for t in run(no, nh, nl, nc, ts, N, 0.0005, "close", "2R", False, **kw)]
            keep, busy = [], -1
            for t in sorted(lo + sh):
                if t[0] > busy:
                    keep.append(t)
                    busy = t[1]
            res[name] += keep
        del o, h, l, c, no, nh, nl, nc
        gc.collect()
        print(f"  ({cn} done)", flush=True)
    print("\n### BTC ETH SOL XRP, 15m only, 0.05% cushion, buy on a candle CLOSE at/below the fib level, 2:1 target, Binance.US costs\n")
    print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
          "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in vers:
        print(row(v[0], res[v[0]], years), flush=True)


def main():
    if sys.argv[1:] == ["v2"]:
        return main_v2()
    years = (dt.datetime.now(dt.timezone.utc) - B.START).days / 365.25
    # trail-to-breakeven lost in every version on the BTC trial (Oct 9), so the full run is trail "none" only
    vers = [(f"swing {N}, cushion {'0.05%' if cu else '0'}, {tr}, target {tg}", N, cu, tr, tg, False)
            for N in (3, 5) for cu in (0.0, 0.0005) for tr in ("touch", "green") for tg in ("near", "2R")]
    best = [("ZERO FEES: swing 3, cushion 0.05%, touch, target 2R", 3, 0.0005, "touch", "2R", False, "zero"),
            ("ZERO FEES: swing 5, cushion 0.05%, green, target near", 5, 0.0005, "green", "near", False, "zero")]
    sets = [("crypto: " + " ".join(COINS), COINS), ("forex/gold: " + " ".join(FOREX), FOREX)]
    if sys.argv[1:]:
        sets = [(" ".join(sys.argv[1:]), sys.argv[1:])]
    for title, coins in sets:
        vs = vers + best
        res = {v[0]: [] for v in vs}
        for cn in coins:
            raw, spr = load(cn)
            ts = [x["ts"] for x in raw]
            o, h, l, c = ([x[k] for x in raw] for k in "ohlc")
            del raw
            gc.collect()
            no, nh, nl, nc = [-v for v in o], [-v for v in l], [-v for v in h], [-v for v in c]
            for name, *a in vs:
                kw = {}
                if len(a) > 5:
                    a = a[:5]
                    kw = {"spr": [0.0] * len(ts)} if spr else {"taker": 0.0}
                elif spr:
                    kw = {"spr": spr}
                lo = [t + (1,) for t in run(o, h, l, c, ts, *a, **kw)]
                sh = [t + (-1,) for t in run(no, nh, nl, nc, ts, *a, **kw)]
                keep, busy = [], -1
                for t in sorted(lo + sh):  # one trade per market at a time
                    if t[0] > busy:
                        keep.append(t)
                        busy = t[1]
                res[name] += keep
            del o, h, l, c, no, nh, nl, nc
            gc.collect()
            print(f"  ({cn} done)", flush=True)
        print(f"\n### {title}, 15m only. Crypto: taker 0.02% + 0.02% slippage, maker 0% targets. Forex: OANDA spread\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for v in vs:
            print(row(v[0], res[v[0]], years), flush=True)


if __name__ == "__main__":
    main()
