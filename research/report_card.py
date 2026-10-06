"""
Report card for every running bot: drawdowns, consistency and trade frequency, from an 8-year replay of bot.py's own
code at the real fee (0.35% per buy and per sell), 2018-05 to now. Writes REPORT_CARD.md. Read-only.

Run: python research/report_card.py
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

UTC = dt.timezone.utc


def coins(bid):
    return [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def settings(bid):
    b = next(b for b in bot.BOTS if b["id"] == bid)
    return {k: b[k] for k in ("risk", "half_at_2r", "max_open", "pyramid") if k in b}


def daily(cs):
    return {c: (d, d) for c, (_, d) in e.load(cs).items()}


def runs():
    btc_d = e.load(["BTC"])["BTC"][1]
    dcd = daily(coins("dc-okx"))
    dc_coin = {id(v[0]): c for c, v in dcd.items()}

    def leashed(b, _d):
        a = bot.analyse_donchian(b)
        ok = bot.btc_leash(b, btc_d, dc_coin[id(b)])
        return {**a, "signal": [s and o for s, o in zip(a["signal"], ok)]}
    return {
        "Trend Rider (demo)": lambda: e.bot_sim("tr", coins("tr-okx"), e.load(coins("tr-okx")),
                                                lambda b, d: bot.analyse_tr(b, d, 5), e.START, None,
                                                extra=lambda x: {"hi": x["c"]}, settings=settings("tr-okx")),
        "Donchian Trend (demo)": lambda: e.bot_sim("donchian", coins("dc-okx"), dcd, leashed, e.START, None,
                                                   settings=settings("dc-okx")),
        "NNFX Aroon (demo)": lambda: e.bot_sim("nnfx", coins("nnfx-okx"), daily(coins("nnfx-okx")),
                                               lambda b, d: bot.analyse_nnfx(b), e.START, None,
                                               settings=settings("nnfx-okx")),
        "Follow Line (paper)": lambda: e.bot_sim("followline", coins("fl-paper"), daily(coins("fl-paper")),
                                                 lambda b, d: bot.analyse_followline(b), e.START, None,
                                                 settings=settings("fl-paper")),
        "Double Bottom (paper)": lambda: e.bot_sim("dbottom", coins("db-paper"), daily(coins("db-paper")),
                                                   lambda b, d: bot.analyse_dbottom(b), e.START, None,
                                                   settings=settings("db-paper")),
        "BTC Protected Hold (paper)": lambda: e.bot_sim("hold", ["BTC"], daily(["BTC"]),
                                                        lambda b, d: bot.analyse_hold(b), e.START, None,
                                                        settings=settings("hold-paper")),
    }


def card(curve, n_trades, win, pf):
    days = {}
    for ts, v in curve:
        days[dt.datetime.fromtimestamp(ts / 1000, UTC).date()] = v
    ds = sorted(days)
    vals = [days[d] for d in ds]
    years = (ds[-1] - ds[0]).days / 365.25
    peak, dd, under, longest, start_under = vals[0], 0.0, None, 0, None
    for d, v in zip(ds, vals):
        if v >= peak:
            peak = v
            if start_under:
                longest = max(longest, (d - start_under).days)
            start_under = None
        else:
            start_under = start_under or d
            dd = min(dd, v / peak - 1)
    if start_under:
        longest = max(longest, (ds[-1] - start_under).days)
    m_end, y_end = {}, {}
    for d, v in zip(ds, vals):
        m_end[(d.year, d.month)] = v
        y_end[d.year] = v
    def rets(ends):
        out, prev = [], vals[0]
        for k in sorted(ends):
            out.append((k, ends[k] / prev - 1))
            prev = ends[k]
        return out
    mr, yr = rets(m_end), rets(y_end)
    return {"total": vals[-1] / vals[0] - 1, "cagr": (vals[-1] / vals[0]) ** (1 / years) - 1, "dd": dd,
            "under_days": longest, "pos_months": sum(r > 0 for _, r in mr) / len(mr),
            "pos_years": sum(r > 0 for _, r in yr) / len(yr), "best_year": max(yr, key=lambda x: x[1]),
            "worst_year": min(yr, key=lambda x: x[1]), "worst_month": min(r for _, r in mr),
            "trades_year": n_trades / years, "win": win, "pf": pf, "years": yr}


def main():
    rows, curves = [], {}
    for name, fn in runs().items():
        r = fn()
        c = card(r["curve"], r["trades"], r["win"], r["pf"])
        rows.append((name, c))
        curves[name] = r["curve"]
        print(name, f"{c['total'] * 100:+.0f}%", flush=True)
    demo = [n for n in curves if "(demo)" in n]
    comb = e.combine([curves[n] for n in demo], [1 / len(demo)] * len(demo))
    rows.append(("All 3 demo bots together", card(comb, sum(0 for _ in demo), None, None)))
    pct = lambda x: f"{x * 100:+.0f}%"  # noqa: E731
    md = ["# Bot report card", "",
          f"Generated {dt.datetime.now(UTC):%Y-%m-%d} by research/report_card.py: bot.py's own code replayed on 2018-05 to now "
          "at the real OKX fee (0.35% per buy and per sell), each bot with its live settings (Trend Rider without its fear "
          "filter). A backtest is the best case; live results will be a bit worse. Trades still open at the end are valued at "
          "entry price where a coin's saved history stops early (ETH ends 2026-08-31), so totals can be a few points below "
          "the research numbers (e.g. Donchian +148% here vs +154% with open trades closed at their last price).", "",
          "| Bot | Total | Per year | Worst drop | Longest time below a high | Months up | Years up | Best year | Worst year | Worst month | Trades a year | Win % | PF |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, c in rows:
        tpy = "-" if "together" in name else f"{c['trades_year']:.0f}"
        win = "-" if c["win"] is None else f"{c['win']:.0f}%"
        pf = "-" if c["pf"] is None else f"{c['pf']:.2f}"
        md.append(f"| {name} | {pct(c['total'])} | {pct(c['cagr'])} | {c['dd'] * 100:.1f}% | {c['under_days']} days | "
                  f"{c['pos_months'] * 100:.0f}% | {c['pos_years'] * 100:.0f}% | {c['best_year'][0]} {pct(c['best_year'][1])} | "
                  f"{c['worst_year'][0]} {pct(c['worst_year'][1])} | {c['worst_month'] * 100:.1f}% | {tpy} | {win} | {pf} |")
    md += ["", "## Year by year", "", "| Bot | " + " | ".join(str(y) for y, _ in rows[0][1]["years"]) + " |",
           "|---|" + "---|" * len(rows[0][1]["years"])]
    for name, c in rows:
        yr = dict(c["years"])
        md.append(f"| {name} | " + " | ".join(pct(yr[y]) if y in yr else "-" for y, _ in rows[0][1]["years"]) + " |")
    with open(os.path.join(ROOT, "REPORT_CARD.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print("wrote REPORT_CARD.md")


if __name__ == "__main__":
    main()
