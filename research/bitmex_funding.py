"""Download BitMEX XBTUSD funding-rate history (public, no key) to research/.cache/bitmex_funding_XBTUSD.json.
Used by F11 (L3 crowding filter) as the market-wide funding signal, since Binance/Bybit block the US and OKX keeps ~3 months."""
import json
import os
import time
import urllib.request

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".cache", "bitmex_funding_XBTUSD.json")
rows, start = [], 0
while True:
    url = f"https://www.bitmex.com/api/v1/funding?symbol=XBTUSD&count=500&start={start}&reverse=false&startTime=2017-12-01"
    page = json.loads(urllib.request.urlopen(url, timeout=30).read())
    rows += [{"t": r["timestamp"], "rate": r["fundingRate"]} for r in page]
    if len(page) < 500:
        break
    start += 500
    time.sleep(2.5)
with open(OUT, "w") as f:
    json.dump(rows, f)
print(len(rows), rows[0]["t"], "->", rows[-1]["t"])
