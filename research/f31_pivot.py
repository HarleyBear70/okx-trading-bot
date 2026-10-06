"""
F31: TradingView "Pivot Points Standard", P only (the central pivot), as a buy filter for Trend Rider and Donchian.
P = (prior period high + low + close) / 3 for daily, weekly (Mon-Sun, UTC) and monthly periods. A buy is kept only if the
signal candle's close is above the current period's P. Live bot.py settings, real fee 0.35% a side. Research only.
"""
import datetime as dt
import engine as e
import bot

LIVE = {b["id"]: b for b in bot.BOTS}


def settings(bid):
    return {k: v for k, v in LIVE[bid].items() if k not in ("id", "name", "strat", "venue", "mode", "coins", "equity", "prefix")}


def coins(bid):
    return [c.split("-")[0] for c in LIVE[bid]["coins"]]


def period_key(ts, kind):
    d = dt.datetime.fromtimestamp(ts / 1000, e.UTC)
    if kind == "D":
        return d.date()
    if kind == "W":
        return d.date() - dt.timedelta(days=d.weekday())
    return (d.year, d.month)


def pivot_map(daily, kind):
    """period key -> P computed from the previous completed period."""
    groups, order = {}, []
    for b in daily:
        k = period_key(b["ts"], kind)
        if k not in groups:
            groups[k] = {"h": b["h"], "l": b["l"], "c": b["c"]}
            order.append(k)
        g = groups[k]
        g["h"], g["l"], g["c"] = max(g["h"], b["h"]), min(g["l"], b["l"]), b["c"]
    return {order[i]: (groups[order[i - 1]]["h"] + groups[order[i - 1]]["l"] + groups[order[i - 1]]["c"]) / 3
            for i in range(1, len(order))}


def above_p(bars, daily, kind):
    pm = pivot_map(daily, kind)
    return [(lambda p: p is not None and b["c"] > p)(pm.get(period_key(b["ts"], kind))) for b in bars]


def masked(a, ok):
    a["signal"] = [s and o for s, o in zip(a["signal"], ok)]
    return a


def tr_run(kind):
    cs = coins("tr-okx")
    d = e.load(cs)

    def an(bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        return masked(a, above_p(bars, daily, kind)) if kind else a
    return lambda t0, t1: e.bot_sim("tr", cs, d, an, t0, t1, extra=lambda x: {"hi": x["c"]}, settings=settings("tr-okx"))


def dc_run(kind):
    cs = coins("dc-okx")
    dn = {c: (daily, daily) for c, (_, daily) in e.load(cs).items()}
    btc = e.load(["BTC"])["BTC"][1]
    per = {}
    for c in cs:
        a = masked(bot.analyse_donchian(dn[c][1]), bot.btc_leash(dn[c][1], btc, c))
        per[id(dn[c][1])] = masked(a, above_p(dn[c][1], dn[c][1], kind)) if kind else a
    return lambda t0, t1: e.bot_sim("donchian", cs, dn, lambda b, d: per[id(b)], t0, t1,
                                    extra=lambda x: {"no_half": True}, settings=settings("dc-okx"))


def main():
    print("| Variant | 2018-now return / DD / PF (trades) | 1st half (2018-21) | 2nd half (2022-now) |")
    print("|---|---|---|---|")
    for name, fn in [("Trend Rider", tr_run), ("Donchian", dc_run)]:
        for kind, lab in [(None, "as live"), ("D", "+ above daily P"), ("W", "+ above weekly P"), ("M", "+ above monthly P")]:
            run = fn(kind)
            cells = []
            for _, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
                r = run(t0, t1)
                cells.append(f"{r['ret']:+.1f}% / {r['dd']:.1f}% / {r['pf']:.2f} ({r['trades']})")
            print(f"| {name} {lab} | " + " | ".join(cells) + " |", flush=True)


if __name__ == "__main__":
    main()
