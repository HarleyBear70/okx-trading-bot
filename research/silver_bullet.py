"""
SILVER_BULLET: Brad's "ICT Silver Bullet" video (research/transcripts/The ICT Silver Bullet Strategy...), as Jeff
set it up on issue #4, Oct 10 2026. Every rule and its tag: Claude Files/From Claude/SILVER_BULLET_rules_tagged.txt.
Jeff approved the run and asked to TEST the open options instead of picking one. Long rules; shorts = mirror.

  Version A "9 AM candle": at 10:00 AM ET mark the 9:00-10:00 AM ET 1H candle's low. 10-11 AM ET: a 5m wick below
            it = the sweep (long setup). Shift, FVG and fill must all happen by 12:00 PM ET.
  Version B "session": London = 2-5 AM ET, NY = 7-10 AM ET (Jeff's killzones). The sweep must take out the London
            low during NY, and the order must fill during NY (by 10:00 AM ET).
  Both      the level must still be untouched when the sweep window opens [small guess: else no setup that side].
            Price sweeps both sides = the first sweep decides the side for the day; max 1 trade per coin per day.
  Shift     after the sweep, a 5m candle BODY closes above the last 5m swing high body (Jeff). Swing 1/3/5 (test).
  Displace  a bullish 5m candle between the sweep low and up to 3 candles after the shift with a body >= X times the
            average body of the 20 candles before it, that leaves an FVG (candle before's high < candle after's low).
            X = 1.5 / 2 / 3 (test). No FVG = no trade. Newest one is used.
  Entry     limit at the FVG's near edge (top) or its 50% line (test). Maker 0%.
  Stop      below the sweep low, or below the 15m STRONG low (Jeff's BOS/iBOS rule, swing 5 on 15m) (test), +0.05%.
            Skip if more than 1.35% away (Jeff's max stop, rule S2).
  Target    the nearest untouched 5m swing high above the entry (opposite liquidity). Under 2:1 = skip.
  Exit      stop (0.02% taker + 0.02% slippage), target (0%), or close at 4:00 PM ET (taker + slippage).
  Coins     main BTC ETH SOL XRP; never-seen BNB ADA DOGE LINK LTC. Binance 5m, 2019 - Sep 30 2026.

  python3 research/silver_bullet.py
"""
import array
import datetime as dt
import gc
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_day as D  # noqa: E402
import pure15 as P  # noqa: E402

NY = ZoneInfo("America/New_York")
TAKER, CUSH, MAXSTOP, MINRR = 0.0004, 0.0005, 0.0135, 2.0
MAIN, UNSEEN = ["BTC", "ETH", "SOL", "XRP"], ["BNB", "ADA", "DOGE", "LINK", "LTC"]
# (level window, sweep window, last fill) in minutes after midnight ET
VER = {"A": ((540, 600), (600, 660), 720), "B": ((120, 300), (420, 600), 600)}
CLOSE = 960


