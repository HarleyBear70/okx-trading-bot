"""
JEFF_SETUP2: Jeff's exact setup, round 2 (JEFF_RULES.md + Jeff's test-case and Look Left answers, Oct 10 2026).
Structure = research/jeff_struct.py (Heart), checked against Jeff's BTC 5m test case. Paper research only.
[NOT JEFF] = Claude's reading of Jeff's words (listed in the results header).

  4H Heart leg = direction (longs only while UP). 15m = working chart.
  Long setup on the 15m:
    1) the 15m leg is DOWN (a pullback, "each pullback is its own small leg")
    2) a sweep inside it: a wick past equal lows (within 0.01%) or past the last 15m swing low, body closing back inside
    3) the sweep low is in the DISCOUNT of the last 15m UP leg (below its 0.5)
    4) MS UP (body close past the down leg's STRONG wick, not undone by the next candle)
  Entry A = limit at the confirming candle's close. Entry B = limit at the retest of the broken STRONG level.
  Stop S1 = beyond the sweep low (= the new STRONG). Stop S2 = LOOK LEFT: beyond the nearest untouched demand level
       (swing low / equal lows, bullish FVG, demand OB, on the 15m) below the sweep low [NOT JEFF: which level].
       Gap past the level 0.05 / 0.15 / 0.30% [NOT JEFF: Jeff said "test a few"].
  Targets: 2R | 3R | -27% extension of the 15m UP leg the pullback retraces (WEAK + 0.27 x leg) |
           LOOK LEFT = the nearest untouched supply level above (swing high / equal highs, bearish FVG, supply OB
           on the 15m; Jeff: look left on the working timeframe), skip if under 2:1 | LOOK LEFT 2:1+ = the first untouched level at least 2R away.
  Levels: FVG (Brad) = gap between candle 1 and candle 3 wicks, alive until completely filled. OB (Brad) = the last
       opposite candle (up to 5 back) before the FVG move, only if that move closed past the last swing (BOS/MS),
       gone once price trades into it [NOT JEFF: "up to 5 back"]. Swing highs/lows gone once price trades past them.
  Cancel an unfilled order: a 15m close below the stop level, or price reaches the target first. One trade per coin,
  any time, no daily limit. Costs: limit entry 0%, stop 0.02% + slippage 0 / 0.02 / 0.05%, target 0%.

  python3 research/jeff_setup2.py
"""
import datetime as dt
import gc
import heapq
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_day as D  # noqa: E402
import pure15 as P  # noqa: E402
from jeff_struct import Heart  # noqa: E402

TAKER, M15, H1, H4 = 0.0002, 900000, 3600000, 14400000
NS, ENTRIES, GAPS, STOPS = (1, 2, 3), ("A", "B"), (0.0005, 0.0015, 0.003), ("S1 sweep", "S2 look left")
TGTS, SLIPS = ("2R", "3R", "-27% ext", "look left nearest", "look left 2:1+"), (0.0, 0.0002, 0.0005)
MAIN, UNSEEN = ["BTC", "ETH", "SOL", "XRP"], ["BNB", "ADA", "DOGE", "LINK", "LTC"]


