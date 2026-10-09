"""
Download Binance (global) 1H klines with TAKER BUY volume from data.binance.vision (free, public), 2019-now,
for the order-flow test (research/orderflow.py). Saved to ~/.cache/binance_1h/<COIN>.json.gz: {ts: taker buy share}.
Binance global is only the SIGNAL source (far more volume than Binance.US); trades are still costed at Binance.US.

  python3 research/orderflow_data.py
"""
import concurrent.futures as cf
import datetime as dt
import gzip
import io
import json
import os
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from brad_more import COINS23  # noqa: E402

OUT = os.path.expanduser("~/.cache/binance_1h")
URL = "https://data.binance.vision/data/spot/{kind}/klines/{s}USDT/1h/{s}USDT-1h-{p}.zip"


def get(s, kind, p):
    try:
        with urllib.request.urlopen(URL.format(kind=kind, s=s, p=p), timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        rows = []
        for line in z.read(z.namelist()[0]).decode().splitlines():
            f = line.split(",")
            if not f[0].isdigit():
                continue
            ts = int(f[0])
            ts = ts // 1000 if ts > 10 ** 14 else ts  # 2025+ files are in microseconds
            rows.append((ts, float(f[5]), float(f[9])))  # open time, volume, taker buy base volume
        return rows
    except Exception:
        return []


def coin(s):
    today = dt.date.today()
    months = [f"{y}-{m:02d}" for y in range(2019, today.year + 1) for m in range(1, 13)
              if (y, m) < (today.year, today.month)]
    days = [(today.replace(day=1) + dt.timedelta(days=i)).isoformat() for i in range(today.day - 1)]
    rows = [r for p in months for r in get(s, "monthly", p)] + [r for p in days for r in get(s, "daily", p)]
    share = {ts: (tb / v if v else 0.5) for ts, v, tb in rows}
    with gzip.open(os.path.join(OUT, f"{s}.json.gz"), "wt") as f:
        json.dump(share, f)
    return s, len(share)


def main():
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(8) as ex:
        for s, n in ex.map(coin, COINS23):
            print(s, n, flush=True)


if __name__ == "__main__":
    main()
