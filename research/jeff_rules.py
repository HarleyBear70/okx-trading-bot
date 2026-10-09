"""
JEFF_RULES: Jeff's own rules, tested EXACTLY as written in rules/JEFF_RULES_from_Brad.txt (Oct 9 2026).
Nothing marked OPEN is used as a filter. Shorts are the mirror of longs (the code runs the long logic on
upside-down prices, so the mirror is exact).

HOW EACH RULE IS MEASURED (Claude's measuring choices are marked [CHOICE] - Jeff can change any of them)
  Daily bias  (1, 18.1)  daily trend (Smoke Detector engine, last completed daily candle) = trade direction.
  4H range    (3)        Smoke Detector 4H swing range; longs only when the zone sits in the DISCOUNT (zone top at
                         or below the 4H 50% line), shorts mirror.
  4H zone     (8)        origin of a strong move = a 4H move that left an imbalance (fair value gap).
                         [CHOICE] "before the move" = the 3 4H candles before the gap's big candle.
                         Pivot method: the single turning candle (lowest low of those 3), wick to wick.
                         Range method: high-to-low of those 3 candles. Both are tested (rule 8 is OPEN).
  Zone dies   (4, 9)     a 4H candle BODY closes below it, or it was used up: price reached its 50%, left
                         (closed above it), and came back.
  Touch       (2, 18.3)  nothing happens until a 15m candle trades into a live zone.
  Sweep       (12)       a 15m candle wicks under a 15m swing low (5 candles each side) and closes back above it,
                         with its low inside the zone. No sweep, no entry.
  Shift       (13c)      a 15m candle BODY closes above the last lower high (the last 1-candle swing high before
                         the sweep - the 2:30 PM kind). A new low under the sweep before that = setup gone.
  Way A       (13d-e)    after the shift, wait for price to pull back into the small zone that created the shift
                         [CHOICE] = the last down candle before the shift candle (Pivot) / the candles from the sweep
                         to the shift (Range). Then a rejection candle in it (lower wick at least as big as the body),
                         then a candle that closes up AND above the rejection candle's high -> buy at the next open.
                         Target hit first = no pullback = no Way A trade.
  Way B       (36)       buy at the open of the 2nd candle after the shift; stop at the bottom (or halfway) of the
                         shift candle.
  Stop        (14)       just below the market-shift candle [CHOICE] "just" = 0.1 ATR.
  Target      (15, 34)   the nearest 15m swing high above entry that price hasn't already taken out.
  Trailing    (37)       stop moves under each new higher 15m swing low (5 candles each side = not too tight).
  One try     (16)       one trade per market shift. Daily trend checked again at entry (18.1).
  No-trade    (20)       last day of the month and December: no new trades. News / "choppy" not tested (no data).
  OPEN items  min R:R, killzone, days to skip, losses in a row, risk size: NOT used. Results in R.
  Fees        Binance.US 0.05% a side (0.02% + slippage); 0% and OKX 0.35% shown only as a check.
PASS RULES: 100+ trades, PF 1.3+, +0.10R a trade or better, PF 1.1+ in BOTH halves (2019-22 / 2023-now),
never-seen coins PF 1.1+.

  python3 research/jeff_rules.py
"""
import datetime as dt
import gc
import os
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402
import m15  # noqa: E402

M15, H4, D1 = 900000, 4 * 3600000, 86400000
CUSH, SW, PRE = 0.1, 5, 3
NY = zoneinfo.ZoneInfo("America/New_York")
MAIN = ["BTC", "ETH", "SOL", "XRP", "BNB"]
UNSEEN = ["ADA", "DOGE", "LINK", "AVAX", "LTC", "DOT"]


def bars_of(o, h, l, c, ts, span):
    out = {}
    for i in range(len(ts)):
        k = ts[i] - ts[i] % span
        y = out.get(k)
        if y is None:
            out[k] = {"ts": k, "o": o[i], "h": h[i], "l": l[i], "c": c[i]}
        else:
            y["h"], y["l"], y["c"] = max(y["h"], h[i]), min(y["l"], l[i]), c[i]
    return [out[k] for k in sorted(out)]


def htf(hb, span):
    """{close time: (trend, mid)} for each completed higher-timeframe candle"""
    s = J.structure(hb)
    return {x["ts"] + span: (s["trend"][i], s["mid"][i]) for i, x in enumerate(hb)}


