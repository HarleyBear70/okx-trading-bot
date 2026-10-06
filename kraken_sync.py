"""
Kraken account reader for the dashboard. READ-ONLY: it calls only the query endpoints listed in READ_ONLY and can never
place, change or cancel an order or move money, whatever permissions the key has.

Every hour (bot.yml) it writes journal/kraken.json: balances valued in USD, the account's fee tier for the coins the
bots use, recent trades and open orders. Any endpoint the key isn't allowed to use is recorded under "errors" (e.g.
"EGeneral:Permission denied"), so the dashboard can say which permission to switch on.

Secrets (GitHub → Settings → Secrets and variables → Actions): KRAKEN_API_KEY, KRAKEN_PRIVATE_KEY.
Run by hand: python kraken_sync.py
"""
import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import time
import urllib.parse
import urllib.request

URL = "https://api.kraken.com"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "journal", "kraken.json")
READ_ONLY = {"Balance", "TradeVolume", "TradesHistory", "OpenOrders"}
FEE_PAIRS = ["XBTUSD", "ETHUSD", "XRPUSD"]  # the Kraken bot's coins


def sign(path, data, secret):
    """Kraken API-Sign: HMAC-SHA512 of path + SHA256(nonce + POST body), keyed with the base64-decoded secret."""
    body = urllib.parse.urlencode(data)
    digest = hashlib.sha256((data["nonce"] + body).encode()).digest()
    return base64.b64encode(hmac.new(base64.b64decode(secret), path.encode() + digest, hashlib.sha512).digest()).decode(), body


def pair_coin(p):
    """XXBTZUSD / XBTUSD / ETHUSD -> BTC / ETH."""
    for end in ("ZUSD", "USD"):
        if p.endswith(end):
            return coin(p[: -len(end)])
    return coin(p)


def private(method, data=None):
    if method not in READ_ONLY:
        raise ValueError(f"{method} is not a read-only endpoint")
    key, secret = os.environ["KRAKEN_API_KEY"], os.environ["KRAKEN_PRIVATE_KEY"]
    path = f"/0/private/{method}"
    data = {"nonce": str(int(time.time() * 1000)), **(data or {})}
    sig, body = sign(path, data, secret)
    req = urllib.request.Request(URL + path, body.encode(), {
        "API-Key": key, "API-Sign": sig,
        "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "okx-trading-bot dashboard"})
    out = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if out.get("error"):
        raise RuntimeError(", ".join(out["error"]))
    time.sleep(1.1)  # stay well inside Kraken's private rate limit
    return out["result"]


def ticker(pairs):
    q = urllib.parse.urlencode({"pair": ",".join(pairs)})
    out = json.loads(urllib.request.urlopen(f"{URL}/0/public/Ticker?{q}", timeout=30).read())
    return out.get("result", {})


def coin(asset):
    """Kraken asset code -> plain coin name (XXBT -> BTC, ZUSD -> USD, XETH -> ETH, SOL.F -> SOL)."""
    a = asset.split(".")[0]
    if len(a) == 4 and a[0] in "XZ" and a not in ("ZEUS",):
        a = a[1:]
    return {"XBT": "BTC", "XDG": "DOGE"}.get(a, a)


def main():
    res = {"updated_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"), "errors": {}}
    if not os.environ.get("KRAKEN_API_KEY") or not os.environ.get("KRAKEN_PRIVATE_KEY"):
        res["errors"]["setup"] = "KRAKEN_API_KEY / KRAKEN_PRIVATE_KEY not set"
    else:
        try:
            bal = {coin(a): float(v) for a, v in private("Balance").items() if float(v) > 0}
            px = {}
            want = [c for c in bal if c not in ("USD", "USDT", "USDC")]
            if want:
                for k, v in ticker([("XBT" if c == "BTC" else c) + "USD" for c in want]).items():
                    for c in want:
                        alt = "XBT" if c == "BTC" else c
                        if k in (alt + "USD", "X" + alt + "ZUSD"):
                            px[c] = float(v["c"][0])
            res["balances"] = [{"coin": c, "amount": a, "usd": round(a * (1.0 if c in ("USD", "USDT", "USDC") else px.get(c, 0)), 2),
                                "priced": c in ("USD", "USDT", "USDC") or c in px} for c, a in sorted(bal.items())]
            res["total_usd"] = round(sum(b["usd"] for b in res["balances"]), 2)
        except Exception as e:
            res["errors"]["Balance"] = str(e)
        try:
            tv = private("TradeVolume", {"pair": ",".join(FEE_PAIRS)})
            res["fees"] = {"volume_30d_usd": float(tv.get("volume") or 0),
                           "taker": {pair_coin(p): float(f["fee"]) for p, f in (tv.get("fees") or {}).items()},
                           "maker": {pair_coin(p): float(f["fee"]) for p, f in (tv.get("fees_maker") or {}).items()}}
        except Exception as e:
            res["errors"]["TradeVolume"] = str(e)
        try:
            th = private("TradesHistory")
            res["trades_count"] = int(th.get("count") or 0)
            res["trades"] = sorted([{"id": tid, "pair": t["pair"], "time": t["time"], "side": t["type"], "type": t["ordertype"],
                                     "price": float(t["price"]), "cost": float(t["cost"]), "fee": float(t["fee"]),
                                     "vol": float(t["vol"])} for tid, t in (th.get("trades") or {}).items()],
                                   key=lambda x: -x["time"])
        except Exception as e:
            res["errors"]["TradesHistory"] = str(e)
        try:
            oo = private("OpenOrders")
            res["open_orders"] = [{"id": oid, "pair": o["descr"]["pair"], "side": o["descr"]["type"], "type": o["descr"]["ordertype"],
                                   "price": o["descr"]["price"], "vol": float(o["vol"]), "opened": o["opentm"]}
                                  for oid, o in (oo.get("open") or {}).items()]
        except Exception as e:
            res["errors"]["OpenOrders"] = str(e)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(res, f, indent=1)
    print("kraken:", "ok" if not res["errors"] else res["errors"], "| total", res.get("total_usd"), "| trades", res.get("trades_count"))


if __name__ == "__main__":
    main()
