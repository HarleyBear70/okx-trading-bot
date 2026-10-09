"""
BRAD_MM: Brad Goh's full "Market Mechanics" rules (research/BRAD_RULEBOOK.md, all 35 episodes) that
research/brad_rules.py never tested, added one at a time on top of the brad_bot.py version (Oct 8 2026).

Base (= brad_bot.py): 1H, 4H trend, price in the 4H discount/premium, sweep of a swing low/high in the last
48 candles, then a market shift (body close) that left a fair value gap; limit at the gap's near edge for 1 day;
stop past the sweep extreme - 0.1 ATR; fixed 3R; set and forget.
New knobs (rulebook section 9):
  zone   entry at the zone that caused the shift (Brad's "market shift entry model"): the candle with the
         extreme low/high between sweep and shift (pivot method), limit at its far edge (top for longs).
         No pullback within 1 day = no trade.
  struct target = the swing high/low the pullback came from (highest high / lowest low of the 100 candles
         before the sweep, Brad's "next opposing level"); skip the trade if it is under 2R away.
  pdh    target = prior UTC day's high (longs) / low (shorts); skip if under 2R.
  cal    no new setups on Mondays, Fridays, in December, or on the last day of the month (UTC).
Costs and data as research/battery.py (crypto 0.05% a side = Binance.US 0.02% fee + slippage).

  python3 research/brad_mm.py
"""
import calendar
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_more as BM  # noqa: E402
import brad_rules as BR  # noqa: E402
import jeff_topdown as J  # noqa: E402

UTC = dt.timezone.utc
LOOK = 100


def blocked(ts):
    d = dt.datetime.fromtimestamp(ts / 1000, UTC)
    return d.weekday() in (0, 4) or d.month == 12 or d.day == calendar.monthrange(d.year, d.month)[1]


