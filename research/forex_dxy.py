"""
Job 2c: the bots on forex (EUR/USD, GBP/USD, USD/JPY) and the US Dollar Index (DXY) as a filter.

Forex: SP-12 v4, SP-12 v2 and Trend Rider, long only (like the bots), no leverage, 0.5% risk.
  - "crypto settings": bot.py's settings unchanged.
  - "ATR-scaled": SP-12's % stop / target limits (min_risk, max_risk, tp_min, tp_max) multiplied by
    (pair's median 4H ATR %) / (median 4H ATR % of BTC, ETH, XRP since Mar 2024, what v4 was tuned on).
    Trend Rider's stop and trail are already in ATR, so it has one version.
  Fee: 0.075% each side (Kraken Futures' general taker rate; FX perp fees not confirmed).
  No leverage means one trade can use at most the whole balance, so with forex's tight stops the
  0.5% risk is often not reached (the cash cap binds).

DXY filter: enter only when the dollar trend agrees, judged on the last completed daily close:
  long EUR/USD, GBP/USD, BTC, ETH, XRP: DXY below its daily 50 EMA (weak dollar)
  long USD/JPY: DXY above its daily 50 EMA (strong dollar)
  Exits are untouched. Crypto uses 0.1% fees and the long-history data from research/long_history.py.

Data:
  Forex: FXCM's public hourly bid candles (candledata.fxcorporate.com, 2012-now), built into 4H UTC
  candles; weekend candles dropped. (Dukascopy goes back to 2003 but downloads at about one file a
  minute from here, too slow for three pairs; it is still used for spot gold / silver, which FXCM lacks.)
  Yahoo Finance DX-Y.NYB daily for DXY.
Cached in research/.cache/.

Run:
  python research/forex_dxy.py        # writes research/FOREX_DXY.md
"""
import datetime as dt
import gzip
import json
import lzma
import os
import struct
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import long_history as lh  # noqa: E402

UTC = dt.timezone.utc
H4 = bot.H4_MS
FX = {"EURUSD": 1e5, "GBPUSD": 1e5, "USDJPY": 1e3}  # Dukascopy price scale
FX_FEE = 0.00075
WANT_WEAK_USD = {"EURUSD": True, "GBPUSD": True, "USDJPY": False, "BTC": True, "ETH": True, "XRP": True}
UA = {"User-Agent": "Mozilla/5.0"}


def d(y, m=1, day=1):
    return dt.datetime(y, m, day, tzinfo=UTC)


FX_HALVES = [("Full 2012-now", d(2012), None), ("1st half 2012-18", d(2012), d(2019)), ("2nd half 2019-now", d(2019), None)]
FX_ERAS = [("2012-14", d(2012), d(2015)), ("2015-19", d(2015), d(2020)), ("2020-22", d(2020), d(2023)),
           ("2023-now", d(2023), None)]
# eras for the long Dukascopy series (spot gold / silver)
LONG_ERAS = [("2003-07", d(2003), d(2008)), ("2008-09 crisis", d(2008), d(2010)), ("2010-14", d(2010), d(2015)),
             ("2015-19", d(2015), d(2020)), ("2020-22", d(2020), d(2023)), ("2023-now", d(2023), None)]
CR_HALVES = [("Full (start-now)", d(2013), None), ("1st half (start-2019)", d(2013), d(2020)),
             ("2nd half (2020-now)", d(2020), None)]


def get(url, tries=10):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(65 if e.code == 429 else 5 * (k + 1))
        except Exception:
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {url}")


# ───────── data ─────────
def to_4h(hours):
    """Hourly candles -> 4H UTC candles, weekend hours dropped."""
    bars = {}
    for x in sorted(hours, key=lambda x: x["ts"]):
        if dt.datetime.fromtimestamp(x["ts"] / 1000, UTC).weekday() >= 5:
            continue
        k = x["ts"] - x["ts"] % H4
        if k not in bars:
            bars[k] = {"ts": k, "o": x["o"], "h": x["h"], "l": x["l"], "c": x["c"], "v": x["v"], "confirm": True}
        else:
            b = bars[k]
            b["h"], b["l"], b["c"], b["v"] = max(b["h"], x["h"]), min(b["l"], x["l"]), x["c"], b["v"] + x["v"]
    now_ms = time.time() * 1000
    return [b for b in sorted(bars.values(), key=lambda b: b["ts"]) if b["ts"] + H4 <= now_ms]


