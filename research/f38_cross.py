"""
F38: Jeff (Oct 7 2026): "find me a strategy that will work with forex and crypto". The family with the most published
cross-asset evidence is trend following / time-series momentum (Moskowitz, Ooi & Pedersen 2012 "Time Series Momentum";
the Turtle / Donchian channel rules; recent crypto TSMOM studies). Tested here on Jeff's markets, daily bars:
  crypto BTC ETH SOL XRP BNB, long only (spot), Binance.US fee 0.02% (and OKX 0.35% for reference), 2018-now
  forex EUR/USD + GBP/USD, long AND short, cost 0.01% a side (~1 pip spread), 2012-now (FXCM history)
Strategies (rules fixed before running):
  D20  Donchian 20/10: enter on a close beyond the prior 20-day high (long) / low (short); first stop 2 ATR(20);
       trail at the 10-day low (long) / high (short).
  D55  Turtle 55/20: same with 55-day entry, 20-day trail.
  M90  Time-series momentum: long while the 90-day return is positive, short (forex) / cash (crypto) while negative;
       checked daily; safety stop 3 ATR(20) trailing at the 20-day extreme.
  M200 same with a 200-day return.
Risk 0.5% per trade, one shared $1,000 per market group. Research only.
"""
import engine as e
import bot
import forex_dxy as fx

CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB"]
FOREX = ["EURUSD", "GBPUSD"]


def ind(bars):
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    return h, l, c, bot.atr(h, l, c, 20)


def donchian(n_in, n_out, shorts):
    def entries(coin, bars, _d):
        h, l, c, a = ind(bars)
        out = [None] * len(bars)
        for k in range(n_in, len(bars)):
            if a[k] is None:
                continue
            if c[k] > max(h[k - n_in:k]):
                out[k] = {"stop": c[k] - 2 * a[k], "side": 1}
            elif shorts and c[k] < min(l[k - n_in:k]):
                out[k] = {"stop": c[k] + 2 * a[k], "side": -1}
        return out

    def manage(p, bars, k):
        if k < n_out:
            return None
        w = bars[k - n_out + 1:k + 1]
        return min(b["l"] for b in w) if p["side"] == 1 else max(b["h"] for b in w)
    return entries, manage


def momentum(look, shorts):
    def sign(c, k):
        return 0 if k < look else (1 if c[k] > c[k - look] else -1)

    def entries(coin, bars, _d):
        h, l, c, a = ind(bars)
        out = [None] * len(bars)
        for k in range(look + 1, len(bars)):
            s, s0 = sign(c, k), sign(c, k - 1)
            if a[k] is None or s == s0:
                continue
            if s == 1:
                out[k] = {"stop": c[k] - 3 * a[k], "side": 1}
            elif shorts:
                out[k] = {"stop": c[k] + 3 * a[k], "side": -1}
        return out

    def manage(p, bars, k):
        c = [b["c"] for b in bars[:k + 1]]
        if sign(c, k) != p["side"]:
            return "exit"
        w = bars[max(0, k - 19):k + 1]
        return min(b["l"] for b in w) if p["side"] == 1 else max(b["h"] for b in w)
    return entries, manage


STRATS = [("D20 Donchian 20/10", lambda s: donchian(20, 10, s)), ("D55 Turtle 55/20", lambda s: donchian(55, 20, s)),
          ("M90 momentum 90d", lambda s: momentum(90, s)), ("M200 momentum 200d", lambda s: momentum(200, s))]


def cell(r):
    return f"{r['ret']:+.0f}% / {r['dd']:.1f}% / PF {r['pf']:.2f} / win {r['win']:.0f}% ({r['trades']})"


def main():
    crypto = {c: (d, d) for c, (_, d) in e.load(CRYPTO).items()}
    forex = {p: (d, d) for p, d in ((p, fx.fx_daily(fx.fxcm(p))) for p in FOREX)}
    cut_fx = e.dt.datetime(2019, 1, 1, tzinfo=e.UTC)
    fx0 = e.dt.datetime(2012, 3, 1, tzinfo=e.UTC)
    print("| Strategy | Market | Cost | Full period | 1st half | 2nd half |\n|---|---|---|---|---|---|")
    for name, mk in STRATS:
        for label, data, coins, shorts, fees, t0, cut in (
                ("crypto (long only)", crypto, CRYPTO, False, (("Binance.US 0.02%", 0.0002), ("OKX 0.35%", 0.0035)),
                 e.START, e.CUT),
                ("EUR/USD + GBP/USD (long+short)", forex, FOREX, True, (("~1 pip 0.01%", 0.0001),), fx0, cut_fx)):
            ent, man = mk(shorts)
            for flab, fee in fees:
                rs = [e.trade_sim(coins, data, ent, a, b, risk=0.005, max_open=len(coins), fee=fee, manage=man)
                      for a, b in ((t0, None), (t0, cut), (cut, None))]
                print(f"| {name} | {label} | {flab} | " + " | ".join(cell(r) for r in rs) + " |", flush=True)


if __name__ == "__main__":
    main()
