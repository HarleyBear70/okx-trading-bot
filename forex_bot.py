"""
Forex DEMO bot on OANDA's Practice server: RSI(2) snap-back on 7 major pairs, long + short (Jeff, Oct 8 2026:
"build a bot for the demo on oanda"). Places real orders on the PRACTICE account only (fake money); the host is
hard-wired to api-fxpractice, so it can never trade a live account. Separate from bot.py (which is long-only and
runs real crypto money).

Rules (research/F39.md, research/FX_RSI2_TF.md, research/BATTERY.md), daily candles (UTC):
  long : close > 200-day average and RSI(2) < 5  -> buy; exit at the first daily close above the 5-day average
  short: close < 200-day average and RSI(2) > 95 -> sell; exit at the first daily close below the 5-day average
  safety stop 3 ATR(20), held by OANDA (stopLossOnFill); 0.5% risk of the account a trade; one trade per pair.
Backtest 7 majors 2012-now: PF 1.16, win 67%, ~35 trades/year; 2019-now PF 1.33, win 70%.
15m and 1H versions of every strategy tested lost money on forex (research/BATTERY.md), so this bot stays daily.

  python forex_bot.py      (state: forex_state.json, log: forex_trades.csv)
Env: OANDA_TOKEN (GitHub secret OANDAAPIKEYDEMO).
"""
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from bot import atr, rsi, sma  # noqa: E402  (pure indicator functions)

HOST = "https://api-fxpractice.oanda.com"  # PRACTICE ONLY
PAIRS = ["EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY"]
RISK, STOP_ATR, RSI_LO = 0.005, 3.0, 5
STATE = os.path.join(HERE, "forex_state.json")
TRADES = os.path.join(HERE, "forex_trades.csv")
UTC = dt.timezone.utc
TOKEN = os.environ.get("OANDA_TOKEN", "")


def api(method, path, q=None, body=None):
    url = HOST + path + ("?" + urllib.parse.urlencode(q) if q else "")
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json",
                                          "User-Agent": "forex-demo"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d")


def candles(pair):
    rows = api("GET", f"/v3/instruments/{pair}/candles", {"granularity": "D", "count": 300, "price": "M",
                                                          "dailyAlignment": 0, "alignmentTimezone": "UTC"})["candles"]
    return [{"ts": int(dt.datetime.fromisoformat(x["time"][:19]).replace(tzinfo=UTC).timestamp() * 1000),
             "o": float(x["mid"]["o"]), "h": float(x["mid"]["h"]), "l": float(x["mid"]["l"]),
             "c": float(x["mid"]["c"])} for x in rows if x["complete"]]


def signal(bars):
    """(side, stop) for the last bar, or None; and RSI(2)."""
    c = [b["c"] for b in bars]
    h, l = [b["h"] for b in bars], [b["l"] for b in bars]
    s200, r2, a = sma(c, 200), rsi(c, 2), atr(h, l, c, 20)
    k = len(bars) - 1
    if not (s200[k] and r2[k] is not None and a[k]):
        return None, r2[k]
    if c[k] > s200[k] and r2[k] < RSI_LO:
        return (1, c[k] - STOP_ATR * a[k]), r2[k]
    if c[k] < s200[k] and r2[k] > 100 - RSI_LO:
        return (-1, c[k] + STOP_ATR * a[k]), r2[k]
    return None, r2[k]


def log_trade(row):
    new = not os.path.exists(TRADES)
    with open(TRADES, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "pair", "action", "side", "units", "price", "pnl_usd", "balance", "reason"])
        w.writerow(row)


def now():
    return dt.datetime.now(UTC).strftime("%Y-%m-%d %H:%M")


