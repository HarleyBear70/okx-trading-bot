"""
SWING_HOLD: Jeff's "sell high, buy back low" idea on coins he already holds (Oct 10 2026, chat). Paper research only.
Jeff: wait for confirmation the rise is over, sell near the top; buy back once it's done falling; doesn't have to be
perfect, just profit. If I miss it (price runs away), I miss it: reset and look for the next high / low.
Score = coins at the end vs just holding (ratio > 1.00 = more coins than holding).

  Structure = Jeff's heartbeat (research/jeff_struct.py Heart), swing 1/2/3 (Jeff marks by eye -> test all three).
  Sell    = MS DOWN confirmed (Jeff's MS rule: a body close past STRONG's wick, not undone by the next candle),
            at the next candle's open.  [NOT JEFF: MS = his "confirmation the rise is over"]
  Buy     = MS UP confirmed, at the next candle's open.
     A "plain":    buy back on the next MS UP, whatever the price.
     B "no chase": only buy back BELOW the sell price. An MS UP above it = missed, skipped; reset at the next MS DOWN
                   (that price becomes the new sell price, as if he sold there).  [NOT JEFF: how "reset" works]
  Timeframes 4H and daily (Jeff didn't pick -> both).  Costs per side: 0.02% taker + 0.05% slippage (Binance.US).
  Starts holding the coin. Halves 2019-22 / 2023-now each start fresh from holding.

  python3 research/swing_hold.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COST = 0.0007
TFS = (("4H", 14400000), ("daily", 86400000))
MAIN, UNSEEN = ["BTC", "ETH", "SOL", "XRP"], ["BNB", "ADA", "DOGE", "LINK", "LTC"]
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)


def run(T, O, H, L, C, N, mode, a, b):
    """candles a..b-1 (signals use all history before them). returns (coins ratio vs hold, round trips, % time in cash)"""
    s = Heart(H, L, C, N)
    for k in range(a):
        s.step(k)
    coins, cash, ref, act, trips, out_bars = 1.0, 0.0, None, None, 0, 0
    p0 = O[a]
    for k in range(a, b):
        if act == "sell" and coins > 0:
            cash, coins, ref = coins * O[k] * (1 - COST), 0.0, O[k]
        elif act == "buy" and coins == 0:
            if mode == "A" or O[k] < ref:
                coins, cash = cash / O[k] * (1 - COST), 0.0
                trips += 1
        elif act == "reset" and coins == 0:
            ref = O[k]
        act = None
        if coins == 0:
            out_bars += 1
        ev = s.step(k)
        if ev in ("MS DOWN", "start DOWN"):
            act = "sell" if coins > 0 else "reset"
        elif ev in ("MS UP", "start UP"):
            act = "buy"
    end = coins + cash / C[b - 1]  # value in coins
    yrs = (T[b - 1] - T[a]) / 3.15576e10
    return end, trips / yrs, 100 * out_bars / (b - a), C[b - 1] / p0


def main():
    rows = []
    for coin in MAIN + UNSEEN:
        d = D.load(coin)
        for tfn, size in TFS:
            O, H, L, C, e = D.resample(d["ts"], d["o"], d["h"], d["l"], d["c"], size)
            T = [d["ts"][i] for i in range(len(e)) if e[i] >= 0]
            n = len(C)
            a0 = next(k for k in range(n) if T[k] >= int(dt.datetime(2019, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000))
            a0 = max(a0, 30)
            cut = next(k for k in range(n) if T[k] >= CUT)
            for N in (1, 2, 3):
                for mode in ("A", "B"):
                    full = run(T, O, H, L, C, N, mode, a0, n)
                    h1 = run(T, O, H, L, C, N, mode, a0, cut)
                    h2 = run(T, O, H, L, C, N, mode, cut, n)
                    rows.append((coin, tfn, N, mode, full, h1[0], h2[0]))
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    print("\n### Sell high / buy back low (coins vs just holding; 1.00 = same as holding)\n")
    print("| Version | Group | Avg coins vs hold | Coins beat hold | 2019-22 avg | 2023-now avg | Trips/yr | % time in cash |")
    print("|---|---|---|---|---|---|---|---|")
    for tfn, _ in TFS:
        for N in (1, 2, 3):
            for mode in ("A", "B"):
                for grp, cs in (("main", MAIN), ("never-seen", UNSEEN)):
                    r = [x for x in rows if x[1] == tfn and x[2] == N and x[3] == mode and x[0] in cs]
                    av = lambda f: sum(f(x) for x in r) / len(r)
                    nm = f"{tfn}, swing {N}, {'A plain' if mode == 'A' else 'B no chase'}"
                    print(f"| {nm} | {grp} | {av(lambda x: x[4][0]):.2f}x | {sum(x[4][0] > 1 for x in r)}/{len(r)} | "
                          f"{av(lambda x: x[5]):.2f}x | {av(lambda x: x[6]):.2f}x | {av(lambda x: x[4][1]):.1f} | "
                          f"{av(lambda x: x[4][2]):.0f}% |")
    print("\n### Per coin (coins vs hold, full period)\n")
    for x in rows:
        print(f"{x[0]:5} {x[1]:5} swing {x[2]} {x[3]}: {x[4][0]:.2f}x  (2019-22 {x[5]:.2f}x, 2023-now {x[6]:.2f}x)  "
              f"trips/yr {x[4][1]:.1f}, cash {x[4][2]:.0f}%, coin price x{x[4][3]:.1f}")


if __name__ == "__main__":
    main()
