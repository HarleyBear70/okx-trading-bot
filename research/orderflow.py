"""
ORDER FLOW as a filter on Brad's sweep -> shift bot (research/brad_mm.py base = brad_bot.py), asked for by Chrome Claude
on issue #4 (Oct 8 2026, Jeff approved: "anything for an edge"). Not a new bot: the same trades, minus the ones the
filter rejects. Signal = Binance global taker-buy share per 1H candle (research/orderflow_data.py); costs Binance.US.

PLAN (written before any results), 1H, 23 coins, 2019-now:
  delta   the shift candle was won by buyers (taker-buy share > 50%) for a long, by sellers for a short.
  absorb  the sweep candle (the extreme) had big volume (1.5x its 20-candle average), sellers were aggressive
          (taker-buy share < 50% for a long) but it closed in its top half (long lower wick): selling absorbed.
  cvd     buyers out-traded sellers over the whole move from the sweep extreme to the shift (cumulative delta > 0).
  Crowding filter (funding + open interest): not tested. Binance open-interest history only starts late 2021.

PASS RULES: a filter is worth adding only if it beats the base on profit factor AND average R in BOTH halves
(2019-22, 2023-now) AND on the never-seen coins (the last 11 of the 23), with at least 100 trades left.

  python3 research/orderflow_data.py   (once, downloads the data)
  python3 research/orderflow.py
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_mm as BMM  # noqa: E402
from brad_more import COINS23  # noqa: E402

DATA = os.path.expanduser("~/.cache/binance_1h")
MAIN, UNSEEN = COINS23[:12], COINS23[12:]


def filters(b, share):
    sh = [share.get(str(x["ts"])) for x in b]
    v = [x.get("v") or 0.0 for x in b]
    avg = B.sma(v, 20)

    def delta(sd, j, m, k):
        return sh[k] is not None and (sh[k] - 0.5) * sd > 0

    def absorb(sd, j, m, k):
        x = b[m]
        if sh[m] is None or not avg[m - 1] or x["h"] == x["l"]:
            return False
        upper = (x["c"] - x["l"]) / (x["h"] - x["l"]) if sd == 1 else (x["h"] - x["c"]) / (x["h"] - x["l"])
        return v[m] >= 1.5 * avg[m - 1] and (sh[m] - 0.5) * sd < 0 and upper >= 0.5

    def cvd(sd, j, m, k):
        if any(sh[i] is None for i in range(m, k + 1)):
            return False
        return sum((2 * sh[i] - 1) * v[i] for i in range(m, k + 1)) * sd > 0

    return {"base": None, "delta": delta, "absorb": absorb, "cvd": cvd}


def main():
    B.MS_CUR[0] = B.MS["1H"]
    print("| Coins | Filter | Trades/wk | Trades | Win % | PF | R/trade | 2019-22 PF | 2023-now PF | Long PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for title, coins in (("main 12", MAIN), ("never-seen 11", UNSEEN)):
        data = {}
        for c in coins:
            with gzip.open(os.path.join(DATA, f"{c}.json.gz"), "rt") as f:
                data[c] = (B.load("crypto", c, "1H"), json.load(f))
        for name in ("base", "delta", "absorb", "cvd"):
            all_tr, curves = [], []
            for c, (b, share) in data.items():
                tr, cv = BMM.run("crypto", b, "1H", flt=filters(b, share)[name])
                all_tr += tr
                curves.append(cv)
            port = B.mix(curves)
            f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
            n = sum(1 for _, _, t in all_tr if t >= B.ms(B.START))
            r = sum(p for _, p, t in all_tr if t >= B.ms(B.START)) / max(n, 1) / (1000 * B.RISK)
            pf = lambda s: "-" if s is None else f"{s['pf']:.2f}"
            lp = "-" if f["long_pf"] is None else f"{f['long_pf']:.2f}"
            print(f"| {title} | {name} | {f['tpw']:.1f} | {n} | {f['win']:.0f}% | {f['pf']:.2f} | {r:+.2f} | "
                  f"{pf(h1)} | {pf(h2)} | {lp} |", flush=True)


if __name__ == "__main__":
    main()
