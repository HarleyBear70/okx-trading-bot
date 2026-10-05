"""
N1 range bot: buy near the bottom of a sideways range, sell near the top, only when ADX says not trending.
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/n1_range.py        # writes research/N1_RANGE.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

ADX_MAX, W_MIN, W_MAX, BUY_ZONE, MAX_BARS = 20, 0.04, 0.25, 0.20, 30


def entries(n, target_frac):
    def fn(coin, bars, daily):
        h, l, c = ([b[x] for b in bars] for x in "hlc")
        ad, at = e.adx(h, l, c, 14), bot.atr(h, l, c, 14)
        hh, ll = bot.highest(h, n), bot.lowest(l, n)
        out = [None] * len(bars)
        for k in range(n + 1, len(bars)):
            top, bot_ = hh[k - 1], ll[k - 1]  # range of the previous n candles
            if ad[k] is None or at[k] is None or top is None or bot_ is None or bot_ <= 0:
                continue
            w = (top - bot_) / bot_
            if ad[k] < ADX_MAX and W_MIN <= w <= W_MAX and bot_ < c[k] <= bot_ + BUY_ZONE * (top - bot_):
                out[k] = {"stop": bot_ - 0.5 * at[k], "target": bot_ + target_frac * (top - bot_), "max_bars": MAX_BARS}
        return out
    return fn


def variant(n, frac):
    fn = entries(n, frac)
    return (lambda data, t0, t1: e.trade_sim(e.DESIGN, data, fn, t0, t1),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1))


def main():
    rows, verdicts, best = e.evaluate({
        "R1: 60 candles, target 80%": variant(60, 0.8),
        "R2: 60 candles, target 50%": variant(60, 0.5),
        "R3: 120 candles, target 80%": variant(120, 0.8),
    })
    lines = ["# N1 range bot", "", "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. "
             "Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per period, pooled. "
             "0.5% risk, 0.1% fee each side. Script: research/n1_range.py.", ""] + rows + [""] + verdicts + [
             "", f"Result: {'PASS - ' + best if best else 'no variant passes'}"]
    with open(os.path.join(HERE, "N1_RANGE.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
