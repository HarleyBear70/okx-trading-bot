"""
ASIAN RANGE -> LONDON PUSH -> NEW YORK REVERSAL ("power of three"), asked for by Chrome Claude on issue #4
(Oct 8 2026, Jeff approved). 15m candles, times are US Eastern (New York clock, DST handled).

PLAN (written before any results)
  1. Asian range: high/low of 19:00-24:00 ET (variant B: 00:00-05:00 UTC).
  2. London push: 02:00-05:00 ET trades beyond ONE side of the Asian range (a wick is enough).
     Both sides taken before New York = messy day, skip. Neither side = no trade.
  3. The push's extreme keeps updating until the reversal (the high of a push up, the low of a push down).
  4. New York reversal: 08:00-11:00 ET a 15m candle CLOSES past the start of the last leg into the extreme
     (lowest low of the 6 candles up to the high, for a push up) = Brad's market shift, the other way.
     The move must leave a fair value gap (displacement) or there is no trade.
  5. Entry: limit at the gap's near edge, valid until 12:00 ET. Stop: past the push extreme + 0.1 ATR.
     Target: the OTHER side of the Asian range; skip if under 2R. Still open at 16:00 ET: close at market.
     One trade a day. Costs: forex = OANDA spread (half each side), crypto = 0.05% a side (Binance.US + slippage).
  Variants (max 3): A = base, B = Asian range 00-05 UTC, C = A + only in the 4H trend's direction.
  Also reported: A without Mondays/Fridays (Brad's rule), as information only.

PASS RULES (all must hold, judged on R per trade after costs)
  - 100+ trades on the main markets (EUR/USD, GBP/USD, gold)    - profit factor 1.3+, average +0.15R or better
  - PF 1.1+ in BOTH halves (2019-22 and 2023-now)               - worst drawdown under 24R (12% at 0.5% risk = Jeff's guard)
  - never-seen markets (AUD, NZD, CAD, CHF, JPY) also PF 1.1+
  Crypto (BTC ETH SOL, then XRP BNB ADA DOGE never-seen) is checked the same way to see if it carries over.

  python3 research/asian_range.py
"""
import datetime as dt
import os
import sys
import zoneinfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_rules as BR  # noqa: E402
import jeff_topdown as J  # noqa: E402

NY = zoneinfo.ZoneInfo("America/New_York")
UTC = dt.timezone.utc
LEG = 6


