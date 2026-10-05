"""
N3 squeeze breakout bot: wait for Bollinger width to compress, then buy the breakout above the upper band.
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/n3_squeeze.py        # writes research/N3_SQUEEZE.md
"""
import bisect
import math
import os
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

N, MULT, AFTER, BASE, MAX_STOP, RR, MAX_BARS = 20, 2.0, 6, 20, 0.10, 2.0, 30


def squeezes(width, window, mode):
    """mode 'pct10': width <= 10th percentile of the previous `window`; 'lowest': width <= the lowest of them."""
    q, ordered, out = deque(), [], []
    for w in width:
        hit = False
        if w is not None and len(ordered) >= window:
            ref = ordered[0] if mode == "lowest" else ordered[int(0.10 * (len(ordered) - 1))]
            hit = w <= ref
        out.append(hit)
        if w is not None:
            q.append(w)
            bisect.insort(ordered, w)
            if len(q) > window:
                ordered.pop(bisect.bisect_left(ordered, q.popleft()))
    return out


def entries(window, mode, daily_filter):
    def fn(coin, bars, daily):
        c, l = [b["c"] for b in bars], [b["l"] for b in bars]
        mid = bot.sma(c, N)
        width, upper = [None] * len(c), [None] * len(c)
        for k in range(N - 1, len(c)):
            m = mid[k]
            sd = math.sqrt(sum((x - m) ** 2 for x in c[k - N + 1:k + 1]) / N)
            upper[k] = m + MULT * sd
            width[k] = 2 * MULT * sd / m if m else None
        sq = squeezes(width, window, mode)
        dc = [d["c"] for d in daily]
        de, dk = bot.ema(dc, 50), bot.daily_lookup(bars, daily)
        out, last_sq = [None] * len(c), None
        for k in range(len(c)):
            if sq[k]:
                last_sq = k
            if upper[k] is None or last_sq is None or not (1 <= k - last_sq <= AFTER) or c[k] <= upper[k] or k < BASE:
                continue
            if daily_filter:
                j = dk[k]
                if j is None or de[j] is None or dc[j] <= de[j]:
                    continue
            stop = min(l[k - BASE:k])
            if stop <= 0 or (c[k] - stop) / c[k] > MAX_STOP:
                continue
            out[k] = {"stop": stop, "target": c[k] + RR * (c[k] - stop), "max_bars": MAX_BARS}
        return out
    return fn


def variant(window, mode, daily_filter):
    fn = entries(window, mode, daily_filter)
    return (lambda data, t0, t1: e.trade_sim(e.DESIGN, data, fn, t0, t1),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1))


def main():
    rows, verdicts, best = e.evaluate({
        "S1: squeeze = 10th pct of 90 days": variant(540, "pct10", False),
        "S2: S1 + daily trend filter": variant(540, "pct10", True),
        "S3: squeeze = lowest of 180 days": variant(1080, "lowest", False),
    })
    lines = ["# N3 squeeze breakout bot", "", "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. "
             "Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. "
             "0.5% risk, 0.1% fee each side. Script: research/n3_squeeze.py.", ""] + rows + [""] + verdicts + [
             "", f"Result: {'PASS - ' + best if best else 'no variant passes'}"]
    with open(os.path.join(HERE, "N3_SQUEEZE.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
