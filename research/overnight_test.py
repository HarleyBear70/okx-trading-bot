"""
OVERNIGHT_TEST: the "edge is overnight" idea from the David Delaney ad Jeff sent (Oct 11 2026), on crypto.
Hold the coin only OUTSIDE US stock hours (sell 4:00 PM ET weekdays, buy back 9:30 AM ET next weekday; weekends held),
vs hold only DURING stock hours, vs just holding. Costs per side 0.02% taker + 0.02% slippage (Binance.US).
Paper research only.

  python3 research/overnight_test.py
"""
import datetime as dt
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402

NY, COST = ZoneInfo("America/New_York"), 0.0004
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def run(d, a, b):
    ts, o = d["ts"], d["o"]
    eq = {"night": 1.0, "day": 1.0, "hold": 1.0}
    pk = {k: 1.0 for k in eq}
    dd = {k: 0.0 for k in eq}
    in_day, last = None, o[a]
    for i in range(a, b):
        t = dt.datetime.fromtimestamp(ts[i] / 1000, NY)
        m = t.hour * 60 + t.minute
        day = t.weekday() < 5 and 570 <= m < 960
        px = o[i]
        g = px / last
        if in_day is not None:
            eq["hold"] *= g
            if in_day:
                eq["day"] *= g
            else:
                eq["night"] *= g
            if day != in_day:  # switch: one side sells, the other buys
                eq["day"] *= 1 - COST
                eq["night"] *= 1 - COST
        in_day, last = day, px
        if i % 12 == 0:
            for k in eq:
                pk[k] = max(pk[k], eq[k])
                dd[k] = min(dd[k], eq[k] / pk[k] - 1)
    yrs = (ts[b - 1] - ts[a]) / 3.15576e10
    return {k: (eq[k] ** (1 / yrs) - 1, dd[k]) for k in eq}


def main():
    print("| Coin | Period | Hold only outside stock hours | Hold only during stock hours | Just hold |")
    print("|---|---|---|---|---|")
    for coin in COINS:
        d = D.load(coin)
        n = len(d["ts"])
        cut = next(i for i in range(n) if d["ts"][i] >= CUT)
        for name, a, b in (("all", 0, n), ("2019-22", 0, cut), ("2023-now", cut, n)):
            r = run(d, a, b)
            f = lambda k: f"{100 * r[k][0]:+.0f}%/yr, worst drop {100 * r[k][1]:.0f}%"
            print(f"| {coin} | {name} | {f('night')} | {f('day')} | {f('hold')} |", flush=True)
        del d


if __name__ == "__main__":
    main()