def clock(ts):
    """minutes after midnight ET and ET day number for every candle."""
    cache, mins, days = {}, array.array("h"), array.array("l")
    for t in ts:
        hr = t // 3600000
        off = cache.get(hr)
        if off is None:
            off = cache[hr] = int(dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).astimezone(NY)
                                  .utcoffset().total_seconds() * 1000)
        e = t + off
        mins.append((e // 60000) % 1440)
        days.append(e // 86400000)
    spans, a = [], 0
    for i in range(1, len(ts) + 1):
        if i == len(ts) or days[i] != days[a]:
            spans.append((a, i))
            a = i
    return mins, spans


def prep(d, Ns):
    """per side: average body, 15m STRONG low, and per swing size: body-break-up candles and swing highs."""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    n = len(ts)
    avg, run = array.array("d", [0.0] * n), 0.0
    body = [abs(c[i] - o[i]) for i in range(n)]
    for i in range(n):
        if i >= 20:
            avg[i] = run / 20
            run -= body[i - 20]
        run += body[i]
    O15, H15, L15, C15, end15 = D.resample(ts, o, h, l, c, D.M15)
    s15 = D.RangeStruct(O15, H15, L15, C15, 5)
    strong, cur = array.array("d", [float("nan")] * n), float("nan")
    for i in range(n):
        k = end15[i]
        if k >= 0:
            s15.step(k)
            cur = s15.rlo if s15.rlo is not None and s15.trend == 1 else float("nan")
        strong[i] = cur
    per = {}
    for N in Ns:
        s5 = D.Struct(o, h, l, c, N)
        brk, sh = bytearray(n), bytearray(n)
        for i in range(n):
            ev = s5.step(i)
            if ev and ev[0] == "bull":
                brk[i] = 1
            j = i - N
            if j >= N and h[j] == max(h[j - N:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                sh[j] = 1
        per[N] = (brk, sh)
    return {"avg": avg, "strong": strong, "per": per}


def target(h, sh, N, cur, lvl):
    """nearest swing high above lvl that is confirmed by candle cur and not touched since."""
    j0 = cur - N
    runmax = max(h[j0 + 1:cur + 1])
    best = None
    for j in range(j0, max(0, cur - 576), -1):
        if sh[j] and h[j] > runmax and h[j] > lvl:
            best = h[j] if best is None else min(best, h[j])
        runmax = max(runmax, h[j])
    return best


def day_run(d, pre, mins, a, b, ver, N, X, entry, stopm, taker=TAKER, allow=None):
    """one ET day, long side. Returns (sweep candle index or None, trade (entry ts, exit ts, R) or None)."""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    (la, lb), (sa, sb), last = VER[ver]
    brk, sh = pre["per"][N]
    avg, strong = pre["avg"], pre["strong"]
    lev = None
    i = a
    while i < b and mins[i] < sa:
        if la <= mins[i] < lb:
            lev = l[i] if lev is None else min(lev, l[i])
        elif mins[i] >= lb and lev is not None and l[i] < lev:
            return None, None  # already taken before the window opened
        i += 1
    if lev is None:
        return None, None
    swb = None
    sl = slb = None
    shift = None
    pend = pos = None
    while i < b:
        m = mins[i]
        if pos:
            px = f = None
            if m >= CLOSE:
                px, f = o[i], taker * abs(o[i])
            elif l[i] <= pos["stop"]:
                px = min(pos["stop"], o[i])
                f = taker * abs(px)
            elif h[i] >= pos["tgt"]:
                px, f = max(pos["tgt"], o[i]), 0.0
            if px is not None:
                return swb, (pos["ts"], ts[i], (px - pos["e"] - f) / pos["r"])
            i += 1
            continue
        if m >= last and not pos:
            return swb, None
        if pend:
            if l[i] <= pend["e"] and (allow is None or allow[i]):
                e = min(o[i], pend["e"])
                pos = dict(pend, e=e, ts=ts[i], r=e - pend["stop"])
                if l[i] <= pos["stop"]:
                    return swb, (ts[i], ts[i], (pos["stop"] - e - taker * abs(pos["stop"])) / pos["r"])
            elif h[i] >= pend["tgt"]:
                return swb, None
            i += 1
            continue
        if swb is None:
            if m >= sb:
                return None, None
            if l[i] < lev:
                swb, sl, slb = i, l[i], i
            i += 1
            continue
        if shift is None:
            if l[i] < sl:
                sl, slb = l[i], i
            if brk[i] and i > swb:
                shift = i
        if shift is not None:
            if i > shift + 3:
                return swb, None
            k = None
            for kk in range(i - 1, slb, -1):
                if (c[kk] > o[kk] and c[kk] - o[kk] >= X * avg[kk] and l[kk + 1] > h[kk - 1]):
                    k = kk
                    break
            if k is not None:
                top, bot = l[k + 1], h[k - 1]
                lvl = top if entry == "near" else (top + bot) / 2
                base = sl if stopm == "sweep" else strong[i]
                if base != base:  # no 15m STRONG low (15m not bullish)
                    return swb, None
                stop = base - CUSH * abs(base)
                r = lvl - stop
                if not (0 < r <= MAXSTOP * abs(lvl)) or lvl >= c[i]:
                    return swb, None
                tg = target(h, sh, N, i, lvl)
                if tg is None or tg - lvl < MINRR * r:
                    return swb, None
                pend = {"e": lvl, "stop": stop, "tgt": tg}
        i += 1
    if pos:  # data ended mid-day
        return swb, (pos["ts"], ts[b - 1], (c[b - 1] - pos["e"] - taker * abs(c[b - 1])) / pos["r"])
    return swb, None


def main():
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    t0 = B.ms(B.START)
    Ns, Xs = (1, 3, 5), (1.5, 2.0, 3.0)
    vers = [(f"{v}, swing {N}, displacement {X}x, {en} entry, stop {sm}", v, N, X, en, sm)
            for v in ("A", "B") for N in Ns for X in Xs for en in ("near", "50%") for sm in ("sweep", "strong")]
    res = {g: {v[0]: [] for v in vers} for g in ("main", "unseen")}
    for cn in MAIN + UNSEEN:
        grp = "main" if cn in MAIN else "unseen"
        d = D.load(cn)
        mins, spans = clock(d["ts"])
        sides = []
        for s, dd in ((1, d), (-1, D.mirror(d))):
            sides.append((s, dd, prep(dd, Ns)))
            gc.collect()
        for name, v, N, X, en, sm in vers:
            for a, b in spans:
                if d["ts"][a] < t0:
                    continue
                got = []
                for s, dd, pre in sides:
                    swb, tr = day_run(dd, pre, mins, a, b, v, N, X, en, sm)
                    if swb is not None:
                        got.append((swb, s, tr))
                if got:
                    swb, s, tr = min(got)  # the first sweep decides the side
                    if tr:
                        res[grp][name].append(tr + (s,))
        print(f"  ({cn} done)", flush=True)
        del d, sides
        gc.collect()
    for grp, title in (("main", "main coins BTC ETH SOL XRP"), ("unseen", "NEVER-SEEN coins BNB ADA DOGE LINK LTC")):
        print(f"\n### Silver Bullet, {title}, Binance.US costs (maker entry)\n")
        print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
              "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        for v in vers:
            print(P.row(v[0], res[grp][v[0]], years), flush=True)


if __name__ == "__main__":
    main()
