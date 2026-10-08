"""
CANDLE_PATTERNS: do the poster candle patterns work at Jeff's levels? (Oct 8 2026)

Only in the trend direction and only at a level, never mid-range:
  trend = 4H trend (Smoke Detector engine), level = 4H discount for buys / premium for sells (50% of the swing).
Signal on the candle close, enter at the next open. Stop just past the pattern's low/high (- 0.1 ATR).
Target 2R. One trade per coin at a time. Costs 0.07% a side (Binance.US). Results in R (1R = the amount risked).

Patterns (buy version; sells are the mirror):
  hammer       lower wick >= 60% of the candle, body <= 35%            (shooting star)
  engulfing    red candle, then a green body that covers it            (bearish engulfing)
  piercing     red candle, green opens below its close, closes past its middle   (dark cloud cover)
  tweezer      red then green with lows within 0.1 ATR                 (tweezer top)
  morning star big red, small body, green closing past the red's middle  (evening star)
  3 soldiers   three green candles, each closing higher, solid bodies  (three black crows)
  double bottom  a new swing low within 0.3 ATR of the last one, then a close back above it   (double top)
  small shift  market shift on swings of 2 candles (the little turn the bots normally miss)
  pattern + shift  any pattern above, then a small shift within the next 6 candles
  any candle   baseline: every candle at the level in the trend direction (do patterns beat just being there?)

  python3 research/candle_patterns.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import battery as B  # noqa: E402
import jeff_topdown as J  # noqa: E402

COST, RR, CUSH = 0.0007, 2.0, 0.1
COINS23 = "BTC ETH SOL XRP BNB ADA DOGE AVAX LINK LTC DOT XLM BCH HBAR NEAR UNI ATOM SHIB TRX SUI AAVE ETC ALGO".split()
NAMES = ["hammer", "engulfing", "piercing", "tweezer", "morning star", "3 soldiers", "double bottom",
         "small shift", "pattern + shift", "any candle"]


def flip(b):
    """mirror prices so every sell pattern is the buy pattern on the flipped chart"""
    return [dict(x, o=-x["o"], h=-x["l"], l=-x["h"], c=-x["c"]) for x in b]


def patterns(b, a, small):
    """per candle: set of buy patterns that completed on it, and the pattern's low"""
    n = len(b)
    out = [None] * n
    lastL, prevL = None, None
    for k in range(3, n):
        x, p, q = b[k], b[k - 1], b[k - 2]
        if not a[k]:
            continue
        hits = set()
        rng = x["h"] - x["l"]
        body = abs(x["c"] - x["o"])
        green, pred = x["c"] > x["o"], p["c"] < p["o"]
        if rng > 0 and body <= 0.35 * rng and min(x["o"], x["c"]) - x["l"] >= 0.6 * rng:
            hits.add("hammer")
        if pred and green and x["o"] <= p["c"] and x["c"] >= p["o"]:
            hits.add("engulfing")
        if pred and green and x["o"] < p["c"] and (p["o"] + p["c"]) / 2 < x["c"] < p["o"]:
            hits.add("piercing")
        if pred and green and abs(x["l"] - p["l"]) <= 0.1 * a[k]:
            hits.add("tweezer")
        qb = q["o"] - q["c"]
        if qb > 0.6 * a[k] and abs(p["c"] - p["o"]) <= 0.3 * qb and green and x["c"] > (q["o"] + q["c"]) / 2:
            hits.add("morning star")
        if all(y["c"] > y["o"] and y["c"] - y["o"] >= 0.5 * (y["h"] - y["l"]) for y in (q, p, x)) \
                and q["c"] < p["c"] < x["c"]:
            hits.add("3 soldiers")
        # double bottom: swing lows of 2 candles each side, confirmed 2 candles later
        j = k - 2
        if j >= 2 and b[j]["l"] == min(y["l"] for y in b[j - 2:k + 1]):
            prevL, lastL = lastL, (j, b[j]["l"])
        if lastL and prevL and lastL[0] == k - 2 and abs(lastL[1] - prevL[1]) <= 0.3 * a[k] and x["c"] > lastL[1]:
            hits.add("double bottom")
        if small["shift"][k] and small["trend"][k] == 1:
            hits.add("small shift")
        if hits:
            span = 3 if hits & {"morning star", "3 soldiers"} else 2
            low = min(y["l"] for y in b[k - span + 1:k + 1])
            if "double bottom" in hits or "small shift" in hits:
                low = min(low, min(y["l"] for y in b[k - 6:k + 1]))
            out[k] = (hits, low)
    # pattern, then a small shift within 6 candles
    last_pat = None
    for k in range(n):
        if out[k] and out[k][0] - {"small shift"}:
            last_pat = (k, out[k][1])
        if out[k] and "small shift" in out[k][0] and last_pat and 0 < k - last_pat[0] <= 6:
            out[k][0].add("pattern + shift")
            out[k] = (out[k][0], min(out[k][1], last_pat[1]))
    return out


