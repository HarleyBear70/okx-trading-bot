"""F47 research scout 2026-11-07. Forex, DAILY CLOSES ONLY (Fed H.10 noon rates via github.com/datasets/exchange-rates;
no highs/lows, so stops are checked on closes and ATR = mean |close change| of 20 days). Rules fixed BEFORE testing.
M month-end dollar flow: close of 3rd-from-last trading day of the month: SHORT EUR/USD and GBP/USD (USD bought); exit at the
   close of the 1st trading day of next month; stop 3 ATR(20). Mirror (long) also reported.
B Bollinger stretch fade: close < SMA20-2sd -> long; close > SMA20+2sd -> short; exit first close back across SMA20; stop 3 ATR(20).
Forex cost 0.01%/side, risk 0.5%/trade, leverage cap 10x, halves 2012-03..2018 / 2019..now."""
import csv, datetime as dt, statistics as st, urllib.request, os, sys
FP = "/tmp/fx.csv"
def load(country):
    d = {}
    for r in csv.DictReader(open(FP)):
        if r["Country"] == country and r["Exchange rate"] not in ("", "ND"):
            try: d[r["Date"]] = 1 / float(r["Exchange rate"])
            except: pass
    ks = sorted(k for k in d if k >= "2011-01-01")
    return ks, [d[k] for k in ks]
def sigs(kind, ds, c):
    n = len(c); out = [None] * n
    tr = [0] + [abs(c[i] - c[i-1]) for i in range(1, n)]
    for k in range(25, n - 1):
        a = sum(tr[k-19:k+1]) / 20
        if kind in ("M", "Mlong"):
            # 3rd-from-last trading day of month: month of ds[k+2] differs from ds[k] and ds[k+1]... use known calendar of dataset
            m = ds[k][:7]
            later = [j for j in range(k, min(k + 6, n)) if ds[j][:7] == m]
            if len(later) == 3 and k + 3 < n or (len(later) == 3 and k + 3 >= n and False):
                side = -1 if kind == "M" else 1
                nxt = later[-1] + 1
                if nxt < n and ds[nxt][:7] != m:
                    out[k] = (side, c[k] + (-side) * 3 * a, lambda j, nxt=nxt: j >= nxt)
        else:
            w = c[k-19:k+1]; mu = sum(w) / 20; sd = st.pstdev(w)
            if c[k] < mu - 2 * sd: out[k] = (1, c[k] - 3 * a, lambda j: c[j] >= sum(c[j-19:j+1]) / 20)
            elif c[k] > mu + 2 * sd: out[k] = (-1, c[k] + 3 * a, lambda j: c[j] <= sum(c[j-19:j+1]) / 20)
    return out
def sim(ds, c, sg, t0, t1, cost=0.0001, risk=0.005, lev=10):
    eq, peak, mdd, tr, i, n = 1000.0, 1000.0, 0.0, [], 0, len(c)
    while i < n:
        s = sg[i]
        if not s or ds[i] < t0 or ds[i] >= t1: i += 1; continue
        side, stop, ex = s; e = c[i]
        dist = abs(e - stop)
        units = min(eq * risk / dist, eq * lev / e)
        j = i + 1; px = None
        while j < n:
            if (side == 1 and c[j] <= stop) or (side == -1 and c[j] >= stop): px = c[j]; break
            if ex(j): px = c[j]; break
            j += 1
        if px is None: break
        pnl = side * (px - e) * units - (e + px) * units * cost
        eq += pnl; tr.append(pnl); peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak * 100); i = j + 1
    w = sum(p for p in tr if p > 0); l = -sum(p for p in tr if p < 0)
    return (eq / 1000 - 1) * 100, mdd, (w / l if l else 9.99), len(tr)
if __name__ == "__main__":
    P = {"EURUSD": load("Euro"), "GBPUSD": load("United Kingdom")}
    halves = [("2012-18", "2012-03-01", "2019-01-01"), ("2019-now", "2019-01-01", "2099")]
    for kind in ("M", "Mlong", "B"):
        for p, (ds, c) in P.items():
            sg = sigs(kind, ds, c)
            for hn, a, b in halves:
                print(kind, p, hn, "ret %+6.1f%% dd %4.1f%% PF %.2f trades %d" % sim(ds, c, sg, a, b))
