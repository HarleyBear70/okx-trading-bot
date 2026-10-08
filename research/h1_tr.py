"""
H1-TR: Trend Rider's exact rules on 1H candles instead of 4H, at the Binance.US cost (Jeff, Oct 7 2026:
"why don't we use the 1 hr chart, it takes all day for one move").

  4H  : Trend Rider as live (4H BOS + 4H 50 EMA + daily 50 EMA), the baseline
  1H-D: same rules on 1H candles, daily 50 EMA trend filter
  1H-4: same rules on 1H candles, 4H 50 EMA trend filter (one step down, like 4H -> daily)
Exit as F3: stop at the swing low, then a 3 ATR trail. 0.4% risk, max 3 open, shared $1,000.
Cost each side: 0.02% fee + 0.05% slippage (also 0.15% to show what the old tests charged).
Design coins = Trend Rider's; never-seen coins pooled on their own $1,000.

Run: python3 research/h1_tr.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import hourly as hr  # noqa: E402
import long_history as lh  # noqa: E402

DESIGN = ["BTC", "ETH", "SOL", "BNB", "SUI"]
UNSEEN = ["XRP", "LTC", "DOGE", "ADA", "LINK", "AVAX"]
H, H4 = 3600000, 4 * 3600000
ORIG_LOOKUP = bot.daily_lookup


def h4_lookup(bars, h4):
    idx = {b["ts"]: k for k, b in enumerate(h4)}
    # last 4H candle that closed by the end of this 1H candle
    return [idx.get(b["ts"] + H - (b["ts"] + H) % H4 - H4) for b in bars]


def load(coins, tf):
    out = {}
    for c in coins:
        if tf == "4H":
            out[c] = lh.load(c)
        else:
            b1 = hr.hourly(c)
            b4 = hr.to_4h(b1)
            out[c] = (b1, lh.to_daily(b4) if tf == "1H-D" else b4)
    return out


def sim(coins, tf, cost, t0, t1):
    data = load(coins, tf)
    bot.daily_lookup = h4_lookup if tf == "1H-4" else ORIG_LOOKUP
    atrs = {}

    def entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        atrs[id(bars)] = a["atr"]
        return [{"stop": a["info"][i]["sl"], "target": None, "max_bars": None} if a["signal"][i] else None
                for i in range(len(bars))]

    def manage(p, bars, k):
        x = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * x if x is not None else None

    r = e.trade_sim(coins, data, entries, t0, t1, risk=0.004, max_open=3, fee=cost, manage=manage)
    bot.daily_lookup = ORIG_LOOKUP
    return r


def main():
    print("| Chart | Cost/side | Coins | Period | Trades | Trades/week | Win % | Return | Worst drop | PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for cost in (0.0007, 0.0015):
        for tf in ("4H", "1H-D", "1H-4"):
            for label, coins in (("design", DESIGN), ("never-seen", UNSEEN)):
                for per, t0, t1 in [("2018-now", e.START, None)] + list(e.HALVES):
                    r = sim(coins, tf, cost, t0, t1)
                    weeks = ((t1 or e.now()) - t0).days / 7
                    print(f"| {tf} | {cost * 100:.2f}% | {label} | {per} | {r['trades']} | {r['trades'] / weeks:.1f} | "
                          f"{r['win']:.0f}% | {r['ret']:+.0f}% | {r['dd']:.1f}% | {r['pf']:.2f} |", flush=True)


if __name__ == "__main__":
    main()