def handle(st, acct, nav, pair):
    bars = candles(pair)
    b = bars[-1]
    if st["last_bar"].get(pair) == b["ts"]:
        return  # this daily candle was already handled
    st["last_bar"][pair] = b["ts"]
    t = st["trades"].get(pair)
    if t:
        avg5 = sum(x["c"] for x in bars[-5:]) / 5
        if not ((b["c"] > avg5) if t["side"] == 1 else (b["c"] < avg5)):
            return
        r = api("PUT", f"/v3/accounts/{acct}/trades/{t['id']}/close", body={"units": "ALL"})
        fill = r.get("orderFillTransaction", {})
        log_trade([now(), pair, "close", t["side"], t["units"], fill.get("price", ""), fill.get("pl", ""),
                   fill.get("accountBalance", ""), "back past the 5-day average"])
        print(f"forex {pair}: CLOSED {'long' if t['side'] == 1 else 'short'} at {fill.get('price')} "
              f"P/L {fill.get('pl')}")
        del st["trades"][pair]
    sig, r2 = signal(bars)
    print(f"forex {pair}: {iso(b['ts'])} close {b['c']} RSI(2) {r2 if r2 is None else round(r2, 1)}"
          f"{' -> SIGNAL' if sig else ''}")
    if not sig:
        return
    side, stop = sig
    dist = abs(b["c"] - stop)
    usd_per_unit = dist if pair.endswith("_USD") else dist / b["c"]  # stop distance in USD per unit
    units = int(nav * RISK / usd_per_unit)
    if units < 1:
        return
    prec = 3 if pair.endswith("JPY") else 5
    r = api("POST", f"/v3/accounts/{acct}/orders", body={"order": {
        "type": "MARKET", "instrument": pair, "units": str(side * units), "timeInForce": "FOK",
        "positionFill": "DEFAULT", "stopLossOnFill": {"price": f"{stop:.{prec}f}"}}})
    fill = r.get("orderFillTransaction")
    if not fill or "tradeOpened" not in fill:
        print(f"forex {pair}: order NOT filled: {json.dumps(r)[:300]}")
        return
    st["trades"][pair] = {"id": fill["tradeOpened"]["tradeID"], "side": side, "units": units,
                          "entry": float(fill["price"])}
    log_trade([now(), pair, "open", side, units, fill["price"], "", fill.get("accountBalance", ""),
               f"RSI(2) {r2:.1f}, stop {stop:.{prec}f}"])
    print(f"forex {pair}: OPENED {'long' if side == 1 else 'short'} {units} units at {fill['price']}, "
          f"stop {stop:.{prec}f}")


def main():
    if not TOKEN:
        print("forex: no OANDA_TOKEN, skipped")
        return
    st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    st.setdefault("last_bar", {})
    st.setdefault("trades", {})  # pair -> {"id", "side", "units", "entry"}
    for k in ("equity", "positions", "host"):  # old paper-bot fields
        st.pop(k, None)
    acct = st.get("account") or api("GET", "/v3/accounts")["accounts"][0]["id"]
    st["account"] = acct
    summ = api("GET", f"/v3/accounts/{acct}/summary")["account"]
    nav = float(summ["NAV"])
    open_ids = {t["id"] for t in api("GET", f"/v3/accounts/{acct}/openTrades")["trades"]}
    # trades OANDA closed on its own (safety stop hit)
    for pair, t in list(st["trades"].items()):
        if t["id"] not in open_ids:
            d = api("GET", f"/v3/accounts/{acct}/trades/{t['id']}")["trade"]
            log_trade([now(), pair, "closed by OANDA", t["side"], t["units"], d.get("averageClosePrice", ""),
                       d.get("realizedPL", ""), summ["balance"], "safety stop"])
            print(f"forex {pair}: trade {t['id']} closed by OANDA (stop), P/L {d.get('realizedPL')}")
            del st["trades"][pair]
    for pair in PAIRS:
        try:
            handle(st, acct, nav, pair)
        except Exception as e:  # one pair failing must not lose what the others did
            print(f"forex {pair}: ERROR {e}")
        with open(STATE, "w") as f:
            json.dump(st, f, indent=1)
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    print(f"forex demo: account {acct} NAV {nav:,.2f}, open {list(st['trades'])}")


if __name__ == "__main__":
    main()
