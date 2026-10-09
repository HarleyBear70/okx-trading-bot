"""
JEFF15: the 15m test "done Jeff's way", asked for by Chrome Claude on issue #4 (Oct 9 2026, Jeff asked). Built on the
Smoke Detector structure engine (research/jeff_topdown.py). Crypto, longs AND shorts.

PLAN (written before any results)
  Direction  daily trend (Smoke Detector structure, last completed daily candle).
  Zone       the 4H range (4H strong level to 4H extreme). Longs only in the DISCOUNT, shorts only in the PREMIUM,
             and skip the middle: longs need price in the lowest 40% of the range, shorts the top 40%.
  Entry      a 15m market shift back in the daily direction (body close through the 15m strong level = BOS / reclaim
             at the level), filled at the next candle's open.
  Stop       the 15m strong level -/+ 0.15 ATR. Jeff's max stop 1.35%: farther than that = skip the trade.
  Target     at least 2% (Jeff's min TP) and at least 2R.
  One trade per coin at a time; equal mix of coins; costs per side; results in R (0.5% risk).
VERSIONS (each changes ONE thing from the base, so a failure points at the piece that fails)
  base         as above
  capstop      stop = whichever is closer: the structure stop or 1.35% (instead of skipping wide ones)
  trail        no fixed target: the stop follows the 15m strong level after each BOS, exit on a 15m shift against
  nomiddle     middle filter off (longs anywhere below the 50% line, shorts above)
  30m          entries on 30m candles instead of 15m
  hourly       bot checks once an hour (not every 5 min): a 15m signal is acted on at the next full hour's open
  Fees: Binance.US 0.05% a side (0.02% fee + slippage) main; also 0% and OKX 0.35%.
PASS RULES: 100+ trades, PF 1.3+, average +0.10R or better, PF 1.1+ in BOTH halves (2019-22 / 2023-now), worst
drawdown under 24R, never-seen coins PF 1.1+. Main coins BTC ETH SOL XRP BNB; never-seen ADA DOGE LINK AVAX LTC DOT.

  python3 research/jeff15.py
"""
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402
import m15  # noqa: E402

CUSH, MAXSTOP, MINTP, ZONE = 0.15, 0.0135, 0.02, 0.4
MAIN = ["BTC", "ETH", "SOL", "XRP", "BNB"]
UNSEEN = ["ADA", "DOGE", "LINK", "AVAX", "LTC", "DOT"]


def htf_range(b, span, tf_ms):
    """per entry bar: (trend, low, high) of the higher-timeframe range as of its last completed candle"""
    hb = J.resample(b, span)
    s = J.structure(hb)
    known = {}
    for i, x in enumerate(hb):
        st, mid = s["strong"][i], s["mid"][i]
        rng = None
        if st is not None and mid is not None:
            ext = 2 * mid - st
            rng = (min(st, ext), max(st, ext))
        known[x["ts"] + span] = (s["trend"][i], rng)
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


def run(b, tf_ms, ver, fee):
    s = J.structure(b)
    d1 = J.htf_view(b, J.D1, tf_ms)
    h4 = htf_range(b, J.H4, tf_ms)
    a = B.atr(b)
    t0 = B.ms(B.START)
    zone = 0.5 if ver == "nomiddle" else ZONE
    out = []  # (ts, side, R)
    pos, pend, pend_exit = None, None, False

    def close(px):
        sd = pos["sd"]
        out.append((pos["ts"], sd, (sd * (px - pos["entry"]) - fee * (pos["entry"] + px)) / pos["risk"]))

    for k, x in enumerate(b):
        if x["ts"] < t0:
            continue
        if pos and pend_exit:
            close(x["o"])
            pos, pend_exit = None, False
        if pend and not pos and (ver != "hourly" or x["ts"] % 3600000 == 0):
            sd, stop = pend
            pend = None
            px = x["o"]
            dist = (px - stop) * sd
            if ver == "capstop" and dist > MAXSTOP * px:
                stop, dist = px - sd * MAXSTOP * px, MAXSTOP * px
            if 0 < dist <= MAXSTOP * px * 1.0001:
                tgt = None if ver == "trail" else px + sd * max(MINTP * px, 2 * dist)
                pos = {"sd": sd, "entry": px, "stop": stop, "tgt": tgt, "risk": dist, "ts": x["ts"]}
        elif pend and not pos:
            pass  # hourly: wait for the next full hour
        else:
            pend = None
        if pos:
            sd = pos["sd"]
            if (x["l"] <= pos["stop"]) if sd == 1 else (x["h"] >= pos["stop"]):
                close(min(pos["stop"], x["o"]) if sd == 1 else max(pos["stop"], x["o"]))
                pos, pend_exit = None, False
            elif pos["tgt"] is not None and ((x["h"] >= pos["tgt"]) if sd == 1 else (x["l"] <= pos["tgt"])):
                close(max(pos["tgt"], x["o"]) if sd == 1 else min(pos["tgt"], x["o"]))
                pos = None
        if pos:
            sd = pos["sd"]
            if ver == "trail":
                if s["trend"][k] == -sd:
                    pend_exit = True
                elif s["strong"][k] is not None and a[k]:
                    t = s["strong"][k] - sd * CUSH * a[k]
                    pos["stop"] = max(pos["stop"], t) if sd == 1 else min(pos["stop"], t)
            continue
        if not (s["shift"][k] and a[k] and s["strong"][k] is not None):
            continue
        sd = s["trend"][k]
        trend, rng = h4[k]
        if d1[k][0] != sd or rng is None or rng[1] <= rng[0]:
            continue
        p = (x["c"] - rng[0]) / (rng[1] - rng[0])
        if (sd == 1 and p > zone) or (sd == -1 and p < 1 - zone):
            continue
        pend = (sd, s["strong"][k] - sd * CUSH * a[k])
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


