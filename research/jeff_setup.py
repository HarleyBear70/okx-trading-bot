"""
JEFF_SETUP: ONE test of Jeff's exact setup, rules from research/JEFF_RULES.md v3 (Jeff's answers on issue #4, Oct 10 2026).
Paper research only. Lines marked [NOT JEFF] are the only places Claude had to turn Jeff's words into code.

  Structure  (every timeframe, swing = N candles each side, N = 1 / 2 / 3, Jeff marks by eye -> test all three)
             Up leg: WEAK = the newest high. Once a pullback starts (a swing low forms after WEAK), WEAK is fixed.
             BOS  = a candle BODY closes past WEAK -> STRONG = the lowest low that led to it, WEAK = the new high.
             MS   = a candle BODY closes past STRONG's WICK -> the leg flips (Jeff #4 11:33). A wick past = sweep only.
             Down leg = mirror.  Fib 1 = STRONG, 0 = WEAK, 0.5 = middle.
  4H         gives the direction: longs only while the 4H leg is UP, shorts only while it is DOWN.
  15m        the working chart. Long setup:
               1) price in the DISCOUNT of the 15m leg (below its 0.5)
               2) sweep = a 15m wick below the last 15m swing low with the body closing back above it (the fuel grab)
               3) small MS = a 15m BODY closes above the last 15m swing high
             Entry A = limit at that confirming candle's close.  Entry B = limit at the retest of the level it broke.
  Stop       below the sweep low (and below the 15m STRONG wick when the 15m leg is up), never right at the wick:
             gap 0.05% / 0.15% / 0.30% [NOT JEFF: Jeff said "test a few gap sizes", the three sizes are Claude's].
  Target     -27% extension of the 15m leg (WEAK + 0.27 x leg), only if it gives 2:1 or better,
             vs fixed 2R vs fixed 3R. Set and forget (stall management = optional test, not run here).
  Cancel     an unfilled order: a 15m body close below the stop level (MS against it) or price reaches the target first.
  Trades     one at a time per coin, no daily limit, no killzones, any time.
  Costs      limit entries 0% (maker), stop-outs 0.02% taker + slippage 0% / 0.02% / 0.05%, targets 0%.
  Fills      orders and exits are checked on the 5m candles inside each 15m candle; stop + target in the same 5m candle
             = the stop [NOT JEFF: the safe way].
  Coins      BTC ETH SOL XRP; never-seen BNB ADA DOGE LINK LTC. Binance 5m archive 2019 - Sep 30 2026.

  python3 research/jeff_setup.py [with|against|any] [hold]   (hold = Brad's 'close and hold': wait for the next 15m close)
             4H filter: with = Jeff rule 1 (default), against = only setups against the 4H leg,
             any = no 4H filter (Jeff rule 1b, Oct 15: he trades both ways no matter the 4H)
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

TAKER, M15, H4 = 0.0002, 900000, 14400000
NS, ENTRIES, GAPS, TGTS, SLIPS = (1, 2, 3), ("A", "B"), (0.0005, 0.0015, 0.003), ("-27% ext", "2R", "3R"), (0.0, 0.0002, 0.0005)
MODE = sys.argv[1] if len(sys.argv) > 1 else "with"
HOLD = len(sys.argv) > 2 and sys.argv[2] == "hold"  # Brad: the turn candle's close must HOLD (next 15m also closes past)
MAIN, UNSEEN = ["BTC", "ETH", "SOL", "XRP"], ["BNB", "ADA", "DOGE", "LINK", "LTC"]


class Leg:
    """Jeff's structure on one timeframe; step(k) on the close of candle k. No look-ahead."""

    def __init__(self, h, l, c, N):
        self.h, self.l, self.c, self.N = h, l, c, N
        self.trend, self.strong, self.weak, self.sb, self.wb, self.frozen = 0, None, None, 0, 0, False
        self.pl = self.ph = None  # last swing low / high (wicks) and where
        self.plb = self.phb = -1

    @property
    def rng(self):
        if self.trend == 1:
            return self.strong, self.weak
        if self.trend == -1:
            return self.weak, self.strong
        return None, None

    def step(self, k):
        h, l, c, N = self.h, self.l, self.c, self.N
        j = k - N
        if j >= N:
            if l[j] == min(l[j - N:k + 1]) and l[j] < min(l[j + 1:k + 1]):
                self.pl, self.plb = l[j], j
            if h[j] == max(h[j - N:k + 1]) and h[j] > max(h[j + 1:k + 1]):
                self.ph, self.phb = h[j], j
        if self.trend == 0:
            if self.ph is not None and c[k] > self.ph:
                sb = min(range(self.phb, k + 1), key=lambda x: l[x])
                self.trend, self.strong, self.sb, self.weak, self.wb, self.frozen = 1, l[sb], sb, h[k], k, False
            elif self.pl is not None and c[k] < self.pl:
                sb = max(range(self.plb, k + 1), key=lambda x: h[x])
                self.trend, self.strong, self.sb, self.weak, self.wb, self.frozen = -1, h[sb], sb, l[k], k, False
            return
        if self.trend == 1:
            if c[k] < self.strong:  # MS: body close past STRONG's wick
                sb = max(range(self.sb, k + 1), key=lambda x: h[x])
                self.trend, self.strong, self.sb, self.weak, self.wb, self.frozen = -1, h[sb], sb, l[k], k, False
            elif self.frozen and c[k] > self.weak:  # BOS
                sb = min(range(self.wb, k + 1), key=lambda x: l[x])
                self.strong, self.sb, self.weak, self.wb, self.frozen = l[sb], sb, h[k], k, False
            else:
                if not self.frozen and h[k] >= self.weak:
                    self.weak, self.wb = h[k], k
                if self.plb > self.wb:
                    self.frozen = True
        else:
            if c[k] > self.strong:
                sb = min(range(self.sb, k + 1), key=lambda x: l[x])
                self.trend, self.strong, self.sb, self.weak, self.wb, self.frozen = 1, l[sb], sb, h[k], k, False
            elif self.frozen and c[k] < self.weak:
                sb = max(range(self.wb, k + 1), key=lambda x: h[x])
                self.strong, self.sb, self.weak, self.wb, self.frozen = h[sb], sb, l[k], k, False
            else:
                if not self.frozen and l[k] <= self.weak:
                    self.weak, self.wb = l[k], k
                if self.phb > self.wb:
                    self.frozen = True


