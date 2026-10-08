"""
SB: session-open breakout on crypto (Jeff's plan, Claude Files/To Claude/"my question lol I", Oct 7 2026).

Box = 00:00 UTC to London open (DST-aware). Skip if box wider than its 20-day median. 4H trend filter
(50 EMA or Supertrend 10/3). A 1H close outside the box with volume >= 1.5x the 20-bar average, inside the
first 4 hours after London open (A) or New York 09:30 (B); enter at the next open; one trade per coin per day.
Stop at box middle (or opposite side) +/- 0.1 ATR cushion; skip if > 1.35% away. Exit A: 2R target. Exit B:
breakeven at 1R, then 2 ATR(14) trail. Everything still open is closed at 21:00 UTC.
Costs 0.1% fee + 0.05% slippage each side. 0.5% risk of balance, $1,000, 2022-now.
Tune on 2022-2024, one run on 2025-now (unseen). Same-bar stop and target: the stop counts.

Run: python3 research/sb_session.py
"""
import datetime as dt
import json
import os
import random
import statistics
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hourly as hr  # noqa: E402

UTC = dt.timezone.utc
LON, NYC = zoneinfo.ZoneInfo("Europe/London"), zoneinfo.ZoneInfo("America/New_York")
COINS = ["BTC", "ETH", "SOL", "XRP"]
H = 3600000
START = dt.datetime(2022, 1, 1, tzinfo=UTC)
SPLIT = dt.datetime(2025, 1, 1, tzinfo=UTC)
COST = 0.0015  # each side
RISK = 0.005
MAX_STOP = 0.0135


def ema(xs, n):
    out, k, e = [], 2 / (n + 1), None
    for x in xs:
        e = x if e is None else e + k * (x - e)
        out.append(e)
    return out


def atr(bars, n):
    out, a = [], None
    for i, b in enumerate(bars):
        tr = b["h"] - b["l"] if i == 0 else max(b["h"] - b["l"], abs(b["h"] - bars[i - 1]["c"]), abs(b["l"] - bars[i - 1]["c"]))
        a = tr if a is None else (a * (n - 1) + tr) / n
        out.append(a if i >= n else None)
    return out


def supertrend(bars, n=10, m=3):
    a = atr(bars, n)
    up_dir, fu, fl, out = True, None, None, []
    for i, b in enumerate(bars):
        if a[i] is None:
            out.append(None)
            continue
        mid = (b["h"] + b["l"]) / 2
        bu, bl = mid + m * a[i], mid - m * a[i]
        pc = bars[i - 1]["c"]
        fu = bu if fu is None or bu < fu or pc > fu else fu
        fl = bl if fl is None or bl > fl or pc < fl else fl
        if up_dir and b["c"] < fl:
            up_dir = False
        elif not up_dir and b["c"] > fu:
            up_dir = True
        out.append(up_dir)
    return out


def prep(coin):
    bars = [b for b in hr.hourly(coin) if b["ts"] >= int((START - dt.timedelta(days=60)).timestamp() * 1000)]
    h4 = hr.to_4h(bars)
    e50 = ema([b["c"] for b in h4], 50)
    st = supertrend(h4)
    # trend known at time T = last 4H bar that closed at or before T
    trend = {}
    for i, b in enumerate(h4):
        trend[b["ts"] + 4 * H] = {"ema": b["c"] > e50[i] if i >= 50 else None, "st": st[i]}
    a14 = atr(bars, 14)
    days = {}
    for i, b in enumerate(bars):
        days.setdefault(dt.datetime.fromtimestamp(b["ts"] / 1000, UTC).date(), []).append(i)
    return {"bars": bars, "trend": trend, "atr": a14, "days": days, "idx": {b["ts"]: i for i, b in enumerate(bars)}}


def trend_at(d, close_ts, kind):
    k = close_ts - close_ts % (4 * H)
    t = d["trend"].get(k)
    return None if t is None else t[kind]


