"""5m candles from the Binance public archive, cached in research/.cache/M5_<coin>.json (from 2019)."""
import csv, io, json, os, re, sys, time, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import universe as u  # noqa: E402


def m5(coin):
    path = os.path.join(u.CACHE, f"M5_{coin}.json")
    if os.path.exists(path):
        return json.load(open(path))
    sym = f"{coin}USDT"
    listing = u.get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/spot/monthly/klines/"
                    f"{sym}/5m/&delimiter=/").decode()
    rows = {}
    for m in re.findall(rf"{sym}-5m-(\d{{4}}-\d{{2}})\.zip</Key>", listing):
        if m < "2019-01":
            continue
        blob = u.get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/5m/{sym}-5m-{m}.zip")
        if not blob:
            continue
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
                if x and x[0].isdigit():
                    ts = int(x[0]); ts = ts // 1000 if ts > 10 ** 14 else ts
                    rows[ts] = {"ts": ts, "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4]), "v": float(x[5])}
    bars = [rows[k] for k in sorted(rows)]
    json.dump(bars, open(path, "w"))
    return bars


if __name__ == "__main__":
    for c in sys.argv[1:]:
        print(c, len(m5(c)), flush=True)
