"""
BRAD_MORE: how often can Brad's model trade, and does it still pay? (Oct 8 2026)
research/brad_rules.py with looser knobs: sweep window, 4H discount on/off, 23 coins + 8 forex on 1H.
"R/trade" = average result per trade in units of the 0.5% risk (after costs).

  python3 research/brad_more.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_rules as BR  # noqa: E402

COINS23 = "BTC ETH SOL XRP BNB ADA DOGE AVAX LINK LTC DOT XLM BCH HBAR NEAR UNI ATOM SHIB TRX SUI AAVE ETC ALGO".split()


def main():
    print("| Market | Chart | Sweep window | Discount rule | Target | Trades/wk | Win % | PF | R/trade | 2019-22 PF | 2023-now PF |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    sets = [("crypto", "1H", COINS23, 1.0), ("crypto", "15m", B.CRYPTO, 1.0)]
    if os.path.isdir(B.FXDIR):
        sets += [("forex", "1H", B.FOREX, 20.0), ("forex", "15m", B.FOREX, 20.0)]
    for market, tf, insts, lev in sets:
        B.MS_CUR[0] = B.MS[tf]
        data = {}
        for i in insts:
            try:
                data[i] = B.load(market, i, tf)
            except Exception:
                pass
        for win in (12, 24, 48):
            for disc in (True, False):
                for rr in (2, 3):
                    all_tr, curves = [], []
                    for i, b in data.items():
                        tr, cv = BR.run(market, b, tf, rr, lev=lev, win=win, discount=disc)
                        all_tr += tr
                        curves.append(cv)
                    port = B.mix(curves)
                    f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in
                                 ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
                    n = sum(1 for _, _, t in all_tr if t >= B.ms(B.START))
                    r = sum(p for _, p, t in all_tr if t >= B.ms(B.START)) / max(n, 1) / (1000 * B.RISK)
                    pf2 = lambda s: "-" if s is None else f"{s['pf']:.2f}"
                    print(f"| {market} ({len(data)}) | {tf} | {win} candles | {'on' if disc else 'off'} | {rr}R | "
                          f"{f['tpw']:.1f} | {f['win']:.0f}% | {f['pf']:.2f} | {r:+.2f} | {pf2(h1)} | {pf2(h2)} |", flush=True)


if __name__ == "__main__":
    main()
