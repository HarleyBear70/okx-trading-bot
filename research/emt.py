"""
EMT / "Exhaustion Mean Theory": mean reversion back to VWAP after a stretched, stalling candle. Asked for by
Chrome Claude on issue #4 (Oct 9 2026, Jeff approved), from a YouTube short.

PLAN (written before any results). Long and short. One trade at a time per market.
  VWAP    typical price x volume, resets 00:00 UTC (crypto) / 17:00 New York, the forex day roll (forex: tick volume).
  Stretch the exhaustion candle CLOSES 2.0+ ATR(14) away from VWAP and on the same side of the 9 EMA.
  Exhaust its wick in the stretch direction is 50%+ of its range, and it stalls: its close is not beyond the
          previous candle's close.
  Entry   ONLY on the next candle, when it breaks the exhaustion candle's low (short) / high (long); fill at that
          level, or at the open if it opens past it. Not broken on that next candle = setup cancelled.
  Stop    just past the wick (+0.1 ATR). Target = VWAP at the moment of entry (fixed, not trailing).
          Skip if VWAP is less than 1x the stop distance away. Stop and target in the same candle = stop (worst case).
          Still open when VWAP resets: closed at that candle's close.
  Costs   crypto 0.05% a side (Binance.US 0.02% + slippage); also shown at 0% and at OKX's 0.35%. Forex OANDA spread.
  Versions (3): A as stated on 5m; B = A but skip when the 4H trend (Smoke Detector structure) points the
          stretch's way (trend days run these over); C = A on 15m.
          Forex: only 15m history is on file, so forex gets C (and B on 15m).
  Markets main: BTC ETH SOL, EUR/USD gold. Never-seen: XRP BNB (5m; + ADA DOGE on 15m), GBP AUD JPY.

PASS RULES (judged on R per trade after costs, not win %): 100+ trades, profit factor 1.3+, average +0.10R or
better, PF 1.1+ in BOTH halves (2019-22 / 2023-now), worst drawdown under 24R, never-seen markets PF 1.1+.

  python3 research/emt.py
"""
import datetime as dt
import os
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402
import m5  # noqa: E402

B.MS["5m"] = 300000
NY = zoneinfo.ZoneInfo("America/New_York")
UTC = dt.timezone.utc
X, WICK, CUSH = 2.0, 0.5, 0.1


def day_key(market, ts):
    if market == "crypto":
        return ts // 86400000
    e = dt.datetime.fromtimestamp(ts / 1000, UTC).astimezone(NY)
    return (e + dt.timedelta(hours=7)).date()  # 17:00 NY starts the next forex day