def fxcm(pair):
    path = os.path.join(lh.CACHE, f"FXCM_{pair}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    print(f"downloading {pair} from FXCM ...", flush=True)
    now = dt.datetime.now(UTC)
    weeks = [(y, w) for y in range(2012, now.year + 1) for w in range(1, 54)]

    def week(yw):
        blob = get(f"https://candledata.fxcorporate.com/H1/{pair}/{yw[0]}/{yw[1]}.csv.gz")
        if not blob:
            return []
        rows = []
        for line in gzip.decompress(blob).decode("utf-8", "replace").splitlines()[1:]:
            x = line.split(",")
            if len(x) < 5:
                continue
            t = dt.datetime.strptime(x[0][:19], "%m/%d/%Y %H:%M:%S").replace(tzinfo=UTC)
            rows.append({"ts": int(t.timestamp() * 1000), "o": float(x[1]), "h": float(x[2]), "l": float(x[3]),
                         "c": float(x[4]), "v": 1.0})  # FXCM files have no volume; VWAP becomes a plain average
        return rows

    with ThreadPoolExecutor(8) as pool:
        hours = {x["ts"]: x for rows in pool.map(week, weeks) for x in rows}
    out = to_4h(hours.values())
    with open(path, "w") as f:
        json.dump(out, f)
    return out


def dukascopy(pair):
    path = os.path.join(lh.CACHE, f"FX_{pair}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    print(f"downloading {pair} from Dukascopy ...", flush=True)
    now = dt.datetime.now(UTC)
    months = [(y, m) for y in range(2003, now.year + 1) for m in range(1, 13) if (y, m) < (now.year, now.month)]
    mdir = os.path.join(lh.CACHE, f"FX_{pair}_months")
    os.makedirs(mdir, exist_ok=True)

    def month(ym):
        """One month of hourly candles; each month is cached so an interrupted download resumes."""
        y, m = ym
        mpath = os.path.join(mdir, f"{y}-{m:02d}.json")
        if os.path.exists(mpath):
            with open(mpath) as f:
                return json.load(f)
        blob = get(f"https://datafeed.dukascopy.com/datafeed/{pair}/{y}/{m - 1:02d}/BID_candles_hour_1.bi5")
        rows = []
        if blob:
            raw = lzma.decompress(blob)
            base = int(d(y, m).timestamp() * 1000)
            for i in range(len(raw) // 24):
                t, o, c, lo, hi, v = struct.unpack(">iiiiif", raw[i * 24:i * 24 + 24])
                if v > 0:
                    sc = FX[pair]
                    rows.append({"ts": base + t * 1000, "o": o / sc, "h": hi / sc, "l": lo / sc, "c": c / sc, "v": v})
        with open(mpath, "w") as f:
            json.dump(rows, f)
        return rows

    # each request is slow (~15 s here) and parallel requests get throttled, so one at a time
    hours = [x for ym in months for x in month(ym)]
    out = to_4h(hours)
    with open(path, "w") as f:
        json.dump(out, f)
    return out


def fx_daily(bars):
    days = {}
    for b in bars:
        k = b["ts"] - b["ts"] % 86400000
        x = days.setdefault(k, {"ts": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": 0.0, "confirm": True})
        x["h"], x["l"], x["c"], x["v"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"], x["v"] + b["v"]
    return sorted(days.values(), key=lambda x: x["ts"])


def dxy():
    path = os.path.join(lh.CACHE, "DXY.json")
    if not os.path.exists(path):
        print("downloading DXY from Yahoo ...", flush=True)
        r = json.loads(get("https://query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB"
                           "?period1=0&period2=9999999999&interval=1d"))["chart"]["result"][0]
        rows = [(bot.day_of(t * 1000), c) for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"])
                if c is not None]
        with open(path, "w") as f:
            json.dump(rows, f)
    with open(path) as f:
        rows = json.load(f)
    days = [r[0] for r in rows]
    e50 = bot.ema([r[1] for r in rows], 50)
    weak = {day: (e is not None and c < e) for (day, c), e in zip(rows, e50)}
    return days, weak


def last_completed(sorted_days, day):
    """Index in sorted_days of the last day strictly before `day` (binary search)."""
    lo, hi = 0, len(sorted_days)
    while lo < hi:
        mid = (lo + hi) // 2
        if sorted_days[mid] < day:
            lo = mid + 1
        else:
            hi = mid
    return lo - 1


def gap_safe_daily_lookup(bars, daily):
    """Like bot.daily_lookup, but uses the last completed day even across weekends (forex)."""
    days = [bot.day_of(x["ts"]) for x in daily]
    out = []
    for b in bars:
        k = last_completed(days, bot.day_of(b["ts"]))
        out.append(k if k >= 0 else None)
    return out


def apply_dxy(bars, a, coin, dxy_days, weak):
    sig = list(a["signal"])
    for k, b in enumerate(bars):
        if sig[k]:
            j = last_completed(dxy_days, bot.day_of(b["ts"]))
            w = weak.get(dxy_days[j]) if j >= 0 else None
            sig[k] = w is not None and w == WANT_WEAK_USD[coin]
    return {**a, "signal": sig}


def atr_pct(bars, since_ms=0):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    a = bot.atr(h, l, c, 14)
    return median(a[i] / c[i] for i in range(len(bars)) if a[i] and bars[i]["ts"] >= since_ms)


def scaled(cfg, s):
    return {**cfg, **{k: cfg[k] * s for k in ("min_risk", "max_risk", "tp_min", "tp_max")}}


# ───────── report ─────────
HEAD = ("| Version | Market | Period | Trades | Win % | Return | Max DD | PF | B&H return |\n"
        "|---|---|---|---|---|---|---|---|---|")


def row(v, mkt, p, r):
    if r is None:
        return None
    pf = "inf" if r["pf"] == float("inf") else f"{r['pf']:.2f}"
    flag = " **>10%**" if r["dd"] < -10 else ""
    return (f"| {v} | {mkt} | {p} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}%{flag} | "
            f"{pf} | {r['bh']:+.0f}% |")


def run_periods(strat, bars, a, periods):
    now = dt.datetime.now(UTC)
    out = {}
    for p, t0, t1 in periods:
        t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC))
        if t0 >= (t1 or now):
            continue
        out[p] = lh.simulate(strat, bars, a, t0, t1 or now)
    return out


def main():
    dxy_days, weak = dxy()
    crypto_atr = median(atr_pct(lh.load(c)[0], lh.ms(d(2024, 3))) for c in ("BTC", "ETH", "XRP"))
    lines = ["# Forex and DXY filter test (job 2c)", "",
             f"Run {dt.datetime.now(UTC):%Y-%m-%d}. bot.py as it is now ({bot.RISK_PCT * 100:g}% risk), long only, "
             "no leverage, bot.py's own paper-mode functions bar by bar, fresh $1,000 per period. "
             "Script: research/forex_dxy.py.", "",
             f"Forex fee {FX_FEE * 100:g}% each side; crypto 0.1%. Median 4H ATR of BTC/ETH/XRP since Mar 2024: "
             f"{crypto_atr * 100:.2f}%.", ""]
    fx_rows, fx_era_rows, cr_rows, summary = [], [], [], []
    results = {}  # (version, market, period) -> r

    # forex
    orig_fee, orig_be, orig_lookup = bot.FEE, bot.BE_BUFFER, bot.daily_lookup
    bot.FEE, bot.BE_BUFFER, bot.daily_lookup = FX_FEE, 2 * FX_FEE, gap_safe_daily_lookup
    try:
        for pair in FX:
            bars = fxcm(pair)
            daily = fx_daily(bars)
            s = atr_pct(bars) / crypto_atr
            lines.append(f"- {pair}: {len(bars)} 4H candles from {bot.ts_iso(bars[0]['ts'])[:10]}, median 4H ATR "
                         f"{atr_pct(bars) * 100:.3f}%, scale {s:.3f} (v4 min stop {bot.SP_SETTINGS['v4']['min_risk'] * s:.2f}%, "
                         f"max {bot.SP_SETTINGS['v4']['max_risk'] * s:.2f}%)")
            versions = [
                ("v4", "SP-12 v4 crypto settings", bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v4"])),
                ("v4", "SP-12 v4 ATR-scaled", bot.analyse_sp(bars, daily, scaled(bot.SP_SETTINGS["v4"], s))),
                ("v2", "SP-12 v2 crypto settings", bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v2"])),
                ("v2", "SP-12 v2 ATR-scaled", bot.analyse_sp(bars, daily, scaled(bot.SP_SETTINGS["v2"], s))),
                ("tr", "Trend Rider", bot.analyse_tr(bars, daily, 5)),
            ]
            for strat, name, a in versions:
                for tag, aa in (("", a), (" + DXY", apply_dxy(bars, a, pair, dxy_days, weak))):
                    for p, r in run_periods(strat, bars, aa, FX_HALVES).items():
                        results[(name + tag, pair, p)] = r
                        fx_rows.append(row(name + tag, pair, p, r))
                    for p, r in run_periods(strat, bars, aa, FX_ERAS).items():
                        results[(name + tag, pair, p)] = r
                        fx_era_rows.append(row(name + tag, pair, p, r))
            print(f"done {pair}", flush=True)
    finally:
        bot.FEE, bot.BE_BUFFER, bot.daily_lookup = orig_fee, orig_be, orig_lookup

    # crypto with / without DXY
    for coin in ("BTC", "ETH", "XRP"):
        bars, daily = lh.load(coin)
        for strat, name, fn in (("v4", "SP-12 v4", lambda: bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v4"])),
                                ("v2", "SP-12 v2", lambda: bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v2"])),
                                ("tr", "Trend Rider", lambda: bot.analyse_tr(bars, daily, 5))):
            a = fn()
            for tag, aa in (("", a), (" + DXY", apply_dxy(bars, a, coin, dxy_days, weak))):
                for p, r in run_periods(strat, bars, aa, CR_HALVES).items():
                    results[(name + tag, coin, p)] = r
                    cr_rows.append(row(name + tag, coin, p, r))
        print(f"done {coin}", flush=True)

    # does DXY help? per version / market: compare PF and DD in both halves
    def verdict(base, mkts, halves):
        helped, rows = 0, []
        for m in mkts:
            pr = []
            for h in halves:
                r0, r1 = results.get((base, m, h)), results.get((base + " + DXY", m, h))
                if not r0 or not r1 or not r0["trades"] or not r1["trades"]:
                    pr.append(None)
                    continue
                pr.append(r1["pf"] > r0["pf"] and r1["ret"] >= r0["ret"] - 0.5)
            ok = all(x for x in pr if x is not None) and any(x is not None for x in pr)
            helped += ok
            rows.append(f"{m} {'yes' if ok else 'no'}")
        return helped, rows

    lines += ["", "## DXY filter verdict", "",
              "Helps = higher PF and no lower return (within 0.5 points) in BOTH halves.", ""]
    for base in ("SP-12 v4 crypto settings", "SP-12 v4 ATR-scaled", "SP-12 v2 crypto settings", "SP-12 v2 ATR-scaled",
                 "Trend Rider"):
        n, rs = verdict(base, list(FX), [h[0] for h in FX_HALVES[1:]])
        lines.append(f"- Forex, {base}: helps on {n} of 3 pairs ({', '.join(rs)})")
        summary.append((f"Forex, {base}", n, 3))
    for base in ("SP-12 v4", "SP-12 v2", "Trend Rider"):
        n, rs = verdict(base, ["BTC", "ETH", "XRP"], [h[0] for h in CR_HALVES[1:]])
        lines.append(f"- Crypto, {base}: helps on {n} of 3 coins ({', '.join(rs)})")
        summary.append((f"Crypto, {base}", n, 3))

    lines += ["", "## Forex: full period and halves", "", HEAD] + [x for x in fx_rows if x]
    lines += ["", "## Forex: by era", "", HEAD] + [x for x in fx_era_rows if x]
    lines += ["", "## Crypto with and without the DXY filter", "", HEAD] + [x for x in cr_rows if x]
    with open(os.path.join(HERE, "FOREX_DXY.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines[:40]))


if __name__ == "__main__":
    main()
