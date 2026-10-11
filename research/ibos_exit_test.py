"""
IBOS_EXIT_TEST: Jeff's iBOS as an EXIT (Oct 11 2026). iBOS as an entry lost (research/IBOS_TEST.txt); Jeff calls it the
warning that the side pushing is done. Question: does getting out on the iBOS keep more profit than a fixed target?
Fixed rules decided before the results. Paper research only.

  Entries (15m, research/jeff_struct.py Heart swing 1, at the signal candle's close, longs + mirrored shorts):
    MS    the 15m market shift in the trade's direction (confirmed one candle later)
    BOS   a 15m BOS in the trend's direction
    Stop  past MUST HOLD (STRONG) + 0.05%; skip if more than 1.35% away (Jeff's max stop).
  Exits compared on the SAME trades:
    2R           stop or 2R target only
    2R + iBOS    same, but get out at the close of an iBOS against the trade
    iBOS only    no target: stop, or get out on the iBOS (let it run until the warning)
    iBOS after 1R  no target: stop; the iBOS exit only counts once the trade has been 1R in profit
    MS only      no target: stop, or get out on the full 15m MS against the trade (comparison)
  iBOS (for a long) = a 15m close below the low of the candle that made the highest high since entry (Jeff's LINK
  example), not counting the entry candle's own close.
  Costs: entry, stop and early exits 0.02% taker + 0.02% slippage; 2R target is a limit (0%).

  python3 research/ibos_exit_test.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

COST, GAP, MAXSTOP = 0.0004, 0.0005, 0.0135
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]
EXITS = ["2R", "2R + iBOS", "iBOS only", "iBOS after 1R", "MS only"]


def prep(d):
    ts = d["ts"]
    O, H, L, C, e15 = D.resample(ts, d["o"], d["h"], d["l"], d["c"], 900000)
    T = [ts[i] for i in range(len(ts)) if e15[i] >= 0]
    s, sig, flip = Heart(H, L, C, 1), [], []
    for k in range(len(C)):
        ev = s.step(k)
        flip.append(ev == "MS DOWN")
        if ev in ("MS UP", "BOS up") and s.trend == 1:
            stop = s.strong - GAP * abs(s.strong)
            r = C[k] + COST * abs(C[k]) - stop
            if r > 0 and r / abs(C[k]) <= MAXSTOP:
                sig.append((k, "MS" if ev == "MS UP" else "BOS", stop))
    return T, H, L, C, sig, flip


def sim(T, H, L, C, sig, flip, entry, mode):
    n, free, out = len(C), -1, []
    for k, kind, stop in sig:
        if kind != entry or k <= free:
            continue
        e = C[k] + COST * abs(C[k])
        r = e - stop
        tgt = e + 2 * r if mode.startswith("2R") else None
        top, top_lo, best, x = H[k], L[k], 0.0, None
        j = k + 1
        while j < n:
            if L[j] <= stop:
                x = (stop - COST * abs(stop) - e) / r
                break
            if tgt is not None and H[j] >= tgt:
                x = 2.0
                break
            out_now = False
            if "iBOS" in mode and C[j] < top_lo and (mode != "iBOS after 1R" or best >= 1.0):
                out_now = True
            if mode == "MS only" and flip[j]:
                out_now = True
            if out_now:
                x = (C[j] - COST * abs(C[j]) - e) / r
                break
            if H[j] > top:
                top, top_lo = H[j], L[j]
            best = max(best, (H[j] - e) / r)
            j += 1
        if x is None:
            break
        out.append((T[k], x, j - k))
        free = j
    return out


def stats(xs):
    if not xs:
        return "0 trades"
    w = [x for x in xs if x > 0]
    gl = -sum(x for x in xs if x <= 0)
    return (f"{len(xs):6} trades, win {100 * len(w) / len(xs):3.0f}%, avg win {sum(w) / max(1, len(w)):.2f}R, "
            f"avg {sum(xs) / len(xs):+.3f}R, PF {sum(w) / gl if gl else 99:.2f}")


def main():
    res = {(en, m): [] for en in ("MS", "BOS") for m in EXITS}
    for coin in COINS:
        d = D.load(coin)
        for dd in (d, D.mirror(d)):
            p = prep(dd)
            for en in ("MS", "BOS"):
                for m in EXITS:
                    res[(en, m)] += [(coin,) + t for t in sim(*p, en, m)]
            del p
        del d
        gc.collect()
        print(f"  {coin} done", flush=True)
    for en in ("MS", "BOS"):
        print(f"\n### Entry: 15m {en} (longs + shorts, 9 coins)")
        for m in EXITS:
            t = res[(en, m)]
            hold = sum(x[3] for x in t) / max(1, len(t)) / 4
            print(f"{m:14} all     {stats([x[2] for x in t])}, avg hold {hold:.1f} h")
            print(f"{'':14} 2019-22 {stats([x[2] for x in t if x[1] < CUT])}")
            print(f"{'':14} 2023-on {stats([x[2] for x in t if x[1] >= CUT])}")


if __name__ == "__main__":
    main()
