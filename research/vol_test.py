"""
Job 2e: volatility guard for SP-12 v4. Applies the variants and rules fixed in research/VOL_PLAN.md
(committed before this test was run).

Run:
  python research/vol_test.py        # writes research/VOL.md
"""
import bisect
import datetime as dt
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import long_history as lh  # noqa: E402
import score_test as st  # noqa: E402

UTC = dt.timezone.utc
CUT = dt.datetime(2022, 1, 1, tzinfo=UTC)
A_HALVES = [("1st half", dt.datetime(2018, 5, 1, tzinfo=UTC), CUT), ("2nd half", CUT, None)]
BASE = ["BTC", "ETH", "XRP"]
B_COINS = [c for c in sorted(lh.SOURCES) if c != "XAUT"]
WINDOW, PCT, MIN_HIST = 540, 0.95, 100


def hot_flags(bars, kind):
    """True where this candle's ATR% (or range%) is above the 95th percentile of the previous 540 candles."""
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    if kind == "atr":
        a = bot.atr(h, l, c, 14)
        val = [a[i] / c[i] if a[i] else None for i in range(len(bars))]
    else:
        val = [(h[i] - l[i]) / c[i] for i in range(len(bars))]
    window, ordered, out = deque(), [], []
    for v in val:
        hot = False
        if v is not None and len(ordered) >= MIN_HIST:
            hot = v > ordered[int(PCT * (len(ordered) - 1))]
        out.append(hot)
        if v is not None:
            window.append(v)
            bisect.insort(ordered, v)
            if len(window) > WINDOW:
                ordered.pop(bisect.bisect_left(ordered, window.popleft()))
    return out


def make_analyse(mode):
    """mode: None (current), 'G1' skip on hot ATR, 'G2' half size on hot ATR, 'G3' skip on hot candle range."""
    def analyse(bars, daily, cfg):
        a = bot.analyse_sp(bars, daily, cfg)
        if mode is None:
            return a
        hot = hot_flags(bars, "range" if mode == "G3" else "atr")
        sig, info = list(a["signal"]), list(a["info"])
        for k in range(len(bars)):
            if sig[k] and hot[k]:
                if mode == "G2":
                    info[k] = {**info[k], "half": True}
                else:
                    sig[k] = False
        return {**a, "signal": sig, "info": info}
    return analyse


class Recorder:
    """Wraps bot.open_position: half-size entries for G2, and the balance / risk at every entry (for gap losses)."""
    def __init__(self):
        self.entries, self.half = [], False
        self.o_open, self.o_risk = bot.open_position, bot.risk_pct

    def __enter__(self):
        def risk_pct(b, bs):
            r = self.o_risk(b, bs)
            return r / 2 if self.half else r

        def open_position(api, b, bs, coin, bar, inf, extra):
            had = coin in bs["positions"]
            self.half = bool(inf.get("half"))
            eq, r = bs["equity"], risk_pct(b, bs)
            try:
                self.o_open(api, b, bs, coin, bar, inf, extra)
            finally:
                self.half = False
            if not had and coin in bs["positions"]:
                self.entries.append(eq * r)
        bot.open_position, bot.risk_pct = open_position, risk_pct
        return self

    def __exit__(self, *exc):
        bot.open_position, bot.risk_pct = self.o_open, self.o_risk


def gaps(pnls, risks):
    return sum(p < -1.5 * r for p, r in zip(pnls, risks))


def set_a(mode, t0, t1):
    st.COINS = BASE
    data = {c: lh.load(c) for c in BASE}
    with Recorder() as rec:
        r = st.simulate(data, make_analyse(mode), t0, t1 or dt.datetime.now(UTC))
    return {"ret": r["ret"], "dd": r["dd"], "pf": r["pf"], "trades": r["trades"],
            "gaps": gaps([t["pnl"] for t in r["list"]], rec.entries)}


