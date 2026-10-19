# Read-only: downloads Coinbase Exchange public candles (no key, nothing traded).
# usage: python tools/coinbase_history.py "BTC ETH" 15m 2024-09-25 2026-10-19 outdir
import json, sys, time, urllib.request, datetime as dt, os
coins, bar, a, b, out = sys.argv[1].split(), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
gran = {'1m': 60, '5m': 300, '15m': 900, '1h': 3600}[bar]
U = dt.timezone.utc
s = int(dt.datetime.fromisoformat(a).replace(tzinfo=U).timestamp())
e = int(dt.datetime.fromisoformat(b).replace(tzinfo=U).timestamp())
os.makedirs(out, exist_ok=True)
for coin in coins:
    rows = {}; t0 = s; fails = 0
    while t0 < e:
        t1 = min(e, t0 + gran * 300)
        u = (f"https://api.exchange.coinbase.com/products/{coin}-USD/candles?granularity={gran}"
             f"&start={dt.datetime.fromtimestamp(t0, U).isoformat()}&end={dt.datetime.fromtimestamp(t1, U).isoformat()}")
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "jeff-research"})
            d = json.load(urllib.request.urlopen(req, timeout=20))
        except Exception as ex:
            fails += 1
            if fails > 20: print(coin, "gave up", ex); break
            time.sleep(2 * fails); continue
        fails = 0
        for tt, lo, hi, op, cl, vol in d:
            if tt + gran <= time.time(): rows[tt * 1000] = (op, hi, lo, cl, vol)
        t0 = t1
        time.sleep(0.12)
    with open(f"{out}/{coin}_{bar}.csv", "w") as f:
        f.write("ts,o,h,l,c,v\n")
        for t in sorted(rows): f.write(f"{t},{','.join(str(x) for x in rows[t])}\n")
    print(coin, bar, len(rows), flush=True)
