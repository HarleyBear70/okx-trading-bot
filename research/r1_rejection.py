"""
R1 rejection block (ICT), long only, crypto 4H. Variants and rules fixed beforehand in research/IDEAS_PLAN.md.

Run:
  python research/r1_rejection.py        # writes research/R1_REJECTION.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import b_boxes as bb  # noqa: E402
import engine as e  # noqa: E402

PIV, EXPIRE = 3, 60


def entries(move, daily_filter):
    """move: 'atr' (+3 ATR within 6 candles) or 'bos' (close above the last swing high within 10 candles)."""
    def fn(coin, bars, daily):
        o, h, l, c = ([b[x] for b in bars] for x in "ohlc")
        a = bot.atr(h, l, c, 14)
        pl, ph = bot.pivots(l, PIV, False), bot.pivots(h, PIV, True)
        dc = [d["c"] for d in daily]
        de, dk = bot.ema(dc, 50), bot.daily_lookup(bars, daily)
        n = len(bars)
        last_ph = [None] * n  # last swing high confirmed by each candle
        cur = None
        for i in range(n):
            if ph[i] is not None:
                cur = ph[i]
            last_ph[i] = cur
        out = [None] * n
        for i in range(n):
            if pl[i] is None:
                continue
            p = i - PIV  # the swing-low candle; confirmed at candle i
            if a[p] is None:
                continue
            body_low = min(o[p], c[p])
            wick, body = body_low - l[p], abs(c[p] - o[p])
            if not (wick >= 2 * body and wick >= 0.5 * a[p]):
                continue
            j = None
            if move == "atr":
                for q in range(p + 1, min(p + 7, n)):
                    if h[q] >= l[p] + 3 * a[p]:
                        j = q
                        break
            else:
                ref = last_ph[p]
                if ref is not None:
                    for q in range(p + 1, min(p + 11, n)):
                        if c[q] > ref:
                            j = q
                            break
            if j is None:
                continue
            valid = max(i, j)  # both the pivot and the move must be known
            top = max(h[p:valid + 1])
            for k in range(valid + 1, min(p + EXPIRE + 1, n)):
                if l[k] <= body_low:  # first time price comes back into the zone
                    if c[k] > l[p] and a[k] is not None and top > c[k] and out[k] is None:
                        if daily_filter:
                            dd = dk[k]
                            if dd is None or de[dd] is None or dc[dd] <= de[dd]:
                                break
                        out[k] = {"stop": l[p] - 0.25 * a[k], "target": top, "max_bars": None}
                    break
        return out
    return fn


def variant(move, daily_filter):
    fn = entries(move, daily_filter)
    return (lambda data, t0, t1: e.trade_sim(e.DESIGN, data, fn, t0, t1),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1))


def main():
    rows, verdicts, best = e.evaluate({
        "RB1: +3 ATR move within 6": variant("atr", False),
        "RB2: break of structure within 10": variant("bos", False),
        "RB3: RB1 + daily trend": variant("atr", True),
    })
    lines = ["# R1 rejection block (ICT), long only, crypto 4H", "", "Variants and pass rules fixed beforehand in "
             "research/IDEAS_PLAN.md. Design coins BTC ETH XRP on one shared $1,000; never-seen coins one at a time per "
             "period, pooled. 0.5% risk, 0.1% fee each side. Script: research/r1_rejection.py.", ""]
    lines += bb.report("Results", rows, verdicts, best)
    with open(os.path.join(HERE, "R1_REJECTION.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