class Levels:
    """untouched levels on one timeframe. sup = above-price levels (min-heap by the price that kills them),
    dem = below-price levels (max-heap). Items: (kill price, near edge, far edge)."""

    def __init__(self, o, h, l, c, N):
        self.o, self.h, self.l, self.c, self.N = o, h, l, c, N
        self.sup, self.dem = [], []
        self.pl = self.ph = None

    def step(self, k):
        o, h, l, c, N = self.o, self.h, self.l, self.c, self.N
        while self.sup and self.sup[0][0] <= h[k]:
            heapq.heappop(self.sup)
        while self.dem and -self.dem[0][0] >= l[k]:
            heapq.heappop(self.dem)
        j = k - N
        if j >= N:
            if h[j] == max(h[j - N:k + 1]) and h[j] > max(h[j + 1:k + 1]):
                self.ph = h[j]
                if max(h[j + 1:k + 1]) < h[j]:
                    heapq.heappush(self.sup, (h[j] * (1 + 1e-12), h[j], h[j]))
            if l[j] == min(l[j - N:k + 1]) and l[j] < min(l[j + 1:k + 1]):
                self.pl = l[j]
                heapq.heappush(self.dem, (-l[j] * (1 - 1e-12), l[j], l[j]))
        if k >= 2:
            if h[k] < l[k - 2]:  # bearish FVG: supply, alive until price fills it completely (reaches the top)
                heapq.heappush(self.sup, (l[k - 2], h[k], l[k - 2]))
                if self.pl is not None and min(c[k - 1], c[k]) < self.pl:  # the move broke structure -> OB
                    for x in range(k - 2, max(k - 7, -1), -1):
                        if c[x] > o[x]:
                            heapq.heappush(self.sup, (l[x], l[x], h[x]))
                            break
            if l[k] > h[k - 2]:  # bullish FVG: demand
                heapq.heappush(self.dem, (-h[k - 2], l[k], h[k - 2]))
                if self.ph is not None and max(c[k - 1], c[k]) > self.ph:
                    for x in range(k - 2, max(k - 7, -1), -1):
                        if c[x] < o[x]:
                            heapq.heappush(self.dem, (-h[x], h[x], l[x]))
                            break
        if len(self.sup) > 4000:
            self.sup = heapq.nsmallest(2000, self.sup)
        if len(self.dem) > 4000:
            self.dem = heapq.nsmallest(2000, self.dem)


def signals(d, N):
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    tf = {}
    for name, size in (("15m", M15), ("1H", H1), ("4H", H4)):
        tf[name] = D.resample(ts, o, h, l, c, size)
    O, H, L, C, e15 = tf["15m"]
    s15, s4 = Heart(H, L, C, N), Heart(tf["4H"][1], tf["4H"][2], tf["4H"][3], N)
    lv = {"15m": Levels(*tf["15m"][:4], N)}  # Jeff #4 18:48: look left on the working timeframe only
    out, sweep, upleg = [], None, None
    t0 = B.ms(B.START)
    for i in range(len(ts)):
        k = tf["4H"][4][i]
        if k >= 0:
            s4.step(k)
        k = e15[i]
        if k < 0:
            continue
        lv["15m"].step(k)
        was, lo0, hi0, strong0, pl0 = s15.trend, *s15.rng, s15.strong, s15.pl
        ev = s15.step(k)
        if was == 1 and s15.trend == -1:
            upleg, sweep = (lo0, hi0), None  # the up leg this pullback retraces
        if s15.trend == -1:
            if ev == "sweep of equal lows" or (pl0 is not None and L[k] < pl0 and C[k] > pl0):
                sweep = L[k] if sweep is None else min(sweep, L[k])
            continue
        if ev == "MS UP" and was == -1 and sweep is not None and upleg and s4.trend == 1 and ts[i] >= t0:
            ulo, uhi = upleg
            if uhi > ulo and (sweep - ulo) / (uhi - ulo) < 0.5:
                base = min(sweep, s15.strong)
                below = [x for n in lv for x in lv[n].dem if x[1] < base]
                s2 = max(below, key=lambda x: x[1])[2] if below else base  # far edge of the nearest level below
                sup = sorted({x[1] for n in lv for x in lv[n].sup if x[1] > C[k] * 0.98})[:30]
                ext = uhi + 0.27 * (uhi - ulo)  # -27% extension of the 15m UP leg this pullback retraces
                out.append((i, C[k], strong0, base, min(s2, base), ext, tuple(sup)))
        sweep = None if s15.trend == 1 else sweep
    return out, e15, C


