"""
Repair test for SP-12 v2 and Trend Rider gold. The variants and pass rules were fixed in
research/REPAIR_PLAN.md (committed before this test was run); this script only applies them.

Engine: research/long_history.py (bot.py as it is now, 0.5% risk, 0.1% fee each side, one coin at a
time, fresh $1,000 per market period). The gold bot's never-seen markets are four FX pairs from FXCM via
research/forex_dxy.py, at 0.01% cost each side (see the amendment in REPAIR_PLAN.md).

Run:
  python research/repair_test.py        # writes research/REPAIR.md
"""
import datetime as dt
import inspect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import forex_dxy as fx  # noqa: E402
import long_history as lh  # noqa: E402

UTC = dt.timezone.utc
SPLIT = dt.datetime(2022, 1, 1, tzinfo=UTC)
V2_COINS = ["ETH", "SOL", "XAUT"]
V2_UNSEEN = ["LTC", "DOGE", "XLM", "ADA", "BNB", "LINK", "BCH", "AVAX", "SUI", "LUNA", "FTT"]
GOLD_UNSEEN = ["AUDUSD", "NZDUSD", "USDCAD", "USDCHF"]
FX_COST = 0.0001


def patched(fn, old, new):
    src = inspect.getsource(fn)
    assert old in src, f"{fn.__name__} in bot.py changed; update this test"
    ns = {}
    exec(src.replace(old, new), vars(bot), ns)
    return ns[fn.__name__]


V2 = bot.SP_SETTINGS["v2"]
V2_A = {**V2, "filters": True}
V2_C = {**V2_A, "rr": 3.0}
SP_NEED_C1 = patched(bot.analyse_sp, "score >= 2 and raw_risk", "score >= 2 and c1 and raw_risk")
TR_EMA100 = patched(bot.analyse_tr, "de = ema(dc, 50)", "de = ema(dc, 100)")
MANAGE_4ATR = patched(bot.manage_on_close, 'pos["hi"] - 3 * a["atr"][i]', 'pos["hi"] - 4 * a["atr"][i]')

# name -> (strategy used for exits in the simulator, analyse(bars, daily), manage_on_close override)
V2_VERSIONS = {
    "v2 now": ("v2", lambda b, d: bot.analyse_sp(b, d, V2), None),
    "v2 A: v4 trend filter": ("v2", lambda b, d: bot.analyse_sp(b, d, V2_A), None),
    "v2 B: A + daily uptrend": ("v2", lambda b, d: SP_NEED_C1(b, d, V2_A), None),
    # v4 exits: SAR trail after +1R and the 120-candle limit come from running it as strategy "v4"
    "v2 C: A + v4 exits": ("v4", lambda b, d: bot.analyse_sp(b, d, V2_C), None),
}
GOLD_VERSIONS = {
    "gold now (pivot 3)": ("tr", lambda b, d: bot.analyse_tr(b, d, 3), None),
    "gold A: pivot 5": ("tr", lambda b, d: bot.analyse_tr(b, d, 5), None),
    "gold B: daily EMA100": ("tr", lambda b, d: TR_EMA100(b, d, 3), None),
    "gold C: 4 ATR trail": ("tr", lambda b, d: bot.analyse_tr(b, d, 3), MANAGE_4ATR),
}


def load(market):
    """(bars, daily, daily_lookup to use, fee each side)."""
    if market in GOLD_UNSEEN:
        bars = fx.fxcm(market)
        return bars, fx.fx_daily(bars), fx.gap_safe_daily_lookup, FX_COST
    bars, daily = lh.load(market)
    return bars, daily, bot.daily_lookup, bot.FEE


def run(version, market, periods):
    strat, analyse, manage = version
    bars, daily, lookup, fee = load(market)
    orig_lookup, orig_manage, orig_fee, orig_be = bot.daily_lookup, bot.manage_on_close, bot.FEE, bot.BE_BUFFER
    bot.daily_lookup, bot.FEE, bot.BE_BUFFER = lookup, fee, 2 * fee
    if manage:
        bot.manage_on_close = manage
    try:
        a = analyse(bars, daily)
        out = {}
        now = dt.datetime.now(UTC)
        for p, t0, t1 in periods:
            t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC))
            if t0 >= (t1 or now):
                continue
            r = lh.simulate(strat, bars, a, t0, t1 or now)
            if r:
                out[p] = (t0, r)
        return out
    finally:
        bot.daily_lookup, bot.manage_on_close, bot.FEE, bot.BE_BUFFER = orig_lookup, orig_manage, orig_fee, orig_be


