"""
BRAD_DAY: Brad Goh's DAY TRADE top-down method (Market Mechanics Ep 11, entry from Ep 18), as Jeff asked Oct 10 2026:
"day trade first, test both zones. Swing size: test 1, 3 and 5 on every timeframe."
4H = the story, 15m = the map (bias + zones), 5m = the entry. All three are built from the same 5m candles.
Long rules below; shorts are the exact mirror (run on upside-down prices). One trade per coin at a time.

  Swings      N candles each side (N = 1, 3, 5, the same on 4H, 15m and 5m).
  Breaks      a candle BODY closes past the last swing candle's BODY (Jeff: body to body). Wicks don't count.
              Close above = bullish break (market shift if it was bearish, BOS if already bullish).
  Strong/weak on each break: strong low = the lowest low between the broken swing high and the break
              (the low that led to the BOS); weak high = the highest high since. Fib 1 = strong, 0 = weak, 0.5 = middle.
  4H          longs only while price is in the 4H DISCOUNT (below the 4H 0.5). Brad's EURUSD trade in Ep 11 sold
              in the 4H premium against a 4H uptrend, so the 4H trend itself is not a filter [CHOICE 1].
  15m         longs only while the 15m is bullish. Demand zone = the candle at the strong low of each bullish
              BOS/market shift (Brad: zones that caused a BOS).
                pivot  = that one candle, high to low.
                range  = that candle plus the N candles before it (the base), highest high to lowest low [CHOICE 2].
              The zone must sit in the 15m DISCOUNT (zone top at or below the 15m 0.5) when price reaches it.
              A zone is gone when a 15m candle closes below it, or the 15m turns bearish. One try per zone.
              Price already inside a zone and a deeper zone gets touched = switch to the deeper one (Brad: extreme wins).
  5m entry    only after price touches the 15m zone. Brad: "No sweep, no entry."
              1) sweep: a 5m wick below the last 5m swing low.
              2) market shift: a 5m body closes above the last 5m swing high body.
              3) limit order at the 5m zone that caused that shift (same pivot/range rule, top edge for longs).
                 Price never comes back = no trade. Order cancelled if price reaches the target first.
              If price takes out the sweep low before the fill, that shift was fake: wait for a new shift (Ep 18).
  Stop        below the sweep low with Jeff's 0.05% cushion. Skip if more than 1.35% away (Jeff's max stop).
  Target      the nearest untouched 15m swing high (minus the cushion) that gives 2:1 or better (Jeff); none = skip.
  Management  set and forget (Brad Ep 17): full stop or full target.
  Costs       Binance.US, Jeff's numbers: 0.02% taker + 0.02% slippage on entries and stops, 0 on targets.
  Coins       BTC ETH SOL XRP. Binance 5m archive 2019 to Sep 30 2026. Halves 2019-22 / 2023-now.
  Not used    killzones/sessions, news, daily loss limit (not in Ep 11's steps).

  python3 research/brad_day.py v4         (Oct 10: Jeff's answers to the 43 rules, 24 versions)
  python3 research/brad_day.py kz         (Oct 10: killzones + maker entry, swing 5 and 1, range zones)
  python3 research/brad_day.py            (BTC ETH SOL XRP, swing 1/3/5 x pivot/range, with and without fees)
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
import pure15 as P  # noqa: E402  (stats + table row)

TAKER, CUSH, MAXSTOP, MINRR = 0.0004, 0.0005, 0.0135, 2.0
COINS = ["BTC", "ETH", "SOL", "XRP"]
M15, H4 = 900000, 14400000
NY = ZoneInfo("America/New_York")


def load(coin):
    """5m candles from research/.cache/bin (made from m5.py's cache)."""
    out = {}
    for k in ("ts", "o", "h", "l", "c"):
        a = array.array("q" if k == "ts" else "d")
        p = os.path.join(HERE, ".cache", "bin", f"M5_{coin}_{k}.bin")
        with open(p, "rb") as f:
            a.frombytes(f.read())
        out[k] = a
    return out


def resample(ts, o, h, l, c, size):
    """bigger candles from 5m ones. ends[i] = index of the big candle that closes on 5m candle i, else -1."""
    O, Hh, L, C, ends = array.array("d"), array.array("d"), array.array("d"), array.array("d"), array.array("l")
    n = len(ts)
    for i in range(n):
        b = ts[i] // size
        if i == 0 or ts[i - 1] // size != b:
            O.append(o[i]); Hh.append(h[i]); L.append(l[i]); C.append(c[i])
        else:
            if h[i] > Hh[-1]:
                Hh[-1] = h[i]
            if l[i] < L[-1]:
                L[-1] = l[i]
            C[-1] = c[i]
        ends.append(len(C) - 1 if i == n - 1 or ts[i + 1] // size != b else -1)
    return O, Hh, L, C, ends


class Struct:
    """market structure on one timeframe, body-to-body breaks, swings of N candles each side, no look-ahead."""

    def __init__(self, o, h, l, c, N):
        self.o, self.h, self.l, self.c, self.N = o, h, l, c, N
        self.trend = 0
        self.ksh = self.ksl = None  # body levels a close must pass
        self.ish = self.isl = 0
        self.hi_hit = self.lo_hit = True
        self.rlo = self.rhi = None  # strong/weak range (fib 1 / 0)
        self.lsl = None  # last swing low (wick), for sweeps
        self.highs = []  # untouched swing highs (wick), for targets

    def mid(self):
        return None if self.rlo is None else (self.rlo + self.rhi) / 2

    def step(self, i):
        """candle i just closed. Returns ("bull"/"bear", origin candle index) or None."""
        o, h, l, c, N = self.o, self.h, self.l, self.c, self.N
        ev = None
        if self.ksh is not None and not self.hi_hit and c[i] > self.ksh:
            self.hi_hit, self.trend = True, 1
            org = min(range(self.ish, i + 1), key=lambda k: l[k])
            self.rlo, self.rhi = l[org], max(h[org:i + 1])
            ev = ("bull", org)
        elif self.ksl is not None and not self.lo_hit and c[i] < self.ksl:
            self.lo_hit, self.trend = True, -1
            org = max(range(self.isl, i + 1), key=lambda k: h[k])
            self.rlo, self.rhi = min(l[org:i + 1]), h[org]
            ev = ("bear", org)
        elif self.trend == 1:
            self.rhi = max(self.rhi, h[i])
        elif self.trend == -1:
            self.rlo = min(self.rlo, l[i])
        j = i - N
        if j >= N:
            if h[j] == max(h[j - N:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                self.highs.append(h[j])
            if l[j] == min(l[j - N:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                self.lsl = l[j]
            bh = [max(o[k], c[k]) for k in range(j - N, i + 1)]
            bl = [min(o[k], c[k]) for k in range(j - N, i + 1)]
            if bh[N] == max(bh) and bh[N] > max(bh[N + 1:]):
                self.ksh, self.ish, self.hi_hit = bh[N], j, False
            if bl[N] == min(bl) and bl[N] < min(bl[N + 1:]):
                self.ksl, self.isl, self.lo_hit = bl[N], j, False
        if self.highs and h[i] >= min(self.highs):
            self.highs = [v for v in self.highs if v > h[i]][-200:]
        return ev


class RangeStruct(Struct):
    """Jeff's rule #7 (Oct 10): only a BOS resets STRONG/WEAK.
    Uptrend: BOS = a candle BODY closes above the last HH (the body of the newest confirmed swing high at the top of
    the range). New WEAK = the newest high, new STRONG = the lowest low between that HH and the break.
    Market shift = a BODY closes below the STRONG candle's body; then STRONG = the highest high that led to the
    break and WEAK = the newest low. Any other break inside the range = iBOS, warning only, nothing resets.
    Downtrend is the mirror. Before the first break it starts like Struct (first body break of a swing)."""

    def __init__(self, *a):
        super().__init__(*a)
        self.sb = None  # STRONG candle's body edge a close must pass for a market shift
        self.si = 0  # STRONG candle index
        self.hh = None  # body level of the last HH (uptrend) / LL (downtrend) a close must pass for a BOS
        self.hhi = 0

    def _set(self, trend, org, i):
        o, h, l, c = self.o, self.h, self.l, self.c
        self.trend, self.si, self.hh = trend, org, None
        if trend == 1:
            self.rlo, self.rhi, self.sb = l[org], max(h[org:i + 1]), min(o[org], c[org])
        else:
            self.rhi, self.rlo, self.sb = h[org], min(l[org:i + 1]), max(o[org], c[org])

    def step(self, i):
        if self.trend == 0:
            ev = super().step(i)
            if ev:
                self._set(1 if ev[0] == "bull" else -1, ev[1], i)
            return ev
        o, h, l, c, N = self.o, self.h, self.l, self.c, self.N
        ev = None
        if self.trend == 1:
            if c[i] < self.sb:
                org = max(range(self.si, i + 1), key=lambda k: h[k])
                self._set(-1, org, i)
                ev = ("bear", org)
            elif self.hh is not None and c[i] > self.hh:
                org = min(range(self.hhi, i + 1), key=lambda k: l[k])
                self._set(1, org, i)
                ev = ("bull", org)
            else:
                self.rhi = max(self.rhi, h[i])
        else:
            if c[i] > self.sb:
                org = min(range(self.si, i + 1), key=lambda k: l[k])
                self._set(1, org, i)
                ev = ("bull", org)
            elif self.hh is not None and c[i] < self.hh:
                org = max(range(self.hhi, i + 1), key=lambda k: h[k])
                self._set(-1, org, i)
                ev = ("bear", org)
            else:
                self.rlo = min(self.rlo, l[i])
        j = i - N
        if j >= N and j > self.si:
            if self.trend == 1 and h[j] == self.rhi and h[j] == max(h[j - N:i + 1]) and h[j] > max(h[j + 1:i + 1]):
                self.hh, self.hhi = max(o[j], c[j]), j  # the HH is confirmed once price pulls back from it
            if self.trend == -1 and l[j] == self.rlo and l[j] == min(l[j - N:i + 1]) and l[j] < min(l[j + 1:i + 1]):
                self.hh, self.hhi = min(o[j], c[j]), j
        return ev


def zone(h, l, org, N, ztype):
    """(bottom, top) of a demand zone whose low candle is org."""
    if ztype == "pivot":
        return l[org], h[org]
    a = max(0, org - N)
    return min(l[a:org + 1]), max(h[a:org + 1])


def killzone(t):
    """Jeff rule 19 (approved Oct 10): entries only 2-5 AM and 7-10 AM New York time."""
    e = dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).astimezone(NY)
    return 2 <= e.hour < 5 or 7 <= e.hour < 10


def pos_in(x, st):
    """where x sits in a timeframe's range: 0 = the low, 1 = the high."""
    return (x - st.rlo) / (st.rhi - st.rlo) if st.rhi > st.rlo else 0.5


def run(d, N, ztype, taker=TAKER, log=None, kz=False, maker=False, rng=False, stopm="sweep", cap=MAXSTOP,
        band=0.0):
    """long side only. Returns [(entry ts, exit ts, R)].
    kz    = the limit order can only fill inside Jeff's killzones; outside them it waits (Oct 10).
    maker = the limit entry pays 0% (maker); stop exits still pay taker + slippage (Jeff, Oct 10).
    rng   = Jeff's Oct 10 answers: 4H/15m use RangeStruct (#7) and the target is the 15m WEAK high (#33).
    stopm = "sweep" (below the 5m sweep low) or "strong" (below the 15m STRONG low), +0.05% (#31).
    cap   = max stop distance as a fraction of price, None = no cap (#32).
    band  = no-trade band around the 0.5: 0.05 = 0.45-0.55, 0.10 = 0.40-0.60 (#11)."""
    ts, o, h, l, c = d["ts"], d["o"], d["h"], d["l"], d["c"]
    t0 = B.ms(B.START)
    O15, H15, L15, C15, end15 = resample(ts, o, h, l, c, M15)
    O4, H4_, L4, C4, end4 = resample(ts, o, h, l, c, H4)
    SS = RangeStruct if rng else Struct
    s5, s15, s4 = Struct(o, h, l, c, N), SS(O15, H15, L15, C15, N), SS(O4, H4_, L4, C4, N)
    fee = lambda px: taker * abs(px)
    zones = []  # [bottom, top, used]
    setup = None  # {"z": zone, "low": sweep low or None, "swept": bool}
    pend = pos = None
    out = []
    for i in range(len(ts)):
        # 1) open trade
        if pos:
            px = None
            if l[i] <= pos["stop"]:
                px, f = min(pos["stop"], o[i]), fee(pos["stop"])
            elif h[i] >= pos["tgt"]:
                px, f = max(pos["tgt"], o[i]), 0.0
            if px is not None:
                r = (px - pos["e"] - pos["ec"] - f) / pos["r"]
                out.append((pos["ts"], ts[i], r))
                if log is not None:
                    log.append(dict(pos, x_ts=ts[i], x=px, R=r))
                pos = None
        # 2) pending limit order
        if pend and not pos:
            if l[i] <= pend["e"] and (not kz or killzone(ts[i])):
                e = min(o[i], pend["e"])
                pos = dict(pend, e=e, ec=0.0 if maker else fee(e), ts=ts[i], r=e - pend["stop"])
                pend = setup = None
                if l[i] <= pos["stop"]:  # same candle: assume the stop came first
                    r = (pos["stop"] - e - pos["ec"] - fee(pos["stop"])) / pos["r"]
                    out.append((ts[i], ts[i], r))
                    if log is not None:
                        log.append(dict(pos, x_ts=ts[i], x=pos["stop"], R=r))
                    pos = None
            elif h[i] >= pend["tgt"]:
                pend = setup = None  # ran to target without us
        # 3) zone touch (5m wick into a 15m demand zone), in the 15m and 4H discount
        if not pos and not pend and s15.trend == 1 and ts[i] >= t0:
            for z in sorted(zones, key=lambda z: z[0]):  # deepest first
                if z[2] or l[i] > z[1]:
                    continue
                if setup and setup["z"][0] <= z[0]:
                    continue  # already working a deeper zone
                z[2] = True
                if (s15.rlo is not None and s4.rlo is not None and pos_in(z[1], s15) <= 0.5 - band
                        and pos_in(l[i], s4) <= 0.5 - band):
                    setup = {"z": z, "low": None, "swept": False}
                break
        # 4) sweep: a 5m wick under the last 5m swing low while working the zone
        if setup and not pos:
            if setup["low"] is None or l[i] < setup["low"]:
                if s5.lsl is not None and l[i] < s5.lsl:
                    setup["swept"] = True
                if setup["swept"]:
                    setup["low"] = l[i] if setup["low"] is None else min(setup["low"], l[i])
        # 5) structure updates on candle closes
        ev5 = s5.step(i)
        if setup and not pos and not pend and setup["swept"] and ev5 and ev5[0] == "bull":
            org = ev5[1]
            zb, zt = zone(h, l, org, N, "pivot" if ztype == "pivot" else "range")
            e = zt
            base = s15.rlo if stopm == "strong" else setup["low"]
            stop = base - CUSH * abs(base)
            r = e - stop
            if 0 < r and (cap is None or r <= cap * abs(e)) and e < c[i]:
                if rng:
                    w = s15.rhi - CUSH * abs(s15.rhi)
                    tg = [w] if w - e >= MINRR * r else []
                else:
                    tg = sorted(v - CUSH * abs(v) for v in s15.highs if v - CUSH * abs(v) - e >= MINRR * r)
                if tg:
                    pend = {"e": e, "stop": stop, "tgt": tg[0], "z": tuple(setup["z"][:2]), "ms_ts": ts[i]}
        k = end15[i]
        if k >= 0:
            ev = s15.step(k)
            if ev and ev[0] == "bull":
                zb, zt = zone(H15, L15, ev[1], N, ztype)
                zones.append([zb, zt, False])
            elif ev and ev[0] == "bear":
                zones, setup, pend = [], None, None
            zones = [z for z in zones if C15[k] >= z[0]][-50:]
            if setup and C15[k] < setup["z"][0]:
                setup = pend = None
        k = end4[i]
        if k >= 0:
            s4.step(k)
    return out


def mirror(d):
    return {"ts": d["ts"], "o": array.array("d", (-v for v in d["o"])), "h": array.array("d", (-v for v in d["l"])),
            "l": array.array("d", (-v for v in d["h"])), "c": array.array("d", (-v for v in d["c"]))}


def main_kz():
    """Oct 10 round 2 (Jeff): best version (swing 5 range) + swing 1 range, with/without killzones and maker entry."""
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    vers = [(f"swing {N}, range zones{', killzones' if k else ''}{', maker entry' if m else ''}", N, k, m)
            for N in (5, 1) for k in (False, True) for m in (False, True)]
    res = {v[0]: [] for v in vers}
    for cn in COINS:
        d = load(cn)
        md = mirror(d)
        for name, N, k, m in vers:
            lo = [t + (1,) for t in run(d, N, "range", kz=k, maker=m)]
            sh = [t + (-1,) for t in run(md, N, "range", kz=k, maker=m)]
            keep, busy = [], -1
            for t in sorted(lo + sh):
                if t[0] > busy:
                    keep.append(t)
                    busy = t[1]
            res[name] += keep
            print(f"  {cn} {name}: {len(keep)} trades", flush=True)
        del d, md
        gc.collect()
    print("\n### Brad DAY TRADE, range zones: killzones and maker entry, BTC ETH SOL XRP, Binance.US costs\n")
    print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
          "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in vers:
        print(P.row(v[0], res[v[0]], years), flush=True)


def day_limit(tr, lim=6.0):
    """Jeff #43: like the live bots, no new entries once the account is down 3% on the UTC day.
    At the live bots' 0.5% risk a trade, 3% = 6R. All coins share one account. tr = (entry, exit, R, side, coin)."""
    keep, day, lost = [], None, 0.0
    closed = []
    for t in sorted(tr):
        d = t[0] // 86400000
        if d != day:
            day, closed = d, []
        lost = -sum(x[2] for x in closed if x[1] <= t[0] and x[1] // 86400000 == d)
        if lost >= lim:
            continue
        keep.append(t)
        closed.append(t)
    return keep


def main_v4(show10=False):
    """Oct 10 round 3 (Jeff's answers to the 43 rules): swing 5, range zones, maker entry, killzones, RangeStruct,
    target = 15m WEAK, 3% daily loss limit; stops sweep/strong x caps 1.35/2/3/none x middle bands none/0.45-0.55/0.40-0.60."""
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    caps = ((0.0135, "1.35%"), (0.02, "2%"), (0.03, "3%"), (None, "no cap"))
    bands = ((0.0, "no band"), (0.05, "no trades 0.45-0.55"), (0.10, "no trades 0.40-0.60"))
    vers = [(f"stop below {'5m sweep' if sm == 'sweep' else '15m STRONG'}, cap {cn}, {bn}", sm, cv, bv)
            for sm in ("sweep", "strong") for cv, cn in caps for bv, bn in bands]
    res = {v[0]: [] for v in vers}
    logs = {v[0]: [] for v in vers}
    for cn in COINS:
        d = load(cn)
        md = mirror(d)
        for name, sm, cv, bv in vers:
            kw = dict(kz=True, maker=True, rng=True, stopm=sm, cap=cv, band=bv)
            l1, l2 = [], []
            lo = [t + (1, cn) for t in run(d, 5, "range", log=l1, **kw)]
            sh = [t + (-1, cn) for t in run(md, 5, "range", log=l2, **kw)]
            keep, busy = [], -1
            for t in sorted(lo + sh):
                if t[0] > busy:
                    keep.append(t)
                    busy = t[1]
            res[name] += keep
            if cn == "BTC":
                ok = {t[0] for t in keep}
                logs[name] = [dict(x, side=1) for x in l1 if x["ts"] in ok] + [dict(x, side=-1) for x in l2 if x["ts"] in ok]
        print(f"  ({cn} done)", flush=True)
        del d, md
        gc.collect()
    print("\n### Brad DAY TRADE round 3 (Jeff's 43-rule answers): swing 5, range zones, maker entry, killzones, "
          "BOS/iBOS rule, target = 15m WEAK, 3% daily loss limit. BTC ETH SOL XRP, Binance.US costs\n")
    print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
          "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in vers:
        print(P.row(v[0], [t[:4] for t in day_limit(res[v[0]])], years), flush=True)
    import json
    json.dump({k: v for k, v in logs.items()}, open(os.path.join(HERE, ".cache", "brad_day_v4_btc.json"), "w"))


def main():
    if sys.argv[1:] == ["v4"]:
        return main_v4()
    if sys.argv[1:] == ["kz"]:
        return main_kz()
    coins = sys.argv[1:] or COINS
    years = (dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc) - B.START).days / 365.25
    vers = [(f"swing {N}, {z} zones{', ZERO fees' if zf else ''}", N, z, zf)
            for zf in (False, True) for N in (1, 3, 5) for z in ("pivot", "range")]
    res = {v[0]: [] for v in vers}
    for cn in coins:
        d = load(cn)
        md = mirror(d)
        for name, N, z, zf in vers:
            kw = {"taker": 0.0} if zf else {}
            lo = [t + (1,) for t in run(d, N, z, **kw)]
            sh = [t + (-1,) for t in run(md, N, z, **kw)]
            keep, busy = [], -1
            for t in sorted(lo + sh):
                if t[0] > busy:
                    keep.append(t)
                    busy = t[1]
            res[name] += keep
            print(f"  {cn} {name}: {len(keep)} trades", flush=True)
        del d, md
        gc.collect()
    print(f"\n### Brad DAY TRADE (4H story -> 15m zones -> 5m sweep + shift entry), {' '.join(coins)}, Binance.US costs\n")
    print("| Version | Trades/yr | Win % | Avg win | Avg loss | PF | Avg | Max DD | 2019-22 PF | 2023-now PF | "
          "Long PF | Short PF |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in vers:
        print(P.row(v[0], res[v[0]], years), flush=True)


if __name__ == "__main__":
    main()
