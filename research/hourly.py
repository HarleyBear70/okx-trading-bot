"""
1H candles from the Binance public archive (one source per coin) and 4H candles built from them.
Used by the box bots (B1, B2) and the 1H day bots (D1). Cached in research/.cache/H1_<coin>.json.
"""
import csv
import io
import json
import os
import re
import sys
import time
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import universe as u  # noqa: E402

CACHE = u.CACHE
H1, H4 = 3600000, 4 * 3600000
SYMBOLS = {"BCH": ["BCCUSDT", "BCHABCUSDT", "BCHUSDT"]}  # renamed tickers, spliced
CUT = {"LUNA": 1652400000000}  # 2022-05-13: Binance reused LUNAUSDT for Terra 2.0


def _binance(sym):
    listing = u.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/spot/monthly/klines/"
                    f"{sym}/1h/&delimiter=/").decode()
    rows = {}
    for m in re.findall(rf"{sym}-1h-(\d{{4}}-\d{{2}})\.zip</Key>", listing):
        blob = u.get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1h/{sym}-1h-{m}.zip")
        if not blob:
            continue
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
                if x and x[0].isdigit():
                    ts = int(x[0])
                    ts = ts // 1000 if ts > 10 ** 14 else ts
                    rows[ts] = {"ts": ts, "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]),
                                "v": float(x[5]), "confirm": True}
    return rows


def hourly(coin):
    path = os.path.join(CACHE, f"H1_{coin}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    print(f"downloading {coin} 1H from Binance ...", flush=True)
    rows = {}
    for sym in SYMBOLS.get(coin, [f"{coin}USDT"]):
        rows.update(_binance(sym))
    bars = [rows[k] for k in sorted(rows) if k < CUT.get(coin, 1 << 62) and k + H1 <= time.time() * 1000]
    with open(path, "w") as f:
        json.dump(bars, f)
    return bars


def to_4h(bars):
    out = {}
    for b in bars:
        k = b["ts"] - b["ts"] % H4
        if k not in out:
            out[k] = {"ts": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"], "n": 1, "confirm": True}
        else:
            x = out[k]
            x["h"], x["l"], x["c"], x["v"], x["n"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"], x["v"] + b["v"], x["n"] + 1
    return [x for x in sorted(out.values(), key=lambda x: x["ts"]) if x["n"] == 4]


if __name__ == "__main__":
    for c in sys.argv[1:]:
        b = hourly(c)
        print(c, len(b), flush=True)
