"""F28: Jeff's Triple Supertrend (G1-G3) and BTC Trend-Momentum (H1-H2) (research/F28_PLAN.md). Research only.

  python research/f28_st_btc.py <G1|G2|G3> [u]     triple supertrend, 5 coins (u = never-seen coins)
  python research/f28_st_btc.py <H1|H2|HOLD|BH> <BTC|ETH>   all-in single coin
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import f24_jeff2 as f24  # noqa: E402
import f25_tas as f25  # noqa: E402

FEE = 0.0035
rules = {}


def supertrend(h, l, c, factor, period):
    a = bot.atr(h, l, c, period)
    n = len(c)
    st, ub, lb = [None] * n, [None] * n, [None] * n
    d = 1
    for i in range(n):
        if a[i] is None:
            continue
        src = (h[i] + l[i]) / 2
        up, lo = src + factor * a[i], src - factor * a[i]
        if lb[i - 1] is not None:
            lo = lo if lo > lb[i - 1] or c[i - 1] < lb[i - 1] else lb[i - 1]
            up = up if up < ub[i - 1] or c[i - 1] > ub[i - 1] else ub[i - 1]
        if st[i - 1] is None:
            d = 1
        elif st[i - 1] == ub[i - 1]:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lo else -1
        ub[i], lb[i] = up, lo
        st[i] = lo if d == -1 else up
    return st


def adx(h, l, c, n=14):
    dp, dm = f25.dmi(h, l, c, n)
    dx = [None if None in (p, m) or p + m == 0 else 100 * abs(p - m) / (p + m) for p, m in zip(dp, dm)]
    first = next(i for i, x in enumerate(dx) if x is not None)
    return dp, dm, [None] * first + bot.rma(dx[first:], n)


def triple(fast_exit):
    def entries(coin, bars, _daily):
        h, l, c = ([x[f] for x in bars] for f in "hlc")
        s1, s2, s3 = supertrend(h, l, c, 1.5, 10), supertrend(h, l, c, 2.5, 14), supertrend(h, l, c, 3.0, 20)
        dp, dm, ax = adx(h, l, c)
        a = bot.atr(h, l, c, 14)
        out = [None] * len(bars)
        for k in range(len(bars)):
            if None in (s1[k], s2[k], s3[k], ax[k], dp[k], dm[k], a[k]):
                continue
            if c[k] > s1[k] and c[k] > s2[k] and c[k] > s3[k] and ax[k] > 25 and dp[k] > dm[k]:
                out[k] = {"stop": c[k] - max(c[k] - s3[k], 0.5 * a[k]), "target": None, "max_bars": None}
        rules[id(bars)] = (s1, s3)
        return out

    def manage(p, bars, k):
        s1, s3 = rules[id(bars)]
        if fast_exit and bars[k]["c"] < s1[k]:
            return "exit"
        return s3[k] if s3[k] is not None and s3[k] < bars[k]["c"] else None
    return entries, manage


def btc_tm(coin, bars, _daily):
    h, l, c, v = ([x[f] for x in bars] for f in "hlcv")
    n = len(bars)
    em, r, a = bot.ema(c, 200), bot.rsi(c, 14), bot.atr(h, l, c, 14)
    am = bot.sma(a, 20)
    mfv = [((c[i] - l[i]) - (h[i] - c[i])) / (h[i] - l[i]) * v[i] if h[i] != l[i] else 0.0 for i in range(n)]
    cmf = [None] * n
    for i in range(19, n):
        vs = sum(v[i - 19:i + 1])
        cmf[i] = sum(mfv[i - 19:i + 1]) / vs if vs else 0.0
    st = [None] * n
    for i in range(n):
        w = r[i - 13:i + 1] if i >= 13 else []
        if len(w) == 14 and None not in w:
            hi, lo = max(w), min(w)
            st[i] = 100 * (r[i] - lo) / (hi - lo) if hi != lo else 0.0
    kl = bot.sma(st, 3)
    out, ex = [None] * n, [False] * n
    for i in range(1, n):
        if None in (em[i], kl[i], kl[i - 1], cmf[i], am[i]):
            continue
        vol_ok = a[i] > am[i]
        if cmf[i] > 0 and kl[i] > 20 >= kl[i - 1] and vol_ok and c[i] > em[i]:
            out[i] = {"stop": c[i] * 1e-6, "target": None, "max_bars": None}
        ex[i] = cmf[i] < 0 and kl[i] < 80 <= kl[i - 1] and vol_ok
    rules[id(bars)] = ex
    return out


def btc_manage(p, bars, k):
    return "exit" if rules[id(bars)][k] and k > p["k"] else None


def stats(r):
    _, _, ratio = e.ret_dd(r["curve"])
    return {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
            "win": round(r["win"]), "ret_dd": round(ratio, 1)}


def main():
    v = sys.argv[1]
    out = {"variant": v}
    if v.startswith("G"):
        unseen = len(sys.argv) > 2 and sys.argv[2] == "u"
        cs = [c for c in e.UNSEEN if c not in f24.DESIGN] if unseen else f24.DESIGN
        data = {c: (b if v == "G2" else d, d) for c, (b, d) in e.load(cs).items() if d}
        cs = list(data)
        ent, man = triple(v != "G3")
        for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
            r = e.trade_sim(cs, data, ent, t0, t1, risk=0.004, max_open=5, fee=FEE, manage=man)
            out[lab] = stats(r)
            if lab == "full" and not unseen:
                out["corr_dc"] = round(e.corr(e.monthly(r["curve"]), f24.run("DC", False)["_monthly"]), 2)
    else:
        coin = sys.argv[2]
        b4, d = e.load([coin])[coin]
        bars = b4 if v == "H2" else d
        data = {coin: (bars, d)}
        out["coin"] = coin
        for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
            if v in ("H1", "H2"):
                r = e.trade_sim([coin], data, btc_tm, t0, t1, risk=1.0, max_open=1, fee=FEE, manage=btc_manage)
            elif v == "HOLD":
                r = e.bot_sim("hold", [coin], {coin: (d, d)}, lambda b, _d: bot.analyse_hold(b), t0, t1,
                              settings={"risk": 1.0, "half_at_2r": False})
            else:  # BH: buy at the first close, hold to the end
                r = e.trade_sim([coin], {coin: (d, d)},
                                lambda c_, b, _d: [{"stop": x["c"] * 1e-6, "target": None, "max_bars": None} for x in b], t0, t1, risk=1.0, max_open=1, fee=FEE)
            out[lab] = stats(r)
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
