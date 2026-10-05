"""
Job 3: one scoreboard, every bot on equal terms. Rewrites the generated section of SCOREBOARD.md
(between the "equal-terms" markers); the hand-kept parts of SCOREBOARD.md and scoreboard.csv stay as they are.

Equal terms: $1,000, 0.5% risk per trade, 0.1% fee each side (0.15% on the 1H bots, as tested), max 3 open,
2018-05 to now plus the two halves (2018-05 to 2021 / 2022 to now), bot.py's own functions for the bots it
runs, research/engine.py for the rest. The main score is return / max drawdown.

Run:
  python research/scoreboard.py
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

START, END = "<!-- equal-terms start -->", "<!-- equal-terms end -->"
PERIODS = [("full", e.START, None)] + list(e.HALVES)


def bot_coins(bid):
    return [c.split("-")[0].replace("XBT", "BTC").replace("USD", "") for c in
            next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def rows():
    """(name, status, runner(t0, t1) -> result with 'curve', note)"""
    import b_boxes as bb
    import b3_s1 as b3
    import d1_day as d1
    import n1_range as n1
    import n2_rotation as n2
    import n3_squeeze as n3
    import n4_short as n4

    v4c, trc = bot_coins("v4-okx"), bot_coins("tr-okx")
    d4, dtr, dk = e.load(v4c), e.load(trc), e.load(["BTC", "ETH", "XRP"])
    d1h = bb.load_1h(e.DESIGN)
    d4h_b = bb.load_4h(e.DESIGN)
    ddaily = b3.load_daily(e.DESIGN)
    dv2 = e.load(["ETH", "SOL", "XAUT"])
    dg = e.load(["XAUT"])
    D = n2.Data()
    sp = lambda cfg: (lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS[cfg]))  # noqa: E731
    return [
        ("SP-12 v4", "demo, live on OKX", lambda t0, t1: e.v4_sim(d4, t0, t1, coins=v4c), " ".join(v4c)),
        ("SP-12 v4 (Kraken paper)", "paper", lambda t0, t1: e.v4_sim(dk, t0, t1, coins=["BTC", "ETH", "XRP"]), "BTC ETH XRP"),
        ("Trend Rider", "demo, live on OKX (fear filter since Oct 5; row is without it)", lambda t0, t1: e.tr_sim(dtr, t0, t1, coins=trc), " ".join(trc)),
        ("B1c breakout retest", "paper forward test",
         lambda t0, t1: e.trade_sim(e.DESIGN, d1h, bb.b1_entries(2.0, 60), t0, t1), "BTC ETH XRP, 1H"),
        ("SP-12 v2", "paused", lambda t0, t1: e.bot_sim("v2", ["ETH", "SOL", "XAUT"], dv2, sp("v2"), t0, t1), "ETH SOL XAUT"),
        ("Trend Rider gold (pivot 3)", "paused",
         lambda t0, t1: e.bot_sim("tr", ["XAUT"], dg, lambda b, d: bot.analyse_tr(b, d, 3), t0, t1,
                                  extra=lambda x: {"hi": x["c"]}), "XAUT (from 2020)"),
        ("B3 P3 pairs", "paper forward test",
         lambda t0, t1: b3.pairs_sim(["ETH", "XRP"], 60, 2.5, ddaily, t0, t1), "ETH/BTC XRP/BTC, daily"),
        ("N3 S2 squeeze + daily trend", "research: failed",
         lambda t0, t1: e.trade_sim(e.DESIGN, dk, n3.entries(540, "pct10", True), t0, t1), "BTC ETH XRP"),
        ("N4 X2 short side", "research: failed (shorts)",
         lambda t0, t1: e.trade_sim(e.DESIGN, dk, n4.entries(5, True), t0, t1, manage=n4.manage), "BTC ETH XRP"),
        ("D1 I3 intraday momentum", "research: failed",
         lambda t0, t1: e.trade_sim(e.DESIGN, d1h, d1.intraday(0.01, True), t0, t1, fee=d1.COST), "BTC ETH XRP, 1H"),
        ("B2c reclaim + daily trend", "research: failed",
         lambda t0, t1: e.trade_sim(e.DESIGN, d4h_b, bb.b2_entries(3, True), t0, t1), "BTC ETH XRP"),
        ("N1 R3 range bot", "research: failed",
         lambda t0, t1: e.trade_sim(e.DESIGN, dk, n1.entries(120, 0.8), t0, t1), "BTC ETH XRP"),
        ("D1 C3 capitulation buy", "research: failed",
         lambda t0, t1: e.trade_sim(e.DESIGN, d1h, d1.capitulation(3.0, True), t0, t1, fee=d1.COST, cooldown=24),
         "BTC ETH XRP, 1H"),
        ("N2 M3 rotation (not 0.5% risk: allocation)", "research: failed (DD)",
         lambda t0, t1: n2.sim(D, 1, 10, 28, True, t0, t1), "top 10 as listed at the time"),
    ]


def main():
    base = e.baseline()
    mix = e.monthly(base["mix"])
    table = []
    for name, status, run, coins in rows():
        res = {}
        for p, t0, t1 in PERIODS:
            res[p] = run(t0, t1)
        f = res["full"]
        ret, dd, rd = e.ret_dd(f["curve"])
        cr = e.corr(e.monthly(f["curve"]), mix)
        table.append((rd, name, status, coins, f, res, cr))
        print(f"done {name}", flush=True)
    # buy-and-hold BTC on the same footing, for reference
    btc = e.load(["BTC"])["BTC"][0]
    curve = [(b["ts"], b["c"]) for b in btc if e.ms(e.START) <= b["ts"]]
    bh_ret, bh_dd, bh_rd = e.ret_dd(curve)
    table.sort(key=lambda x: -x[0])
    out = [START, "", f"## Equal-terms backtest scoreboard (generated {dt.datetime.now(dt.timezone.utc):%Y-%m-%d} by "
           "research/scoreboard.py)", "",
           "Every bot on the same footing: $1,000, 0.5% risk per trade, 0.1% fee each side (0.15% on the 1H bots), "
           "max 3 open, 2018-05 to now, plus the halves 2018-05 to 2021 and 2022 to now. Sorted by return / max "
           "drawdown (higher = more return for each point of pain). Correlation = monthly returns vs 50/50 v4 + "
           "Trend Rider. Live demo results are in the Scout's weekly report (reports/).", "",
           "| Rank | Bot | Status | Coins | Return | Max DD | Return / DD | PF | Trades | Win % | 1st half return / DD "
           "| 2nd half return / DD | Corr. with v4+TR |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, (rd, name, status, coins, f, res, cr) in enumerate(table, 1):
        h1, h2 = res["1st half"], res["2nd half"]
        r1, d1_, _ = e.ret_dd(h1["curve"])
        r2, d2_, _ = e.ret_dd(h2["curve"])
        ret, dd, _ = e.ret_dd(f["curve"])
        pf = "inf" if f["pf"] == float("inf") else f"{f['pf']:.2f}"
        out.append(f"| {i} | {name} | {status} | {coins} | {ret:+.0f}% | {dd:.1f}% | {rd:.2f} | {pf} | {f['trades']} | "
                   f"{f['win']:.0f}% | {r1:+.0f}% / {d1_:.1f}% | {r2:+.0f}% / {d2_:.1f}% | {cr:.2f} |")
    b_ret, b_dd, b_rd = e.ret_dd(base["mix"])
    out += ["", f"Reference: 50/50 v4 + Trend Rider together {b_ret:+.0f}% / {b_dd:.1f}% (return/DD {b_rd:.2f}); "
            f"buy-and-hold BTC {bh_ret:+.0f}% / {bh_dd:.0f}% (return/DD {bh_rd:.2f}).",
            "Notes: N2 M3 is an allocation bot (no stops), so its 0.5%-risk footing differs. Trend Rider gold only has "
            "data from 2020. B1c / D1 use Binance 1H data; the rest use the long-history 4H data.", "", END]
    path = os.path.join(ROOT, "SCOREBOARD.md")
    with open(path) as fh:
        text = fh.read()
    block = "\n".join(out)
    if START in text and END in text:
        text = text[:text.index(START)] + block + text[text.index(END) + len(END):]
    else:
        text = text.rstrip() + "\n\n" + block + "\n"
    with open(path, "w") as fh:
        fh.write(text)
    print(block)


if __name__ == "__main__":
    main()
