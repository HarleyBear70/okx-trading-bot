"""
Forex PAPER bot: RSI(2) snap-back on 7 major pairs, long + short (Jeff, Oct 8 2026: "trade on forex also").
Prices from OANDA (read-only: candles only, NEVER places orders). Separate from bot.py, so it can't touch the
live crypto bots.

Rules (research/F39.md, research/FX_RSI2_TF.md), daily candles (UTC):
  long : close > 200-day average and RSI(2) < 5  -> buy at the close; exit at the first close above the 5-day average
  short: close < 200-day average and RSI(2) > 95 -> sell at the close; exit at the first close below the 5-day average
  safety stop 3 ATR(20); 0.5% risk of the balance, leverage cap 10x, cost 0.01% each side, one trade per pair.
Backtest 7 majors 2012-now: PF 1.16, win 67%, drop -2.8%, ~35 trades/year; 2019-now PF 1.33, win 70%.

  python forex_bot.py          # update the paper account (state: forex_state.json, trades: forex_trades.csv)
Env: OANDA_TOKEN (GitHub secret OANDAKEYAPI).
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

PAIRS = ["EUR_USD", "GBP_USD", "AUD_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY"]
HOSTS = ["https://api-fxpractice.oanda.com", "https://api-fxtrade.oanda.com"]
RISK, LEV, COST, STOP_ATR, RSI_LO = 0.005, 10.0, 0.0001, 3.0, 5
STATE = os.path.join(HERE, "forex_state.json")
TRADES = os.path.join(HERE, "forex_trades.csv")
UTC = dt.timezone.utc


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, UTC).strftime("%Y-%m-%d")


def candles(token, pair, host_box):
    q = urllib.parse.urlencode({"granularity": "D", "count": 300, "price": "M", "dailyAlignment": 0,
                                "alignmentTimezone": "UTC"})
    hosts = [host_box[0]] if host_box else HOSTS
    err = None
    for h in hosts:
        req = urllib.request.Request(f"{h}/v3/instruments/{pair}/candles?{q}",
                                     headers={"Authorization": f"Bearer {token}", "User-Agent": "forex-paper"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                rows = json.load(r)["candles"]
            if not host_box:
                host_box.append(h)
            return [{"ts": int(dt.datetime.fromisoformat(x["time"][:19]).replace(tzinfo=UTC).timestamp() * 1000),
                     "o": float(x["mid"]["o"]), "h": float(x["mid"]["h"]), "l": float(x["mid"]["l"]),
                     "c": float(x["mid"]["c"]), "complete": x["complete"]} for x in rows]
        except Exception as e:  # wrong host for this token (practice vs live) -> try the other
            err = e
    raise RuntimeError(f"OANDA candles failed for {pair}: {err}")


def signal(bars):
    """(side, stop) for the last bar, or None; plus the exit check for an open trade."""
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
            w.writerow(["date_utc", "pair", "action", "side", "price", "units", "pnl_usd", "equity", "reason"])
        w.writerow(row)


def main():
    token = os.environ.get("OANDA_TOKEN")
    if not token:
        print("forex: no OANDA_TOKEN, skipped")
        return
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"equity": 1000.0, "positions": {}, "last_bar": {}}
    host = [st["host"]] if st.get("host") else []
    for pair in PAIRS:
        bars = [b for b in candles(token, pair, host) if b["complete"]]
        b = bars[-1]
        if st["last_bar"].get(pair) == b["ts"]:
            continue  # this daily candle was already handled
        st["last_bar"][pair] = b["ts"]
        p = st["positions"].get(pair)
        if p:
            side = p["side"]
            avg5 = sum(x["c"] for x in bars[-5:]) / 5
            px, why = None, None
            if (b["l"] <= p["stop"]) if side == 1 else (b["h"] >= p["stop"]):
                px = min(p["stop"], b["o"]) if side == 1 else max(p["stop"], b["o"])
                why = "safety stop"
            elif (b["c"] > avg5) if side == 1 else (b["c"] < avg5):
                px, why = b["c"], "back past the 5-day average"
            if px is not None:
                # same P/L as the backtest: in risk units, so it's in USD for every pair
                pnl = side * (px - p["entry"]) * p["units"] - (p["entry"] + px) * p["units"] * COST
                st["equity"] += pnl
                del st["positions"][pair]
                log_trade([iso(b["ts"]), pair, "close", side, px, round(p["units"], 4), round(pnl, 2),
                           round(st["equity"], 2), why])
                print(f"forex {pair}: CLOSE {'long' if side == 1 else 'short'} at {px} ({why}) P/L {pnl:+.2f}")
        if pair in st["positions"]:
            continue
        sig, r2 = signal(bars)
        print(f"forex {pair}: {iso(b['ts'])} close {b['c']} RSI(2) {r2 if r2 is None else round(r2, 1)}"
              f"{' -> SIGNAL' if sig else ''}")
        if sig:
            side, stop = sig
            dist = abs(b["c"] - stop)
            units = min(st["equity"] * RISK / dist, st["equity"] * LEV / b["c"])
            st["positions"][pair] = {"side": side, "entry": b["c"], "stop": stop, "units": units, "ts": b["ts"]}
            log_trade([iso(b["ts"]), pair, "open", side, b["c"], round(units, 4), "", round(st["equity"], 2),
                       f"RSI(2) {r2:.1f}, stop {stop:.5g}"])
    if host:
        st["host"] = host[0]
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    print(f"forex paper: equity ${st['equity']:.2f}, open {list(st['positions'])}, OANDA {st.get('host', '?')}")


if __name__ == "__main__":
    main()
