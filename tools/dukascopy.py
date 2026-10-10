"""
Free 5m forex history from Dukascopy's public datafeed (Oct 10 2026, Jeff: "test the Brad day method on forex").
Downloads 1-minute BID and ASK candles per UTC day, builds 5m BID candles + the average real spread (ask - bid).
Read-only, no account or key. Output: research/.cache/bin/FX5_<PAIR>_{ts,o,h,l,c,sp}.bin

  python3 tools/dukascopy.py EURUSD GBPUSD ...
"""
import array
import datetime as dt
import lzma
import os
import struct
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("FX_OUT") or os.path.join(HERE, "..", "research", ".cache", "bin")
POINT = {"USDJPY": 1e3, "GBPJPY": 1e3, "XAUUSD": 1e3, "DOLLARIDXUSD": 1e3}
HDR = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.dukascopy.com/"}
START = dt.date(2018, 11, 1)


def get(pair, day, side):
    u = (f"https://datafeed.dukascopy.com/datafeed/{pair}/{day.year}/{day.month - 1:02d}/{day.day:02d}/"
         f"{side}_candles_min_1.bi5")
    for k in range(8):
        try:
            b = urllib.request.urlopen(urllib.request.Request(u, headers=HDR), timeout=30).read()
            if not b:
                return []
            raw = lzma.decompress(b)
            base = int(dt.datetime(day.year, day.month, day.day, tzinfo=dt.timezone.utc).timestamp())
            p = POINT.get(pair, 1e5)
            return [(base + r[0], r[1] / p, r[4] / p, r[3] / p, r[2] / p, r[5])  # file: t, open, close, low, high, vol
                    for r in struct.iter_unpack(">5if", raw)]
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return []
        except Exception:
            pass
        time.sleep(2 + 2 * k)
    raise RuntimeError(f"{pair} {day} {side}: failed")


def day5(pair, day):
    bid, ask = get(pair, day, "BID"), get(pair, day, "ASK")
    ak = {r[0]: r[4] for r in ask}
    out = {}
    for t, o, h, l, c, v in bid:
        if v <= 0:  # no trading in that minute
            continue
        k = t - t % 300
        sp = ak.get(t, c) - c
        x = out.get(k)
        if x is None:
            out[k] = [o, h, l, c, sp, 1]
        else:
            x[1], x[2], x[3] = max(x[1], h), min(x[2], l), c
            x[4] += sp
            x[5] += 1
    return [(k * 1000, x[0], x[1], x[2], x[3], max(x[4] / x[5], 0.0)) for k, x in sorted(out.items())]


def main():
    days = [START + dt.timedelta(n) for n in range((dt.date.today() - START).days)]
    days = [d for d in days if d.weekday() != 5]  # Saturday is always closed
    for pair in sys.argv[1:]:
        t0 = time.time()
        with ThreadPoolExecutor(6) as ex:
            rows = [r for part in ex.map(lambda d: day5(pair, d), days) for r in part]
        cols = list(zip(*rows))
        for k, col in zip(("ts", "o", "h", "l", "c", "sp"), cols):
            array.array("q" if k == "ts" else "d", col).tofile(open(os.path.join(OUT, f"FX5_{pair}_{k}.bin"), "wb"))
        print(f"{pair}: {len(rows)} 5m candles, {dt.datetime.fromtimestamp(rows[0][0] / 1000, dt.timezone.utc):%Y-%m-%d}"
              f" to {dt.datetime.fromtimestamp(rows[-1][0] / 1000, dt.timezone.utc):%Y-%m-%d}, {time.time() - t0:.0f}s",
              flush=True)


if __name__ == "__main__":
    main()
