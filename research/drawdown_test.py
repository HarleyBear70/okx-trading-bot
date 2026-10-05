"""
Drawdown test: which changes get SP-12 v4's max drawdown under 10% without killing the return?

Same test as research/score_test.py (same candles, same v4 settings, bot.py's own paper-mode
functions bar by bar, one $1,000 balance shared by BTC, ETH and XRP, 0.1% fee each side).
The score line is left exactly as it is in bot.py. Each version changes one or two things:

  - risk per trade: bot.py now steps risk up to 1.25 / 1.5 / 2% as the balance grows
    (RISK_STEPS). Jeff's rule is a flat 1%, so most versions use flat 1%.
  - max trades open at once (bot.py: 3). BTC, ETH and XRP tend to fall together.
  - drawdown brake: risk drops to 0.5% while the balance is more than 5% below its best.
  - daily uptrend required: c1 (daily close above a rising daily EMA20) must be true to enter.
  - size cap: 1% risk, but no single trade may use more than 1/3 (or 1/2) of the balance.
    With a typical 2.5% stop, 1% risk buys about 40% of the balance, so the third trade is
    often cut short by lack of cash (50 of 199 entries in the full test).
  - lower flat risk (0.75%, 0.5%).

A change only counts if it helps in BOTH halves, not just the full period.

Run (plain Python, no libraries; downloads candles from OKX's public API):
  python research/drawdown_test.py
"""
import datetime as dt
import inspect
import os
import pickle
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402
import score_test as st  # noqa: E402

ORIG_RISK_PCT, ORIG_MAX_OPEN, ORIG_OPEN = bot.risk_pct, bot.MAX_OPEN, bot.open_position
NEED_C1 = "score >= 2 and raw_risk"
SIZE_LINE = "qty = min(eq * risk_pct(bot, bs) / (close - sl), free / close)"


def patched(fn, old, new):
    src = inspect.getsource(fn)
    assert old in src, f"{fn.__name__} in bot.py changed; update this test"
    ns = {}
    exec(src.replace(old, new), vars(bot), ns)
    return ns[fn.__name__]


def capped_open(cap):
    return patched(ORIG_OPEN, SIZE_LINE, SIZE_LINE[:-1] + f", eq * {cap} / close)")


def flat(pct):
    def risk_pct(_bot, bs):
        bs["peak"] = max(bs.get("peak", bs["equity"]), bs["equity"])
        return pct
    return risk_pct


def brake(pct, low_pct, dd):
    """pct normally, low_pct while the balance is more than dd below its best."""
    def risk_pct(_bot, bs):
        eq = bs["equity"]
        bs["peak"] = max(bs.get("peak", eq), eq)
        return low_pct if eq < bs["peak"] * (1 - dd) else pct
    return risk_pct


def run(data, analyse, risk_fn, max_open, opener, t0, t1):
    bot.risk_pct, bot.MAX_OPEN, bot.open_position = risk_fn, max_open, opener or ORIG_OPEN
    try:
        return st.simulate(data, analyse, t0, t1)
    finally:
        bot.risk_pct, bot.MAX_OPEN, bot.open_position = ORIG_RISK_PCT, ORIG_MAX_OPEN, ORIG_OPEN


def main():
    # optional: python research/drawdown_test.py candles.pkl  (saves / reuses the download)
    cache = sys.argv[1] if len(sys.argv) > 1 else None
    if cache and os.path.exists(cache):
        with open(cache, "rb") as f:
            data = pickle.load(f)
    else:
        api = bot.OKX("", "", "")
        data = {}
        for coin in st.COINS:
            print(f"downloading {coin} ...", flush=True)
            data[coin] = st.load(api, coin)
        if cache:
            with open(cache, "wb") as f:
                pickle.dump(data, f)
    end = dt.datetime.now(dt.timezone.utc)
    periods = [("Full", st.START, end), ("1st half", st.START, st.SPLIT), ("2nd half", st.SPLIT, end)]

    now = st.make_analyse(st.SCORE_NOW)
    need_c1 = patched(bot.analyse_sp, NEED_C1, "score >= 2 and c1 and raw_risk")

    versions = [
        ("bot.py now (1% stepping up to 2%, max 3)", now, ORIG_RISK_PCT, 3),
        ("Flat 1%, max 3", now, flat(0.01), 3),
        ("Flat 1%, max 2", now, flat(0.01), 2),
        ("Flat 1%, max 1", now, flat(0.01), 1),
        ("Flat 1% + brake (0.5% when 5% below best), max 3", now, brake(0.01, 0.005, 0.05), 3),
        ("Flat 1% + brake, max 2", now, brake(0.01, 0.005, 0.05), 2),
        ("Flat 1%, daily uptrend required, max 3", need_c1, flat(0.01), 3),
        ("Flat 1%, daily uptrend required, max 2", need_c1, flat(0.01), 2),
        ("Flat 1% + brake, daily uptrend required, max 2", need_c1, brake(0.01, 0.005, 0.05), 2),
        ("Flat 1%, size cap 1/2 of balance, max 3", now, flat(0.01), 3, capped_open(0.5)),
        ("Flat 1%, size cap 1/3 of balance, max 3", now, flat(0.01), 3, capped_open(1 / 3)),
        ("Flat 0.75%, max 3", now, flat(0.0075), 3),
        ("Flat 0.5%, max 3", now, flat(0.005), 3),
    ]
    versions = [v if len(v) == 5 else v + (None,) for v in versions]

    print("\n| Version | Period | Trades | Win % | Return | Max DD | PF |")
    print("|---|---|---|---|---|---|---|")
    for vname, fn, risk_fn, mx, opener in versions:
        for pname, t0, t1 in periods:
            r = run(data, fn, risk_fn, mx, opener, t0, t1)
            print(f"| {vname} | {pname} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | "
                  f"{r['dd']:.1f}% | {r['pf']:.2f} |", flush=True)


if __name__ == "__main__":
    main()