def sim(d, sig, e15, C15, entry, gap, stopm, tgtm):
    ts, o, h, l = d["ts"], d["o"], d["h"], d["l"]
    n, free, out = len(ts), 0, []
    for i, ea, eb, s1, s2, ext, sup in sig:
        if i < free:
            continue
        e = ea if entry == "A" else eb
        base = s1 if stopm == "S1 sweep" else s2
        stop = base - gap * abs(base)
        r = e - stop
        if r <= 0:
            continue
        if tgtm == "2R" or tgtm == "3R":
            tgt = e + (2 if tgtm == "2R" else 3) * r
        elif tgtm == "-27% ext":
            tgt = ext
        else:
            above = [x for x in sup if x > e]
            if tgtm == "look left nearest":
                tgt = above[0] if above else None
            else:
                tgt = next((x for x in above if x - e >= 2 * r), None)
        if tgt is None or tgt - e < 2 * r - 1e-12:
            continue
        j, filled = i + 1, None
        while j < n:
            if l[j] <= e:
                filled = j
                break
            if h[j] >= tgt:
                break
            k = e15[j]
            if k >= 0 and C15[k] < base:
                break
            j += 1
        if filled is None:
            free = j
            continue
        ep = min(o[j], e)
        r = ep - stop
        x = None
        while j < n:
            if l[j] <= stop:
                x = ("stop", min(o[j], stop) if j > filled else stop)
                break
            if h[j] >= tgt:
                x = ("tgt", max(o[j], tgt))
                break
            j += 1
        if x is None:
            break
        out.append((ts[filled], ts[j], x[0], x[1], ep, r))
        free = j + 1
    return out


def rr(t, slip):
    _, _, kind, px, e, r = t
    return (px - e - ((TAKER + slip) * abs(px) if kind == "stop" else 0.0)) / r


def main():
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    vers = [(N, en, g, sm, tg) for N in NS for en in ENTRIES for g in GAPS for sm in STOPS for tg in TGTS]
    res = {grp: {v: [] for v in vers} for grp in ("main", "unseen")}
    for coin in MAIN + UNSEEN:
        grp = "main" if coin in MAIN else "unseen"
        d = D.load(coin)
        for side, dd in ((1, d), (-1, D.mirror(d))):
            for N in NS:
                sig, e15, C15 = signals(dd, N)
                print(f"  {coin} {'long' if side == 1 else 'short'} swing {N}: {len(sig)} setups", flush=True)
                for v in vers:
                    if v[0] == N:
                        res[grp][v] += [(side, coin, t) for t in sim(dd, sig, e15, C15, *v[1:])]
                del sig, e15, C15
                gc.collect()
            del dd
        del d
        gc.collect()
    for grp, title in (("main", "BTC ETH SOL XRP"), ("unseen", "NEVER-SEEN BNB ADA DOGE LINK LTC")):
        print(f"\n### JEFF'S SETUP round 2 (heartbeat structure + look left), {title}")
        print("Main columns at the WORST slippage (0.05%); last two = PF at 0% and 0.02% slippage.\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF | PF slip 0 | PF slip 0.02% |\n" + "|---" * 14 + "|")
        for v in vers:
            out = {}
            for s in SLIPS:
                keep, busy = [], {}
                for side, coin, t in sorted(res[grp][v], key=lambda x: x[2][0]):
                    if t[0] > busy.get(coin, -1):
                        keep.append((t[0], t[1], rr(t, s), side))
                        busy[coin] = t[1]
                out[s] = keep
            pf = lambda s: (P.stats([t[2] for t in out[s]]) or {"pf": 0})["pf"]
            name = f"swing {v[0]}, entry {v[1]}, gap {v[2] * 100:.2f}%, {v[3]}, target {v[4]}"
            print(P.row(name, out[SLIPS[-1]], years)[:-2] + f" | {pf(0.0):.2f} | {pf(0.0002):.2f} |", flush=True)


if __name__ == "__main__":
    main()
