"""
CLAUDE_HB_BACKTEST: the same rules as tools/claude_hb_trader.py (Claude's own paper trader), replayed on history.
Rules are CLAUDE'S, not Jeff's. Paper research only.

  Bias    = 4H, 1H and 15m heartbeat legs (research/jeff_struct.py, swing 1) all point the same way.
  Trigger = a 5m MS in the bias direction. Entry = limit at the 50% of the new 5m leg ("50%") or the MS close ("close").
  Stop    = 5m MUST HOLD + 0.05%. Target 2R or 3R. Cancel: target first, opposite 5m MS, bias breaks, 2 h unfilled.
  Costs   = Binance.US: limit entry/target 0%, a stop pays 0.02% taker + 0.02% slippage ("close" entry pays 0.02% too).
  Learning splits: entry in the 15m premium vs discount, 1D leg agrees vs disagrees.

  python3 research/claude_hb_backtest.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brad_day as D  # noqa: E402
from jeff_struct import Heart  # noqa: E402

GAP, STOP_COST, MAX_WAIT = 0.0005, 0.0004, 24
CUT = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "LINK", "LTC"]
VERS = [(e, t) for e in ("50%", "close") for t in (2.0, 3.0)]


def signals(d):
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    n = len(ts)
    tf, hs = {}, {}
    for name, size in (("1D", 86400000), ("4H", 14400000), ("1H", 3600000), ("15m", 900000)):
        tf[name] = D.resample(ts, o, h, l, c, size)
        hs[name] = Heart(tf[name][1], tf[name][2], tf[name][3], 1)
    s5 = Heart(h, l, c, 1)
    bias = bytearray(n)  # 1 = all up, 2 = all down, 0 = mixed
    sigs = []
    for i in range(n):
        for name in hs:
            k = tf[name][4][i]
            if k >= 0:
                hs[name].step(k)
        ev = s5.step(i)
        b = {hs[x].trend for x in ("4H", "1H", "15m")}
        bias[i] = 1 if b == {1} else 2 if b == {-1} else 0
        if ev in ("MS UP", "MS DOWN"):
            want = 1 if ev == "MS UP" else 2
            lo, hi = hs["15m"].rng
            entry = (s5.strong + s5.weak) / 2
            z = "" if lo is None else ("premium" if entry > (lo + hi) / 2 else "discount")
            day = hs["1D"].trend
            sigs.append((i, want, s5.strong, s5.weak, c[i], z, (day == 1) == (want == 1) and day != 0))
    return sigs, bias


def sim(d, sigs, bias, entry_mode, tgt_r):
    ts, h, l = d["ts"], d["h"], d["l"]
    n, out, free = len(ts), [], 0
    for idx, (i, want, strong, weak, close, z, day_ok) in enumerate(sigs):
        if i < free or bias[i] != want:
            continue
        up = want == 1
        e = (strong + weak) / 2 if entry_mode == "50%" else close
        stop = strong * (1 - GAP) if up else strong * (1 + GAP)
        r = abs(e - stop)
        if r <= 0 or (up and e <= stop) or (not up and e >= stop):
            continue
        tgt = e + (tgt_r if up else -tgt_r) * r
        nxt = sigs[idx + 1][0] if idx + 1 < len(sigs) and sigs[idx + 1][1] != want else n
        j, filled = i + 1, None
        if entry_mode == "close":
            filled = i + 1
        while filled is None and j < n:
            if (l[j] <= e) if up else (h[j] >= e):
                filled = j
                break
            if ((h[j] >= tgt) if up else (l[j] <= tgt)) or bias[j] != want or j >= nxt or j - i > MAX_WAIT:
                break
            j += 1
        if filled is None:
            free = j
            continue
        j, res = filled, None
        while j < n:
            if (l[j] <= stop) if up else (h[j] >= stop):
                res = -1 - STOP_COST * stop / r
                break
            if (h[j] >= tgt) if up else (l[j] <= tgt):
                res = tgt_r
                break
            j += 1
        if res is None:
            break
        if entry_mode == "close":
            res -= 0.0002 * e / r
        out.append((ts[filled], res, up, z, day_ok))
        free = j + 1
    return out


def stats(rs):
    if not rs:
        return "0 trades"
    w = [x for x in rs if x > 0]
    gl = -sum(x for x in rs if x <= 0)
    pf = sum(w) / gl if gl else float("inf")
    return f"{len(rs)} trades, win {100 * len(w) / len(rs):.0f}%, avg {sum(rs) / len(rs):+.3f}R, PF {pf:.2f}"


def main():
    res = {v: [] for v in VERS}
    for coin in COINS:
        try:
            d = D.load(coin)
        except OSError:
            print(f"  {coin}: no data")
            continue
        sigs, bias = signals(d)
        for v in VERS:
            res[v] += [(coin,) + t for t in sim(d, sigs, bias, *v)]
        print(f"  {coin}: {len(sigs)} 5m shifts", flush=True)
        del d, sigs, bias
        gc.collect()
    for v, tr in res.items():
        print(f"\n### entry {v[0]}, target {v[1]:.0f}R  (Claude's rules, not Jeff's)")
        print("all          ", stats([t[2] for t in tr]))
        print("2019-22      ", stats([t[2] for t in tr if t[1] < CUT]))
        print("2023-now     ", stats([t[2] for t in tr if t[1] >= CUT]))
        print("longs        ", stats([t[2] for t in tr if t[3]]))
        print("shorts       ", stats([t[2] for t in tr if not t[3]]))
        print("15m discount ", stats([t[2] for t in tr if (t[4] == "discount") == t[3]]), "  <- long in discount / short in premium")
        print("15m wrong zn ", stats([t[2] for t in tr if (t[4] == "discount") != t[3]]))
        print("1D agrees    ", stats([t[2] for t in tr if t[5]]))
        print("1D disagrees ", stats([t[2] for t in tr if not t[5]]))
        for coin in COINS:
            x = [t[2] for t in tr if t[0] == coin]
            if x:
                print(f"  {coin:5}", stats(x))


if __name__ == "__main__":
    main()