def run(market, b, tf, trend=False, fee=None):
    cost = (lambda x, px: fee * px) if fee is not None else (lambda x, px: B.cost(market, x, px))
    a = B.atr(b)
    e9 = B.ema([x["c"] for x in b], 9)
    h4 = J.htf_view(b, J.H4, B.MS[tf]) if trend else None
    t0 = B.ms(B.START)
    out = []  # (ts, R)
    pv = vv = 0.0
    dk, vwap = None, [None] * len(b)
    for k, x in enumerate(b):
        d = day_key(market, x["ts"])
        if d != dk:
            dk, pv, vv = d, 0.0, 0.0
        v = x.get("v") or 0.0
        pv += (x["h"] + x["l"] + x["c"]) / 3 * v
        vv += v
        vwap[k] = pv / vv if vv else None
    pos, setup = None, None
    for k in range(1, len(b)):
        x = b[k]
        if pos:
            sd = pos["sd"]
            new_day = day_key(market, x["ts"]) != pos["day"]
            px = None
            if new_day:
                px = b[k - 1]["c"]  # closed at the last candle of the VWAP day
            elif (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"]):
                px = (min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"]))
            elif (x["h"] >= pos["tgt"]) if sd == 1 else (x["l"] <= pos["tgt"]):
                px = max(pos["tgt"], x["o"]) if sd == 1 else min(pos["tgt"], x["o"])
            if px is not None:
                ref = b[k - 1] if new_day else x
                out.append((pos["ts"], (sd * (px - pos["entry"]) - pos["ec"] - cost(ref, px)) / pos["risk"]))
                pos = None
            else:
                continue
        if setup:
            sd, lvl, stp, kk = setup
            setup = None
            if day_key(market, x["ts"]) == day_key(market, b[kk]["ts"]) and \
                    ((x["h"] >= lvl) if sd == 1 else (x["l"] <= lvl)):
                px = max(lvl, x["o"]) if sd == 1 else min(lvl, x["o"])
                risk = (px - stp) * sd
                tgt = vwap[kk]
                if risk > 0 and tgt is not None and (tgt - px) * sd >= risk:
                    pos = {"sd": sd, "entry": px, "stop": stp, "tgt": tgt, "risk": risk, "ts": x["ts"],
                           "ec": cost(x, px), "day": day_key(market, x["ts"])}
                    # the entry candle itself can stop out (worst case first)
                    if (x["l"] <= stp) if sd == 1 else (x["h"] >= stp):
                        out.append((x["ts"], (sd * (stp - px) - pos["ec"] - cost(x, stp)) / risk))
                        pos = None
                    continue
        if x["ts"] < t0 or not a[k] or vwap[k] is None or x["h"] == x["l"]:
            continue
        rng = x["h"] - x["l"]
        p = b[k - 1]
        up = x["c"] - vwap[k] >= X * a[k] and x["c"] > e9[k]   # stretched up -> short
        dn = vwap[k] - x["c"] >= X * a[k] and x["c"] < e9[k]   # stretched down -> long
        if up and (x["h"] - max(x["o"], x["c"])) / rng >= WICK and x["c"] <= p["c"]:
            sd = -1
        elif dn and (min(x["o"], x["c"]) - x["l"]) / rng >= WICK and x["c"] >= p["c"]:
            sd = 1
        else:
            continue
        if trend and h4[k][0] == -sd:  # 4H trend points the stretch's way
            continue
        lvl = x["h"] if sd == 1 else x["l"]
        stp = x["l"] - CUSH * a[k] if sd == 1 else x["h"] + CUSH * a[k]
        setup = (sd, lvl, stp, k)
    return out


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


def row(name, tr):
    tr.sort()
    cut = B.ms(B.CUT)
    f, h1, h2 = (stats([r for t, r in tr if keep(t)]) for keep in
                 (lambda t: True, lambda t: t < cut, lambda t: t >= cut))
    if not f:
        return f"| {name} | 0 | | | | | | |"
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    return (f"| {name} | {f['n']} | {f['win']:.0f}% | {f['pf']:.2f} | {f['avg']:+.2f}R | {f['dd']:.0f}R | "
            f"{p(h1)} | {p(h2)} |")


def load(market, inst, tf):
    if tf == "5m":
        return [dict(x, sp=0.0) for x in m5.m5(inst) if x["ts"] >= B.ms(B.START) - 30 * 86400000]
    return B.load(market, inst, tf)


SETS = [("crypto main: BTC ETH SOL", "crypto", ["BTC", "ETH", "SOL"], ("5m", "15m")),
        ("crypto never-seen: XRP BNB (+ ADA DOGE on 15m)", "crypto", ["XRP", "BNB"], ("5m",)),
        ("crypto never-seen 15m: XRP BNB ADA DOGE", "crypto", ["XRP", "BNB", "ADA", "DOGE"], ("15m",)),
        ("forex main: EUR/USD gold (15m only)", "forex", ["EUR_USD", "XAU_USD"], ("15m",)),
        ("forex never-seen: GBP AUD JPY (15m only)", "forex", ["GBP_USD", "AUD_USD", "USD_JPY"], ("15m",))]


def main():
    for title, market, insts, tfs in SETS:
        print(f"\n### {title}\n")
        print("| Version | Trades | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF |")
        print("|---|---|---|---|---|---|---|---|")
        for tf in tfs:
            data = {i: load(market, i, tf) for i in insts}
            tag = "A" if tf == "5m" else "C"
            print(row(f"{tag} {tf} as stated", [t for b in data.values() for t in run(market, b, tf)]), flush=True)
            print(row(f"B {tf} + skip 4H trend", [t for b in data.values() for t in run(market, b, tf, trend=True)]),
                  flush=True)
            if market == "crypto" and title.startswith("crypto main"):
                for fee, lab in ((0.0, "zero fees"), (0.0035, "OKX 0.35%")):
                    print(row(f"{tag} {tf} at {lab}", [t for b in data.values() for t in run(market, b, tf, fee=fee)]),
                          flush=True)
            del data


if __name__ == "__main__":
    main()
