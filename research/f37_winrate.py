"""
F37: Chrome Claude's win-rate ideas (issue #4, Oct 7 2026), each at OKX's 0.35% and Binance.US's 0.02% fee.
  A  The N1 range bots (research/N1_RANGE.md, failed at 0.1%) re-run at 0.02%: was it only fees?
  B  RSI(2) dip-buy in an uptrend (Connors): daily, close > SMA200 and RSI(2) < 10 -> buy at the close; sell at the
     first close above SMA5; catastrophe stop 3 ATR(14). Variant B2: RSI(2) < 5. Coins BTC ETH SOL XRP BNB, 0.5% risk.
  C  Partial take profit on the live bots (Trend Rider, Donchian, live settings): sell half at +1R, then the rest's
     stop goes to entry and keeps trailing as before. Judged on total profit and drop, not only win %.
Research only.
"""
import engine as e
import bot
import f29_coins as f29
import n1_range as n1

COINS = ["BTC", "ETH", "SOL", "XRP", "BNB"]
FEES = [("OKX 0.35%", 0.0035), ("Binance.US 0.02%", 0.0002)]
PERIODS = [("2018-now", e.START, None), ("2018-21", e.START, e.CUT), ("2022-now", e.CUT, None)]


def cell(r):
    return f"{r['ret']:+.0f}% / {r['dd']:.1f}% / win {r['win']:.0f}% / PF {r['pf']:.2f} ({r['trades']})"


def set_fee(fee):
    bot.FEE, bot.BE_BUFFER = fee, 2 * fee


# ---------- B: RSI(2) dip-buy ----------
def rsi2_entries(th):
    def fn(coin, bars, daily):
        c = [b["c"] for b in bars]
        h, l = [b["h"] for b in bars], [b["l"] for b in bars]
        s200, r2, a = bot.sma(c, 200), bot.rsi(c, 2), bot.atr(h, l, c, 14)
        return [{"stop": c[k] - 3 * a[k]} if (s200[k] and r2[k] is not None and a[k] and c[k] > s200[k] and r2[k] < th)
                else None for k in range(len(bars))]
    return fn


def rsi2_manage(p, bars, k):
    c = [b["c"] for b in bars[max(0, k - 4):k + 1]]
    return "exit" if len(c) == 5 and bars[k]["c"] > sum(c) / 5 else None


# ---------- C: half at +1R on the live bots ----------
def run_half(strat, fee, t0, t1):
    set_fee(fee)
    o_extra = bot.entry_extra

    def extra(b, bar, info):
        x = dict(o_extra(b, bar, info))
        x.pop("no_half", None)
        x["half_at"] = bar["c"] + (bar["c"] - info["sl"])  # +1R
        x["be_after_half"] = True
        return x
    bot.entry_extra = extra
    try:
        if strat == "tr":
            cs = f29.coins("tr-okx")
            d = e.load(cs)
            st = {**f29.settings("tr-okx"), "half_at_2r": True}
            return e.bot_sim("tr", cs, d, lambda b, dd: bot.analyse_tr(b, dd, 5), t0, t1, settings=st)
        cs = f29.coins("dc-okx")
        dn = {c: (daily, daily) for c, (_, daily) in e.load(cs).items()}
        btc = e.load(["BTC"])["BTC"][1]
        per = {}
        for c in cs:
            a = bot.analyse_donchian(dn[c][1])
            ok = bot.btc_leash(dn[c][1], btc, c)
            a["signal"] = [s and o for s, o in zip(a["signal"], ok)]
            per[id(dn[c][1])] = a
        st = {**f29.settings("dc-okx"), "half_at_2r": True}
        return e.bot_sim("donchian", cs, dn, lambda b, d: per[id(b)], t0, t1, settings=st)
    finally:
        bot.entry_extra = o_extra


def run_live(strat, fee, t0, t1):
    set_fee(fee)
    return (f29.tr_run(f29.coins("tr-okx")) if strat == "tr" else f29.dc_run(f29.coins("dc-okx")))(t0, t1)


def main():
    o_fee, o_be = bot.FEE, bot.BE_BUFFER
    try:
        print("## A: N1 range bots at Binance.US fees (design coins BTC ETH XRP, 4H)\n")
        print("| Variant | Fee | " + " | ".join(p for p, _, _ in PERIODS) + " |\n|---|---|---|---|---|")
        d4 = e.load(e.DESIGN)
        for name, n, frac in (("R1 60 candles, target 80%", 60, 0.8), ("R3 120 candles, target 80%", 120, 0.8)):
            for flab, fee in FEES:
                rs = [e.trade_sim(e.DESIGN, d4, n1.entries(n, frac), t0, t1, fee=fee) for _, t0, t1 in PERIODS]
                print(f"| {name} | {flab} | " + " | ".join(cell(r) for r in rs) + " |", flush=True)

        print("\n## B: RSI(2) dip-buy above the 200-day average (daily)\n")
        print("| Variant | Fee | " + " | ".join(p for p, _, _ in PERIODS) + " |\n|---|---|---|---|---|")
        dd_ = {c: (daily, daily) for c, (_, daily) in e.load(COINS).items()}
        for name, th in (("B1 RSI(2) < 10", 10), ("B2 RSI(2) < 5", 5)):
            for flab, fee in FEES:
                rs = [e.trade_sim(COINS, dd_, rsi2_entries(th), t0, t1, fee=fee, max_open=5, manage=rsi2_manage)
                      for _, t0, t1 in PERIODS]
                print(f"| {name} | {flab} | " + " | ".join(cell(r) for r in rs) + " |", flush=True)

        print("\n## C: sell half at +1R, rest to breakeven and keeps trailing (live bots)\n")
        print("| Bot | Exits | Fee | " + " | ".join(p for p, _, _ in PERIODS) + " |\n|---|---|---|---|---|---|")
        for strat, bname in (("tr", "Trend Rider"), ("dc", "Donchian")):
            for flab, fee in FEES:
                for lab, fn in (("as live", run_live), ("half at +1R", run_half)):
                    rs = [fn(strat, fee, t0, t1) for _, t0, t1 in PERIODS]
                    print(f"| {bname} | {lab} | {flab} | " + " | ".join(cell(r) for r in rs) + " |", flush=True)
    finally:
        bot.FEE, bot.BE_BUFFER = o_fee, o_be


if __name__ == "__main__":
    main()