def signals(d, p):
    """Trades (in R, after costs) for one coin with settings p."""
    bars, a14, idx = d["bars"], d["atr"], d["idx"]
    out, widths = [], []
    for day in sorted(d["days"]):
        lo_open = dt.datetime.combine(day, dt.time(8), LON).astimezone(UTC)
        box_end = int(lo_open.timestamp() * 1000) + p["box_shift"] * H
        day0 = int(dt.datetime.combine(day, dt.time(0), UTC).timestamp() * 1000)
        box = [bars[idx[t]] for t in range(day0, box_end, H) if t in idx]
        if len(box) < 5:
            continue
        hi, lo = max(b["h"] for b in box), min(b["l"] for b in box)
        width = (hi - lo) / ((hi + lo) / 2)
        med = statistics.median(widths[-20:]) if len(widths) >= 20 else None
        widths.append(width)
        if med is None or width > med or dt.datetime.combine(day, dt.time(0), UTC) < START:
            continue
        if p["window"] == "london":
            w0 = int(lo_open.timestamp() * 1000)
        else:  # first full hour bar that starts at/after 09:30 New York
            w0 = int(dt.datetime.combine(day, dt.time(10), NYC).astimezone(UTC).timestamp() * 1000)
        end21 = day0 + 21 * H
        for t in range(w0, w0 + 4 * H, H):
            i = idx.get(t)
            if i is None or i + 1 >= len(bars) or i < 21 or a14[i] is None:
                continue
            b = bars[i]
            vavg = sum(x["v"] for x in bars[i - 20:i]) / 20
            if b["v"] < p["vol"] * vavg:
                continue
            side = 1 if b["c"] > hi else -1 if b["c"] < lo else 0
            if not side or (p["longs_only"] and side < 0):
                continue
            tr = trend_at(d, t + H, p["trend"])
            if tr is None or tr != (side > 0):
                continue
            if p.get("rand_side") is not None:
                side = p["rand_side"]()
            tr_ = simulate(bars, a14, i + 1, side, hi, lo, end21, p)
            if tr_:
                tr_.update(day=day, coin=None, side=side, ts=bars[i + 1]["ts"])
                out.append(tr_)
            break  # one trade per coin per day (first signal)
    return out


def simulate(bars, a14, j, side, hi, lo, end21, p):
    entry = bars[j]["o"]
    if bars[j]["ts"] >= end21:
        return None
    cush = 0.1 * a14[j - 1]
    ref = (hi + lo) / 2 if p["stop"] == "mid" else (lo if side > 0 else hi)
    stop = ref - side * cush
    risk = (entry - stop) * side
    if risk <= 0 or risk / entry > MAX_STOP:
        return None
    target = entry + side * p["rr"] * risk if p["exit"] == "A" else None
    best, be = entry, False
    exit_px = None
    for k in range(j, len(bars)):
        b = bars[k]
        if b["ts"] >= end21:
            exit_px = b["o"]
            break
        o, h, l = b["o"], b["h"], b["l"]
        # gaps through the stop / target fill at the open
        if (o - stop) * side <= 0:
            exit_px = o
            break
        if target is not None and (o - target) * side >= 0:
            exit_px = o
            break
        if ((l if side > 0 else h) - stop) * side <= 0:
            exit_px = stop
            break
        if target is not None and ((h if side > 0 else l) - target) * side >= 0:
            exit_px = target
            break
        if p["exit"] == "B":  # stop moves after the bar closes
            best = max(best, h) if side > 0 else min(best, l)
            if not be and (best - entry) * side >= risk:
                be = True
            if be:
                trail = best - side * p["atr_k"] * a14[k]
                new = max(stop, entry, trail) if side > 0 else min(stop, entry, trail)
                stop = new
    if exit_px is None:
        return None
    gross = (exit_px - entry) * side
    net = gross - COST * (entry + exit_px)
    return {"r": net / risk, "gross_r": gross / risk}


BASE = {"box_shift": 0, "vol": 1.5, "atr_k": 2.0, "rr": 2.0, "longs_only": False}


def run(data, p, t0=START, t1=None):
    trades = []
    for c in COINS:
        for t in signals(data[c], p):
            t["coin"] = c
            trades.append(t)
    trades.sort(key=lambda t: t["ts"])
    return [t for t in trades if dt.datetime.fromtimestamp(t["ts"] / 1000, UTC) >= t0
            and (t1 is None or dt.datetime.fromtimestamp(t["ts"] / 1000, UTC) < t1)]


