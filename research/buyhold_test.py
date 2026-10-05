"""
Job 2: why does SP-12 v4 lose to buy-and-hold on BTC and XRP?

Same test as research/drawdown_test.py (bot.py as it is now: 0.5% risk, max 3 open,
one $1,000 balance shared by BTC, ETH and XRP, bot.py's own paper-mode functions bar by bar).
Every buy, half sell and sell is recorded, then for each coin it measures:

  - time in market: share of 4H candles the bot held that coin
  - average size: trade cost as a share of the balance at entry
  - exposure: time in market x average size = how much of the balance was in that coin on average
  - P/L per coin vs buy-and-hold of the coin's share of the balance (1/3 each)
  - capture: of each big up-move (monthly closes), how much the bot's held position caught
  - exits: count, average R and total P/L by exit reason, and what the coin did in the
    next 30 days after trail / breakeven exits (did the bot get shaken out of a trend?)
  - entry filters: share of time the entry rules were even allowed (c2 trend + filters)

Run:
  python research/buyhold_test.py [candles.pkl]
"""
import datetime as dt
import os
import pickle
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402
import score_test as st  # noqa: E402


def load(cache):
    if cache and os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)
    api = bot.OKX("", "", "")
    data = {c: st.load(api, c) for c in st.COINS}
    if cache:
        with open(cache, "wb") as f:
            pickle.dump(data, f)
    return data


def record(data, t0, t1):
    """Run the normal simulation, recording every fill with its time and balance."""
    fills, cur = [], {"ts": None}
    o_open, o_close, o_half = bot.open_position, bot.close_position, bot.take_half
    o_hit, o_manage = bot.check_hit, bot.manage_on_close

    def check_hit(api, b, bs, coin, bar):
        cur["ts"] = bar["ts"]
        return o_hit(api, b, bs, coin, bar)

    def manage_on_close(api, b, bs, coin, a, i, bar, bars_in):
        cur["ts"] = bar["ts"]
        return o_manage(api, b, bs, coin, a, i, bar, bars_in)

    def open_position(api, b, bs, coin, bar, inf, extra):
        had = coin in bs["positions"]
        eq = bs["equity"]
        o_open(api, b, bs, coin, bar, inf, extra)
        if not had and coin in bs["positions"]:
            p = bs["positions"][coin]
            fills.append({"coin": coin, "kind": "buy", "ts": bar["ts"], "px": p["entry_px"], "cost": p["cost"],
                          "eq": eq, "sl": p["sl"], "score": inf["score"]})

    def close_position(api, b, bs, coin, reason, px):
        p = dict(bs["positions"][coin])
        eq0 = bs["equity"]
        o_close(api, b, bs, coin, reason, px)
        fills.append({"coin": coin, "kind": "sell", "ts": cur["ts"] if reason != "end of test" else None, "px": px, "pnl": bs["equity"] - eq0,
                      "reason": reason, "entry_ts": p["entry_ts"], "entry_px": p["entry_px"], "sl": p["sl"]})

    def take_half(api, b, bs, coin, px):
        eq0 = bs["equity"]
        o_half(api, b, bs, coin, px)
        fills.append({"coin": coin, "kind": "half", "px": px, "pnl": bs["equity"] - eq0,
                      "entry_ts": bs["positions"][coin]["entry_ts"]})

    # check_hit / manage_on_close look these up in bot's globals, so the wrappers see every exit
    bot.open_position, bot.close_position, bot.take_half = open_position, close_position, take_half
    bot.check_hit, bot.manage_on_close = check_hit, manage_on_close
    try:
        res = st.simulate(data, st.make_analyse(st.SCORE_NOW), t0, t1)
    finally:
        bot.open_position, bot.close_position, bot.take_half = o_open, o_close, o_half
        bot.check_hit, bot.manage_on_close = o_hit, o_manage
    return res, fills


def trades_from(fills):
    """Join buy / half / sell fills into trades."""
    open_t, out = {}, []
    for f in fills:
        if f["kind"] == "buy":
            open_t[f["coin"]] = {**f, "pnl": 0.0, "half_pnl": 0.0}
        elif f["kind"] == "half":
            open_t[f["coin"]]["half_pnl"] += f["pnl"]
        else:
            t = open_t.pop(f["coin"])
            t["pnl"] = t["half_pnl"] + f["pnl"]
            t["reason"], t["exit_px"], t["exit_ts"] = f["reason"], f["px"], f["ts"]
            risk_usd = t["eq"] * bot.RISK_PCT
            t["R"] = t["pnl"] / risk_usd if risk_usd else 0.0
            out.append(t)
    return out


