"""
Live bands (Chrome Claude's idea #3, Oct 7 2026): what "normal bad luck" looks like for the two real-money bots, set
BEFORE live results come in, so a losing run can be judged "unlucky" vs "broken" without retuning after the fact.

Backtest each live bot with its live settings at the Binance.US 0.02% fee (2018-05 to now, bot.py's own strategy code
via engine.bot_sim), then reshuffle its trades 5,000 times (Monte Carlo) to see how long a losing streak and how deep
a drop can happen by chance alone. The 95th percentile is the band: beyond it, the watcher raises ATTENTION
(research/scout.py EXPECTED "streak" / "dd").

  python research/live_bands.py
"""
import random

import engine as e  # noqa: I001  (engine before bot)
import bot

FEE = bot.BINANCEUS_FEE
RUNS = 5000
LIVE = {b["id"]: b for b in bot.BOTS if b["mode"] == "live"}


def sim(bot_id):
    b = LIVE[bot_id]
    coins = [c.split("-")[0] for c in b["coins"]]
    data = e.load(coins)
    keep = {k: b[k] for k in ("risk", "half_at_2r", "max_open", "dc", "pivot", "fee") if k in b}
    if b["strat"] == "tr":
        return e.bot_sim("tr", coins, data, lambda x, d: bot.analyse_tr(x, d, b["pivot"]), e.START,
                         extra=lambda x: {"hi": x["c"]}, settings=keep)
    daily = {c: (d, d) for c, (_, d) in data.items()}
    return e.bot_sim("donchian", coins, daily, lambda x, d: bot.analyse_donchian(x, b["dc"]), e.START, settings=keep)


def streak(pnls):
    best = run = 0
    for p in pnls:
        run = run + 1 if p <= 0 else 0
        best = max(best, run)
    return best


def as_returns(pnls, start=1000.0):
    """Each trade's P/L as a share of the balance before it, so a reshuffle doesn't put late, big-balance dollar
    swings at the start."""
    eq, out = start, []
    for p in pnls:
        out.append(p / eq)
        eq += p
    return out


def max_dd(rets):
    eq = peak = 1.0
    dd = 0.0
    for x in rets:
        eq *= 1 + x
        peak = max(peak, eq)
        dd = min(dd, eq / peak - 1)
    return dd * 100


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))]


def main():
    random.seed(7)
    print("| Live bot | Trades | Win | PF | Return | Worst drop (actual) | Losing streak: actual / normal (95%) | "
          "Drop: normal (95%) |\n|---|---|---|---|---|---|---|---|")
    for bid in LIVE:
        o_fee = bot.FEE
        bot.FEE = FEE  # engine's mark-to-market uses bot.FEE
        try:
            r = sim(bid)
        finally:
            bot.FEE = o_fee
        pnls = [t["pnl"] for t in r["list"]]
        rets = as_returns(pnls)
        streaks, dds = [], []
        for _ in range(RUNS):
            s = random.sample(rets, len(rets))
            streaks.append(streak(s))
            dds.append(max_dd(s))
        s95, d95 = pct(streaks, 0.95), -pct([-d for d in dds], 0.95)
        print(f"| {LIVE[bid]['name']} | {r['trades']} | {r['win']:.0f}% | {r['pf']:.2f} | {r['ret']:+.0f}% | {r['dd']:.1f}% | "
              f"{streak(pnls)} / {s95} | {d95:.1f}% |")
        print(f'    EXPECTED "{bid}": {{"win": {r["win"]:.0f}, "pf": {r["pf"]:.2f}, "dd": {d95:.1f}, "streak": {s95}}}',
              flush=True)


if __name__ == "__main__":
    main()
