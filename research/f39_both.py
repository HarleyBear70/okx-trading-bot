"""
F39: looking for ONE strategy that works on crypto AND EUR/USD + GBP/USD (Jeff, Oct 7 2026). Rules fixed before running.
Forex trends faded after ~2019 (F38), so the candidates are a mean-reversion rule and a forex session rule:
  R  RSI(2) mean reversion (Connors), daily. Long: close > SMA200 and RSI(2) < L -> buy at the close, exit at the
     first close above SMA5. Short (forex only): close < SMA200 and RSI(2) > 100-L, exit at the first close below SMA5.
     Safety stop 3 ATR(20). Variants L = 10 and L = 5.
  A  Asian-range breakout ("London open"), forex 4H: range = high/low of the 00:00 and 04:00 UTC candles; if the
     08:00 or 12:00 UTC candle closes above (below) the range, buy (sell) at that close; stop at the other side of the
     range; target 1.5x the range; otherwise exit at the 16:00 UTC candle's close.
Forex sim: own simple simulator (leverage allowed up to 10x like a real forex account; risk 0.5% of balance per
trade from the stop), cost 0.01% a side (~1 pip). Crypto: engine.trade_sim, long only, Binance.US 0.02%.
Research only.
"""
import datetime as dt
import engine as e
import bot
import forex_dxy as fx

FOREX = ["EURUSD", "GBPUSD"]
CRYPTO = ["BTC", "ETH", "SOL", "XRP", "BNB"]
FX_COST, RISK, LEV = 0.0001, 0.005, 10.0
FX0, FXCUT = dt.datetime(2012, 3, 1, tzinfo=e.UTC), dt.datetime(2019, 1, 1, tzinfo=e.UTC)


def fx_sim(signals, data, t0, t1):
    """signals[pair] = list per bar of None or (side, stop, target or None, exit_fn(k) -> bool[, trail_fn(k) -> stop]).
    One trade per pair."""
    t0m, t1m = e.ms(t0), e.ms(t1) if t1 else 1 << 62
    eq, pos, trades, curve = 1000.0, {}, [], []
    times = sorted({b["ts"] for p in data for b in data[p] if t0m <= b["ts"] < t1m})
    idx = {p: {b["ts"]: k for k, b in enumerate(data[p])} for p in data}

    def close(p, px):
        nonlocal eq
        q = pos.pop(p)
        pnl = q["side"] * (px - q["entry"]) * q["units"] - (q["entry"] + px) * q["units"] * FX_COST
        eq += pnl
        trades.append({"pnl": pnl})
    for ts in times:
        for p in data:
            k = idx[p].get(ts)
            if k is None:
                continue
            b = data[p][k]
            if p in pos:
                q = pos[p]
                hit_stop = b["l"] <= q["stop"] if q["side"] == 1 else b["h"] >= q["stop"]
                hit_tp = q["tp"] and (b["h"] >= q["tp"] if q["side"] == 1 else b["l"] <= q["tp"])
                if hit_stop:
                    close(p, min(q["stop"], b["o"]) if q["side"] == 1 else max(q["stop"], b["o"]))
                elif hit_tp:
                    close(p, max(q["tp"], b["o"]) if q["side"] == 1 else min(q["tp"], b["o"]))
                elif q["exit"](k):
                    close(p, b["c"])
                elif q.get("trail"):
                    ns = q["trail"](k)  # trailing stop, set at the close, only tightens
                    q["stop"] = max(q["stop"], ns) if q["side"] == 1 else min(q["stop"], ns)
            s = signals[p][k]
            if p not in pos and s:
                side, stop, tp, ex = s[:4]
                dist = abs(b["c"] - stop)
                if dist <= 0:
                    continue
                units = min(eq * RISK / dist, eq * LEV / b["c"])
                pos[p] = {"side": side, "entry": b["c"], "stop": stop, "tp": tp, "exit": ex, "units": units,
                          "trail": s[4] if len(s) > 4 else None}
        curve.append((ts, eq))
    peak, dd = 1000.0, 0.0
    for _, v in curve:
        peak, dd = max(peak, v), min(dd, v / max(peak, v) - 1)
    won = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    lost = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    return {"ret": eq / 10 - 100, "dd": dd * 100, "pf": won / lost if lost else 0.0, "trades": len(trades),
            "win": 100 * sum(t["pnl"] > 0 for t in trades) / len(trades) if trades else 0.0, "curve": curve}


