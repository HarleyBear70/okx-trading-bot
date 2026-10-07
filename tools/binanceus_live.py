"""
Binance.US live connection, step 1: a small signed client and a supervised $10 round-trip test (Jeff, Oct 7 2026:
"money in binance 100, start it up, test it"). Runs only in GitHub Actions (keys are the BINANCEBOTAPI /
BINACEBOTSECRET secrets; never printed). Workflow: .github/workflows/binanceus-live-test.yml.

  python tools/binanceus_live.py check   # balances (USD, USDC, BTC) + key permissions; no orders
  python tools/binanceus_live.py trade   # $10 test: validate -> market buy $10 BTC -> exchange stop 3% below ->
                                         # cancel the stop -> market sell it all back. Hard cap $12.
"""
import hashlib
import hmac
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://api.binance.us"
TEST_USD, CAP_USD = 10.0, 12.0


class BinanceUS:
    def __init__(self, key, secret):
        self.key, self.secret = key.strip(), secret.strip()

    def _req(self, method, path, params=None, signed=False):
        params = dict(params or {})
        if signed:
            params.update({"timestamp": int(time.time() * 1000), "recvWindow": 10000})
        q = urllib.parse.urlencode(params)
        if signed:
            q += "&signature=" + hmac.new(self.secret.encode(), q.encode(), hashlib.sha256).hexdigest()
        url = f"{BASE}{path}" + (f"?{q}" if q and method in ("GET", "DELETE") else "")
        data = q.encode() if method == "POST" else None
        req = urllib.request.Request(url, data=data, method=method,
                                     headers={"X-MBX-APIKEY": self.key, "User-Agent": "sp12-bot",
                                              "Content-Type": "application/x-www-form-urlencoded"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"Binance.US {method} {path}: HTTP {e.code} {e.read().decode()[:300]}")

    def account(self):
        return self._req("GET", "/api/v3/account", signed=True)

    def balances(self):
        return {b["asset"]: (float(b["free"]), float(b["locked"])) for b in self.account()["balances"]
                if float(b["free"]) or float(b["locked"])}

    def rules(self, symbol):
        s = self._req("GET", "/api/v3/exchangeInfo", {"symbol": symbol})["symbols"][0]
        f = {x["filterType"]: x for x in s["filters"]}
        notional = f.get("NOTIONAL") or f.get("MIN_NOTIONAL") or {}
        return {"step": float(f["LOT_SIZE"]["stepSize"]), "tick": float(f["PRICE_FILTER"]["tickSize"]),
                "min_notional": float(notional.get("minNotional", 1.0)), "types": s["orderTypes"]}

    def price(self, symbol):
        return float(self._req("GET", "/api/v3/ticker/price", {"symbol": symbol})["price"])

    def order(self, test=False, **p):
        p.setdefault("newOrderRespType", "FULL")
        return self._req("POST", "/api/v3/order/test" if test else "/api/v3/order", p, signed=True)

    def cancel(self, symbol, order_id):
        return self._req("DELETE", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, signed=True)

    def get_order(self, symbol, order_id):
        return self._req("GET", "/api/v3/order", {"symbol": symbol, "orderId": order_id}, signed=True)


def floor_step(x, step):
    return math.floor(x / step + 1e-9) * step


def fmt(x, step):
    dec = max(0, -int(math.floor(math.log10(step)))) if step < 1 else 0
    return f"{floor_step(x, step):.{dec}f}"


def fills_summary(o):
    fills = o.get("fills", [])
    qty = sum(float(f["qty"]) for f in fills) or float(o.get("executedQty", 0))
    quote = sum(float(f["qty"]) * float(f["price"]) for f in fills) or float(o.get("cummulativeQuoteQty", 0))
    fees = {}
    for f in fills:
        fees[f["commissionAsset"]] = fees.get(f["commissionAsset"], 0.0) + float(f["commission"])
    return qty, quote, fees


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "check").lower()
    api = BinanceUS(os.environ.get("BINANCEUS_KEY", ""), os.environ.get("BINANCEUS_SECRET", ""))
    bal = api.balances()
    acct = api.account()
    print(f"key works: YES | can trade: {'YES' if acct.get('canTrade') else 'NO'}")
    for a in ("USD", "USDC", "USDT", "BTC"):
        if a in bal:
            print(f"balance {a}: free {bal[a][0]:.8g}, locked {bal[a][1]:.8g}")
    if mode != "trade":
        print("check only: no orders placed")
        return
    quote = "USD" if bal.get("USD", (0, 0))[0] >= TEST_USD + 1 else "USDC" if bal.get("USDC", (0, 0))[0] >= TEST_USD + 1 else None
    if not quote:
        raise SystemExit("STOP: less than $11 free in USD and in USDC - deposit not arrived yet? No orders placed.")
    sym = "BTC" + quote
    r = api.rules(sym)
    px = api.price(sym)
    assert TEST_USD <= CAP_USD and "STOP_LOSS" in r["types"]
    print(f"\nTEST on {sym} at about {px:,.2f}: buy ${TEST_USD:.0f}, stop 3% below, cancel, sell back")
    api.order(test=True, symbol=sym, side="BUY", type="MARKET", quoteOrderQty=f"{TEST_USD:.2f}")
    print("1. test order validated by Binance.US (nothing placed)")
    b = api.order(symbol=sym, side="BUY", type="MARKET", quoteOrderQty=f"{TEST_USD:.2f}")
    bq, bcost, bfees = fills_summary(b)
    print(f"2. BOUGHT {bq:.8g} BTC for ${bcost:.4f} (avg {bcost / bq:,.2f}); fees {bfees}")
    sell_qty = floor_step(bq - bfees.get("BTC", 0.0), r["step"])
    stop_px = floor_step(px * 0.97, r["tick"])
    s = api.order(symbol=sym, side="SELL", type="STOP_LOSS", quantity=fmt(sell_qty, r["step"]),
                  stopPrice=fmt(stop_px, r["tick"]))
    st = api.get_order(sym, s["orderId"])
    print(f"3. exchange STOP placed: sell {fmt(sell_qty, r['step'])} BTC if price hits {stop_px:,.2f} -> status {st['status']}")
    c = api.cancel(sym, s["orderId"])
    print(f"4. stop cancelled -> status {c.get('status')}")
    x = api.order(symbol=sym, side="SELL", type="MARKET", quantity=fmt(sell_qty, r["step"]))
    sq, sval, sfees = fills_summary(x)
    print(f"5. SOLD {sq:.8g} BTC for ${sval:.4f} (avg {sval / sq:,.2f}); fees {sfees}")
    fee_usd = bfees.get(quote, 0) + sfees.get(quote, 0) + (bfees.get("BTC", 0) + sfees.get("BTC", 0)) * px
    print(f"\nRESULT: spent ${bcost:.4f}, got back ${sval:.4f} -> net ${sval - bcost - sfees.get(quote, 0):+.4f} "
          f"(fees about ${fee_usd:.4f}; other fee assets: {[k for k in {**bfees, **sfees} if k not in (quote, 'BTC')]})")
    left = api.balances()
    print(f"leftover BTC dust: {left.get('BTC', (0, 0))[0]:.8g}")


if __name__ == "__main__":
    main()
