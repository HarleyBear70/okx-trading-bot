"""F48 research scout 2026-11-14. Rules fixed BEFORE testing. Reuses F46 crypto sim (Binance.US daily, halves 2022-01-01) and F47 forex close-only sim (Fed H.10).
N crypto NR4 vol-contraction breakout (Street Smarts / cryptodatadownload): day k: close>SMA100, 6d stdev of daily returns / 100d stdev < 0.5, range of day k is the narrowest of last 4 days.
  Entry at close of day k+1 if close[k+1] > high[k] (breakout). Exit close < lowest low of prior 5 days, or after 15 bars. Stop 3 ATR(20).
S forex 3-day streak fade (tastyfx 'fade multi-day dollar moves'; Moskowitz-style short reversal): 3 consecutive higher closes -> SHORT, 3 lower -> LONG at close.
  Exit first close that moves the other way, or after 5 bars. Stop 3 ATR (20d mean abs close change).
P forex trend pullback both ways (own variant): close>SMA200 and close is lowest close of last 5 -> LONG; close<SMA200 and highest close of last 5 -> SHORT.
  Exit close back above/below SMA5 (long: close>SMA5), or after 10 bars. Stop 3 ATR.
Forex cost 0.01%/side, risk 0.5%, leverage cap 10x, halves 2012-18 / 2019-now. Crypto fees 0.35% and 0.02%, risk 0.5%."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import f46_scout as c46, f47_fx_close as f47, statistics as st

def nr4(kind_b):
    b = kind_b; c = [x["c"] for x in b]; h = [x["h"] for x in b]; l = [x["l"] for x in b]; a = c46.atr(b); n = len(b); sig = [None]*n
    ret = [0] + [c[i]/c[i-1]-1 for i in range(1, n)]
    for k in range(210, n-2):
        j = k+1
        if not a[j]: continue
        # day k setup
        rng = [h[i]-l[i] for i in range(k-3, k+1)]
        if rng[-1] != min(rng): continue
        if c[k] <= sum(c[k-99:k+1])/100: continue
        v6 = st.pstdev(ret[k-5:k+1]); v100 = st.pstdev(ret[k-99:k+1])
        if v100 == 0 or v6/v100 >= 0.5: continue
        if c[j] > h[k]:
            sig[j] = (c[j]-3*a[j], lambda m, j=j: l[m] < 0 or c[m] < min(l[m-5:m]) or m-j >= 15)
    return sig

def fxsig(kind, ds, c):
    n = len(c); out = [None]*n
    tr = [0]+[abs(c[i]-c[i-1]) for i in range(1, n)]
    for k in range(205, n-1):
        a = sum(tr[k-19:k+1])/20
        if kind == "S":
            if c[k]>c[k-1]>c[k-2]>c[k-3]:
                out[k] = (-1, c[k]+3*a, lambda j, k=k: c[j] > c[j-1] or j-k >= 5)
            elif c[k]<c[k-1]<c[k-2]<c[k-3]:
                out[k] = (1, c[k]-3*a, lambda j, k=k: c[j] < c[j-1] or j-k >= 5)
        else:
            s200 = sum(c[k-199:k+1])/200
            if c[k] > s200 and c[k] <= min(c[k-4:k+1]):
                out[k] = (1, c[k]-3*a, lambda j, k=k: c[j] > sum(c[j-4:j+1])/5 or j-k >= 10)
            elif c[k] < s200 and c[k] >= max(c[k-4:k+1]):
                out[k] = (-1, c[k]+3*a, lambda j, k=k: c[j] < sum(c[j-4:j+1])/5 or j-k >= 10)
    return out

def crypto():
    data = {c: c46.load(c) for c in c46.SEEN + c46.UNSEEN}
    for fee in (0.0035, 0.0002):
        for grp, coins in (("seen", c46.SEEN), ("unseen", c46.UNSEEN)):
            for name, t0, t1 in (("1st", 0, c46.CUT), ("2nd", c46.CUT, None)):
                rs = [c46.sim(data[c], nr4(data[c]), fee, t0, t1) for c in coins]
                print("N fee %.2f%% %-6s %s half: avg %+6.1f%% worst dd %5.1f%% avg PF %.2f trades %4d coins+ %d/%d" % (fee*100, grp, name,
                    sum(r["ret"] for r in rs)/len(rs), max(r["dd"] for r in rs), sum(r["pf"] for r in rs)/len(rs), sum(r["n"] for r in rs), sum(r["ret"]>0 for r in rs), len(rs)))
def forex():
    P = {"EURUSD": f47.load("Euro"), "GBPUSD": f47.load("United Kingdom")}
    for kind in ("S", "P"):
        for p, (ds, c) in P.items():
            sg = fxsig(kind, ds, c)
            for hn, a, b in [("2012-18", "2012-03-01", "2019-01-01"), ("2019-now", "2019-01-01", "2099")]:
                print(kind, p, hn, "ret %+6.1f%% dd %4.1f%% PF %.2f trades %d" % f47.sim(ds, c, sg, a, b))
if __name__ == "__main__":
    crypto(); forex()
