"""
STRUCT_T1: Tier 1 market structure only (issue #6, Chrome Claude + Jeff, Oct 13 2026). Same logic as
pine/structure_t1.pine; this file checks it against Jeff's test cases on OKX 1H candles and prints the event list.

  All breaks are candle BODY closes; a wick alone never counts. No "N candles each side" pivots.
  Up trend:   WEAK = the newest high (follows the wicks). STRONG = the low the BOS move started from.
    BOS up    a body closes above WEAK after a pullback (at least one candle since WEAK did not make a new high).
              STRONG = the lowest low between the WEAK candle and the BOS candle; WEAK = the new high.
              [CLAUDE: "pullback" = 1 candle that did not make a new high; without one, a close above just stretches WEAK]
              A wick-only new high never moves STRONG (Jeff, Oct 13: removed fill-in #2). It is a sweep of WEAK.
    MS down   a body closes below STRONG's wick. Trend flips: STRONG = the old WEAK (the high that led to it).
    Sweep     a wick goes past WEAK or STRONG but no body closes past it, OR a body closes past and the very next candle
              closes back inside (then it was a fuel grab). Sweep of WEAK: WEAK follows the wick; STRONG stays.
              So BOS/MS are confirmed one candle later (no look-ahead); the break candle is the one that gets colored.
  Down trend = mirror.
  Internal (iBOS)  bullish: a body closes above the HIGH of the candle just before the low candle (the candle the
              last drop into the low started from). The low = lowest low since the last bullish break; equal lows
              (within 0.01%) count as the first one. Bearish = mirror. Does not flip the trend. One per low/high.
              [CLAUDE: "the candle the last drop started from" = the candle before the low candle - matched all 3 of
              Jeff's iBOS examples]
  Start: the first body close above (below) all candles so far starts an up (down) trend.

  python3 research/struct_t1.py           Jeff's test cases on OKX 1H (the prices Chrome Claude used), read-only
  python3 research/struct_t1.py week      every event, last 7 days, BTCUSD 1H on Binance.US (Jeff's exchange)
"""
import datetime as dt
import os
import sys

TOL = 0.0001


class Tier1:
    def __init__(self, h, l, c):
        self.h, self.l, self.c = h, l, c
        self.trend, self.strong, self.sb, self.weak, self.wb = 0, None, -1, None, -1
        self.pulled = False
        self.pend = None  # (kind, candle) waiting for the next candle's close
        self.ilo = self.ihi = None  # candle index of the current low / high for internal breaks
        self.ilo_from = self.ihi_from = 0

    def _ext(self, k, up):
        """WEAK follows a new extreme; returns True if it was a new extreme"""
        if (self.h[k] > self.weak) if up else (self.l[k] < self.weak):
            self.weak, self.wb, self.pulled = (self.h[k] if up else self.l[k]), k, False
            return True
        return False

    def _internal(self, k):
        h, l, c = self.h, self.l, self.c
        ev = None
        # current low since the last bullish break (equal lows keep the first)
        if k > self.ilo_from and (self.ilo is None or l[k] < l[self.ilo] * (1 - TOL)):
            if l[k] < l[k - 1]:
                self.ilo = k
        if k > self.ihi_from and (self.ihi is None or h[k] > h[self.ihi] * (1 + TOL)):
            if h[k] > h[k - 1]:
                self.ihi = k
        if self.ilo is not None and k > self.ilo and c[k] > h[self.ilo - 1]:
            ev = ("iBOS up", h[self.ilo - 1])
            self.ilo, self.ilo_from = None, k
        elif self.ihi is not None and k > self.ihi and c[k] < l[self.ihi - 1]:
            ev = ("iBOS down", l[self.ihi - 1])
            self.ihi, self.ihi_from = None, k
        return ev

    def reset_internal(self, up, k):
        if up:
            self.ilo, self.ilo_from = None, k
        else:
            self.ihi, self.ihi_from = None, k

    def step(self, k):
        """returns a list of (candle, event, level). BOS/MS are confirmed one candle later and reported on the BREAK candle."""
        h, l, c = self.h, self.l, self.c
        out = []
        if self.trend == 0:
            if k > 0 and c[k] > max(h[:k]):
                self.trend, self.sb = 1, min(range(k), key=lambda x: l[x])
                self.strong, self.weak, self.wb = l[self.sb], h[k], k
                out.append((k, "start UP", c[k]))
            elif k > 0 and c[k] < min(l[:k]):
                self.trend, self.sb = -1, max(range(k), key=lambda x: h[x])
                self.strong, self.weak, self.wb = h[self.sb], l[k], k
                out.append((k, "start DOWN", c[k]))
            return out
        up = self.trend == 1
        if self.pend is not None:  # confirm or undo last candle's break
            kind, b, lvl = self.pend
            self.pend = None
            if kind == "MS":
                if (c[k] < lvl) if up else (c[k] > lvl):
                    self.trend, up = -self.trend, not up
                    self.strong, self.sb = self.weak, self.wb  # the extreme that led to the MS
                    self.weak, self.wb, self.pulled = (h[b] if up else l[b]), b, False
                    self.reset_internal(up, b)
                    out.append((b, "MS UP" if up else "MS DOWN", c[b]))
                else:
                    out.append((b, "sweep (MS undone)", c[b]))
            else:
                held = (c[k] > lvl) if up else (c[k] < lvl)
                if held:  # STRONG moves only on a confirmed BOS body close (Jeff, Oct 13)
                    self.strong, self.sb = self.pend_s
                    self.reset_internal(up, b)
                out.append((b, ("BOS up" if up else "BOS down") if held else "sweep (BOS undone)", c[b]))
        # MS: a body close past STRONG's wick (waits one candle)
        if (c[k] < self.strong) if up else (c[k] > self.strong):
            self.pend = ("MS", k, self.strong)
            return out
        if (l[k] < self.strong) if up else (h[k] > self.strong):
            out.append((k, "sweep of STRONG", self.strong))
        if (h[k] > self.weak) if up else (l[k] < self.weak):  # new high (low)
            if self.pulled:  # after a pullback: a body close past WEAK = BOS (STRONG moves to the pullback's extreme once confirmed)
                if (c[k] > self.weak) if up else (c[k] < self.weak):
                    s = min(range(self.wb, k + 1), key=lambda x: l[x]) if up else max(range(self.wb, k + 1), key=lambda x: h[x])
                    self.pend_s = ((l[s] if up else h[s]), s)
                    self.pend = ("BOS", k, self.weak)
                else:
                    out.append((k, "sweep of WEAK", self.weak))
            self.weak, self.wb, self.pulled = (h[k] if up else l[k]), k, False
        elif self.wb != k:
            self.pulled = True
        if self.pend is None or self.pend[0] != "BOS":
            iv = self._internal(k)
            if iv and not any(e[0] == k for e in out):
                out.append((k, iv[0], iv[1]))
        else:
            self._internal(k)
        return out