def zones_4h(hb, method):
    """demand zones: (time it's known, bottom, top), from 4H moves that left a fair value gap"""
    out = []
    for i in range(PRE + 2, len(hb)):
        if hb[i]["l"] > hb[i - 2]["h"] and hb[i - 1]["c"] > hb[i - 1]["o"]:
            pre = hb[i - 1 - PRE:i - 1]
            if method == "pivot":
                t = min(pre, key=lambda x: x["l"])
                bot, top = t["l"], t["h"]
            else:
                bot, top = min(x["l"] for x in pre), max(x["h"] for x in pre)
            if top < hb[i]["l"]:
                out.append((hb[i]["ts"] + H4, bot, top))
    return out


def run(o, h, l, c, ts, way, zmethod, fee, bstop="bottom", minrr=None, kz=False, exitm="target", tf=M15):
    """exitm: "target" = target + trailing (rule 15 + 37); "trail" = no target, the trailing stop is the only exit;
    "trail2r" = no target, stop stays put until price reaches 2R, then trails."""
    """long side only (shorts: call with upside-down prices). Returns trades (entry ts, exit ts, R, planned R:R)."""
    n = len(ts)
    hb = bars_of(o, h, l, c, ts, H4)
    v4, vd = htf(hb, H4), htf(bars_of(o, h, l, c, ts, D1), D1)
    zl = zones_4h(hb, zmethod)
    del hb
    bars = [{"h": h[i], "l": l[i], "c": c[i]} for i in range(n)]
    a = B.atr(bars)
    del bars
    t0 = B.ms(B.START)
    cur4, curd, zi = (0, None), (0, None), 0
    zones = []  # [bot, top, mid, touched, mit, left, dead]
    swl = swh = None  # last 15m swing low / high (5 each side)
    swl_done = True
    highs = []  # unbroken 15m swing highs (targets)
    leg_hi = None  # last 1-candle swing high
    trail_low = None
    setup, pos, out = None, None, []
    for i in range(n):
        x_ts = ts[i]
        # newly confirmed swings (no look-ahead: a 5-candle swing at j is known at j+5)
        j = i - SW
        if j >= SW:
            if h[j] == max(h[j - SW:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                swh = h[j]
                highs.append(h[j])
            if l[j] == min(l[j - SW:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                swl, swl_done = l[j], False
                trail_low = l[j]
        if i >= 2 and h[i - 1] >= h[i - 2] and h[i - 1] > h[i]:
            leg_hi = h[i - 1]
        while zi < len(zl) and zl[zi][0] <= x_ts:
            _, bot, top = zl[zi]
            zones.append([bot, top, (bot + top) / 2, False, False, False, False])
            zi += 1
        # exits first
        if pos:
            if l[i] <= pos["stop"]:
                px = min(pos["stop"], o[i])
            elif exitm == "target" and h[i] >= pos["tgt"]:
                px = max(pos["tgt"], o[i])
            else:
                px = None
            if px is not None:
                out.append((pos["ts"], x_ts, ((px - pos["e"]) - fee * (abs(pos["e"]) + abs(px))) / pos["r"], pos["rr"]))
                pos = None
            else:
                if h[i] >= pos["e"] + 2 * pos["r"]:
                    pos["armed"] = True
                if trail_low is not None and a[i] and trail_low > pos["e0low"] and (exitm != "trail2r" or pos["armed"]):
                    pos["stop"] = max(pos["stop"], trail_low - CUSH * a[i])
        # pending entry at this candle's open
        if setup and setup.get("go") == i:
            ok = not pos and curd[0] == 1 and allowed(x_ts)
            px = o[i]
            r = px - setup["stop"]
            if ok and r > 0 and minrr is not None:
                ok = (setup["tgt"] - px) >= minrr * r  # rule 17: target at least 2x the risk (before fees)
            if ok and kz:
                ok = killzone(x_ts)  # rule 19: entry candle opens in London 2-5 AM or New York 7-10 AM ET
            if ok and r > 0 and setup["tgt"] > px:
                pos = {"e": px, "stop": setup["stop"], "tgt": setup["tgt"], "r": r, "ts": x_ts,
                       "rr": (setup["tgt"] - px) / r, "e0low": setup["stop"], "armed": False}
                trail_low = None
                if l[i] <= pos["stop"]:  # the entry candle itself can stop out
                    out.append((x_ts, x_ts, ((pos["stop"] - px) - fee * (abs(px) + abs(pos["stop"]))) / r, pos["rr"]))
                    pos = None
            setup = None
        # zone upkeep on this candle
        for z in zones:
            if z[6]:
                continue
            if z[5] and l[i] <= z[1]:
                z[6] = True  # used up: came back after reaching 50% and leaving
                continue
            if l[i] <= z[1]:
                z[3] = True
                if l[i] <= z[2]:
                    z[4] = True
            if z[4] and c[i] > z[1]:
                z[5] = True
        highs = [v for v in highs if v > h[i]][-200:]
        if x_ts >= t0 and a[i]:
            box = [setup]
            step(i, o, h, l, c, a, way, zmethod, bstop, curd, cur4, zones, swl, swl_done, leg_hi, box, highs, pos)
            setup = box[0]
        if swl is not None and not swl_done and l[i] < swl and c[i] >= swl:
            swl_done = True
        elif swl is not None and not swl_done and c[i] < swl:
            swl_done = True
        # candle i closed: update the 4H / daily view and kill zones on a 4H body close below them
        end = x_ts + tf
        if end % H4 == 0:
            cur4 = v4.get(end, cur4)
            for z in zones:
                if not z[6] and c[i] < z[0]:
                    z[6] = True
            zones = [z for z in zones if not z[6]][-20:]
        if end % D1 == 0:
            curd = vd.get(end, curd)
    return out


def killzone(t):
    e = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).astimezone(NY)
    return 2 <= e.hour < 5 or 7 <= e.hour < 10


def allowed(t):
    d = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc)
    return d.month != 12 and (d + dt.timedelta(days=1)).month == d.month


def step(i, o, h, l, c, a, way, zmethod, bstop, curd, cur4, zones, swl, swl_done, leg_hi, box, highs, pos):
    s = box[0]
    if s and s["stage"] in ("swept",):
        if l[i] < s["low"]:
            s = None  # new low under the sweep before the shift: setup gone (a new sweep can start below)
        elif c[i] > s["lh"]:
            ms_low = l[i]
            stop = ((o[i] + c[i]) / 2 if way == "B" and bstop == "half" else ms_low) - CUSH * a[i]
            above = [v for v in highs if v > c[i]]
            if not above:
                box[0] = None
                return
            tgt = min(above)
            if way == "B":
                box[0] = {"stage": "wait", "go": i + 2, "stop": stop, "tgt": tgt}
                return
            if zmethod == "pivot":
                downs = [k for k in range(s["k"], i) if c[k] < o[k]]
                k0 = downs[-1] if downs else s["k"]
                ztop = h[k0]
            else:
                ztop = max(h[s["k"]:i])
            box[0] = {"stage": "shifted", "stop": stop, "tgt": tgt, "ztop": ztop, "rej": None}
            return
    if s and s["stage"] == "wait":
        if l[i] <= s["stop"] or h[i] >= s["tgt"]:
            box[0] = None
        return
    if s and s["stage"] == "shifted":
        if l[i] <= s["stop"] or h[i] >= s["tgt"]:
            box[0] = None  # failed (one try) / ran to target with no pullback
            return
        if s["rej"] is not None and c[i] > o[i] and c[i] > s["rej"]:
            s["go"] = i + 1
            box[0] = s
            return
        if l[i] <= s["ztop"] and min(o[i], c[i]) - l[i] >= abs(c[i] - o[i]):
            s["rej"] = h[i]
        box[0] = s
        return
    # new sweep at a live 4H zone in the discount, daily trend up
    if pos or s is not None or curd[0] != 1 or cur4[1] is None or leg_hi is None:
        box[0] = s
        return
    if swl is not None and not swl_done and l[i] < swl and c[i] >= swl:
        for z in zones:
            if not z[6] and z[3] and z[1] <= cur4[1] and l[i] <= z[1] and c[i] >= z[0]:
                if leg_hi > c[i]:
                    box[0] = {"stage": "swept", "low": l[i], "lh": leg_hi, "k": i}
                return
    box[0] = s


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
    lo, sh = stats([t[2] for t in tr if t[4] == 1]), stats([t[2] for t in tr if t[4] == -1])
    rr = sorted(t[3] for t in tr)[len(tr) // 2]
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    w, ls = [t[2] for t in tr if t[2] > 0], [t[2] for t in tr if t[2] <= 0]
    aw = f"{sum(w) / len(w):+.2f}R" if w else "-"
    al = f"{sum(ls) / len(ls):+.2f}R" if ls else "-"
    return (f"| {name} | {f['n']} | {f['n'] / years / 52:.1f} | {f['win']:.0f}% | {aw} | {al} | {rr:.1f} | {f['pf']:.2f} | "
            f"{f['avg']:+.2f}R | {f['dd']:.0f}R | {p(h1)} | {p(h2)} | {p(lo)} | {p(sh)} |")


def both_sides(coin, vers, tf=M15):
    raw = m15.m15(coin)
    t_min = B.ms(B.START) - 120 * 86400000
    raw = [x for x in raw if x["ts"] >= t_min]
    ts = [x["ts"] for x in raw]
    o, h, l, c = ([x[k] for x in raw] for k in "ohlc")
    del raw
    if tf != M15:
        hb = bars_of(o, h, l, c, ts, tf)
        ts = [x["ts"] for x in hb]
        o, h, l, c = ([x[k] for x in hb] for k in "ohlc")
        del hb
    gc.collect()
    res = {}
    for name, way, zm, fee, bs, *opt in vers:
        kw = dict(zip(("minrr", "kz", "exitm"), opt), tf=tf)
        lo = [t + (1,) for t in run(o, h, l, c, ts, way, zm, fee, bs, **kw)]
        sh = [t + (-1,) for t in run([-v for v in o], [-v for v in l], [-v for v in h], [-v for v in c], ts,
                                      way, zm, fee, bs, **kw)]
        # one trade per coin at a time: drop a trade that starts while the other side is still open
        keep, busy = [], -1
        for t in sorted(lo + sh):
            if t[0] > busy:
                keep.append(t)
                busy = t[1]
        res[name] = keep
    return res


def main():
    years = (dt.datetime.now(dt.timezone.utc) - B.START).days / 365.25
    hdr = ("| Version | Trades | /wk | Win % | Avg win | Avg loss | Typical R:R | PF | Avg | Worst DD | 2019-22 PF | "
           "2023-now PF | Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    vers = [("Way A, Pivot zones", "A", "pivot", 0.0005, "bottom"), ("Way A, Range zones", "A", "range", 0.0005, "bottom"),
            ("Way B, stop at bottom", "B", "pivot", 0.0005, "bottom"), ("Way B, stop halfway", "B", "pivot", 0.0005, "half")]
    extra = [("Way A Pivot, zero fees", "A", "pivot", 0.0, "bottom"), ("Way A Range, zero fees", "A", "range", 0.0, "bottom"),
             ("Way B bottom, zero fees", "B", "pivot", 0.0, "bottom"), ("Way A Pivot, OKX 0.35%", "A", "pivot", 0.0035, "bottom")]
    if sys.argv[1:] == ["open"]:  # Oct 9: Jeff filled OPEN rules 17 and 19 with Brad's numbers
        vers = [("Way A Range, as before", "A", "range", 0.0005, "bottom"),
                ("+ rule 17 (target 2x risk)", "A", "range", 0.0005, "bottom", 2.0, False),
                ("+ rule 19 (killzones)", "A", "range", 0.0005, "bottom", None, True),
                ("+ rules 17 and 19", "A", "range", 0.0005, "bottom", 2.0, True)]
        extra = []
    if sys.argv[1:2] == ["trail"]:  # Oct 9: Jeff asked for trailing exits, with/without 2x, on 15m and 1H
        return trail_main(years, hdr)
    only = [x for x in sys.argv[1:] if x != "open"]
    for title, coins in (("main: BTC ETH SOL XRP BNB", MAIN), ("never-seen: ADA DOGE LINK AVAX LTC DOT", UNSEEN)):
        vs = vers + extra
        allr = {v[0]: [] for v in vs}
        for cn in coins:
            if only and cn not in only:
                continue
            for k, v in both_sides(cn, vs).items():
                allr[k] += v
            gc.collect()
            print(f"  ({cn} done)", flush=True)
        print(f"\n### {title} (Binance.US 0.05% a side unless noted)\n\n{hdr}")
        for v in vs:
            print(row(v[0], allr[v[0]], years))
        sys.stdout.flush()


def trail_main(years, hdr):
    F = 0.0005
    exits = [("target + trail", "target"), ("trail only", "trail"), ("trail after 2R", "trail2r")]
    filt = [("", None, False), (" + rule 17", 2.0, False), (" + rule 19", None, True), (" + 17 + 19", 2.0, True)]
    rng = [(f"Range, {en}{fn}", "A", "range", F, "bottom", mr, kz, ex) for en, ex in exits for fn, mr, kz in filt]
    base1h = [("Way A, Pivot zones", "A", "pivot", F, "bottom"), ("Way B, stop at bottom", "B", "pivot", F, "bottom"),
              ("Way B, stop halfway", "B", "pivot", F, "half")]
    charts = [x for x in (("15m", M15, rng), ("1H", 3600000, base1h + rng)) if x[0] in (sys.argv[2:] or ("15m", "1H"))]
    for chart, tf, vs in charts:
        for title, coins in (("main: BTC ETH SOL XRP BNB", MAIN), ("never-seen: ADA DOGE LINK AVAX LTC DOT", UNSEEN)):
            allr = {v[0]: [] for v in vs}
            for cn in coins:
                for k, v in both_sides(cn, vs, tf).items():
                    allr[k] += v
                gc.collect()
            print(f"\n### {chart} chart, {title} (Binance.US 0.05% a side)\n\n{hdr}")
            for v in vs:
                print(row(v[0], allr[v[0]], years))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
