"""
Backtest history for the dashboard's equity chart: SP-12 v4, its Kraken copy and Trend Rider, replayed with
research/engine.py on bot.py's own code and each bot's LIVE settings (risk, no half sell), $1,000 from 2018-05
up to the day the bot started on demo/paper. Saved daily to dashboard/backtest.json. Read-only: never trades.
Trend Rider's backtest has no fear filter (same as SCOREBOARD.md). Fees: the user's real OKX rate, 0.35% per buy and
per sell (market orders, spot Lv1, checked 2026-10-05), not bot.py's 0.1%; see research/FEES_PLAN.md.

Run (slow, rerun only when a bot's rules change):
  python dashboard/backtest_curves.py
"""
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "research"))
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import cards  # noqa: E402
import engine as e  # noqa: E402


def coins(bid):
    return [c.split("-")[0].replace("XBT", "BTC").replace("USD", "") for c in
            next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def settings(bid):
    b = next(b for b in bot.BOTS if b["id"] == bid)
    return {k: b[k] for k in ("risk", "half_at_2r") if k in b}


def daily(curve):
    out = {}
    for ts, v in curve:
        out[dt.datetime.fromtimestamp(ts / 1000, dt.timezone.utc).strftime("%Y-%m-%d")] = round(v, 2)
    return [[d, v] for d, v in out.items()]


REAL_FEE = 0.0035  # OKX spot Lv1 taker, per side


def main():
    bot.FEE, bot.BE_BUFFER = REAL_FEE, 2 * REAL_FEE
    sp = lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"])  # noqa: E731
    tr = lambda b, d: bot.analyse_tr(b, d, 5)  # noqa: E731
    jobs = {
        "v4-okx": lambda t1: e.bot_sim("v4", coins("v4-okx"), e.load(coins("v4-okx")), sp, e.START, t1,
                                       settings=settings("v4-okx")),
        "v4-kraken": lambda t1: e.bot_sim("v4", ["BTC", "ETH", "XRP"], e.load(["BTC", "ETH", "XRP"]), sp, e.START, t1,
                                          settings=settings("v4-kraken")),
        "tr-okx": lambda t1: e.bot_sim("tr", coins("tr-okx"), e.load(coins("tr-okx")), tr, e.START, t1,
                                       extra=lambda x: {"hi": x["c"]}, settings=settings("tr-okx")),
    }
    out = {"made_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M"), "fee_pct": REAL_FEE * 100, "bots": {}}
    for bid, run in jobs.items():
        t1 = dt.datetime.fromtimestamp(cards.start_ms({"id": bid}) / 1000, dt.timezone.utc)
        res = run(t1)
        out["bots"][bid] = {"until": t1.strftime("%Y-%m-%d"), "settings": settings(bid), "curve": daily(res["curve"])}
        print(bid, "backtest", out["bots"][bid]["curve"][0], "->", out["bots"][bid]["curve"][-1], flush=True)
    with open(os.path.join(HERE, "backtest.json"), "w") as f:
        json.dump(out, f)


if __name__ == "__main__":
    main()