def main():
    data = load(sys.argv[1] if len(sys.argv) > 1 else None)
    t0, t1 = st.START, dt.datetime.now(dt.timezone.utc)
    res, fills = record(data, t0, t1)
    trades = trades_from(fills)
    print(f"Whole bot: {res['trades']} trades, {res['ret']:+.1f}%, max DD {res['dd']:.1f}%, PF {res['pf']:.2f}\n")

    # bars per coin in the test window, and when each trade was open
    bars_in = {c: [x for x in data[c][0] if st.ms(t0) <= x["ts"] < st.ms(t1)] for c in st.COINS}
    held = {c: [False] * len(bars_in[c]) for c in st.COINS}
    for t in trades:
        c, bars = t["coin"], bars_in[t["coin"]]
        idx = {x["ts"]: k for k, x in enumerate(bars)}
        t["k0"] = idx[t["ts"]]
        t["k1"] = idx[t["exit_ts"]] if t["exit_ts"] is not None else len(bars) - 1
        for k in range(t["k0"] + 1, t["k1"] + 1):
            held[c][k] = True

    print("| Coin | Buy & hold | Bot P/L (USD) | Bot P/L as % of a 1/3 share | Time in market | Avg size (% of balance) | Exposure | Bot return per unit of exposure |")
    print("|---|---|---|---|---|---|---|---|")
    for c in st.COINS:
        bars = bars_in[c]
        bh = bars[-1]["c"] / bars[0]["c"] * 100 - 100
        mine = [t for t in trades if t["coin"] == c]
        pnl = sum(t["pnl"] for t in mine)
        tim = sum(held[c]) / len(bars)
        size = sum(t["cost"] / t["eq"] for t in mine) / len(mine) if mine else 0
        expo = tim * size
        share = pnl / (1000 / 3) * 100
        per_expo = pnl / 1000 / expo * 100 if expo else 0
        print(f"| {c.split('-')[0]} | {bh:+.0f}% | {pnl:+.0f} | {share:+.1f}% | {tim * 100:.0f}% | {size * 100:.0f}% | "
              f"{expo * 100:.1f}% | {per_expo:+.0f}% |")

    # buy and hold max drawdown, for comparison
    print()
    for c in st.COINS:
        peak, dd = 0, 0
        for x in bars_in[c]:
            peak = max(peak, x["c"])
            dd = min(dd, x["c"] / peak - 1)
        print(f"Buy & hold {c.split('-')[0]} max drawdown: {dd * 100:.0f}%")

    # monthly capture: months where the coin rose 15%+, how much of that the bot held
    print("\nBig up months (coin +15% or more): coin move, share of candles held, bot P/L that month (USD)")
    for c in st.COINS:
        bars = bars_in[c]
        months = defaultdict(list)
        for k, x in enumerate(bars):
            months[bot.ts_iso(x["ts"])[:7]].append(k)
        rows = []
        for m, ks in sorted(months.items()):
            move = bars[ks[-1]]["c"] / bars[ks[0]]["o"] * 100 - 100
            if move < 15:
                continue
            h = sum(held[c][k] for k in ks) / len(ks)
            pm = sum(t["pnl"] for t in trades if t["coin"] == c and bot.ts_iso(bars[min(t["k1"], len(bars) - 1)]["ts"])[:7] == m)
            rows.append(f"{m} {move:+.0f}% held {h * 100:.0f}% P/L {pm:+.0f}")
        print(f"  {c.split('-')[0]}: " + ("; ".join(rows) or "none"))

    # exits
    print("\n| Exit reason | Trades | Avg R | Total P/L (USD) | Coin move 30 days after exit (avg) |")
    print("|---|---|---|---|---|")
    by = defaultdict(list)
    for t in trades:
        by[t["reason"]].append(t)
    for reason, ts in sorted(by.items(), key=lambda kv: -len(kv[1])):
        after = []
        for t in ts:
            bars = bars_in[t["coin"]]
            k2 = min(t["k1"] + 180, len(bars) - 1)
            if k2 > t["k1"]:
                after.append(bars[k2]["c"] / t["exit_px"] * 100 - 100)
        avg_after = sum(after) / len(after) if after else 0
        print(f"| {reason} | {len(ts)} | {sum(t['R'] for t in ts) / len(ts):+.2f} | "
              f"{sum(t['pnl'] for t in ts):+.0f} | {avg_after:+.1f}% |")

    hold_bars = [t["k1"] - t["k0"] for t in trades]
    print(f"\nAverage trade length: {sum(hold_bars) / len(hold_bars) / 6:.1f} days; "
          f"best trade {max(t['R'] for t in trades):+.1f}R; trades over +5R: {sum(t['R'] > 5 for t in trades)}")

    # how often the entry gate is even open
    cfg = bot.SP_SETTINGS["v4"]
    for c in st.COINS:
        bars, daily = data[c]
        a = st.make_analyse(st.SCORE_NOW)(bars, daily, cfg)
        ks = [k for k, x in enumerate(bars) if st.ms(t0) <= x["ts"] < st.ms(t1)]
        sig = sum(a["signal"][k] for k in ks)
        print(f"{c.split('-')[0]}: entry signal on {sig} of {len(ks)} candles ({sig / len(ks) * 100:.1f}%)")


if __name__ == "__main__":
    main()
