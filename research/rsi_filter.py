"""
RSI_FILTER (Jeff, Oct 10 2026): "for a long, RSI is above its yellow average line (and 50). For a short, RSI is under it.
Don't wait for 30/70. Test it as an optional filter, with vs without, and show whether it raises PF or just cuts trades."
  RSI      14, close (Jeff's setting), 5m candles. Yellow line = TradingView's default RSI average: SMA 14 of the RSI.
  Rule     a long may only FILL when the last closed 5m candle had RSI > its average AND RSI > 50; shorts = both below.
           (On upside-down prices RSI becomes 100 - RSI, so the same code checks shorts.)
  Tested on the versions that actually trade: Brad day round 3 (stop below 15m STRONG or below the 5m sweep; no cap,
  no trades 0.40-0.60) and the two Silver Bullet paper bots (A, 3x displacement, sweep stop, swing 5, near / 50% entry).
  Main coins BTC ETH SOL XRP + never-seen BNB ADA DOGE LINK LTC. Same costs as before.

  python3 research/rsi_filter.py
"""
import datetime as dt
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_day as D  # noqa: E402
import pure15 as P  # noqa: E402
import silver_bullet as S  # noqa: E402

MAIN, UNSEEN = ["BTC", "ETH", "SOL", "XRP"], ["BNB", "ADA", "DOGE", "LINK", "LTC"]


def rsi_ok(c, n=14, m=14):
    """bytearray: 1 = the PREVIOUS closed candle had RSI > its SMA(m) and RSI > 50 (long side of these prices)."""
    N = len(c)
    out = bytearray(N)
    ag = al = None
    r = [50.0] * N
    for i in range(1, N):
        ch = c[i] - c[i - 1]
        g, lo = max(ch, 0.0), max(-ch, 0.0)
        if i <= n:
            ag = (ag or 0.0) + g / n
            al = (al or 0.0) + lo / n
        else:
            ag = (ag * (n - 1) + g) / n
            al = (al * (n - 1) + lo) / n
        r[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    run = 0.0
    for i in range(N):
        run += r[i]
        if i >= m:
            run -= r[i - m]
        if i >= m and i + 1 < N:
            out[i + 1] = 1 if (r[i] > run / m and r[i] > 50) else 0
    return out


def main():
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    t0 = B.ms(B.START)
    bd = [("Brad day R3, stop 15m STRONG", "strong"), ("Brad day R3, stop 5m sweep", "sweep")]
    sb = [("Silver Bullet A 3x, near entry", "near"), ("Silver Bullet A 3x, 50% entry", "50%")]
    names = [f"{n}{', RSI filter' if f else ''}" for n, _ in bd + sb for f in (False, True)]
    res = {g: {n: [] for n in names} for g in ("main", "unseen")}
    for cn in MAIN + UNSEEN:
        g = "main" if cn in MAIN else "unseen"
        d = D.load(cn)
        md = D.mirror(d)
        allow = {1: rsi_ok(d["c"]), -1: rsi_ok(md["c"])}
        for name, sm in bd:
            for f in (False, True):
                kw = dict(kz=True, maker=True, rng=True, stopm=sm, cap=None, band=0.10)
                lo = [t + (1, cn) for t in D.run(d, 5, "range", allow=allow[1] if f else None, **kw)]
                sh = [t + (-1, cn) for t in D.run(md, 5, "range", allow=allow[-1] if f else None, **kw)]
                keep, busy = [], -1
                for t in sorted(lo + sh):
                    if t[0] > busy:
                        keep.append(t)
                        busy = t[1]
                res[g][f"{name}{', RSI filter' if f else ''}"] += D.day_limit(keep)
        mins, spans = S.clock(d["ts"])
        sides = [(1, d, S.prep(d, (5,))), (-1, md, S.prep(md, (5,)))]
        for name, en in sb:
            for f in (False, True):
                for a, b in spans:
                    if d["ts"][a] < t0:
                        continue
                    got = []
                    for s, dd, pre in sides:
                        swb, tr = S.day_run(dd, pre, mins, a, b, "A", 5, 3.0, en, "sweep", allow=allow[s] if f else None)
                        if swb is not None:
                            got.append((swb, s, tr))
                    if got:
                        swb, s, tr = min(got)
                        if tr:
                            res[g][f"{name}{', RSI filter' if f else ''}"].append(tr + (s,))
        print(f"  ({cn} done)", flush=True)
        del d, md, sides
        gc.collect()
    for g, title in (("main", "main coins BTC ETH SOL XRP"), ("unseen", "NEVER-SEEN coins BNB ADA DOGE LINK LTC")):
        print(f"\n### RSI filter (RSI 14 above/below its yellow SMA-14 line and 50), {title}\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for n in names:
            print(P.row(n, [t[:4] for t in res[g][n]], years), flush=True)


if __name__ == "__main__":
    main()
