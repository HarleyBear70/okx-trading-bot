"""
BRAD_FX: the best Brad day-trade version on FOREX (Jeff, issue #4, Oct 10 2026): "test the Brad day method on forex,
where Brad trades." Exact round-3 version (research/BRAD_DAY.md): swing 5, range zones, BOS/iBOS rule, stop below
the 15m STRONG +0.05% (no cap), no trades 0.40-0.60, target 15m WEAK (min 2:1), 3% daily loss limit (6R a day).
Costs: REAL OANDA spreads (ask - bid at each 5m candle's close, practice-account history); half on entry, half on exit.
Data: OANDA practice M5 history (tools/oanda_history.py, read-only practice key; Dukascopy refused bulk downloads).

  Sessions  NO Asia. London only (2-5 AM ET), NY only (7-10 AM ET), both (Jeff).
  DXY       only buy XXX/USD pairs when the dollar index is in a 4H downtrend, only sell when it's up (Jeff).
            Downtrend = the same BOS/STRONG/WEAK structure rules, swing 5 (no new numbers).
            OANDA has no DXY, so it is built from the official ICE formula: 50.14348112 x EURUSD^-0.576 x USDJPY^0.136
            x GBPUSD^-0.119 x USDCAD^0.091 x USDSEK^0.042 x USDCHF^0.036 (5m closes, only when all six have a candle).
            USDJPY (USD first) = the opposite [GUESS]. GBPJPY has no USD: not filtered [GUESS].
  COT       only trade the way big speculators (CFTC legacy report, non-commercial long minus short) are net
            positioned (Jeff). USDJPY = opposite of the yen. GBPJPY = long only if specs are net long GBP AND net short
            JPY, short only for the reverse, else no trade [GUESS]. A report (Tuesday) counts from that Friday
            4 PM ET, when the CFTC publishes it (no peeking).
  Pairs     EURUSD GBPUSD GBPJPY USDJPY XAUUSD (Jeff); never-seen pair AUDUSD. OANDA 5m (mid prices), 2019 - now.

  python3 research/brad_fx.py          (round-3 bigger swing)
  python3 research/brad_fx.py leg5     (Jeff's newest leg, leg swing 5; leg3 etc.)
"""
import array
import csv
import datetime as dt
import gc
import glob
import io
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_day as D  # noqa: E402
import pure15 as P  # noqa: E402

MAIN, UNSEEN = ["EURUSD", "GBPUSD", "GBPJPY", "USDJPY", "XAUUSD"], ["AUDUSD"]
KW = dict(kz=True, maker=True, rng=True, stopm="strong", cap=None, band=0.10)
SESS = {"London only": [(2, 5)], "NY only": [(7, 10)], "London + NY": [(2, 5), (7, 10)]}
COT = {"EUR": "EURO FX - CHICAGO", "GBP": "BRITISH POUND", "JPY": "JAPANESE YEN - CHICAGO",
       "XAU": "GOLD - COMMODITY EXCHANGE", "AUD": "AUSTRALIAN DOLLAR - CHICAGO"}


OANDA = {"EURUSD": "EUR_USD", "GBPUSD": "GBP_USD", "GBPJPY": "GBP_JPY", "USDJPY": "USD_JPY", "XAUUSD": "XAU_USD",
         "AUDUSD": "AUD_USD", "USDCAD": "USD_CAD", "USDSEK": "USD_SEK", "USDCHF": "USD_CHF"}
DXY_W = {"EURUSD": -0.576, "USDJPY": 0.136, "GBPUSD": -0.119, "USDCAD": 0.091, "USDSEK": 0.042, "USDCHF": 0.036}


def load(pair):
    """OANDA M5 rows [ts, o, h, l, c (mid), spread at close, volume] from research/.cache/oanda5/,
    turned into compact arrays once (research/.cache/bin/OA5_*) so the Chromebook doesn't run out of memory."""
    keys = ("ts", "o", "h", "l", "c", "sp")
    path = lambda k: os.path.join(HERE, ".cache", "bin", f"OA5_{pair}_{k}.bin")
    if not os.path.exists(path("sp")):
        import gzip
        import json
        rows = json.load(gzip.open(os.path.join(HERE, ".cache", "oanda5", f"{OANDA[pair]}_M5.json.gz"), "rt"))
        for j, k in enumerate(keys):
            array.array("q" if k == "ts" else "d", (r[j] for r in rows)).tofile(open(path(k), "wb"))
        del rows
        gc.collect()
    out = {}
    for k in keys:
        x = array.array("q" if k == "ts" else "d")
        with open(path(k), "rb") as f:
            x.frombytes(f.read())
        out[k] = x
    return out


def dxy_series():
    """the dollar index from its six currencies (ICE formula), 5m candles where all six have one."""
    import math
    parts = {p: load(p) for p in DXY_W}
    ptr = {p: 0 for p in DXY_W}
    out = {k: array.array("q" if k == "ts" else "d") for k in ("ts", "o", "h", "l", "c")}
    base = math.log(50.14348112)
    for t in parts["EURUSD"]["ts"]:
        ok = True
        for p in DXY_W:
            ts_, j = parts[p]["ts"], ptr[p]
            while j < len(ts_) and ts_[j] < t:
                j += 1
            ptr[p] = j
            if j >= len(ts_) or ts_[j] != t:
                ok = False
        if not ok:
            continue
        vals = []
        for k in "ohlc":
            v = base
            for p, w in DXY_W.items():
                v += w * math.log(parts[p][k][ptr[p]])
            vals.append(math.exp(v))
        o, h, l, c = vals
        out["ts"].append(t)
        # negative weights turn a pair's high into the index's low: keep each candle consistent
        for k, v in zip("ohlc", (o, max(vals), min(vals), c)):
            out[k].append(v)
    return out