def sim(b, a, sig, ok, real_px):
    """buy trades on the (possibly flipped) chart; returns [(R after costs, ts)]"""
    res, k, n = [], 0, len(b)
    while k < n - 1:
        if not (sig[k] and ok[k]):
            k += 1
            continue
        low = sig[k]
        ent = b[k + 1]["o"]
        stop = low - CUSH * a[k]
        risk = ent - stop
        if risk <= 0:
            k += 1
            continue
        tgt = ent + RR * risk
        r, m = None, k + 1
        while m < n:
            x = b[m]
            if x["l"] <= stop:
                r = (min(stop, x["o"]) - ent) / risk
                break
            if x["h"] >= tgt:
                r = (max(tgt, x["o"]) - ent) / risk
                break
            m += 1
        if r is None:
            break
        fee = COST * (abs(real_px(ent)) + abs(real_px(ent + r * risk))) / risk
        res.append((r - fee, b[k]["ts"]))
        k = m + 1
    return res


def stats(rs, weeks):
    if not rs:
        return "-"
    won, lost = sum(r for r in rs if r > 0), -sum(r for r in rs if r < 0)
    return f"{len(rs)} | {100 * sum(r > 0 for r in rs) / len(rs):.0f}% | {sum(rs) / len(rs):+.2f} | " \
           f"{won / lost if lost else 99:.2f}"


def run_set(market, tf, coins):
    B.MS_CUR[0] = B.MS[tf]
    t0, cut = B.ms(B.START), B.ms(B.CUT)
    res = {(nm, sd): [] for nm in NAMES for sd in (1, -1)}
    weeks = 0
    for c in coins:
        try:
            b = B.load(market, c, tf)
        except Exception:
            continue
        h4 = J.htf_view(b, J.H4, B.MS[tf])
        a = B.atr(b)
        weeks = max(weeks, (b[-1]["ts"] - t0) / 604800000)
        for sd in (1, -1):
            bb = b if sd == 1 else flip(b)
            J.L = 2
            small = J.structure(bb)
            J.L = 5
            pats = patterns(bb, a, small)
            ok = [x["ts"] >= t0 and h4[k][0] == sd and h4[k][1] is not None and
                  (b[k]["c"] <= h4[k][1] if sd == 1 else b[k]["c"] >= h4[k][1]) for k, x in enumerate(b)]
            for nm in NAMES:
                if nm == "any candle":
                    sig = [min(y["l"] for y in bb[max(0, k - 2):k + 1]) for k in range(len(bb))]
                else:
                    sig = [p[1] if p and nm in p[0] else None for p in pats]
                for r, ts in sim(bb, a, sig, ok, abs):
                    res[(nm, sd)].append((r, ts))
    for nm in NAMES:
        for sd in (1, -1):
            rs = res[(nm, sd)]
            allr = [r for r, _ in rs]
            h1 = [r for r, t in rs if t < cut]
            h2 = [r for r, t in rs if t >= cut]
            print(f"| {market} {tf} ({len(coins)}) | {nm} | {'buy' if sd == 1 else 'sell'} | {stats(allr, weeks)} | "
                  f"{len(allr) / max(weeks, 1):.1f} | {stats(h1, 0).split(' | ')[-1]} | {stats(h2, 0).split(' | ')[-1]} |",
                  flush=True)


def main():
    print("| Market | Pattern | Side | Trades | Win % | R/trade | PF | Trades/wk | 2019-22 PF | 2023-now PF |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    run_set("crypto", "1H", COINS23)
    run_set("crypto", "15m", B.CRYPTO)


if __name__ == "__main__":
    main()
