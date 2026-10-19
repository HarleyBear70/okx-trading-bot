# Read-only: downloads Binance.US public candles (no key, nothing traded).
# usage: python tools/binanceus_history.py "BTC ETH" 15m 2024-09-25 2026-10-19 outdir
import json, sys, time, urllib.request, datetime as dt, os
coins, bar, a, b, out = sys.argv[1].split(), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
U = dt.timezone.utc
s = int(dt.datetime.fromisoformat(a).replace(tzinfo=U).timestamp() * 1000)
e = int(dt.datetime.fromisoformat(b).replace(tzinfo=U).timestamp() * 1000)
os.makedirs(out, exist_ok=True)
for coin in coins:
    rows = {}; start = s; fails = 0
    while start < e:
        u = f"https://api.binance.us/api/v3/klines?symbol={coin}USDT&interval={bar}&limit=1000&startTime={start}&endTime={e}"
        try:
            d = json.load(urllib.request.urlopen(u, timeout=20))
        except Exception as ex:
            fails += 1
            if fails > 20: print(coin, "gave up", ex); break
            time.sleep(2 * fails); continue
        fails = 0
        if not d: break
        for r in d:
            if r[6] < time.time() * 1000: rows[int(r[0])] = r[1:6]
        start = int(d[-1][0]) + 1
        time.sleep(0.15)
    with open(f"{out}/{coin}_{bar}.csv", "w") as f:
        f.write("ts,o,h,l,c,v\n")
        for t in sorted(rows): f.write(f"{t},{','.join(rows[t])}\n")
    print(coin, bar, len(rows), flush=True)
