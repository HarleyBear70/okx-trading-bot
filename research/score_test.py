"""
Score test: SP-12 v4 with the score as it is in bot.py now vs. three other score lines.

bot.py line 391 adds c1, c7, c11, c12 and SUBTRACTS c3 (BOS), c5 (FVG retest), c6 (OB retest)
and c10 (engulf / hammer). Versions tested: as now, all 8 added, BOS added with the other three
still subtracted, and the four left out of the score entirely. Everything else is the same:
same candles, same v4 settings, same entry / stop / half at +2R / SAR trail / time exit,
same 1% risk sizing, max 3 open, one $1,000 balance shared by BTC, ETH and XRP.

It runs bot.py's own functions in paper mode (no orders, no API key), bar by bar, so trades
are managed exactly the way the live bot manages them.

Run (plain Python, no libraries; downloads candles from OKX's public API):
  python research/score_test.py
"""
import datetime as dt
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402

START = dt.datetime(2024, 3, 1, tzinfo=dt.timezone.utc)
SPLIT = dt.datetime(2025, 7, 1, tzinfo=dt.timezone.utc)
COINS = ["BTC-USDT", "ETH-USDT", "XRP-USDT"]
WARMUP_DAYS = 60  # candles before START so indicators are ready on day one

SCORE_NOW = "score = int(c1) + int(c7) + int(c11) + int(c12) - int(c3) - int(c5) - int(c6) - int(c10)"
SCORE_ALL = "score = int(c1) + int(c7) + int(c11) + int(c12) + int(c3) + int(c5) + int(c6) + int(c10)"
SCORE_BOS = "score = int(c1) + int(c7) + int(c11) + int(c12) + int(c3) - int(c5) - int(c6) - int(c10)"
SCORE_OUT = "score = int(c1) + int(c7) + int(c11) + int(c12)"


def make_analyse(score_line):
    src = inspect.getsource(bot.analyse_sp)
    assert SCORE_NOW in src, "score line in bot.py changed; update this test"
    ns = {}
    exec(src.replace(SCORE_NOW, score_line), vars(bot), ns)
    return ns["analyse_sp"]


def ms(d):
    return int(d.timestamp() * 1000)


def load(api, coin):
    days = (dt.datetime.now(dt.timezone.utc) - START).days + WARMUP_DAYS
    raw4 = api.candles(coin, "4H", days * 6 + 10)
    rawd = api.candles(coin, "1Dutc", days + 10)
    return [b for b in raw4 if b["confirm"]], [d for d in rawd if d["confirm"]]


def simulate(data, analyse, t0, t1):
    """One bot, one shared balance, trades opened between t0 and t1 (open ones are closed at t1)."""
    cfg = bot.SP_SETTINGS["v4"]
    b = {"id": "test", "name": "test", "strat": "v4", "venue": "okx", "mode": "paper",
         "coins": COINS, "equity": 1000.0}
    bs = {"equity": 1000.0, "positions": {}, "last_bar": {}}
    trades, open_id = [], {}

    def log_trade(_bot, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
        if side == "buy":
            open_id[coin] = len(trades)
            trades.append({"coin": coin, "pnl": 0.0, "exit": None})
        else:
            t = trades[open_id[coin]]
            t["pnl"] += pnl
            if reason != "half profit +2R":
                t["exit"] = reason
    bot.log_trade, bot.log = log_trade, lambda *a: None

    per = {}
    for coin, (bars, daily) in data.items():
        a = analyse(bars, daily, cfg)
        per[coin] = (bars, a, {x["ts"]: k for k, x in enumerate(bars)})
    times = sorted({x["ts"] for bars, _, _ in per.values() for x in bars if ms(t0) <= x["ts"] < ms(t1)})

    peak, low_dd = 1000.0, 0.0
    for ts in times:
        for coin in COINS:
            bars, a, idx = per[coin]
            k = idx.get(ts)
            if k is None:
                continue
            x = bars[k]
            if coin in bs["positions"] and x["ts"] > bs["positions"][coin]["entry_ts"]:
                if not bot.check_hit(None, b, bs, coin, x):
                    p = bs["positions"][coin]
                    bot.manage_on_close(None, b, bs, coin, a, k, x, k - idx[p["entry_ts"]])
            if coin not in bs["positions"] and a["signal"][k]:
                bot.open_position(None, b, bs, coin, x, a["info"][k], {})
        # mark to market at each candle close for drawdown
        mtm = bs["equity"]
        for coin, p in bs["positions"].items():
            bars, _, idx = per[coin]
            k = idx.get(ts)
            if k is not None:
                mtm += (p["qty"] * bars[k]["c"] * (1 - bot.FEE) - p["cost"]) * p.get("pnl_scale", 1.0)
        peak = max(peak, mtm)
        low_dd = min(low_dd, mtm / peak - 1)

    for coin in list(bs["positions"]):
        bars, _, idx = per[coin]
        last = max(k for k, x in enumerate(bars) if x["ts"] < ms(t1))
        bot.close_position(None, b, bs, coin, "end of test", bars[last]["c"])

    wins = sum(t["pnl"] > 0 for t in trades)
    won = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    lost = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    return {"trades": len(trades), "win": wins / len(trades) * 100 if trades else 0.0,
            "ret": bs["equity"] / 1000 * 100 - 100, "dd": low_dd * 100,
            "pf": won / lost if lost else float("inf"), "list": trades}


def main():
    api = bot.OKX("", "", "")
    data = {}
    for coin in COINS:
        print(f"downloading {coin} ...", flush=True)
        data[coin] = load(api, coin)
        print(f"  {len(data[coin][0])} 4H candles from {bot.ts_iso(data[coin][0][0]['ts'])}", flush=True)
    end = dt.datetime.now(dt.timezone.utc)
    periods = [("Full (Mar 2024 - now)", START, end), ("1st half (Mar 2024 - Jun 2025)", START, SPLIT),
               ("2nd half (Jul 2025 - now)", SPLIT, end)]
    versions = [("Score now (4 subtract)", make_analyse(SCORE_NOW)), ("All 8 added", make_analyse(SCORE_ALL)),
                ("BOS added, 3 subtract", make_analyse(SCORE_BOS)), ("4 left out", make_analyse(SCORE_OUT))]

    print("\n| Version | Period | Trades | Win % | Return | Max drawdown | Profit factor |")
    print("|---|---|---|---|---|---|---|")
    for vname, fn in versions:
        for pname, t0, t1 in periods:
            r = simulate(data, fn, t0, t1)
            print(f"| {vname} | {pname} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | "
                  f"{r['dd']:.1f}% | {r['pf']:.2f} |")
            if pname.startswith("Full"):
                by = {}
                for t in r["list"]:
                    c = by.setdefault(t["coin"], [0, 0.0])
                    c[0] += 1
                    c[1] += t["pnl"]
                print("|  | by coin: " + ", ".join(f"{k.split('-')[0]} {n} trades {p:+.0f} USD"
                                                for k, (n, p) in by.items()) + " | | | | | |")
    for coin in COINS:
        bars = data[coin][0]
        first = next(x for x in bars if x["ts"] >= ms(START))
        print(f"Buy and hold {coin.split('-')[0]}: {bars[-1]['c'] / first['c'] * 100 - 100:+.1f}%")


if __name__ == "__main__":
    main()