def set_b(mode):
    """Pooled over every coin-period; returns {half: summary}."""
    out = {h: {"pnl": 0.0, "worst": 0.0, "gaps": 0, "trades": 0} for h in ("1st half", "2nd half")}
    now = dt.datetime.now(UTC)
    an = make_analyse(mode)
    for c in B_COINS:
        bars, daily = lh.load(c)
        a = an(bars, daily, bot.SP_SETTINGS["v4"])
        for p, t0, t1 in lh.PERIODS:
            t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC))
            t1 = t1 or now
            if t0 >= t1 or bars[-1]["ts"] < lh.ms(t0):
                continue
            with Recorder() as rec:
                r = lh.simulate("v4", bars, a, t0, t1)
            if not r:
                continue
            h = out["1st half" if t0 < CUT else "2nd half"]
            h["pnl"] += r["pnl"]
            h["worst"] = min(h["worst"], r["dd"])
            h["trades"] += r["trades"]
            h["gaps"] += gaps(r["trade_pnls"], rec.entries)
    return out


def main():
    versions = {"current": None, "G1: skip on hot ATR": "G1", "G2: half size on hot ATR": "G2",
                "G3: skip on hot candle range": "G3"}
    res = {}
    for name, mode in versions.items():
        res[name] = {"A": {h: set_a(mode, t0, t1) for h, t0, t1 in A_HALVES}, "B": set_b(mode)}
        print(f"done {name}", flush=True)

    base = res["current"]
    verdict = {}
    for name in list(versions)[1:]:
        r, why = res[name], []
        for h, _, _ in A_HALVES:
            a, a0, b, b0 = r["A"][h], base["A"][h], r["B"][h], base["B"][h]
            if not (a["dd"] >= a0["dd"] and b["worst"] >= b0["worst"] and (a["dd"] > a0["dd"] or b["worst"] > b0["worst"])):
                why.append(f"{h}: DD not better (A {a['dd']:.1f}% vs {a0['dd']:.1f}%, B worst {b['worst']:.1f}% vs {b0['worst']:.1f}%)")
            if not a["gaps"] + b["gaps"] < a0["gaps"] + b0["gaps"]:
                why.append(f"{h}: gap losses not fewer ({a['gaps'] + b['gaps']} vs {a0['gaps'] + b0['gaps']})")
            for got, ref, label in ((a["ret"], a0["ret"], "A return"), (b["pnl"], b0["pnl"], "B P/L")):
                need = 0.9 * ref if ref > 0 else ref
                if got < need:
                    why.append(f"{h}: {label} {got:+.1f} below 90% of {ref:+.1f}")
        verdict[name] = why

    lines = ["# Volatility guard for SP-12 v4 (job 2e)", "",
             f"Run {dt.datetime.now(UTC):%Y-%m-%d}. Variants and rules fixed beforehand in research/VOL_PLAN.md. "
             "A = v4 bot as it trades (BTC ETH XRP, shared $1,000, max 3 open); B = 15 coins one at a time per "
             "market period, pooled. Gap loss = lost more than 1.5x planned risk. Script: research/vol_test.py.", "",
             "| Version | Half | A trades | A return | A max DD | A PF | A gaps | B trades | B P/L (USD) | B worst DD | B gaps | Pass? |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in versions:
        for h, _, _ in A_HALVES:
            a, b = res[name]["A"][h], res[name]["B"][h]
            v = "(current)" if name == "current" else ("PASS" if not verdict[name] else "fail")
            lines.append(f"| {name} | {h} | {a['trades']} | {a['ret']:+.1f}% | {a['dd']:.1f}% | {a['pf']:.2f} | {a['gaps']} | "
                         f"{b['trades']} | {b['pnl']:+.0f} | {b['worst']:.1f}% | {b['gaps']} | {v} |")
    lines.append("")
    lines += [f"- {n}: " + ("PASS" if not w else "; ".join(w)) for n, w in verdict.items()]
    with open(os.path.join(HERE, "VOL.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
