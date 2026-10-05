"""
Historical top-coin universe for the rotation bot (N2): CoinMarketCap monthly snapshots (as listed at the
time) plus daily closes for every coin that appeared, from the Binance archive or Bitfinex.
Everything is cached in research/.cache/.
"""
import csv
import datetime as dt
import glob
import io
import json
import os
import re
import time
import urllib.error
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
UTC = dt.timezone.utc
UA = {"User-Agent": "Mozilla/5.0"}
STABLE = {"USDT", "USDC", "BUSD", "DAI", "TUSD", "UST", "USDe", "USD1", "WBTC"}
DAY = 86400000

# CMC symbol -> price series, in order (later ones overwrite earlier ones on the same days)
SOURCES = {
    "BCH": [("binance", "BCCUSDT"), ("binance", "BCHABCUSDT"), ("binance", "BCHUSDT")],
    "MIOTA": [("binance", "IOTAUSDT")],
    "MATIC": [("binance", "MATICUSDT"), ("binance", "POLUSDT")],  # 1:1 migration to POL
    "BSV": [("bitfinex", "tBSVUSD")],
    "LEO": [("bitfinex", "tLEOUSD")],
}
NO_DATA = {"CRO", "HYPE", "HEX", "HT", "PPT", "CC", "GRAM", "TAGZ5", "999", "MIN"}
CUT = {"LUNA": "2022-05-13"}  # Binance reused LUNAUSDT for Terra 2.0


def get(url, tries=6):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(65 if e.code == 429 else 5 * (k + 1))
        except Exception:
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {url}")


def snapshots():
    """{date 'YYYY-MM-DD': [symbols in rank order, top 20]} for the first Sunday of each month since 2018."""
    os.makedirs(os.path.join(CACHE, "cmc"), exist_ok=True)
    out, d = {}, dt.date(2018, 1, 1)
    today = dt.datetime.now(UTC).date()
    while d <= today:
        s = d
        while s.weekday() != 6:
            s += dt.timedelta(days=1)
        if s > today:
            break
        path = os.path.join(CACHE, "cmc", f"{s:%Y%m%d}.json")
        if not os.path.exists(path):
            t = get(f"https://coinmarketcap.com/historical/{s:%Y%m%d}/").decode("utf-8", "replace")
            with open(path, "w") as f:
                json.dump(re.findall(r'cmc-table__column-name--symbol[^>]*>([A-Za-z0-9.$-]+)<', t), f)
            time.sleep(1)
        with open(path) as f:
            out[str(s)] = json.load(f)[:20]
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out


def ranked(snap, lo, hi):
    """Symbols ranked lo..hi (1-based, inclusive) after removing stablecoins / wrapped coins."""
    return [x for x in snap if x not in STABLE][lo - 1:hi]


def _binance_daily(sym):
    listing = get(f"https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=data/spot/monthly/klines/"
                  f"{sym}/1d/&delimiter=/").decode()
    months = re.findall(rf"{sym}-1d-(\d{{4}}-\d{{2}})\.zip</Key>", listing)
    rows = {}
    for m in months:
        blob = get(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1d/{sym}-1d-{m}.zip")
        if not blob:
            continue
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
                if x and x[0].isdigit():
                    ts = int(x[0])
                    ts = ts // 1000 if ts > 10 ** 14 else ts
                    rows[ts - ts % DAY] = float(x[4])
    return rows


def _bitfinex_daily(sym):
    rows, start = {}, 1356998400000
    while True:
        raw = json.loads(get(f"https://api-pub.bitfinex.com/v2/candles/trade:1D:{sym}/hist?limit=10000&sort=1&start={start}"))
        if raw and raw[0] == "error":
            time.sleep(65)
            continue
        for x in raw or []:
            rows[x[0] - x[0] % DAY] = float(x[2])
        if not raw or len(raw) < 10000:
            break
        start = raw[-1][0] + 1
        time.sleep(4)
    time.sleep(4)
    return rows


def daily(symbol):
    """{day ms: close} for a CMC symbol, or {} if no free data."""
    if symbol in NO_DATA or symbol in STABLE:
        return {}
    path = os.path.join(CACHE, f"D_{symbol}.json")
    if os.path.exists(path):
        with open(path) as f:
            return {int(k): v for k, v in json.load(f).items()}
    rows = {}
    for src, sym in SOURCES.get(symbol, [("binance", f"{symbol}USDT")]):
        rows.update(_binance_daily(sym) if src == "binance" else _bitfinex_daily(sym))
    if symbol in CUT:
        cut = int(dt.datetime.fromisoformat(CUT[symbol]).replace(tzinfo=UTC).timestamp() * 1000)
        rows = {k: v for k, v in rows.items() if k < cut}
    today = int(time.time() * 1000) // DAY * DAY
    rows = {k: v for k, v in rows.items() if k < today}  # completed days only
    with open(path, "w") as f:
        json.dump(rows, f)
    return rows


def all_symbols():
    return sorted({x for s in snapshots().values() for x in ranked(s, 1, 20)})
