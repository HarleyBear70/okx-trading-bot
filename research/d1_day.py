"""
D1 1H day bots: capitulation buy (D1-C) and US-session intraday momentum (D1-I).
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/d1_day.py        # writes research/D1_DAY.md
"""
import datetime as dt
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import b_boxes as bb  # noqa: E402
import engine as e  # noqa: E402
import hourly as hr  # noqa: E402

COST = 0.0015  # 0.1% taker + 0.05% slippage, each side
UTC = dt.timezone.utc
_btc_ok = {}


def btc_bull():
    """{day ms: True if BTC's daily close that day is above its 200-day average} (Binance 1H data)."""
    if not _btc_ok:
        closes = {}
        for b in hr.hourly("BTC"):
            closes[b["ts"] - b["ts"] % 86400000] = b["c"]  # last hourly close of the day = daily close
        days = sorted(closes)
        cs = [closes[d] for d in days]
        sma = bot.sma(cs, 200)
        _btc_ok.update({d: (s is not None and c > s) for d, c, s in zip(days, cs, sma)})
    return _btc_ok


def btc_ok_at(ts):
    """BTC filter using the last COMPLETED day before this candle."""
    day = ts - ts % 86400000
    return btc_bull().get(day - 86400000, False)


def capitulation(k_sigma, btc_filter):
    def fn(coin, bars, daily):
        c, l, h = ([b[x] for b in bars] for x in "clh")
        at = bot.atr(h, l, c, 14)
        n = len(bars)
        r24 = [None] * n
        for k in range(24, n):
            r24[k] = c[k] / c[k - 24] - 1
        out = [None] * n
        s = sq = 0.0
        cnt = 0
        for k in range(n):
            # rolling stats of r24 over the previous 720 values (k-720 .. k-1)
            if k - 1 >= 24 and r24[k - 1] is not None:
                s += r24[k - 1]
                sq += r24[k - 1] ** 2
                cnt += 1
            if k - 721 >= 24 and r24[k - 721] is not None:
                s -= r24[k - 721]
                sq -= r24[k - 721] ** 2
                cnt -= 1
            if cnt < 720 or r24[k] is None or at[k] is None:
                continue
            mean = s / cnt
            sd = math.sqrt(max(sq / cnt - mean * mean, 0.0))
            if sd <= 0 or r24[k] >= -k_sigma * sd:
                continue
            if btc_filter and not btc_ok_at(bars[k]["ts"]):
                continue
            stop = min(l[k - 23:k + 1]) - at[k]
            out[k] = {"stop": stop, "target": c[k] + 0.5 * (c[k - 24] - c[k]), "max_bars": 48}
        return out
    return fn


def intraday(x_pct, btc_filter):
    def fn(coin, bars, daily):
        out = [None] * len(bars)
        idx = {b["ts"]: k for k, b in enumerate(bars)}
        for k, b in enumerate(bars):
            if dt.datetime.fromtimestamp(b["ts"] / 1000, UTC).hour != 13:  # the 13:00 candle closes at 14:00 UTC
                continue
            day0 = b["ts"] - b["ts"] % 86400000
            k0 = idx.get(day0)
            if k0 is None or k - k0 != 13:
                continue  # missing candles today
            if b["c"] / bars[k0]["o"] - 1 <= x_pct:
                continue
            if btc_filter and not btc_ok_at(b["ts"]):
                continue
            stop = min(x["l"] for x in bars[k0:k + 1])
            out[k] = {"stop": stop, "target": None, "max_bars": 10}
        return out
    return fn


def variant(fn, cooldown=0):
    return (lambda data, t0, t1: e.trade_sim([c for c in e.DESIGN if c in data], data, fn, t0, t1, fee=COST,
                                             cooldown=cooldown),
            lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1, fee=COST, cooldown=cooldown))


def main():
    lines = ["# D1 1H day bots", "", "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Binance "
             "archive 1H candles. Cost 0.15% each side (0.1% taker + 0.05% slippage). Design coins BTC ETH XRP on one "
             "shared $1,000; never-seen coins one at a time per period, pooled. Script: research/d1_day.py.", ""]
    for title, variants in (
        ("D1-C capitulation buy", {"C1: drop > 3 sigma": variant(capitulation(3.0, False), 24),
                                   "C2: drop > 2.5 sigma": variant(capitulation(2.5, False), 24),
                                   "C3: drop > 3 sigma, BTC above 200-day": variant(capitulation(3.0, True), 24)}),
        ("D1-I intraday momentum", {"I1: up > 1% by 14:00 UTC": variant(intraday(0.01, False)),
                                    "I2: up > 2% by 14:00 UTC": variant(intraday(0.02, False)),
                                    "I3: up > 1%, BTC above 200-day": variant(intraday(0.01, True))})):
        rows, verdicts, best = e.evaluate(variants, loader=bb.load_1h)
        lines += bb.report(title, rows, verdicts, best)
    with open(os.path.join(HERE, "D1_DAY.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
