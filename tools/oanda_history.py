"""Download OANDA history (bid/ask, M15 + H1) for the research battery. Read-only; runs in GitHub Actions
(.github/workflows/oanda-history.yml) where the Practice token lives. Writes oanda_hist/<PAIR>_<GRAN>.json.gz:
rows [ts_ms, o, h, l, c (mid), spread_at_close, volume]. Also prints the Practice account id(s)."""
import datetime as dt
import gzip
import json
import os
import time
import urllib.parse
import urllib.request

HOST = "https://api-fxpractice.oanda.com"
TOKEN = os.environ["OANDA_TOKEN"]
PAIRS = os.environ.get("PAIRS", "").split() or ["EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF",
                                                "USD_JPY", "XAU_USD"]
GRANS = os.environ.get("GRANS", "").split() or ["H1", "M15"]  # Oct 10 2026: M5 for the Brad forex test
START = "2019-01-01T00:00:00Z"


def get(path, q=None):
    url = HOST + path + ("?" + urllib.parse.urlencode(q) if q else "")
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:
            print("retry", e, flush=True)
            time.sleep(3 * (i + 1))
    raise RuntimeError(url)


def ts(s):
    return int(dt.datetime.fromisoformat(s[:19]).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def main():
    print("accounts:", [a["id"] for a in get("/v3/accounts")["accounts"]])
    os.makedirs("oanda_hist", exist_ok=True)
    for gran in GRANS:
        for p in PAIRS:
            rows, frm = [], START
            while True:
                d = get(f"/v3/instruments/{p}/candles", {"granularity": gran, "price": "MBA", "from": frm,
                                                          "count": 5000})
                cs = [c for c in d["candles"] if c["complete"]]
                for c in cs:
                    m = c["mid"]
                    rows.append([ts(c["time"]), float(m["o"]), float(m["h"]), float(m["l"]), float(m["c"]),
                                 float(c["ask"]["c"]) - float(c["bid"]["c"]), c["volume"]])
                if len(d["candles"]) < 5000 or not cs:
                    break
                frm = d["candles"][-1]["time"]
                rows = [r for i, r in enumerate(rows) if i == 0 or r[0] > rows[i - 1][0]]
            with gzip.open(f"oanda_hist/{p}_{gran}.json.gz", "wt") as f:
                json.dump(rows, f)
            print(gran, p, len(rows), flush=True)


if __name__ == "__main__":
    main()
