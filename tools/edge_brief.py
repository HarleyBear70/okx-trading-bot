"""
Edge brief (Jeff, Oct 7 2026: "add everything I would need to get an edge"). One plain-English page, built from
public data only (no keys, never trades). The News Watch adds the news on top and emails the morning edition.

Sections:
  1. Crypto chart read (daily + 4H): trend, phase, must-hold level, liquidity targets (analyst/chart_read.py =
     the Smoke Detector's rules) for BTC ETH SOL XRP BNB LINK.
  2. Mood: Crypto Fear & Greed (yesterday).
  3. Whales: Hyperliquid's most profitable traders' positions + funding / open interest (tools/whale_check.py).
  4. Forex: dollar index (DXY) trend vs its 50-day EMA -> which way to lean on EUR/USD and GBP/USD (tested filter,
     research/FOREX_DXY.md), plus each pair's daily trend and RSI(2) setup check (research/F39.md).
  5. Bots: open trades and balances (state.json), and the Claudes' waiting orders.

  python tools/edge_brief.py > EDGE.md
"""
import datetime as dt
import io
import json
import os
import subprocess
import sys
import urllib.request
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "analyst"))
import bot  # noqa: E402

COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK"]
UA = {"User-Agent": "Mozilla/5.0"}


def get_json(url):
    return json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read())


def yahoo_daily(symbol, days=300):
    r = get_json(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=2y&interval=1d")["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    rows = [(t, o, h, l, c) for t, o, h, l, c in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"])
            if None not in (o, h, l, c)]
    return rows[-days:]


def section(title, fn):
    out = io.StringIO()
    try:
        with redirect_stdout(out):
            fn()
    except Exception as ex:
        print(f"(unavailable: {str(ex)[:120]})", file=out)
    return f"## {title}\n\n{out.getvalue().strip()}\n"


def crypto():
    import chart_read
    print("| Coin | Daily | 4-hour | Must hold (4H) | Next liquidity above | below |\n|---|---|---|---|---|---|")
    api = bot.OKX("", "", "")
    for c in COINS:
        rd = chart_read.read([b for b in api.candles(f"{c}-USDT", "1Dutc", 300) if b["confirm"]])
        r4 = chart_read.read([b for b in api.candles(f"{c}-USDT", "4H", 300) if b["confirm"]])
        tr = {1: "UP", -1: "DOWN", 0: "no trend"}
        f = chart_read.fmt
        print(f"| {c} {f(r4['px'])} | {tr[rd['trend']]}, {rd['phase']} | {tr[r4['trend']]}, {r4['phase']} | "
              f"{f(r4['strong'])} | {f(r4['above'][0]) if r4['above'] else 'new highs'} | "
              f"{f(r4['below'][0]) if r4['below'] else '-'} |")


def mood():
    fg = bot.fear_greed()
    k = sorted(fg)[-7:]
    v = fg[k[-1]]
    word = "extreme fear" if v <= 25 else "fear" if v < 45 else "neutral" if v <= 55 else "greed" if v < 75 else "extreme greed"
    print(f"Fear & Greed: **{v} ({word})**; last 7 days: {', '.join(str(fg[x]) for x in k)}.")
    print("Trend Rider skips new buys at 25 or below.")


def whales():
    out = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "whale_check.py")], capture_output=True,
                         text=True, timeout=240).stdout
    print(out.strip())
    print("\nContext, not a signal: a few big wallets dominate and some are hedges.")


def forex():
    def ema(xs, n):
        return bot.ema(xs, n)[-1]
    d = yahoo_daily("DX-Y.NYB")
    c = [x[4] for x in d]
    e50 = ema(c, 50)
    weak = c[-1] < e50
    print(f"Dollar index (DXY) {c[-1]:.2f} vs its 50-day EMA {e50:.2f}: **dollar {'WEAK' if weak else 'STRONG'}** "
          f"-> lean {'BUY' if weak else 'SELL'} on EUR/USD and GBP/USD (only when the pair's own chart agrees).\n")
    print("| Pair | Price | Daily trend (vs 50 EMA) | Agrees with dollar? | RSI(2) setup today |\n|---|---|---|---|---|")
    for sym, name in (("EURUSD=X", "EUR/USD"), ("GBPUSD=X", "GBP/USD")):
        p = yahoo_daily(sym)
        pc = [x[4] for x in p]
        up = pc[-1] > ema(pc, 50)
        s200 = sum(pc[-200:]) / 200
        r2 = bot.rsi(pc, 2)[-1]
        setup = ("BUY setup (RSI(2) < 5 above SMA200)" if pc[-1] > s200 and r2 < 5 else
                 "SELL setup (RSI(2) > 95 below SMA200)" if pc[-1] < s200 and r2 > 95 else f"none (RSI(2) {r2:.0f})")
        agree = (up and weak) or (not up and not weak)
        print(f"| {name} | {pc[-1]:.4f} | {'UP' if up else 'DOWN'} | {'YES' if agree else 'no - skip'} | {setup} |")


def bots():
    st = json.load(open(os.path.join(ROOT, "state.json")))["bots"]
    names = {b["id"]: b["name"] for b in bot.BOTS if not b.get("retired")}
    opn = [(names[k], c, p["entry_px"], p["stop"]) for k, v in st.items() if k in names
           for c, p in v.get("positions", {}).items()]
    print("Open trades: " + ("; ".join(f"{n} {c.split('-')[0]} from {e:,.6g} (stop {s:,.6g})" for n, c, e, s in opn)
                             if opn else "none (bots are waiting for setups)"))
    for lab, path in (("Claude", "analyst/ledger.json"), ("Chrome Claude", "analyst/chrome/ledger.json")):
        try:
            led = json.load(open(os.path.join(ROOT, path)))
            o = led.get("orders", {})
            print(f"{lab}: balance ${led['equity']:,.2f}; waiting orders: "
                  + (", ".join(f"{c} {x['side']} {x['trigger']:g}" for c, x in o.items()) or "none"))
        except Exception:
            pass


def main():
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    print(f"# Edge brief ({now})\n\nEverything that gives an edge, in one place. Public data only. Read top to bottom.\n")
    for title, fn in (("1. Crypto charts (Smoke Detector rules)", crypto), ("2. Market mood", mood),
                      ("3. Whale check (Hyperliquid)", whales), ("4. Forex: EUR/USD and GBP/USD", forex),
                      ("5. Bots and Claudes", bots)):
        print(section(title, fn))


if __name__ == "__main__":
    main()
