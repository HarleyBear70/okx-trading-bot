"""
F45 research scout (2026-10-24). Crypto only (forex history hosts blocked). Rules fixed BEFORE testing.
M  Turn of month (F43 rule): long at close of 3rd-from-last trading day of month, exit close of 1st trading day of next month. Stop 3 ATR(20).
B  Bollinger stretch fade (F43 rule): long when close < SMA20 - 2sd; exit first close > SMA20; stop 3 ATR(20).
S  Squeeze breakout (new): Bollinger(20,2) bandwidth (upper-lower)/SMA is at its lowest in 120 days (within last 5 bars)
   and close > upper band -> long; exit first close < SMA20; stop = lowest low of last 10 bars.
Daily bars from Binance.US public API. One coin at a time, $1000 start, risk 0.5% of equity from the stop, position capped at 100% of equity,
fee per side 0.35% and 0.02%. Halves split 2022-01-01. Research only.
"""
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
    c = [x["c"] for x in b]; a = atr(b); n = len(b); sig = [None] * n
    sma = [None if i < 19 else sum(c[i-19:i+1]) / 20 for i in range(n)]
    sd = [None if i < 19 else st.pstdev(c[i-19:i+1]) for i in range(n)]
    ym = [dt.datetime.fromtimestamp(x["ts"] / 1000, dt.timezone.utc).strftime("%Y%m") for x in b]
    bw = [None if sma[i] is None else 4 * sd[i] / sma[i] for i in range(n)]
    for k in range(140, n - 3):
        if not a[k] or not sd[k]: continue
        if kind == "M":
            if ym[k+3] != ym[k] and ym[k+2] == ym[k]:
                sig[k] = (c[k] - 3 * a[k], lambda j, k=k: ym[j] != ym[k])
        elif kind == "B":
            if c[k] < sma[k] - 2 * sd[k]:
                sig[k] = (c[k] - 3 * a[k], lambda j: c[j] > sma[j])
        elif kind == "S":
            mn = min(bw[k-119:k+1])
            if min(bw[k-4:k+1]) <= mn + 1e-12 and c[k] > sma[k] + 2 * sd[k]:
                sig[k] = (min(x["l"] for x in b[k-9:k+1]), lambda j: c[j] < sma[j])
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
    for kind in "MBS":
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