def run(market, b, asia="et", trend=False, skip_mf=False):
    a = B.atr(b)
    h4 = J.htf_view(b, J.H4, B.MS["15m"]) if trend else None
    t0 = B.ms(B.START)
    out = []  # (ts, R)
    day = None
    for k, x in enumerate(b):
        u = dt.datetime.fromtimestamp(x["ts"] / 1000, UTC)
        e = u.astimezone(NY)
        mins = e.hour * 60 + e.minute
        tday = (e + dt.timedelta(hours=5)).date()  # 19:00 ET starts the next trading day
        if day is None or day["d"] != tday:
            day = {"d": tday, "ah": None, "al": None, "side": 0, "ext": None, "m": None, "done": False,
                   "order": None, "pos": None}
        D = day
        in_asia = (mins >= 19 * 60) if asia == "et" else u.hour < 5
        if in_asia:
            D["ah"] = x["h"] if D["ah"] is None else max(D["ah"], x["h"])
            D["al"] = x["l"] if D["al"] is None else min(D["al"], x["l"])
            continue
        if D["ah"] is None or D["done"] or x["ts"] < t0 or not a[k]:
            continue
        if 120 <= mins < 300 and not D["side"]:  # London push
            up, dn = x["h"] > D["ah"], x["l"] < D["al"]
            if up and dn:
                D["done"] = True
                continue
            if up or dn:
                D["side"] = 1 if up else -1  # side of the push; the trade goes the other way
        if not D["side"] or mins < 120:
            continue
        sd = -D["side"]  # trade direction
        pos = D["pos"]
        if pos:
            stop_hit = (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"])
            tgt_hit = (x["h"] >= pos["tgt"]) if sd == 1 else (x["l"] <= pos["tgt"])
            px = None
            if stop_hit:
                px = (min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"])) if not pos["new"] else pos["stop"]
            elif tgt_hit and not pos["new"]:
                px = max(pos["tgt"], x["o"]) if sd == 1 else min(pos["tgt"], x["o"])
            elif mins >= 16 * 60 - 15:
                px = x["c"]
            pos["new"] = False
            if px is not None:
                pnl = sd * (px - pos["entry"]) - pos["ec"] - B.cost(market, x, px)
                out.append((pos["ts"], pnl / pos["risk"], pos["wd"]))
                D["done"] = True
            continue
        if D["order"]:
            ent, stp, tg = D["order"]
            if mins >= 12 * 60 or ((x["h"] >= tg) if sd == 1 else (x["l"] <= tg)):
                D["done"] = True
                continue
            if (x["l"] <= ent) if sd == 1 else (x["h"] >= ent):
                if (x["o"] <= stp) if sd == 1 else (x["o"] >= stp):
                    D["done"] = True
                    continue
                px = min(ent, x["o"]) if sd == 1 else max(ent, x["o"])
                D["pos"] = {"entry": px, "stop": stp, "tgt": tg, "risk": (px - stp) * sd, "new": True, "ts": x["ts"],
                            "ec": B.cost(market, x, px), "wd": e.weekday()}
                # same candle can still stop it out
                if (x["l"] <= stp) if sd == 1 else (x["h"] >= stp):
                    pnl = sd * (stp - px) - D["pos"]["ec"] - B.cost(market, x, stp)
                    out.append((x["ts"], pnl / D["pos"]["risk"], e.weekday()))
                    D["done"] = True
            continue
        # track the push extreme (high of a push up / low of a push down)
        far = x["h"] if D["side"] == 1 else x["l"]
        if D["ext"] is None or (far - D["ext"]) * D["side"] > 0:
            D["ext"], D["m"] = far, k
            continue
        if D["side"] == -1 and x["h"] > D["ah"] or D["side"] == 1 and x["l"] < D["al"]:
            D["done"] = True  # both sides taken: messy day
            continue
        if not (8 * 60 <= mins < 11 * 60):
            if mins >= 11 * 60:
                D["done"] = True
            continue
        m = D["m"]
        leg = b[max(0, m - LEG):m + 1]
        start = min(y["l"] for y in leg) if D["side"] == 1 else max(y["h"] for y in leg)
        if (x["c"] - start) * sd <= 0:
            continue
        D["done"] = True  # one shot per day
        if trend and h4[k][0] != sd:
            continue
        if skip_mf and e.weekday() in (0, 4):
            continue
        gap = BR.fvg(b, sd, m, k)
        if not gap:
            continue
        ent = gap[0]
        stp = D["ext"] - sd * BR.CUSH * a[k]
        tg = D["al"] if sd == -1 else D["ah"]
        risk = (ent - stp) * sd
        if risk > 0 and (tg - ent) * sd >= 2 * risk and (ent - x["c"]) * sd < 0:
            D["order"], D["done"] = (ent, stp, tg), False
    return out


def stats(rs):
    if not rs:
        return None
    win = sum(r for r in rs if r > 0)
    loss = -sum(r for r in rs if r < 0)
    eq = peak = dd = 0.0
    for r in rs:
        eq += r
        peak = max(peak, eq)
        dd = max(dd, peak - eq)
    return {"n": len(rs), "win": 100 * sum(r > 0 for r in rs) / len(rs), "pf": win / loss if loss else 99,
            "avg": sum(rs) / len(rs), "dd": dd}


def row(name, trades, years):
    trades.sort()
    cut = B.ms(B.CUT)
    f, h1, h2 = (stats([r for t, r, _ in trades if keep(t)]) for keep in
                 (lambda t: True, lambda t: t < cut, lambda t: t >= cut))
    if not f:
        return f"| {name} | 0 | | | | | | | |"
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    return (f"| {name} | {f['n']} | {f['n'] / years / 52:.1f} | {f['win']:.0f}% | {f['pf']:.2f} | {f['avg']:+.2f} | "
            f"{f['dd']:.1f}R | {p(h1)} | {p(h2)} |")


VERSIONS = [("A base (Asia 19-24 ET)", dict()), ("B Asia 00-05 UTC", dict(asia="utc")),
            ("C base + 4H trend", dict(trend=True)), ("(info) A, no Mon/Fri", dict(skip_mf=True))]
SETS = [("forex main: EUR GBP gold", "forex", ["EUR_USD", "GBP_USD", "XAU_USD"]),
        ("forex never-seen: AUD NZD CAD CHF JPY", "forex", ["AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY"]),
        ("crypto main: BTC ETH SOL", "crypto", ["BTC", "ETH", "SOL"]),
        ("crypto never-seen: XRP BNB ADA DOGE", "crypto", ["XRP", "BNB", "ADA", "DOGE"])]


def main():
    years = (dt.datetime.now(UTC) - B.START).days / 365.25
    for title, market, insts in SETS:
        data = {i: B.load(market, i, "15m") for i in insts}
        print(f"\n### {title}\n")
        print("| Version | Trades | /wk | Win % | PF | Avg R | Worst DD | 2019-22 PF | 2023-now PF |")
        print("|---|---|---|---|---|---|---|---|---|")
        for name, kw in VERSIONS:
            tr = [t for b in data.values() for t in run(market, b, **kw)]
            print(row(name, tr, years), flush=True)
        per = [f"{i} {stats([r for _, r, _ in run(market, b)])['pf']:.2f}" if run(market, b) else f"{i} -"
               for i, b in data.items()]
        print("\nA per market (PF): " + ", ".join(per), flush=True)


if __name__ == "__main__":
    main()
