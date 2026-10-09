"""
LEG TEST (Oct 9 2026, Jeff: "yes"): does the Smoke Detector's new market-shift rule (strong level follows each leg,
pine commit 520c390, jeff_topdown.structure(leg=1)) make the bots that use the structure engine better?
Bots: jeff_bot.py (15m top-down, accounts A "turnaround" and BC "full-recipe", 5 coins) and brad_bot.py
(1H sweep -> shift -> gap, research/brad_mm.py, 23 coins: first 12 main, last 11 never-seen).
PASS: the new rule must beat the old on PF in BOTH halves and on the never-seen coins, without losing average R.
One coin in memory at a time (Chromebook memory).

  python3 research/leg_test.py
"""
import gc
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_mm as BMM  # noqa: E402
import jeff_topdown as J  # noqa: E402
from brad_more import COINS23  # noqa: E402

ORIG = J.structure
LEG = [None]
J.structure = lambda b, leg=None: ORIG(b, leg=LEG[0])


def line(name, trades, curves):
    port = B.mix(curves)
    f, h1, h2 = (B.summarize(trades, port, a, z) for a, z in ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
    n = sum(1 for _, _, t in trades if t >= B.ms(B.START))
    r = sum(p for _, p, t in trades if t >= B.ms(B.START)) / max(n, 1) / (1000 * B.RISK)
    pf = lambda s: "-" if s is None else f"{s['pf']:.2f}"
    lp = "-" if f.get("long_pf") is None else f"{f['long_pf']:.2f}"
    print(f"| {name} | {n} | {f['win']:.0f}% | {f['pf']:.2f} | {r:+.2f}R | {f['dd']:.1f}% | {pf(h1)} | {pf(h2)} | {lp} |",
          flush=True)


def main():
    print("| Test | Trades | Win % | PF | R/trade | Worst drop | 2019-22 PF | 2023-now PF | Long PF |")
    print("|---|---|---|---|---|---|---|---|---|")
    # jeff_bot: 15m, 5 coins, both directions as in the bot
    B.MS_CUR[0] = B.MS["15m"]
    res = {}
    for c in B.CRYPTO:
        b = B.load("crypto", c, "15m")
        for leg in (None, 1):
            LEG[0] = leg
            for v in ("A", "BC"):
                tr, cv = J.run("crypto", b, "15m", v, None, 1.0)
                r = res.setdefault((v, leg), ([], []))
                r[0].extend(tr)
                r[1].append(cv)
        del b
        gc.collect()
    for (v, leg), (tr, cvs) in res.items():
        line(f"jeff_bot 15m {v} {'NEW leg rule' if leg else 'old rule'}", tr, cvs)
    # brad_bot: 1H, main 12 and never-seen 11
    B.MS_CUR[0] = B.MS["1H"]
    for title, coins in (("main 12", COINS23[:12]), ("never-seen 11", COINS23[12:])):
        res = {}
        for c in coins:
            b = B.load("crypto", c, "1H")
            for leg in (None, 1):
                LEG[0] = leg
                tr, cv = BMM.run("crypto", b, "1H")
                r = res.setdefault(leg, ([], []))
                r[0].extend(tr)
                r[1].append(cv)
            del b
            gc.collect()
        for leg, (tr, cvs) in res.items():
            line(f"brad_bot 1H {title} {'NEW leg rule' if leg else 'old rule'}", tr, cvs)


if __name__ == "__main__":
    main()
