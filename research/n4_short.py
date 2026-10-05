"""
N4 short side (backtest only): Trend Rider mirrored for falling markets.
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/n4_short.py        # writes research/N4_SHORT.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import long_history as lh  # noqa: E402

_atr = {}
_btc = {}


def btc_bear_days():
    """{day number: True if BTC's daily close is below its 200-day average}."""
    if not _btc:
        daily = lh.load("BTC")[1]
        cs = [d["c"] for d in daily]
        sma = bot.sma(cs, 200)
        _btc.update({bot.day_of(d["ts"]): (s is not None and c < s) for d, c, s in zip(daily, cs, sma)})
    return _btc


def entries(pivot, btc_filter):
    def fn(coin, bars, daily):
        h, l, c = ([b[x] for b in bars] for x in "hlc")
        e50, a = bot.ema(c, 50), bot.atr(h, l, c, 14)
        _atr[id(bars)] = a
        dc = [d["c"] for d in daily]
        de, dk = bot.ema(dc, 50), bot.daily_lookup(bars, daily)
        ph_l, pl_l = bot.pivots_ge(h, pivot, True), bot.pivots_ge(l, pivot, False)
        ph = pl = None
        bear = btc_bear_days() if btc_filter else None
        out = [None] * len(bars)
        for i in range(len(bars)):
            if ph_l[i] is not None:
                ph = ph_l[i]
            if pl_l[i] is not None:
                pl = pl_l[i]
            if i < 61 or a[i] is None or e50[i] is None or pl is None:
                continue
            k = dk[i]
            if not (k is not None and de[k] is not None and dc[k] < de[k]):
                continue
            if not (c[i] < pl <= c[i - 1] and c[i] < e50[i]):
                continue
            if bear is not None and not bear.get(bot.day_of(bars[i]["ts"]) - 1, False):
                continue
            s = ph * 1.002 if ph is not None else c[i] + 2 * a[i]
            s = max(min(s, c[i] + 3 * a[i]), c[i] + a[i])
            out[i] = {"stop": s, "target": None, "max_bars": None, "side": -1}
        return out
    return fn


def manage(p, bars, k):
    a = _atr[id(bars)][k]
    x = bars[k]
    p.setdefault("r0", p["stop"] - p["entry"])
    p["lo"] = min(p["lo"], x["c"])
    if x["l"] <= p["entry"] - p["r0"]:
        p["be"] = True  # 1R in profit: stop never goes back above breakeven
    new = p["lo"] + 3 * a if a is not None else p["stop"]
    if p.get("be"):
        new = min(new, p["entry"] * (1 - 2 * bot.FEE))
    return new


def variant(pivot, btc_filter):
    fn = entries(pivot, btc_filter)
    return (lambda data, t0, t1: e.trade_sim(e.DESIGN, data, fn, t0, t1, manage=manage),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1, manage=manage))


def main():
    rows, verdicts, best = e.evaluate({
        "X1: pivot 5": variant(5, False),
        "X2: pivot 5, BTC below 200-day": variant(5, True),
        "X3: pivot 3": variant(3, False),
    })
    lines = ["# N4 short side (mirrored Trend Rider), backtest only", "",
             "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Shorts, no leverage, 0.5% risk, "
             "0.1% fee each side, funding ignored. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one "
             "at a time per period, pooled. Script: research/n4_short.py.", ""] + rows + [""] + verdicts + [
             "", f"Result: {'PASS - ' + best if best else 'no variant passes'}"]
    with open(os.path.join(HERE, "N4_SHORT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