def dxy_trend():
    """[(close time of each 4H dollar-index candle, trend after it)]"""
    d = dxy_series()
    O, H, L, C, end = D.resample(d["ts"], d["o"], d["h"], d["l"], d["c"], D.H4)
    s = D.RangeStruct(O, H, L, C, 5)
    out = []
    for i, k in enumerate(end):
        if k >= 0:
            s.step(k)
            out.append((d["ts"][i] + 300000, s.trend))
    return out


def cot_net():
    """{currency: [(time the report becomes public, net non-commercial position)]}"""
    rows = {c: {} for c in COT}
    for f in sorted(glob.glob(os.path.join(HERE, ".cache", "cot", "deacot*.zip"))):
        z = zipfile.ZipFile(f)
        r = csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]), encoding="latin-1"))
        head = next(r)
        il, is_ = head.index("Noncommercial Positions-Long (All)"), head.index("Noncommercial Positions-Short (All)")
        for x in r:
            for cur, name in COT.items():
                if x[0].startswith(name):
                    day = dt.datetime.strptime(x[2], "%Y-%m-%d").replace(tzinfo=dt.timezone.utc)
                    pub = day + dt.timedelta(days=3, hours=21)  # Friday 4-5 PM ET
                    rows[cur][int(pub.timestamp() * 1000)] = int(x[il]) - int(x[is_])
    return {c: sorted(v.items()) for c, v in rows.items()}


def step_series(ts, series):
    """value of a (time, value) series as of each 5m candle (0 before the first one)."""
    out, j, cur = array.array("b"), 0, 0
    for t in ts:
        while j < len(series) and series[j][0] <= t:
            cur = series[j][1]
            j += 1
        out.append(cur)
    return out


def sign(v):
    return (v > 0) - (v < 0)


def allow(pair, ts, side, use_dxy, use_cot, dx, cot):
    """bytearray: 1 = this side (1 long / -1 short, in real-price terms) may enter on this candle."""
    n = len(ts)
    ok = bytearray(b"\x01" * n)
    if use_dxy and "USD" in pair:
        want = -side if pair.endswith("USD") else side  # XXX/USD: buy when the dollar falls
        tr = step_series(ts, dx)
        for i in range(n):
            if tr[i] != want:
                ok[i] = 0
    if use_cot:
        if pair == "GBPJPY":
            g = step_series(ts, [(t, sign(v)) for t, v in cot["GBP"]])
            y = step_series(ts, [(t, sign(v)) for t, v in cot["JPY"]])
            for i in range(n):
                if not (g[i] == side and y[i] == -side):
                    ok[i] = 0
        else:
            base = pair[:3] if pair[:3] != "USD" else pair[3:]
            flip = -1 if pair.startswith("USD") else 1
            v = step_series(ts, [(t, sign(x)) for t, x in cot[base]])
            for i in range(n):
                if v[i] * flip != side:
                    ok[i] = 0
    return ok


def main():
    if sys.argv[1:2] and sys.argv[1].startswith("leg"):  # Oct 10: Jeff's NEWEST leg (brad_day.LegStruct), e.g. "leg5"
        KW.update(rng="leg", leg=int(sys.argv[1][3:]))
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    dx, cot = dxy_trend(), cot_net()
    vers = [(f"{sn}{', DXY filter' if ud else ''}{', COT filter' if uc else ''}", sw, ud, uc)
            for sn, sw in SESS.items() for ud in (False, True) for uc in (False, True)]
    res = {g: {v[0]: [] for v in vers} for g in ("main", "unseen")}
    for pair in MAIN + UNSEEN:
        grp = "main" if pair in MAIN else "unseen"
        d = load(pair)
        md = dict(D.mirror(d), sp=d["sp"])
        for name, sw, ud, uc in vers:
            lo = [t + (1, pair) for t in D.run(d, 5, "range", kzw=sw, spr=d["sp"],
                                               allow=allow(pair, d["ts"], 1, ud, uc, dx, cot), **KW)]
            sh = [t + (-1, pair) for t in D.run(md, 5, "range", kzw=sw, spr=d["sp"],
                                                allow=allow(pair, d["ts"], -1, ud, uc, dx, cot), **KW)]
            keep, busy = [], -1
            for t in sorted(lo + sh):
                if t[0] > busy:
                    keep.append(t)
                    busy = t[1]
            res[grp][name] += keep
            print(f"  {pair} {name}: {len(keep)} trades", flush=True)
        del d, md
        gc.collect()
    for grp, title in (("main", "EURUSD GBPUSD GBPJPY USDJPY XAUUSD"), ("unseen", "NEVER-SEEN AUDUSD")):
        lab = f"NEWEST leg (leg swing {KW['leg']})" if KW.get("rng") == "leg" else "bigger swing (round 3)"
        print(f"\n### Brad day best version on forex, {lab}, {title}, real OANDA spreads\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for v in vers:
            print(P.row(v[0], [t[:4] for t in D.day_limit(res[grp][v[0]])], years), flush=True)


if __name__ == "__main__":
    main()
