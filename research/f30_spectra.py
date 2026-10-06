"""
F30: a copy of "SPECTRA - Signal Processing Engine" (SentioEdge, invite-only TradingView script) built from its public
description (screenshots, Oct 6 2026). Closed source, so the settings below are guesses at sensible defaults.
Long only (OKX spot), 4H candles, real fee 0.35% a side, 0.4% risk (like Trend Rider), one shared $1,000.

Rules from the description:
  1. Kalman filter on HL2 and on ATR.
  2. Supertrend on the filtered price/ATR; BUY needs a bullish flip.
  3. Smart Trail: price must be above an ATR trailing stop (only ratchets in the trend direction).
  4. RSI(14) above 50 and rising.
  5. Volume: "Strong" if the signal bar's volume > its 20-bar SMA, else "Normal".
  6. Cooldown: a minimum number of bars between signals.
  Stop: lowest low of the last N bars minus an ATR buffer. TP1 = 1R, TP2 = 2R.
  Modes: TP1 only, TP2 only, split (half at TP1, half at TP2, stop unchanged).
Research only, bot.py is not changed.
"""
import itertools
import engine as e
import bot

COINS = ["BTC", "ETH", "SOL", "XRP", "BNB"]
RISK = 0.004


def kalman(z, ratio):
    """Scalar random-walk Kalman filter; ratio = process noise / measurement noise (higher = reacts faster)."""
    out, x, p = [], None, 1.0
    for v in z:
        if v is None:
            out.append(x)
            continue
        if x is None:
            x = v
        else:
            p += ratio
            k = p / (p + 1.0)
            x += k * (v - x)
            p *= 1 - k
        out.append(x)
    return out


def signals(bars, mult=3.0, smooth=0.1, trail_k=2.5, swing=10, buf=0.5, cool=5, strong_only=False):
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    v = [b.get("v", 0) or 0 for b in bars]
    n = len(bars)
    a10, a14 = bot.atr(h, l, c, 10), bot.atr(h, l, c, 14)
    src, ka = kalman([(h[i] + l[i]) / 2 for i in range(n)], smooth), kalman(a10, smooth)
    rsi = bot.rsi(c, 14)
    vma = [None] * n
    for i in range(19, n):
        vma[i] = sum(v[i - 19:i + 1]) / 20
    # Supertrend on the filtered inputs
    up, dn, trend = [None] * n, [None] * n, [1] * n
    # Smart Trail
    trail, tdir = [None] * n, [1] * n
    out, last_sig = [None] * n, -10 ** 9
    for i in range(1, n):
        if ka[i] is None or a14[i] is None:
            continue
        bu, bd = src[i] - mult * ka[i], src[i] + mult * ka[i]
        up[i] = max(bu, up[i - 1]) if up[i - 1] is not None and c[i - 1] > up[i - 1] else bu
        dn[i] = min(bd, dn[i - 1]) if dn[i - 1] is not None and c[i - 1] < dn[i - 1] else bd
        if trend[i - 1] == -1 and dn[i - 1] is not None and c[i] > dn[i - 1]:
            trend[i] = 1
        elif trend[i - 1] == 1 and up[i - 1] is not None and c[i] < up[i - 1]:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1]
        t_prev = trail[i - 1]
        if t_prev is None:
            trail[i], tdir[i] = c[i] - trail_k * a14[i], 1
        elif tdir[i - 1] == 1:
            if c[i] < t_prev:
                trail[i], tdir[i] = c[i] + trail_k * a14[i], -1
            else:
                trail[i], tdir[i] = max(t_prev, c[i] - trail_k * a14[i]), 1
        else:
            if c[i] > t_prev:
                trail[i], tdir[i] = c[i] - trail_k * a14[i], 1
            else:
                trail[i], tdir[i] = min(t_prev, c[i] + trail_k * a14[i]), -1
        flip = trend[i] == 1 and trend[i - 1] == -1
        if not flip or i < swing or rsi[i] is None or rsi[i - 1] is None:
            continue
        if not (tdir[i] == 1 and c[i] > trail[i] and rsi[i] > 50 and rsi[i] > rsi[i - 1]):
            continue
        if i - last_sig < cool:
            continue
        strong = vma[i] is not None and v[i] > vma[i]
        if strong_only and not strong:
            continue
        sl = min(l[i - swing + 1:i + 1]) - buf * a14[i]
        if sl >= c[i]:
            continue
        last_sig = i
        out[i] = {"stop": sl, "r": c[i] - sl}
    return out


def run(coins, data, t0, t1, mode, **kw):
    """mode: 'tp1', 'tp2' or 'split' (two half-risk pieces per signal, one per target)."""
    cache = {c: signals(data[c][0], **kw) for c in coins}

    def make(mult_r):
        def ent(key, bars, _d):
            sig = cache[key.split("#")[0]]
            return [None if s is None else {"stop": s["stop"], "target": bars[k]["c"] + mult_r * s["r"]}
                    for k, s in enumerate(sig)]
        return ent
    if mode == "split":
        keys = [f"{c}#1" for c in coins] + [f"{c}#2" for c in coins]
        d2 = {k: data[k.split("#")[0]] for k in keys}

        def ent(key, bars, d):
            return make(1 if key.endswith("#1") else 2)(key, bars, d)
        return e.trade_sim(keys, d2, ent, t0, t1, risk=RISK / 2, max_open=2 * len(coins))
    return e.trade_sim(coins, data, make(1 if mode == "tp1" else 2), t0, t1, risk=RISK, max_open=len(coins))


def fmt(r):
    return f"{r['ret']:+.1f}% / {r['dd']:.1f}% / {r['pf']:.2f} ({r['trades']})"


def main():
    data = e.load(COINS)
    print("| Variant | 2018-now return / DD / PF (trades) | 1st half (2018-21) | 2nd half (2022-now) |")
    print("|---|---|---|---|")
    rows = []
    for mult, smooth, mode, strong in itertools.product([2.0, 3.0], [0.05, 0.3], ["tp1", "tp2", "split"], [False, True]):
        kw = {"mult": mult, "smooth": smooth, "strong_only": strong}
        res = [run(COINS, data, t0, t1, mode, **kw) for _, t0, t1 in [("full", e.START, None)] + list(e.HALVES)]
        label = f"ST x{mult:g}, smooth {smooth}, {mode}, {'strong only' if strong else 'all signals'}"
        rows.append((res[0]["ret"], label, kw, mode))
        print(f"| {label} | " + " | ".join(fmt(r) for r in res) + " |", flush=True)
    # never-seen coins for the best full-period variant
    best = max(rows)
    _, label, kw, mode = best
    print(f"\nBest variant: {label}. Never-seen coins (each alone, pooled per half):")
    u = e.unseen_pooled(lambda c, d, t0, t1: run([c], d, t0, t1, mode, **kw), coins=["LTC", "DOGE", "ADA", "LINK", "AVAX", "XLM"])
    for h, x in u.items():
        print(f"- {h}: {x['trades']} trades, P/L {x['pnl']:+.1f} on $1,000 per coin-period, PF {x['pf']:.2f}, worst DD {x['worst']:.1f}%")


if __name__ == "__main__":
    main()
