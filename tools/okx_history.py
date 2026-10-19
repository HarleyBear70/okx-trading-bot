# Read-only: downloads OKX public candles (no key, nothing traded).
# usage: python tools/okx_history.py "BTC ETH" 15m 2024-09-25 2026-10-19 outdir
import json, sys, time, urllib.request, datetime as dt, os
coins, bar, a, b, out = sys.argv[1].split(), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
U = dt.timezone.utc
s = int(dt.datetime.fromisoformat(a).replace(tzinfo=U).timestamp() * 1000)
e = int(dt.datetime.fromisoformat(b).replace(tzinfo=U).timestamp() * 1000)
os.makedirs(out, exist_ok=True)
for coin in coins:
    rows = {}; after = e; fails = 0
    while True:
        u = f"https://www.okx.com/api/v5/market/history-candles?instId={coin}-USDT&bar={bar}&limit=100&after={after}"
        try:
            d = json.load(urllib.request.urlopen(u, timeout=20))["data"]
        except Exception as ex:
            fails += 1
            if fails > 20: print(coin, "gave up", ex); break
            time.sleep(2 * fails); continue
        fails = 0
        if not d: break
        for r in d:
            if r[8] == "1": rows[int(r[0])] = r[1:6]
        after = int(d[-1][0])
        if after <= s: break
        time.sleep(0.11)
    with open(f"{out}/{coin}_{bar}.csv", "w") as f:
        f.write("ts,o,h,l,c,v\n")
        for t in sorted(rows):
            if s <= t < e: f.write(f"{t},{','.join(rows[t])}\n")
    print(coin, bar, len(rows), flush=True)
