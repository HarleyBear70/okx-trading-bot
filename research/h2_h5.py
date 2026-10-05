"""
H2 market mood detector and H5 profit sweeper, on v4 + Trend Rider as they trade.
Variants and rules fixed beforehand in research/HELPERS_PLAN.md.

Run:
  python research/h2_h5.py        # writes research/H2_MOOD.md and research/H5_SWEEP.md
"""
import bisect
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import long_history as lh  # noqa: E402


# ───────── H2 ─────────
def btc_labels():
    """{day number: (above_200, sma_rising, crash_30d, adx)} from BTC's daily candles."""
    daily = lh.load("BTC")[1]
    h, l, c = ([d[x] for d in daily] for x in "hlc")
    sma = bot.sma(c, 200)
    adx = e.adx(h, l, c, 14)
    out = {}
    for i, d in enumerate(daily):
        if sma[i] is None or i < 30:
            continue
        out[bot.day_of(d["ts"])] = {"above": c[i] > sma[i], "rising": i >= 20 and sma[i - 20] is not None and sma[i] > sma[i - 20],
                                    "crash": c[i] / c[i - 30] - 1 <= -0.20, "adx": adx[i]}
    return out


def mood_up(lab, mode):
    if lab is None:
        return False
    if mode == "M1":
        return lab["above"]
    if mode == "M2":
        return lab["above"] and lab["rising"] and not lab["crash"]
    return lab["above"] and lab["adx"] is not None and lab["adx"] >= 20


def gated_specs(mode):
    labels = btc_labels()
    specs = []
    for name, strat, coins, data, analyse, extra in e.demo_specs():
        def an(bars, daily, analyse=analyse):
            a = analyse(bars, daily)
            if mode is None:
                return a
            sig = [s and mood_up(labels.get(bot.day_of(b["ts"]) - 1), mode) for s, b in zip(a["signal"], bars)]
            return {**a, "signal": sig}
        specs.append((name, strat, coins, data, an, extra))
    return specs


def h2():
    versions = {"all bots always on": None, "M1: BTC above 200-day": "M1",
                "M2: above + 200-day rising, off in a 20% crash": "M2", "M3: above + ADX >= 20": "M3"}
    res = {}
    for name, mode in versions.items():
        specs = gated_specs(mode)
        res[name] = {}
        for h, t0, t1 in e.HALVES:
            r = e.multi_sim(specs, t0, t1)
            ret, dd, rd = e.ret_dd(r["combined"])
            res[name][h] = {"ret": ret, "dd": dd, "rd": rd, "n": sum(b["trades"] for b in r["bots"].values())}
        print(f"done {name}", flush=True)
    base = res["all bots always on"]
    lines = ["# H2 market mood detector", "", "Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. "
             "v4 + Trend Rider as they trade, $1,000 each; new trades only on 'up' days (BTC's last completed daily "
             "candle). Script: research/h2_h5.py.", "",
             "| Version | Half | Trades | Combined return | Combined max DD | Return/DD | Pass? |", "|---|---|---|---|---|---|---|"]
    for name in versions:
        ok = versions[name] is not None and all(res[name][h]["rd"] > base[h]["rd"] for h in base)
        for h, _, _ in e.HALVES:
            r = res[name][h]
            lines.append(f"| {name} | {h} | {r['n']} | {r['ret']:+.1f}% | {r['dd']:.1f}% | {r['rd']:.2f} | "
                         f"{'-' if versions[name] is None else ('PASS' if ok else 'fail')} |")
    with open(os.path.join(HERE, "H2_MOOD.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


# ───────── H5 ─────────
def h5():
    px = {}
    for c in ("BTC", "XRP"):
        bars = lh.load(c)[0]
        px[c] = ([b["ts"] for b in bars], [b["c"] for b in bars])

    def price(c, ts):
        tss, cs = px[c]
        i = bisect.bisect_right(tss, ts) - 1
        return cs[i] if i >= 0 else None

    lines = ["# H5 profit sweeper", "", "Rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider as they "
             "trade, $1,000 each. A share of every winning sale moves into a BTC + XRP 50/50 hold pile (0.1% fee). "
             "Combined = both trading balances + the hold pile. Script: research/h2_h5.py.", "",
             "| Version | Half | Combined return | Combined max DD | Return/DD | Moved to hold pile | Hold pile at end | "
             "Trading balances at end |", "|---|---|---|---|---|---|---|---|"]
    for name, share in (("no sweeping", 0.0), ("K1: 25% of each win", 0.25), ("K2: 50% of each win", 0.5)):
        for h, t0, t1 in e.HALVES:
            cur, buys = {"ts": None}, []
            o_close, o_half, o_hit, o_manage = bot.close_position, bot.take_half, bot.check_hit, bot.manage_on_close

            def sweep(bs):
                def after(eq0):
                    gain = bs["equity"] - eq0
                    if share and gain > 0:
                        amt = share * gain
                        bs["equity"] -= amt
                        units = {c: amt / 2 / (1 + bot.FEE) / price(c, cur["ts"]) for c in ("BTC", "XRP")}
                        buys.append((cur["ts"], amt, units))
                return after

            def close_position(api, b, bs, coin, reason, paper_px):
                eq0 = bs["equity"]
                o_close(api, b, bs, coin, reason, paper_px)
                if reason != "end of test":
                    sweep(bs)(eq0)

            def take_half(api, b, bs, coin, paper_px):
                eq0 = bs["equity"]
                o_half(api, b, bs, coin, paper_px)
                sweep(bs)(eq0)

            def check_hit(api, b, bs, coin, bar):
                cur["ts"] = bar["ts"]
                return o_hit(api, b, bs, coin, bar)

            def manage_on_close(api, b, bs, coin, a, i, bar, bars_in):
                cur["ts"] = bar["ts"]
                return o_manage(api, b, bs, coin, a, i, bar, bars_in)
            bot.close_position, bot.take_half, bot.check_hit, bot.manage_on_close = (close_position, take_half,
                                                                                  check_hit, manage_on_close)
            try:
                r = e.multi_sim(e.demo_specs(), t0, t1)
            finally:
                bot.close_position, bot.take_half, bot.check_hit, bot.manage_on_close = o_close, o_half, o_hit, o_manage
            # combined curve + hold pile value at each time
            curve, bi, held = [], 0, {"BTC": 0.0, "XRP": 0.0}
            for ts, v in r["combined"]:
                while bi < len(buys) and buys[bi][0] <= ts:
                    for c in held:
                        held[c] += buys[bi][2][c]
                    bi += 1
                curve.append((ts, v + sum(held[c] * price(c, ts) * (1 - bot.FEE) for c in held)))
            ret, dd, rd = e.ret_dd(curve)
            hold_end = curve[-1][1] - r["combined"][-1][1]
            lines.append(f"| {name} | {h} | {ret:+.1f}% | {dd:.1f}% | {rd:.2f} | ${sum(b[1] for b in buys):,.0f} | "
                         f"${hold_end:,.0f} | ${r['combined'][-1][1]:,.0f} |")
        print(f"done {name}", flush=True)
    with open(os.path.join(HERE, "H5_SWEEP.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    h2()
    h5()
