"""
F40: forex by trading session (Jeff, Oct 7 2026: "trade on all time zones like London, US, maybe Asia").
EUR/USD + GBP/USD, FXCM 4H candles (00/04 = Asia, 08/12 = London (12 = London+NY overlap), 16/20 = New York),
2012-now, both directions, ~1 pip cost, 0.5% risk, leverage up to 10x (f39_both.fx_sim). Rules fixed before running.
  S0  Session drift table: average move of each 4H session candle, both halves (for insight, not a trade).
  S1  London breakout WITH the trend: Asian range (00+04 candles); trade an 08/12 close beyond it only in the direction
      of the daily trend (prior day's close vs its 50-day SMA); stop at the other side; target 2x the range; else exit
      at the 20:00 UTC close.
  S2  New York fade: if the London candles (08+12) moved more than 0.8x the 20-day average daily range, fade that
      move at the 12:00 candle's close; stop beyond London's extreme; exit at the 20:00 close.
  S3  Dollar trend + 4H break of structure: DXY below its daily 50 EMA (dollar weak) -> only BUY EUR/GBP on a 4H close
      above the last 5-bar swing high while above the 4H 50 EMA; DXY above (dollar strong) -> only SELL on the mirror;
      first stop 2 ATR(14); trailing stop 3 ATR from the best close (like Trend Rider). Uses only the prior day's DXY.
Research only.
"""
import datetime as dt
import engine as e
import bot
import forex_dxy as fx
import f39_both as f39

FOREX = f39.FOREX
PERIODS = ((f39.FX0, None), (f39.FX0, f39.FXCUT), (f39.FXCUT, None))


def hours(bars):
    return [dt.datetime.fromtimestamp(b["ts"] / 1000, e.UTC).hour for b in bars]


def daily_maps(daily):
    """day -> (prior-day trend sign vs SMA50, prior 20-day average range), using only completed days."""
    c = [d["c"] for d in daily]
    s50 = bot.sma(c, 50)
    days = [bot.day_of(d["ts"]) for d in daily]
    rngs = [d["h"] - d["l"] for d in daily]
    out = {}
    for i in range(51, len(daily)):
        j = i - 1
        out[days[i]] = (1 if c[j] > s50[j] else -1, sum(rngs[j - 19:j + 1]) / 20)
    return days, out


def lookup(days, m, day):
    j = fx.last_completed(days, day)
    return m.get(days[j + 1]) if 0 <= j + 1 < len(days) and days[j + 1] == day else (m.get(day) if day in m else None)


def s1_signals(bars, daily):
    days, m = daily_maps(daily)
    h, out = hours(bars), [None] * len(bars)
    day = [bot.day_of(b["ts"]) for b in bars]
    for k in range(2, len(bars)):
        if h[k] not in (8, 12):
            continue
        asia = [j for j in range(max(0, k - 4), k) if day[j] == day[k] and h[j] in (0, 4)]
        info = m.get(day[k])
        if len(asia) != 2 or not info:
            continue
        hi, lo = max(bars[j]["h"] for j in asia), min(bars[j]["l"] for j in asia)
        rng, c, trend = hi - lo, bars[k]["c"], info[0]
        ex = (lambda d0: lambda j: h[j] >= 20 or day[j] != d0)(day[k])
        if rng > 0 and trend == 1 and c > hi:
            out[k] = (1, lo, c + 2 * rng, ex)
        elif rng > 0 and trend == -1 and c < lo:
            out[k] = (-1, hi, c - 2 * rng, ex)
    return out


def s2_signals(bars, daily):
    days, m = daily_maps(daily)
    h, out = hours(bars), [None] * len(bars)
    day = [bot.day_of(b["ts"]) for b in bars]
    for k in range(1, len(bars)):
        if h[k] != 12 or h[k - 1] != 8 or day[k - 1] != day[k] or not m.get(day[k]):
            continue
        move = bars[k]["c"] - bars[k - 1]["o"]
        hi, lo = max(bars[k]["h"], bars[k - 1]["h"]), min(bars[k]["l"], bars[k - 1]["l"])
        ex = (lambda d0: lambda j: h[j] >= 20 or day[j] != d0)(day[k])
        if abs(move) > 0.8 * m[day[k]][1]:
            out[k] = (-1, hi * 1.0005, None, ex) if move > 0 else (1, lo * 0.9995, None, ex)
    return out