def stats(trades):
    bal, peak, dd, curve = 1000.0, 1000.0, 0.0, []
    for t in trades:
        bal += bal * RISK * t["r"]
        peak, dd = max(peak, bal), min(dd, bal / max(peak, bal) - 1)
        curve.append((t["ts"], bal))
    wins = [t["r"] for t in trades if t["r"] > 0]
    losses = [t["r"] for t in trades if t["r"] <= 0]
    pf = sum(wins) / -sum(losses) if losses and sum(losses) else float("inf")
    return {"n": len(trades), "win": 100 * len(wins) / len(trades) if trades else 0, "pf": pf,
            "aw": statistics.mean(wins) if wins else 0, "al": statistics.mean(losses) if losses else 0,
            "dd": 100 * dd, "net": bal - 1000, "curve": curve}


def variants():
    for trend in ("ema", "st"):
        for window in ("london", "ny"):
            for stop in ("mid", "opp"):
                for ex in ("A", "B"):
                    yield dict(BASE, trend=trend, window=window, stop=stop, exit=ex)


def name(p):
    return f"{p['trend'].upper():3} {p['window']:6} stop={p['stop']:3} exit={p['exit']}"


def main():
    data = {c: prep(c) for c in COINS}
    rows = []
    for p in variants():
        tr = run(data, p)
        tune = stats([t for t in tr if t["ts"] < SPLIT.timestamp() * 1000])
        test = stats([t for t in tr if t["ts"] >= SPLIT.timestamp() * 1000])
        rows.append((p, tr, tune, test))
        print(f"{name(p)} | tune n={tune['n']} pf={tune['pf']:.2f} net={tune['net']:+.0f} dd={tune['dd']:.1f}"
              f" | unseen n={test['n']} pf={test['pf']:.2f} net={test['net']:+.0f} dd={test['dd']:.1f}", flush=True)
    best = max(rows, key=lambda r: (r[2]["pf"] if r[2]["n"] >= 50 else 0))
    p, tr, tune, test = best
    res = {"variants": [{"name": name(r[0]), "tune": {k: v for k, v in r[2].items() if k != "curve"},
                         "unseen": {k: v for k, v in r[3].items() if k != "curve"}} for r in rows],
           "best": name(p), "params": p}
    unseen = [t for t in tr if t["ts"] >= SPLIT.timestamp() * 1000]
    res["per_coin"] = {c: {k: v for k, v in stats([t for t in unseen if t["coin"] == c]).items() if k != "curve"} for c in COINS}
    res["per_year"] = {}
    for y in range(2022, 2027):
        s = stats([t for t in tr if dt.datetime.fromtimestamp(t["ts"] / 1000, UTC).year == y])
        res["per_year"][y] = {k: v for k, v in s.items() if k != "curve"}
    res["longs"] = {k: v for k, v in stats([t for t in unseen if t["side"] > 0]).items() if k != "curve"}
    res["shorts"] = {k: v for k, v in stats([t for t in unseen if t["side"] < 0]).items() if k != "curve"}
    lo_only = run(data, dict(p, longs_only=True), SPLIT)
    res["longs_only_account"] = {k: v for k, v in stats(lo_only).items() if k != "curve"}
    # skeptic 2: random direction at the same entry times, same stops/exits (200 runs)
    rng = random.Random(7)
    rand_pf = []
    for _ in range(200):
        rp = dict(p, rand_side=lambda: rng.choice((1, -1)))
        rand_pf.append(stats(run(data, rp, SPLIT))["pf"])
    rand_pf.sort()
    res["random"] = {"median": rand_pf[100], "p95": rand_pf[190], "strategy": test["pf"]}
    # skeptic 3: neighbours (unseen period)
    nb = []
    for k, vals in (("box_shift", (-1, 1)), ("vol", (1.3, 2.0)), ("atr_k", (1.5, 2.5) if p["exit"] == "B" else ())):
        for v in vals:
            s = stats(run(data, dict(p, **{k: v}), SPLIT))
            nb.append({"change": f"{k}={v}", "n": s["n"], "pf": s["pf"], "net": s["net"], "dd": s["dd"]})
    res["neighbours"] = nb
    res["curve_all"] = stats(tr)["curve"]
    res["gross_pf_unseen"] = (sum(t["gross_r"] for t in unseen if t["gross_r"] > 0) /
                              -sum(t["gross_r"] for t in unseen if t["gross_r"] <= 0)) if unseen else 0
    print(json.dumps({k: v for k, v in res.items() if k not in ("variants", "curve_all")}, default=str, indent=1))


if __name__ == "__main__":
    main()