def run(market, b, tf, rr=3, lev=1.0, win=48, entry="fvg", tgt="R", cal=False):
    tf_ms = B.MS[tf]
    s = J.structure(b)
    h4 = J.htf_view(b, J.H4, tf_ms)
    a = B.atr(b)
    t0 = B.ms(B.START)
    dayb = 86400000 // tf_ms
    # prior completed UTC day high/low per bar
    pdh, pdl, cur_day, dh, dl, prev = [], [], None, None, None, (None, None)
    for x in b:
        d = x["ts"] // 86400000
        if d != cur_day:
            if cur_day is not None:
                prev = (dh, dl)
            cur_day, dh, dl = d, x["h"], x["l"]
        else:
            dh, dl = max(dh, x["h"]), min(dl, x["l"])
        pdh.append(prev[0])
        pdl.append(prev[1])
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
        if order and not pos:
            sd, ent, stp, tg, exp = order
            if k > exp or (x["h"] >= tg if sd == 1 else x["l"] <= tg):
                order = None
            elif (x["o"] <= stp) if sd == 1 else (x["o"] >= stp):
                order = None
            elif (x["l"] <= ent) if sd == 1 else (x["h"] >= ent):
                px = min(ent, x["o"]) if sd == 1 else max(ent, x["o"])
                dist = (px - stp) * sd
                if dist > 0:
                    u = min(eq * B.RISK / dist, eq * lev / px)
                    pos = {"side": sd, "entry": px, "stop": stp, "tgt": tg, "u": u, "ts": x["ts"],
                           "ec": B.cost(market, x, px), "new": True}
                order = None
        if pos:
            sd = pos["side"]
            if (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"]):
                gap_px = min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"])
                close(x, pos["stop"] if pos["new"] else gap_px)
            elif not pos["new"] and ((x["h"] >= pos["tgt"]) if sd == 1 else (x["l"] <= pos["tgt"])):
                close(x, max(pos["tgt"], x["o"]) if sd == 1 else min(pos["tgt"], x["o"]))
            else:
                pos["new"] = False
        if not pos and not order and s["shift"][k] and a[k] and not (cal and blocked(x["ts"])):
            sd = s["trend"][k]
            mid = h4[k][1]
            ok = h4[k][0] == sd and mid is not None and ((x["c"] <= mid) if sd == 1 else (x["c"] >= mid))
            want = -1 if sd == 1 else 1
            js = [j for j in range(max(0, k - win), k + 1) if s["tdir"][j] == want] if ok else []
            gap = BR.fvg(b, sd, js[-1], k) if js else None
            if gap:
                j = js[-1]
                seg = range(j, k + 1)
                m = min(seg, key=lambda i: b[i]["l"]) if sd == 1 else max(seg, key=lambda i: b[i]["h"])
                ext = b[m]["l"] if sd == 1 else b[m]["h"]
                stp = ext - sd * BR.CUSH * a[k]
                ent = gap[0] if entry == "fvg" else (b[m]["h"] if sd == 1 else b[m]["l"])
                if (ent - x["c"]) * sd >= 0:  # zone edge not below price: no pullback possible, skip
                    ent = None
                risk = (ent - stp) * sd if ent is not None else 0
                if risk > 0:
                    if tgt == "R":
                        tg = ent + sd * rr * risk
                    elif tgt == "struct":
                        back = b[max(0, j - LOOK):j + 1]
                        tg = max(y["h"] for y in back) if sd == 1 else min(y["l"] for y in back)
                    else:
                        tg = pdh[k] if sd == 1 else pdl[k]
                    if tg is not None and (tg - ent) * sd >= 2 * risk:
                        order = (sd, ent, stp, tg, k + dayb)
        if k % dayb == 0:
            op = pos["side"] * (x["c"] - pos["entry"]) * pos["u"] if pos else 0
            curve.append((x["ts"], eq + op))
    curve.append((b[-1]["ts"], eq))
    return trades, curve


VERSIONS = [
    ("base = brad_bot (FVG entry, 3R)", dict()),
    ("+ zone entry", dict(entry="zone")),
    ("+ structural target (min 2R)", dict(tgt="struct")),
    ("+ prior-day high/low target (min 2R)", dict(tgt="pdh")),
    ("+ calendar skips (Mon/Fri/Dec/month-end)", dict(cal=True)),
    ("zone + struct", dict(entry="zone", tgt="struct")),
    ("zone + 3R + calendar", dict(entry="zone", cal=True)),
    ("ALL: zone + struct + calendar", dict(entry="zone", tgt="struct", cal=True)),
]


def main():
    print("| Market | Version | Trades/wk | Win % | PF | R/trade | 2019-22 PF | 2023-now PF | Long PF | Short PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    sets = [("crypto", "1H", BM.COINS23, 1.0)]
    if os.path.isdir(B.FXDIR):
        sets.append(("forex", "1H", B.FOREX, 20.0))
    for market, tf, insts, lev in sets:
        B.MS_CUR[0] = B.MS[tf]
        data = {}
        for i in insts:
            try:
                data[i] = B.load(market, i, tf)
            except Exception:
                pass
        for name, kw in VERSIONS:
            all_tr, curves = [], []
            for i, b in data.items():
                tr, cv = run(market, b, tf, lev=lev, **kw)
                all_tr += tr
                curves.append(cv)
            port = B.mix(curves)
            f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
            n = sum(1 for _, _, t in all_tr if t >= B.ms(B.START))
            r = sum(p for _, p, t in all_tr if t >= B.ms(B.START)) / max(n, 1) / (1000 * B.RISK)
            pf = lambda s: "-" if s is None else f"{s['pf']:.2f}"
            lp = "-" if f["long_pf"] is None else f"{f['long_pf']:.2f}"
            sp = "-" if f["short_pf"] is None else f"{f['short_pf']:.2f}"
            print(f"| {market} ({len(data)}) {tf} | {name} | {f['tpw']:.1f} | {f['win']:.0f}% | {f['pf']:.2f} | {r:+.2f} | "
                  f"{pf(h1)} | {pf(h2)} | {lp} | {sp} |", flush=True)


if __name__ == "__main__":
    main()