def s3_signals(bars, dxy_days, weak):
    c = [b["c"] for b in bars]
    hh, ll = [b["h"] for b in bars], [b["l"] for b in bars]
    e50, a = bot.ema(c, 50), bot.atr(hh, ll, c, 14)
    out = [None] * len(bars)
    swing_hi = swing_lo = None
    for k in range(11, len(bars)):
        j = k - 5  # a swing point is confirmed 5 bars later
        if hh[j] == max(hh[j - 5:k + 1]):
            swing_hi = hh[j]
        if ll[j] == min(ll[j - 5:k + 1]):
            swing_lo = ll[j]
        i = fx.last_completed(dxy_days, bot.day_of(bars[k]["ts"]))
        if i < 0 or a[k] is None or e50[k] is None:
            continue
        dollar_weak = weak[dxy_days[i]]

        def trail(side, k0):
            def fn(jj):
                best = max(c[k0:jj + 1]) if side == 1 else min(c[k0:jj + 1])
                return best - side * 3 * (a[jj] or a[k0])
            return fn
        if dollar_weak and swing_hi and c[k] > swing_hi and c[k - 1] <= swing_hi and c[k] > e50[k]:
            out[k] = (1, c[k] - 2 * a[k], None, lambda jj: False, trail(1, k))
        elif not dollar_weak and swing_lo and c[k] < swing_lo and c[k - 1] >= swing_lo and c[k] < e50[k]:
            out[k] = (-1, c[k] + 2 * a[k], None, lambda jj: False, trail(-1, k))
    return out


def cell(r):
    return f39.cell(r)


def main():
    h4 = {p: fx.fxcm(p) for p in FOREX}
    daily = {p: fx.fx_daily(h4[p]) for p in FOREX}
    print("## S0 average move per session candle (in pips; + = up), EUR/USD and GBP/USD\n")
    print("| Pair | Half | 00 Asia | 04 Asia | 08 London | 12 London+NY | 16 NY | 20 NY late |\n|---|---|---|---|---|---|---|---|")
    for p in FOREX:
        for lab, (t0, t1) in (("2012-18", PERIODS[1]), ("2019-now", PERIODS[2])):
            acc = {}
            for b, hr in zip(h4[p], hours(h4[p])):
                if e.ms(t0) <= b["ts"] < (e.ms(t1) if t1 else 1 << 62):
                    acc.setdefault(hr, []).append((b["c"] - b["o"]) * 10000)
            print(f"| {p} | {lab} | " + " | ".join(f"{sum(acc.get(x, [0])) / max(1, len(acc.get(x, []))):+.2f}"
                                                  for x in (0, 4, 8, 12, 16, 20)) + " |")
    print("\n| Strategy | Full 2012-now | 2012-18 | 2019-now |\n|---|---|---|---|")
    sig = {p: s1_signals(h4[p], daily[p]) for p in FOREX}
    print("| S1 London breakout with the daily trend | " + " | ".join(cell(f39.fx_sim(sig, h4, a, b)) for a, b in PERIODS) + " |", flush=True)
    sig = {p: s2_signals(h4[p], daily[p]) for p in FOREX}
    print("| S2 New York fade of a big London move | " + " | ".join(cell(f39.fx_sim(sig, h4, a, b)) for a, b in PERIODS) + " |", flush=True)
    dd, weak = fx.dxy()
    sig = {p: s3_signals(h4[p], dd, weak) for p in FOREX}
    print("| S3 dollar trend + 4H BOS, both ways, trailing | " + " | ".join(cell(f39.fx_sim(sig, h4, a, b)) for a, b in PERIODS) + " |", flush=True)


if __name__ == "__main__":
    main()
