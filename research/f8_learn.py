"""
F8: learning without self-harm (research/F8_PLAN.md). Research only, bot.py is not changed.

  python research/f8_learn.py L1 <tr|dc|nnfx> <0|5|8>     drawdown brake (0 = no brake, the comparison)
  python research/f8_learn.py L2 <0|30|50>                AI filter skipping the bottom N% (0 = unfiltered)
"""
import datetime as dt
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035
bot.FEE, bot.BE_BUFFER = FEE, 2 * FEE


def report(sim, periods):
    out = {}
    for lab, t0, t1 in periods:
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    return out


# ───────── L1: drawdown brake ─────────
def l1(which, x):
    if x:
        orig = bot.risk_pct

        def risk_pct(b, bs):
            base = orig(b, bs)
            bs["pk"] = max(bs.get("pk", bs["equity"]), bs["equity"])
            return base * 0.5 if bs["equity"] < bs["pk"] * (1 - x / 100) else base
        bot.risk_pct = risk_pct
    bid = {"tr": "tr-okx", "dc": "dc-okx", "nnfx": "nnfx-okx"}[which]
    b = next(b for b in bot.BOTS if b["id"] == bid)
    cs = [c.split("-")[0] for c in b["coins"]]
    st = {k: b[k] for k in ("risk", "half_at_2r", "max_open") if k in b}
    if which == "tr":
        d = e.load(cs)
        return lambda t0, t1: e.bot_sim("tr", cs, d, lambda bb, dd: bot.analyse_tr(bb, dd, 5), t0, t1,
                                        extra=lambda x_: {"hi": x_["c"]}, settings=st)
    d = {c: (dd, dd) for c, (_, dd) in e.load(cs).items()}
    an = bot.analyse_donchian if which == "dc" else bot.analyse_nnfx
    return lambda t0, t1: e.bot_sim(b["strat"], cs, d, lambda bb, dd: an(bb), t0, t1, settings=st)


# ───────── L2: walk-forward AI filter on Trend Rider's entries ─────────
def indicator_cache(bars, daily, btc_daily):
    """Every indicator once per coin; value k only uses candles up to k (no look-ahead)."""
    h, l, c, v = ([x[f] for x in bars] for f in "hlcv")
    dcl = [d["c"] for d in daily]
    bcl = [d["c"] for d in btc_daily]
    return {"c": c, "v": v, "atr": bot.atr(h, l, c, 14), "e50": bot.ema(c, 50), "rsi": bot.rsi(c, 14),
            "dc": dcl, "de": bot.ema(dcl, 50), "dk": {bot.day_of(d["ts"]): j for j, d in enumerate(daily)},
            "bc": bcl, "bs": bot.sma(bcl, 200), "bk": {bot.day_of(d["ts"]): j for j, d in enumerate(btc_daily)}}


def features(cache, bars, k, info):
    c, v = cache["c"], cache["v"]
    a, e50, r = cache["atr"][k], cache["e50"][k], cache["rsi"][k]
    va = sum(v[k - 20:k]) / 20 if k >= 20 else None
    day = bot.day_of(bars[k]["ts"]) - 1  # last completed day
    j, jb = cache["dk"].get(day), cache["bk"].get(day)
    de = cache["de"][j] if j is not None else None
    bs = cache["bs"][jb] if jb is not None else None
    vals = [info["raw_risk"], a / c[k] * 100 if a else None, (c[k] / e50 - 1) * 100 if e50 else None, r,
            (c[k] / c[k - 20] - 1) * 100 if k >= 20 else None, v[k] / va if va else None,
            (cache["dc"][j] / de - 1) * 100 if de else None, (cache["bc"][jb] / bs - 1) * 100 if bs else None]
    return None if None in vals else vals


def fit(X, y, lam=1.0, iters=400, lr=0.1):
    n, m = len(X), len(X[0])
    mu = [sum(r[j] for r in X) / n for j in range(m)]
    sd = [max(1e-9, math.sqrt(sum((r[j] - mu[j]) ** 2 for r in X) / n)) for j in range(m)]
    Z = [[(r[j] - mu[j]) / sd[j] for j in range(m)] for r in X]
    w, b0 = [0.0] * m, 0.0
    for _ in range(iters):
        gw, gb = [lam * wj / n for wj in w], 0.0
        for z, t in zip(Z, y):
            p = 1 / (1 + math.exp(-(b0 + sum(wj * zj for wj, zj in zip(w, z)))))
            for j in range(m):
                gw[j] += (p - t) * z[j] / n
            gb += (p - t) / n
        w = [wj - lr * g for wj, g in zip(w, gw)]
        b0 -= lr * gb
    return lambda r: 1 / (1 + math.exp(-(b0 + sum(wj * (r[j] - mu[j]) / sd[j] for j, wj in enumerate(w)))))


def l2(skip_pct):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
    data = e.load(cs)
    btc_daily = e.load(["BTC"])["BTC"][1]
    atrs, feats = {}, {}

    def base_entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        cache = indicator_cache(bars, daily, btc_daily) if (coin, "done") not in feats else None
        out = [None] * len(bars)
        for i, s in enumerate(a["signal"]):
            if s:
                out[i] = {"stop": a["info"][i]["sl"], "target": None, "max_bars": None}
                if cache is not None:
                    feats[(coin, bars[i]["ts"])] = features(cache, bars, i, a["info"][i])
        feats[(coin, "done")] = True
        atrs[id(bars)] = a["atr"]
        return out

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    # pass 1: every entry, unfiltered, to learn from (each trade's own outcome)
    full = e.trade_sim(cs, data, base_entries, e.START, None, risk=0.004, max_open=3, fee=FEE, manage=manage)
    taken = [(t["coin"], t["entry_ts"], t["pnl"] > 0) for t in full["list"]]
    exit_of = {}
    for t in full["list"]:  # exit time is not stored: count a trade as known only 180 days after entry (no leak)
        exit_of[(t["coin"], t["entry_ts"])] = t["entry_ts"] + 180 * 86400000
    allow = {}
    if skip_pct:
        for year in range(2020, dt.datetime.now(dt.timezone.utc).year + 1):
            y0 = e.ms(dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
            train = [(feats[(c, ts)], int(win)) for c, ts, win in taken
                     if exit_of[(c, ts)] < y0 and feats.get((c, ts)) is not None]
            model = fit([f for f, _ in train], [t for _, t in train])
            scores = sorted(model(f) for f, _ in train)
            cut = scores[int(len(scores) * skip_pct / 100)]
            y1 = e.ms(dt.datetime(year + 1, 1, 1, tzinfo=dt.timezone.utc))
            for (c, ts), f in feats.items():
                if ts != "done" and y0 <= ts < y1:
                    allow[(c, ts)] = f is not None and model(f) >= cut

    def entries(coin, bars, daily):
        out = base_entries(coin, bars, daily)
        if skip_pct:
            out = [o if o is None or allow.get((coin, bars[i]["ts"]), True) else None for i, o in enumerate(out)]
        return out

    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def main():
    if sys.argv[1] == "L1":
        sim = l1(sys.argv[2], int(sys.argv[3]))
        out = {"test": "L1", "bot": sys.argv[2], "brake": int(sys.argv[3]),
               **report(sim, [("full", e.START, None)] + list(e.HALVES))}
    else:
        sim = l2(int(sys.argv[2]))
        y20, y22 = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc), e.CUT
        out = {"test": "L2", "skip": int(sys.argv[2]),
               **report(sim, [("2020-now", y20, None), ("2020-21", y20, y22), ("2022-now", y22, None)])}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