def et(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc) - dt.timedelta(hours=4)


def run(inst, bar="1H", rows=None):
    if rows is None:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
        from heartbeat_watch import fetch
        rows = fetch(inst, bar)
    T = [et(int(r[0])) for r in rows]
    h, l, c = ([float(r[i]) for r in rows] for i in (2, 3, 4))
    s, evs = Tier1(h, l, c), []
    for k in range(len(rows)):
        for b, ev, lvl in s.step(k):
            evs.append((T[b], ev, c[b], lvl, s.trend, s.strong, s.weak))
    return evs


def binance_us(sym, interval="1h", limit=500):
    """Binance.US public candles (no key; Jeff trades there). Closed candles only, OKX row layout [ts, o, h, l, c]."""
    import json
    import time
    import urllib.request
    url = f"https://api.binance.us/api/v3/klines?symbol={sym}&interval={interval}&limit={limit}"
    rows = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "struct_t1"}), timeout=20))
    now = time.time() * 1000
    return [r[:5] for r in rows if r[6] < now]


def week_list(sym="BTCUSD", days=7):
    """every event for the last `days` days on Binance.US 1H, for Jeff and Chrome Claude to check on the chart"""
    evs = run(sym, rows=binance_us(sym))
    cut = evs and (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days, hours=4))
    lines = [f"{sym} 1H, Binance.US, times ET (candle open time, like TradingView). Last {days} days.",
             "time               event               candle close   level broken   -> trend / STRONG / WEAK after"]
    for t, ev, cl, lvl, tr, st, wk in evs:
        if t >= cut:
            lines.append(f"{t:%a %b %d %I %p}   {ev:20} {cl:<14g} {lvl:<14g} -> {'UP' if tr == 1 else 'DOWN'} / {st:g} / {wk:g}")
    return "\n".join(lines)


def main():
    import json
    if len(sys.argv) > 1 and sys.argv[1] == "week":
        print(week_list(*(sys.argv[2:3] or ["BTCUSD"])))
        return
    src = sys.argv[1] if len(sys.argv) > 1 else None
    for coin in ("BTC", "ETH", "SOL"):
        rows = json.load(open(os.path.join(src, f"{coin}_1H.json"))) if src else None
        print(f"\n===== {coin}-USDT 1H (OKX), times ET = candle open =====")
        for t, ev, cl, lvl, tr, st, wk in run(f"{coin}-USDT", rows=rows):
            if t >= dt.datetime(2026, 10, 6, tzinfo=dt.timezone.utc):
                print(f"{t:%a %b %d %I %p}  {ev:20} close {cl:<10g} level {lvl:<10g} -> trend {'UP' if tr == 1 else 'DOWN'}, STRONG {st:g}, WEAK {wk:g}")


if __name__ == "__main__":
    main()
