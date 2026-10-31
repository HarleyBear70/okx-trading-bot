"""F46 research scout 2026-10-31. Crypto only (forex hosts blocked). Rules fixed BEFORE testing.
D dip in uptrend: close>SMA100, 3 lower closes in a row, 3-day drop>=8% -> long; exit first close > prior-day high or after 10 bars; stop 3 ATR(20).
G gated fast breakout: close>SMA200, SMA50>SMA200, close = 10-day highest close (fresh) -> long; exit close < lowest close of prior 5 days; stop 3 ATR(20).
Same sim/coins/halves/fees as f45."""
import json, statistics as st, sys, urllib.request, datetime as dt, os
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache_f45"); os.makedirs(CACHE, exist_ok=True)
SEEN = ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK"]
UNSEEN = ["ADA", "DOGE", "AVAX", "LTC", "DOT"]
CUT = int(dt.datetime(2022, 1, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)

def load(c):
    fp = f"{CACHE}/{c}.json"
    if os.path.exists(fp): return json.load(open(fp))
    out, t = [], 1500000000000
    while True:
        u = f"https://api.binance.us/api/v3/klines?symbol={c}USDT&interval=1d&startTime={t}&limit=1000"
        r = json.load(urllib.request.urlopen(u, timeout=30))
        if not r: break
        out += [dict(ts=x[0], o=float(x[1]), h=float(x[2]), l=float(x[3]), c=float(x[4])) for x in r]
        t = r[-1][0] + 1
        if len(r) < 1000: break
    json.dump(out, open(fp, "w")); return out

def atr(b, n=20):
    tr = [None] + [max(b[i]["h"] - b[i]["l"], abs(b[i]["h"] - b[i-1]["c"]), abs(b[i]["l"] - b[i-1]["c"])) for i in range(1, len(b))]
    return [None if i < n else sum(tr[i-n+1:i+1]) / n for i in range(len(b))]

def signals(kind, b):
    c = [x["c"] for x in b]; h = [x["h"] for x in b]; a = atr(b); n = len(b); sig = [None] * n
    sma = lambda i, m: sum(c[i-m+1:i+1]) / m
    for k in range(210, n - 2):
        if not a[k]: continue
        if kind == "D":
            # dip in uptrend: close>SMA100, 3 lower closes in a row, 3-day drop >= 8%; exit first close > prior day high, or 10 bars
            if c[k] > sma(k, 100) and c[k] < c[k-1] < c[k-2] < c[k-3] and c[k] / c[k-3] - 1 <= -0.08:
                sig[k] = (c[k] - 3 * a[k], lambda j, k=k: c[j] > h[j-1] or j - k >= 10)
        elif kind == "G":
            # gated fast breakout: close>SMA200 and close = highest close of 10 days and SMA50 > SMA200; exit close < lowest close of 5 days
            if c[k] > sma(k, 200) and sma(k, 50) > sma(k, 200) and c[k] >= max(c[k-9:k+1]) and c[k-1] < max(c[k-10:k]):
                sig[k] = (c[k] - 3 * a[k], lambda j: c[j] < min(c[j-5:j]))
    return sig

def sim(b, sig, fee, t0, t1, risk=0.005):
    eq, peak, mdd, trades, i = 1000.0, 1000.0, 0.0, [], 0
    n = len(b)
    while i < n:
        s = sig[i]
        if s is None or b[i]["ts"] < t0 or (t1 and b[i]["ts"] >= t1): i += 1; continue
        stop, ex = s; e = b[i]["c"]
        if stop >= e: i += 1; continue
        size = min(eq * risk / (e - stop), eq / (e * (1 + fee)))
        j = i + 1; px = None
        while j < n:
            if b[j]["l"] <= stop: px = min(b[j]["o"], stop); break
            if ex(j): px = b[j]["c"]; break
            j += 1
        if px is None: break
        pnl = size * (px - e) - size * e * fee - size * px * fee
        eq += pnl; trades.append(pnl)
        peak = max(peak, eq); mdd = max(mdd, (peak - eq) / peak * 100); i = j + 1
    w = sum(p for p in trades if p > 0); l = -sum(p for p in trades if p < 0)
    return dict(ret=(eq / 1000 - 1) * 100, dd=mdd, pf=(w / l if l else (9.99 if w else 0)), n=len(trades))

def main():
    data = {c: load(c) for c in SEEN + UNSEEN}
    res = {}
    lines = []
    for kind in "DG":
        for fee in (0.0035, 0.0002):
            for grp, coins in (("seen", SEEN), ("unseen", UNSEEN)):
                for name, t0, t1 in (("1st", 0, CUT), ("2nd", CUT, None)):
                    rs = [sim(data[c], signals(kind, data[c]), fee, t0, t1) for c in coins]
                    tot = sum(r["n"] for r in rs)
                    avg = sum(r["ret"] for r in rs) / len(rs); dd = max(r["dd"] for r in rs)
                    pos = sum(r["ret"] > 0 for r in rs)
                    gw = sum(r["pf"] * 1 for r in rs) / len(rs)
                    lines.append((kind, fee, grp, name, avg, dd, gw, tot, pos, len(coins)))
    for l in lines:
        print("%s fee %.2f%% %-6s %s half: avg %+6.1f%%  worst dd %5.1f%%  avg PF %.2f  trades %4d  coins+ %d/%d" % (l[0], l[1]*100, l[2], l[3], *l[4:]))
main()
