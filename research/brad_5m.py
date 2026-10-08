"""
BRAD_5M: Brad's sweep + FVG model on 5-minute entries (Oct 8 2026), the piece the trading_bots_v1.zip sketch added.
research/brad_rules.py run on 5m candles (Binance archive, research/m5.py), 4H trend, 5 coins, both directions.
Costs 0.07% a side (Binance.US), not the 0.05% of battery.py: on 5m charts stops are small, so fees matter more.
"R/trade" = average result per trade in units of the 0.5% risk, after costs.

  python3 research/brad_5m.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import brad_rules as BR  # noqa: E402
import m5  # noqa: E402

B.MS["5m"] = 300000
B.cost = lambda market, b, px: 0.0007 * px


def main():
    data = {c: [dict(x, sp=0.0) for x in m5.m5(c) if x["ts"] >= B.ms(B.START) - 60 * 86400000] for c in B.CRYPTO}
    print("| Sweep window | Discount rule | Target | Trades/wk | Win % | PF | R/trade | 2019-22 PF | 2023-now PF | Long PF | Short PF |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for win in (36, 96, 288):  # 3 hours, 8 hours, 1 day of 5m candles
        for disc in (True, False):
            for rr in (2, 3):
                all_tr, curves = [], []
                for b in data.values():
                    tr, cv = BR.run("crypto", b, "5m", rr, win=win, discount=disc)
                    all_tr += tr
                    curves.append(cv)
                port = B.mix(curves)
                f, h1, h2 = (B.summarize(all_tr, port, a, z) for a, z in
                             ((B.START, None), (B.START, B.CUT), (B.CUT, None)))
                n = max(len(all_tr), 1)
                r = sum(p for _, p, _ in all_tr) / n / (1000 * B.RISK)
                pf = lambda v: "-" if v is None else f"{v:.2f}"
                print(f"| {win} candles | {'on' if disc else 'off'} | {rr}R | {f['tpw']:.1f} | {f['win']:.0f}% | "
                      f"{f['pf']:.2f} | {r:+.2f} | {pf(h1 and h1['pf'])} | {pf(h2 and h2['pf'])} | "
                      f"{pf(f['long_pf'])} | {pf(f['short_pf'])} |", flush=True)


if __name__ == "__main__":
    main()
