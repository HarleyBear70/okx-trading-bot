"""
F41: a "learning manager" (Jeff, Oct 7 2026: "a learning bot ... learn from bad trades ... build me something").
Learning here means: every quarter, look back at each strategy's last 365 days of results (only the past) and move
money toward the ones that are working and away from the ones that aren't. Strategies keep their own fixed, tested
rules; the manager only decides how much each one trades. Rules fixed before running.

Members (each simulated on its own $1,000 at 0.5% risk; daily equity curves):
  crypto (long only, Binance.US 0.02%): Turtle 55/20, Donchian 20/10, Momentum 90d, RSI(2) < 5    (F38, F39)
  forex EUR/USD + GBP/USD (both ways, ~1 pip): RSI(2) 5/95, Turtle 55/20, Momentum 200d, DXY+4H BOS (F38-F40)
Managers (rebalance every 91 days, using the trailing 365 days of each member's daily returns):
  EQ    equal weight, never changes (no learning; the benchmark)
  L1    weight = trailing return / trailing worst drop, negatives get 0 ("stop funding what's losing")
  L2    all money on the single best member by trailing return/drop (most aggressive learner)
  L3    like L1 but every member keeps a 10% floor so a sleeping strategy can come back
Weights sum to 1 (the manager splits one pot). Research only.
"""
import datetime as dt
import engine as e
import forex_dxy as fx
import f38_cross as f38
import f39_both as f39
import f40_sessions as f40

DAY = 86400000


def daily_returns(curve):
    by = {}
    for ts, v in curve:
        by[ts // DAY] = v
    days = sorted(by)
    return {d: by[d] / by[p] - 1 for p, d in zip(days, days[1:]) if by[p] > 0}


def crypto_members(t0):
    data = {c: (d, d) for c, (_, d) in e.load(f38.CRYPTO).items()}
    out = {}
    for name, mk in (("Turtle 55/20", lambda: f38.donchian(55, 20, False)), ("Donchian 20/10", lambda: f38.donchian(20, 10, False)),
                     ("Momentum 90d", lambda: f38.momentum(90, False))):
        ent, man = mk()
        out[name] = e.trade_sim(f38.CRYPTO, data, ent, t0, None, risk=0.005, max_open=5, fee=0.0002, manage=man)["curve"]

    def ent(coin, bars, _d):
        return [None if s is None else {"stop": s[1]} for s in f39.rsi2_signals(bars, 5, False)]

    def man(p, bars, k):
        c = [b["c"] for b in bars[max(0, k - 4):k + 1]]
        return "exit" if len(c) == 5 and bars[k]["c"] > sum(c) / 5 else None
    out["RSI(2) < 5"] = e.trade_sim(f38.CRYPTO, data, ent, t0, None, risk=0.005, max_open=5, fee=0.0002, manage=man)["curve"]
    return out


def forex_members(t0):
    h4 = {p: fx.fxcm(p) for p in f39.FOREX}
    daily = {p: fx.fx_daily(h4[p]) for p in f39.FOREX}
    out = {"RSI(2) 5/95": f39.fx_sim({p: f39.rsi2_signals(daily[p], 5, True) for p in f39.FOREX}, daily, t0, None)["curve"]}
    for name, mk in (("Turtle 55/20", lambda: f38.donchian(55, 20, True)), ("Momentum 200d", lambda: f38.momentum(200, True))):
        ent, man = mk()
        d2 = {p: (daily[p], daily[p]) for p in f39.FOREX}
        out[name] = e.trade_sim(f39.FOREX, d2, ent, t0, None, risk=0.005, max_open=2, fee=0.0001, manage=man)["curve"]
    dd, weak = fx.dxy()
    out["DXY + 4H BOS"] = f39.fx_sim({p: f40.s3_signals(h4[p], dd, weak) for p in f39.FOREX}, h4, t0, None)["curve"]
    return out


def score(rets):
    v, peak, dd = 1.0, 1.0, 0.0
    for r in rets:
        v *= 1 + r
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
    return (v - 1) / max(abs(dd), 0.02)


def manage(members, start_day, mode):
    rets = {n: daily_returns(c) for n, c in members.items()}
    days = sorted(set().union(*rets.values()))
    days = [d for d in days if d >= start_day]
    names = list(members)
    w = {n: 1 / len(names) for n in names}
    v, peak, dd, curve, last, hist = 1000.0, 1000.0, 0.0, [], None, []
    for d in days:
        if mode != "EQ" and (last is None or d - last >= 91) and d - start_day >= 365:
            look = {n: [rets[n][x] for x in range(d - 365, d) if x in rets[n]] for n in names}
            sc = {n: score(look[n]) for n in names}
            if mode == "L2":
                best = max(sc, key=sc.get)
                w = {n: (1.0 if n == best else 0.0) for n in names}
            else:
                raw = {n: max(sc[n], 0.0) for n in names}
                if mode == "L3":
                    raw = {n: max(raw[n], 0.0) for n in names}
                tot = sum(raw.values())
                w = {n: (raw[n] / tot if tot else 1 / len(names)) for n in names}
                if mode == "L3":
                    w = {n: 0.1 + 0.6 * w[n] for n in names}
                    s = sum(w.values())
                    w = {n: w[n] / s for n in names}
            last = d
            hist.append((d, {n: round(w[n], 2) for n in names}))
        v *= 1 + sum(w[n] * rets[n].get(d, 0.0) for n in names)
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
        curve.append((d, v))
    return curve, dd * 100, hist


def period_ret(curve, a, b):
    xs = [v for d, v in curve if a <= d < b]
    return (xs[-1] / xs[0] - 1) * 100 if len(xs) > 1 else 0.0


def main():
    for label, members, t0, cut in (("CRYPTO", crypto_members(e.START), e.START, e.CUT),
                                    ("FOREX EUR/USD + GBP/USD", forex_members(f39.FX0), f39.FX0, f39.FXCUT)):
        s0, c0 = e.ms(t0) // DAY, e.ms(cut) // DAY
        print(f"\n## {label}\n\n| Manager | Whole period | Worst drop | 1st half | 2nd half |\n|---|---|---|---|---|")
        for n, c in members.items():
            cv = [(ts // DAY, v) for ts, v in c]
            peak, dd = 1000.0, 0.0
            for _, v in cv:
                peak, dd = max(peak, v), min(dd, v / peak - 1)
            print(f"| member: {n} | {(cv[-1][1] / cv[0][1] - 1) * 100:+.0f}% | {dd * 100:.1f}% | "
                  f"{period_ret(cv, s0, c0):+.0f}% | {period_ret(cv, c0, 1 << 40):+.0f}% |")
        for mode, name in (("EQ", "EQ equal weight (no learning)"), ("L1", "L1 learner: fund what works"),
                           ("L2", "L2 learner: all-in on the best"), ("L3", "L3 learner: fund what works, 10% floor")):
            curve, dd, hist = manage(members, s0, mode)
            print(f"| **{name}** | {(curve[-1][1] / curve[0][1] - 1) * 100:+.0f}% | {dd:.1f}% | "
                  f"{period_ret(curve, s0, c0):+.0f}% | {period_ret(curve, c0, 1 << 40):+.0f}% |", flush=True)
            if mode == "L1" and hist:
                print(f"|  (L1's latest weights: {hist[-1][1]}) | | | | |")


if __name__ == "__main__":
    main()
