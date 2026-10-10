"""
JEFF_STRUCT: Jeff's "heartbeat" market structure (JEFF_RULES.md, Jeff's test-case answers Oct 10 2026).
Checked against Jeff's BTC-USDT 5m test case (OKX, Oct 10 2026, 4:45-7:40 AM ET): python3 research/jeff_struct.py

  Each leg: STRONG (fib 1) and WEAK (fib 0, the newest high in an up leg / low in a down leg; follows the wicks).
  New high after a pullback (a swing low formed since WEAK)        -> STRONG moves up to that newest pullback low.
     (Jeff test case: the 5:30 high moved STRONG to the 5:25 low, so 5:45 = MS down.)
  New high that only WICKS past equal highs (a pool) and closes back inside = a SWEEP / fuel grab:
     WEAK follows the wick, STRONG does not move (Jeff: 6:40 = sweep, not BOS).
  Equal highs/lows = within TOL (0.01%) of each other (Jeff).
  MS = a candle BODY closes past STRONG's WICK; the leg flips, new STRONG = the old WEAK (the extreme that led to it).
     If the very next candle closes back inside, it was a fuel grab, not an MS (Jeff: reversal within 1 candle).
     So an MS is confirmed one candle later (no look-ahead).
  Down leg = mirror. Swing = N candles each side.
"""
TOL = 0.0001


class Heart:
    def __init__(self, h, l, c, N, tol=TOL):
        self.h, self.l, self.c, self.N, self.tol = h, l, c, N, tol
        self.trend, self.strong, self.weak, self.sb, self.wb = 0, None, None, 0, 0
        self.pl = self.ph = None
        self.plb = self.phb = -1
        self.pend = None  # candle index of an MS waiting for the next candle's confirmation

    @property
    def rng(self):
        """(fib 1 / fib 0 as low, high)"""
        if self.trend == 1:
            return self.strong, self.weak
        if self.trend == -1:
            return self.weak, self.strong
        return None, None

    def _pool(self, lvl, a, b, low):
        """another candle between a and b (excl. the one at lvl) within tol of lvl = equal lows/highs."""
        x = self.l if low else self.h
        return any(abs(x[i] - lvl) <= self.tol * abs(lvl) for i in range(a, b) if i != self.wb)

    def _flip(self, k):
        if self.trend == 1:
            self.trend, self.strong, self.sb, self.weak, self.wb = -1, self.weak, self.wb, self.l[k], k
        else:
            self.trend, self.strong, self.sb, self.weak, self.wb = 1, self.weak, self.wb, self.h[k], k

    def step(self, k):
        """returns an event string or None"""
        h, l, c, N = self.h, self.l, self.c, self.N
        j = k - N
        if j >= N:
            if l[j] == min(l[j - N:k + 1]) and l[j] < min(l[j + 1:k + 1]):
                self.pl, self.plb = l[j], j
            if h[j] == max(h[j - N:k + 1]) and h[j] > max(h[j + 1:k + 1]):
                self.ph, self.phb = h[j], j
        if self.trend == 0:
            if self.ph is not None and c[k] > self.ph:
                self.sb = min(range(self.phb, k + 1), key=lambda x: l[x])
                self.trend, self.strong, self.weak, self.wb = 1, l[self.sb], h[k], k
                return "start UP"
            if self.pl is not None and c[k] < self.pl:
                self.sb = max(range(self.plb, k + 1), key=lambda x: h[x])
                self.trend, self.strong, self.weak, self.wb = -1, h[self.sb], l[k], k
                return "start DOWN"
            return None
        up = self.trend == 1
        if self.pend is not None:  # MS from the last candle: confirmed unless this candle closed back inside
            self.pend = None
            if (c[k] < self.strong) if up else (c[k] > self.strong):
                self._flip(k - 1)
                ev = "MS DOWN" if up else "MS UP"
                up = not up  # and this candle can already extend the new leg (below)
            else:
                ev = "fuel grab (MS undone)"
        else:
            ev = None
        if (c[k] < self.strong) if up else (c[k] > self.strong):
            self.pend = k
            return ev or "MS? (waiting 1 candle)"
        if up and h[k] > self.weak:
            pulled = self.plb >= self.wb
            grab = self.plb > self.wb and c[k] <= self.weak and self._pool(self.weak, self.sb, k, low=False)
            if pulled and not grab:
                self.sb = min(range(self.wb, k + 1), key=lambda x: l[x])
                self.strong = l[self.sb]
                ev = ev or "BOS up"
            elif grab:
                ev = ev or "sweep of equal highs"
            self.weak, self.wb = h[k], k
        elif not up and l[k] < self.weak:
            pulled = self.phb >= self.wb
            grab = self.phb > self.wb and c[k] >= self.weak and self._pool(self.weak, self.sb, k, low=True)
            if pulled and not grab:
                self.sb = max(range(self.wb, k + 1), key=lambda x: h[x])
                self.strong = h[self.sb]
                ev = ev or "BOS down"
            elif grab:
                ev = ev or "sweep of equal lows"
            self.weak, self.wb = l[k], k
        return ev


def test_case(path):
    import datetime as dt
    import json
    d = sorted(json.load(open(path))["data"])
    T = [dt.datetime.fromtimestamp(int(r[0]) / 1000, dt.timezone.utc) - dt.timedelta(hours=4) for r in d]
    h, l, c = ([float(r[i]) for r in d] for i in (2, 3, 4))
    for N in (1, 2, 3):
        s = Heart(h, l, c, N)
        print(f"\n===== swing {N} =====")
        for k in range(len(d)):
            ev = s.step(k)
            if ev and (5, 0) <= (T[k].hour, T[k].minute) <= (8, 0):
                print(f"{T[k]:%H:%M} close {c[k]:<8} {ev:24} STRONG {s.strong} ({T[s.sb]:%H:%M})  WEAK {s.weak} ({T[s.wb]:%H:%M})")


if __name__ == "__main__":
    import sys
    test_case(sys.argv[1])