def signals(d, N):
    """long setups (run on mirrored prices for shorts): [(5m index of the confirming close, entry A, entry B,
    stop level before the gap, -27% target)]"""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    O, H, L, C, e15 = D.resample(ts, o, h, l, c, M15)
    _, H4_, L4, C4, e4 = D.resample(ts, o, h, l, c, H4)
    s15, s4 = Leg(H, L, C, N), Leg(H4_, L4, C4, N)
    out, armed, pend = [], None, None
    for i in range(len(ts)):
        k = e15[i]
        if k >= 0:
            lo, hi = s15.rng  # the 15m leg as it stood before this candle
            up15, strong15 = s15.trend == 1, s15.strong
            pl, ph = s15.pl, s15.ph
            s15.step(k)
            ok4 = {"with": s4.trend == 1, "against": s4.trend == -1, "any": True}[MODE]
            if not ok4 or lo is None or hi <= lo:
                armed = pend = None
            elif armed is None:
                if pl is not None and L[k] < pl and C[k] > pl and (L[k] - lo) / (hi - lo) < 0.5:
                    armed = L[k]
            elif C[k] < armed:
                armed = pend = None  # body closed below the pool: no fuel grab, it broke down
            elif L[k] < armed:
                armed, pend = L[k], None  # deeper sweep, body still back above
            elif pend is not None:
                if C[k] > pend[1]:  # held: enter on this close
                    if ts[i] >= B.ms(B.START):
                        out.append((i, C[k], pend[1], pend[0], pend[2]))
                    armed = None
                pend = None  # not held = undone (orange); stay armed for the next try
            elif ph is not None and C[k] > ph:
                base = min(armed, strong15) if up15 else armed
                if HOLD:
                    pend = (base, ph, hi + 0.27 * (hi - lo))
                else:
                    if ts[i] >= B.ms(B.START):
                        out.append((i, C[k], ph, base, hi + 0.27 * (hi - lo)))
                    armed = None
        k = e4[i]
        if k >= 0:
            s4.step(k)
    return out, e15, C


def sim(d, sig, e15, C15, entry, gap, tgtm):
    """walk the 5m candles for each signal while the coin is free. [(entry ts, exit ts, kind, exit px, e, r)]"""
    ts, o, h, l = d["ts"], d["o"], d["h"], d["l"]
    n, free, out = len(ts), 0, []
    for i, ea, eb, base, ext in sig:
        if i < free:
            continue
        e = ea if entry == "A" else eb
        stop = base - gap * abs(base)
        r = e - stop
        if r <= 0:
            continue
        tgt = ext if tgtm == "-27% ext" else e + (2 if tgtm == "2R" else 3) * r
        if tgt - e < 2 * r:
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
    cost = (TAKER + slip) * abs(px) if kind == "stop" else 0.0
    return (px - e - cost) / r


def main():
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    vers = [(N, en, g, tg) for N in NS for en in ENTRIES for g in GAPS for tg in TGTS]
    res = {grp: {v: [] for v in vers} for grp in ("main", "unseen")}
    for coin in MAIN + UNSEEN:
        grp = "main" if coin in MAIN else "unseen"
        d = D.load(coin)
        for side, dd in ((1, d), (-1, D.mirror(d))):
            for N in NS:
                sig, e15, C15 = signals(dd, N)
                for v in vers:
                    if v[0] == N:
                        res[grp][v] += [(side, coin, t) for t in sim(dd, sig, e15, C15, v[1], v[2], v[3])]
                del sig, e15, C15
                gc.collect()
            del dd
        print(f"  ({coin} done)", flush=True)
        del d
        gc.collect()
    for grp, title in (("main", "BTC ETH SOL XRP"), ("unseen", "NEVER-SEEN BNB ADA DOGE LINK LTC")):
        print(f"\n### JEFF'S SETUP (4H filter: {MODE}{', HOLD: 2nd close' if HOLD else ', 1st close'}), 100% Jeff's rules except the gap sizes + same-candle rule, {title}")
        print("Main columns at the WORST slippage (0.05%); last two columns = PF at 0% and 0.02% slippage.\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF | PF slip 0 | PF slip 0.02% |\n" + "|---" * 14 + "|")
        for v in vers:
            out = {}
            for s in SLIPS:
                keep, busy = {}, {}
                for side, coin, t in sorted(res[grp][v], key=lambda x: x[2][0]):  # one trade per coin
                    if t[0] > busy.get(coin, -1):
                        keep.setdefault(s, []).append((t[0], t[1], rr(t, s), side))
                        busy[coin] = t[1]
                out[s] = keep.get(s, [])
            pf = lambda s: (P.stats([t[2] for t in out[s]]) or {"pf": 0})["pf"]
            name = f"swing {v[0]}, entry {v[1]}, gap {v[2] * 100:.2f}%, target {v[3]}"
            print(P.row(name, out[SLIPS[-1]], years)[:-2] + f" | {pf(0.0):.2f} | {pf(0.0002):.2f} |", flush=True)


if __name__ == "__main__":
    main()