def rsi2_signals(bars, lo, shorts):
    c = [b["c"] for b in bars]
    h, l = [b["h"] for b in bars], [b["l"] for b in bars]
    s200, r2, a = bot.sma(c, 200), bot.rsi(c, 2), bot.atr(h, l, c, 20)

    def sma5(k):
        return sum(c[k - 4:k + 1]) / 5
    out = [None] * len(bars)
    for k in range(200, len(bars)):
        if not (s200[k] and r2[k] is not None and a[k]):
            continue
        if c[k] > s200[k] and r2[k] < lo:
            out[k] = (1, c[k] - 3 * a[k], None, lambda j: c[j] > sma5(j))
        elif shorts and c[k] < s200[k] and r2[k] > 100 - lo:
            out[k] = (-1, c[k] + 3 * a[k], None, lambda j: c[j] < sma5(j))
    return out


def asian_signals(bars):
    out = [None] * len(bars)
    hour = [dt.datetime.fromtimestamp(b["ts"] / 1000, e.UTC).hour for b in bars]
    day = [b["ts"] // 86400000 for b in bars]
    for k in range(2, len(bars)):
        if hour[k] not in (8, 12):
            continue
        asia = [j for j in range(max(0, k - 4), k) if day[j] == day[k] and hour[j] in (0, 4)]
        if len(asia) != 2:
            continue
        hi, lo = max(bars[j]["h"] for j in asia), min(bars[j]["l"] for j in asia)
        rng, c = hi - lo, bars[k]["c"]
        if rng <= 0:
            continue
        d0 = day[k]
        ex = (lambda d0: lambda j: hour[j] >= 16 or day[j] != d0)(d0)
        if c > hi:
            out[k] = (1, lo, c + 1.5 * rng, ex)
        elif c < lo:
            out[k] = (-1, hi, c - 1.5 * rng, ex)
    return out


def cell(r):
    return f"{r['ret']:+.0f}% / {r['dd']:.1f}% / PF {r['pf']:.2f} / win {r['win']:.0f}% ({r['trades']})"


def crypto_rsi2(lo):
    c_data = {c: (d, d) for c, (_, d) in e.load(CRYPTO).items()}

    def ent(coin, bars, _d):
        sig = rsi2_signals(bars, lo, False)
        return [None if s is None else {"stop": s[1]} for s in sig]

    def man(p, bars, k):
        c = [b["c"] for b in bars[max(0, k - 4):k + 1]]
        return "exit" if len(c) == 5 and bars[k]["c"] > sum(c) / 5 else None
    return [e.trade_sim(CRYPTO, c_data, ent, a, b, risk=RISK, max_open=5, fee=0.0002, manage=man)
            for a, b in ((e.START, None), (e.START, e.CUT), (e.CUT, None))]


def main():
    h4 = {p: fx.fxcm(p) for p in FOREX}
    daily = {p: fx.fx_daily(h4[p]) for p in FOREX}
    periods = ((FX0, None), (FX0, FXCUT), (FXCUT, None))
    print("| Strategy | Market | Full period | 1st half | 2nd half |\n|---|---|---|---|---|")
    for lo in (10, 5):
        sig = {p: rsi2_signals(daily[p], lo, True) for p in FOREX}
        rs = [fx_sim(sig, daily, a, b) for a, b in periods]
        print(f"| R RSI(2) {lo}/{100 - lo}, long+short | EUR/USD + GBP/USD | " + " | ".join(cell(r) for r in rs) + " |",
              flush=True)
        rs = crypto_rsi2(lo)
        print(f"| R RSI(2) < {lo}, long only | crypto (Binance.US fee) | " + " | ".join(cell(r) for r in rs) + " |",
              flush=True)
    sig = {p: asian_signals(h4[p]) for p in FOREX}
    rs = [fx_sim(sig, h4, a, b) for a, b in periods]
    print("| A Asian-range breakout (London open) | EUR/USD + GBP/USD | " + " | ".join(cell(r) for r in rs) + " |")


if __name__ == "__main__":
    main()