def pool(rs):
    rs = [r for r in rs if r]
    won, lost = sum(r["won"] for r in rs), sum(r["lost"] for r in rs)
    return {"pnl": sum(r["pnl"] for r in rs), "pf": won / lost if lost else float("inf"),
            "trades": sum(r["trades"] for r in rs), "worst_dd": min((r["dd"] for r in rs), default=0.0)}


def evaluate(versions, traded, unseen):
    """traded: [(market, periods)], unseen: [(market, periods)]. Returns {version: summary}."""
    res = {}
    for name, v in versions.items():
        h1, h2, un, all_dd = [], [], [], []
        for m, periods in traded:
            for p, (t0, r) in run(v, m, periods).items():
                (h1 if t0 < SPLIT else h2).append(r)
                all_dd.append((m, p, r["dd"]))
        for m, periods in unseen:
            for p, (t0, r) in run(v, m, periods).items():
                un.append(r)
                all_dd.append((m, p, r["dd"]))
        res[name] = {"h1": pool(h1), "h2": pool(h2), "unseen": pool(un),
                     "breaks": [(m, p, dd) for m, p, dd in all_dd if dd < -10]}
        print(f"done {name}", flush=True)
    return res


def judge(res, now_name):
    base = res[now_name]
    out = {}
    for name, r in res.items():
        if name == now_name:
            continue
        reasons = []
        for k, label in (("h1", "1st half"), ("h2", "2nd half"), ("unseen", "never-seen")):
            if not (r[k]["pnl"] > base[k]["pnl"] and r[k]["pf"] > base[k]["pf"]):
                reasons.append(f"doesn't beat now on {label}")
            if not r[k]["pf"] > 1.0:
                reasons.append(f"PF {r[k]['pf']:.2f} on {label} (needs > 1)")
        if r["breaks"]:
            reasons.append("DD > 10%: " + ", ".join(f"{m} {p} {dd:.1f}%" for m, p, dd in r["breaks"]))
        out[name] = reasons
    return out


def table(res, verdicts):
    rows = ["| Version | 1st half P/L | 1st half PF | 2nd half P/L | 2nd half PF | Never-seen P/L | Never-seen PF | "
            "Worst DD | Pass? |", "|---|---|---|---|---|---|---|---|---|"]
    for name, r in res.items():
        worst = min(r["h1"]["worst_dd"], r["h2"]["worst_dd"], r["unseen"]["worst_dd"])
        v = "(current)" if name not in verdicts else ("PASS" if not verdicts[name] else "fail")
        rows.append(f"| {name} | {r['h1']['pnl']:+.0f} | {r['h1']['pf']:.2f} | {r['h2']['pnl']:+.0f} | "
                    f"{r['h2']['pf']:.2f} | {r['unseen']['pnl']:+.0f} | {r['unseen']['pf']:.2f} | {worst:.1f}% | {v} |")
    return rows


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"  # "v2", "gold" or "all"
    lines = []
    if which in ("v2", "all"):
        v2_res = evaluate(V2_VERSIONS, [(c, lh.PERIODS) for c in V2_COINS], [(c, lh.PERIODS) for c in V2_UNSEEN])
        v2_v = judge(v2_res, "v2 now")
        lines += ["## SP-12 v2 (traded: ETH, SOL, XAUT; never-seen: the 11 out-of-sample coins from job 2b)", ""]
        lines += table(v2_res, v2_v) + [""]
        lines += [f"- {n}: " + ("PASS" if not r else "; ".join(r)) for n, r in v2_v.items()] + [""]
    if which in ("gold", "all"):
        gold_res = evaluate(GOLD_VERSIONS, [("XAUT", lh.PERIODS)],
                            [(m, fx.FX_ERAS) for m in GOLD_UNSEEN])
        gold_v = judge(gold_res, "gold now (pivot 3)")
        lines += ["## Trend Rider gold (traded: XAUT; never-seen: AUD/USD, NZD/USD, USD/CAD, USD/CHF 2012-now, "
                  "0.01% cost)", ""]
        lines += table(gold_res, gold_v) + [""]
        lines += [f"- {n}: " + ("PASS" if not r else "; ".join(r)) for n, r in gold_v.items()] + [""]
    head = ["# Repair test: SP-12 v2 and Trend Rider gold", "",
             f"Run {dt.datetime.now(UTC):%Y-%m-%d}. Variants and pass rules fixed beforehand in research/REPAIR_PLAN.md. "
             "P/L in USD summed over coin-periods (fresh $1,000 each); PF pooled over all trades. "
             "Halves: 1st = periods starting before 2022, 2nd = 2022 and 2023-now. Script: research/repair_test.py.", ""]
    lines = head + lines
    name = "REPAIR.md" if which == "all" else f"REPAIR_{which}.md"
    with open(os.path.join(HERE, name), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
