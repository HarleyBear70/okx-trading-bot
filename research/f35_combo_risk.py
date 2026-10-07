"""
F35: Trend Rider + Donchian + NNFX together (each its own $1,000 slice of one $3,000 pot, as F17), with every bot's
risk per trade scaled by 1x, 1.25x, 1.5x, 1.75x, 2x. Live bot.py settings, real fee 0.35% a side. Answers Jeff's
"how do I get from ~+150% to +300%": how much return each risk level buys, and the worst drop it costs.
Research only.
"""
import engine as e
import bot
import f29_coins as f29

MULTS = [1.0, 1.25, 1.5, 1.75, 2.0]
DAY = 86400000


def daily(curve):
    out = {}
    for ts, v in curve:
        out[ts // DAY] = v
    return out


def combo(m, t0, t1):
    o_risk = bot.risk_pct
    bot.risk_pct = lambda b, bs: o_risk(b, bs) * m
    try:
        runs = [f29.tr_run(f29.coins("tr-okx"))(t0, t1), f29.dc_run(f29.coins("dc-okx"))(t0, t1),
                f29.nnfx_run(f29.coins("nnfx-okx"))(t0, t1)]
    finally:
        bot.risk_pct = o_risk
    series = [daily(r["curve"]) for r in runs]
    days = sorted(set().union(*series))
    last = [1000.0] * len(series)
    peak, dd, total = 3000.0, 0.0, 3000.0
    for d in days:
        for i, s in enumerate(series):
            if d in s:
                last[i] = s[d]
        total = sum(last)
        peak = max(peak, total)
        dd = min(dd, total / peak - 1)
    return total / 30 - 100, dd * 100, [r["ret"] for r in runs]


def main():
    print("| Risk per trade | All 3 together: 2018-now | Worst drop | 2018-21 | 2022-now | $200 would become | Each bot (TR / DC / NNFX) |")
    print("|---|---|---|---|---|---|---|")
    for m in MULTS:
        full = combo(m, e.START, None)
        h1 = combo(m, e.START, e.CUT)
        h2 = combo(m, e.CUT, None)
        tr = f"{0.4 * m:.2f}% / {0.32 * m:.2f}% / {0.5 * m:.2f}%"
        print(f"| {m:g}x ({tr}) | {full[0]:+.0f}% | {full[1]:.1f}% | {h1[0]:+.0f}% | {h2[0]:+.0f}% | "
              f"${200 * (1 + full[0] / 100):,.0f} | {' / '.join(f'{x:+.0f}%' for x in full[2])} |", flush=True)


if __name__ == "__main__":
    main()
