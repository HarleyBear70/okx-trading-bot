"""
BRAD: Brad Goh (The Trading Geek) sweep + FVG model, from Jeff's notes (Claude Files/To Claude, Oct 8 2026).
Same structure engine as research/jeff_topdown.py (Smoke Detector: swings of 5, market shift, traps = sweeps).

  1. Direction: 4H trend (optionally the daily too, "+D1").
  2. Location: price in the 4H discount for longs / premium for shorts (50% of the swing range).
  3. Sweep: a liquidity sweep of a swing low (longs) / high (shorts) in the last 12 entry candles.
  4. Shift + displacement: market shift on the entry chart, and the move left a fair value gap
     (no FVG between the sweep and the shift = no displacement = no trade).
  5. Entry: limit order at the near edge of the newest FVG (pullback into it). Cancelled after 1 day,
     or if price reaches the target or the stop first.
  6. Stop: just past the sweep's extreme (protected low/high) -/+ 0.1 ATR.
  7. Target: fixed 2R or 3R. Set and forget, no trailing.
  NY: the shift must happen 12:00-16:00 UTC (New York morning, Silver Bullet style).
Same costs, 0.5% risk and data as research/battery.py; stop and target in the same candle counts as the stop.

  python3 research/brad_rules.py
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402

SWEEP_WIN, CUSH = 12, 0.1


def fvg(b, side, j, k):
    """newest FVG made between the sweep j and the shift k: (near edge, far edge), or None"""
    for m in range(k, max(j + 2, 2) - 1, -1):
        if side == 1 and b[m]["l"] > b[m - 2]["h"]:
            return b[m]["l"], b[m - 2]["h"]
        if side == -1 and b[m]["h"] < b[m - 2]["l"]:
            return b[m]["h"], b[m - 2]["l"]
    return None


def run(market, b, tf, rr, ny=False, daily=False, lev=1.0, win=SWEEP_WIN, discount=True):
    tf_ms = B.MS[tf]
    s = J.structure(b)
    h4 = J.htf_view(b, J.H4, tf_ms)
    d1 = J.htf_view(b, J.D1, tf_ms) if daily else None
    a = B.atr(b)
    t0 = B.ms(B.START)
    dayb = 86400000 // tf_ms
    eq, pos, order, trades, curve = 1000.0, None, None, [], []

    def close(x, px):
        nonlocal eq, pos
        pnl = pos["side"] * (px - pos["entry"]) * pos["u"] - (pos["ec"] + B.cost(market, x, px)) * pos["u"]
        eq += pnl
        trades.append((pos["side"], pnl, pos["ts"]))
        pos = None

    for k, x in enumerate(b):
        if x["ts"] < t0:
            continue
        # working limit order
        if order and not pos:
            sd, ent, stp, tgt, exp = order
            if k > exp or (x["h"] >= tgt if sd == 1 else x["l"] <= tgt):
                order = None
            elif (x["o"] <= stp) if sd == 1 else (x["o"] >= stp):
                order = None
            else:
                hit = (x["l"] <= ent) if sd == 1 else (x["h"] >= ent)
                if hit:
                    px = min(ent, x["o"]) if sd == 1 else max(ent, x["o"])
                    dist = (px - stp) * sd
                    if dist > 0:
                        u = min(eq * B.RISK / dist, eq * lev / px)
                        pos = {"side": sd, "entry": px, "stop": stp, "tgt": tgt, "u": u, "ts": x["ts"],
                               "ec": B.cost(market, x, px), "new": True}
                    order = None
        # open trade: stop first, then target
        if pos:
            sd = pos["side"]
            if (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"]):
                gap_px = min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"])
                close(x, pos["stop"] if pos["new"] else gap_px)
            elif not pos["new"] and ((x["h"] >= pos["tgt"]) if sd == 1 else (x["l"] <= pos["tgt"])):
                close(x, max(pos["tgt"], x["o"]) if sd == 1 else min(pos["tgt"], x["o"]))
            else:
                pos["new"] = False
        # new setup
        if not pos and not order and s["shift"][k] and a[k]:
            sd = s["trend"][k]
            ok = h4[k][0] == sd and (not daily or d1[k][0] == sd)
            mid = h4[k][1]
            if discount:
                ok = ok and mid is not None and ((x["c"] <= mid) if sd == 1 else (x["c"] >= mid))
            if ok and ny:
                hr = dt.datetime.fromtimestamp(x["ts"] / 1000, dt.timezone.utc).hour
                ok = 12 <= hr < 16
            if ok:
                want = -1 if sd == 1 else 1  # longs need a swept low, shorts a swept high
                js = [j for j in range(max(0, k - win), k + 1) if s["tdir"][j] == want]
                gap = fvg(b, sd, js[-1], k) if js else None
                if gap:
                    j = js[-1]
                    ext = min(y["l"] for y in b[j:k + 1]) if sd == 1 else max(y["h"] for y in b[j:k + 1])
                    stp = ext - sd * CUSH * a[k]
                    ent = gap[0]
                    risk = (ent - stp) * sd
                    if risk > 0:
                        order = (sd, ent, stp, ent + sd * rr * risk, k + dayb)
        if k % dayb == 0:
            op = pos["side"] * (x["c"] - pos["entry"]) * pos["u"] if pos else 0
            curve.append((x["ts"], eq + op))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


def main():
    sets = [("crypto", B.CRYPTO, 1.0)]
    if os.path.isdir(B.FXDIR):
        sets.append(("forex", B.FOREX, 20.0))
    versions = [("2R", 2, False, False), ("3R", 3, False, False), ("2R + daily", 2, False, True),
                ("2R + NY time", 2, True, False), ("3R + NY time", 3, True, False)]
    print("| Market | Chart | Version | 2019-now (return / drop / PF) | 2019-22 | 2023-now | Win % | Trades/wk | Long PF | Short PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for market, insts, lev in sets:
        for tf in ("1H", "15m"):
            B.MS_CUR[0] = B.MS[tf]
            data = {i: B.load(market, i, tf) for i in insts}
            for name, rr, ny, daily in versions:
                all_tr, curves = [], []
                for i in insts:
                    tr, cv = run(market, data[i], tf, rr, ny, daily, lev)
                    all_tr += tr
                    curves.append(cv)
                port = B.mix(curves)
                f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in
                             ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
                lp = "-" if f["long_pf"] is None else f"{f['long_pf']:.2f}"
                sp = "-" if f["short_pf"] is None else f"{f['short_pf']:.2f}"
                print(f"| {market} | {tf} | {name} | {B.cell(f)} | {B.cell(h1)} | {B.cell(h2)} | {f['win']:.0f}% | "
                      f"{f['tpw']:.1f} | {lp} | {sp} |", flush=True)


if __name__ == "__main__":
    main()
