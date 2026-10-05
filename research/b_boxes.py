"""
Box bots: B1 breakout retest (4H box, 1H entry) and B2 failed-breakdown reclaim (4H).
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/b_boxes.py        # writes research/B_BOXES.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import hourly as hr  # noqa: E402
import long_history as lh  # noqa: E402

H_MIN, H_MAX = 0.03, 0.12


def load_1h(coins):
    out = {}
    for c in coins:
        b1 = hr.hourly(c)
        if b1:
            out[c] = (b1, lh.to_daily(hr.to_4h(b1)))
    return out


def load_4h(coins):
    out = {}
    for c in coins:
        b1 = hr.hourly(c)
        if b1:
            b4 = hr.to_4h(b1)
            out[c] = (b4, lh.to_daily(b4))
    return out


def box(h, l, j, n):
    if j < n:
        return None
    hi, lo = max(h[j - n:j]), min(l[j - n:j])
    return (hi, lo) if lo > 0 and H_MIN <= (hi - lo) / lo <= H_MAX else None


def b1_entries(rr, n):
    def fn(coin, bars1, daily):
        b4 = hr.to_4h(bars1)
        h4, l4, c4 = ([b[x] for b in b4] for x in "hlc")
        idx1 = {b["ts"]: k for k, b in enumerate(bars1)}
        out = [None] * len(bars1)
        for j in range(n + 1, len(b4)):
            bx = box(h4, l4, j, n)
            if not bx or not (c4[j] > bx[0] >= c4[j - 1]):
                continue
            hi, lo = bx
            start = b4[j]["ts"] + hr.H4
            for t in range(start, start + 12 * hr.H4, hr.H1):
                k = idx1.get(t)
                if k is None:
                    continue
                x = bars1[k]
                if x["l"] <= hi * 1.002 and x["c"] > hi:
                    stop = hi - 0.25 * (hi - lo)
                    out[k] = {"stop": stop, "target": x["c"] + rr * (x["c"] - stop), "max_bars": 48}
                    break
        return out
    return fn


def b2_entries(n_reclaim, daily_filter):
    def fn(coin, b4, daily):
        h, l, c = ([b[x] for b in b4] for x in "hlc")
        dc = [d["c"] for d in daily]
        de, dk = bot.ema(dc, 50), bot.daily_lookup(b4, daily)
        out = [None] * len(b4)
        for j in range(31, len(b4)):
            bx = box(h, l, j, 30)
            if not bx or not (c[j] < bx[1] <= c[j - 1]):
                continue
            hi, lo = bx
            for m in range(j + 1, min(j + 1 + n_reclaim, len(b4))):
                if c[m] > lo:
                    if daily_filter:
                        d = dk[m]
                        if d is None or de[d] is None or dc[d] <= de[d]:
                            break
                    out[m] = {"stop": min(l[j:m + 1]) * 0.999, "target": hi, "max_bars": 30}
                    break
        return out
    return fn


def variant(fn):
    return (lambda data, t0, t1: e.trade_sim([c for c in e.DESIGN if c in data], data, fn, t0, t1),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1))


def report(title, rows, verdicts, best):
    return [f"## {title}", ""] + rows + [""] + verdicts + ["", f"Result: {'PASS - ' + best if best else 'no variant passes'}", ""]


def main():
    lines = ["# Box bots B1 and B2", "", "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Binance "
             "archive 1H candles (4H built from them). Design coins BTC ETH XRP on one shared $1,000; never-seen coins "
             "one at a time per period, pooled. 0.5% risk, 0.1% fee each side. Script: research/b_boxes.py.", ""]
    rows, verdicts, best = e.evaluate({
        "B1a: retest, target 2R": variant(b1_entries(2.0, 30)),
        "B1b: retest, target 3R": variant(b1_entries(3.0, 30)),
        "B1c: retest, target 2R, 60-candle box": variant(b1_entries(2.0, 60)),
    }, loader=load_1h)
    lines += report("B1 breakout retest", rows, verdicts, best)
    rows, verdicts, best = e.evaluate({
        "B2a: reclaim within 3": variant(b2_entries(3, False)),
        "B2b: reclaim within 6": variant(b2_entries(6, False)),
        "B2c: reclaim within 3 + daily trend": variant(b2_entries(3, True)),
    }, loader=load_4h)
    lines += report("B2 failed-breakdown reclaim", rows, verdicts, best)
    with open(os.path.join(HERE, "B_BOXES.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