def row(name, tr, years):
    tr.sort()
    cut = B.ms(B.CUT)
    f = stats([r for _, _, r in tr])
    if not f:
        return f"| {name} | 0 |"
    h1, h2 = stats([r for t, _, r in tr if t < cut]), stats([r for t, _, r in tr if t >= cut])
    lo, sh = stats([r for _, sd, r in tr if sd == 1]), stats([r for _, sd, r in tr if sd == -1])
    p = lambda s: "-" if not s else f"{s['pf']:.2f}"
    return (f"| {name} | {f['n']} | {f['n'] / years / 52:.1f} | {f['win']:.0f}% | {f['pf']:.2f} | {f['avg']:+.2f}R | "
            f"{f['dd']:.0f}R | {p(h1)} | {p(h2)} | {p(lo)} | {p(sh)} |")


def load(c, ver):
    b = [dict(x, sp=0.0) for x in m15.m15(c) if x["ts"] >= B.ms(B.START) - 60 * 86400000]
    if ver == "30m":
        b = J.resample(b, 1800000)
    return b


def main():
    import datetime as dt
    years = (dt.datetime.now(dt.timezone.utc) - B.START).days / 365.25
    hdr = ("| Version | Trades | /wk | Win % | PF | Avg | Worst DD | 2019-22 PF | 2023-now PF | Long PF | Short PF |\n"
           "|---|---|---|---|---|---|---|---|---|---|---|")
    vers = ("base", "capstop", "trail", "nomiddle", "30m", "hourly")
    fees = [("base", 0.0, "zero fees"), ("base", 0.0035, "OKX 0.35%"), ("trail", 0.0, "zero fees"),
            ("trail", 0.0035, "OKX 0.35%")]
    for title, coins in (("main: BTC ETH SOL XRP BNB", MAIN), ("never-seen: ADA DOGE LINK AVAX LTC DOT", UNSEEN)):
        res = {v: [] for v in vers}
        fres = {f"{v} at {lab}": [] for v, _, lab in fees}
        for c in coins:  # one coin in memory at a time (the Chromebook has ~2.7 GB)
            b = load(c, "base")
            for ver in vers:
                if ver != "30m":
                    res[ver] += run(b, 900000, ver, 0.0005)
            if coins is MAIN:
                for ver, fee, lab in fees:
                    fres[f"{ver} at {lab}"] += run(b, 900000, ver, fee)
            b = J.resample(b, 1800000)
            res["30m"] += run(b, 1800000, "30m", 0.0005)
            del b
            gc.collect()
            print(f"  ({c} done)", flush=True)
        print(f"\n### {title} (Binance.US 0.05% a side)\n\n{hdr}")
        for ver in vers:
            print(row(ver, res[ver], years))
        if coins is MAIN:
            print(f"\n### main, fee check\n\n{hdr}")
            for name, tr in fres.items():
                print(row(name, tr, years))
        sys.stdout.flush()

if __name__ == "__main__":
    main()
