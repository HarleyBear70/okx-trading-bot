"""
T1 trend-strength sizing (Jeff, 2026-10-05). Written by Terminal Claude BEFORE any run; the Scout only executes it.

Risk per trade scales with trend strength between 0.25% and 0.75% (the bots' base is 0.5%), set at entry.
Applied to v4 and Trend Rider as they trade (Trend Rider with its fear filter). Exits untouched.
Variants (fixed here, never tuned):
- TS1: 4H ADX(14) at the signal candle: risk = 0.25% + 0.5% x clamp((ADX - 15) / 30, 0, 1)
       (ADX 15 or less -> 0.25%, ADX 45 or more -> 0.75%; ADX 30 -> 0.5%).
- TS2: the same mapping on the last completed DAILY ADX(14).
- TS3: trend slope: s = (4H EMA50 now - EMA50 10 candles ago) / ATR(14); risk = 0.25% + 0.5% x clamp(s / 4, 0, 1).
Pass (spec_runner overlay rules): for a bot, in BOTH halves (2018-05 to 2021 and the 2022-now holdout) return / max DD
higher, PF not lower and max DD within 10%; AND on never-seen coins (each alone per market period, pooled) P/L and
PF not lower in both halves. The average risk actually used is reported (target about 0.5%).
"""
import bot
import engine as e

SPEC = {"id": "T1", "title": "Trend-strength sizing", "written": "2026-10-05", "author": "Terminal Claude",
        "kind": "overlay", "bots": ["v4", "tr"]}


def _scale(x):
    return 0.5 + clamp(x, 0.0, 1.0)  # multiplier on the 0.5% base: 0.5x .. 1.5x = 0.25% .. 0.75%


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def ts1(bars, daily):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    a = e.adx(h, l, c, 14)
    return [None if v is None else _scale((v - 15) / 30) for v in a]


def ts2(bars, daily):
    h, l, c = ([d[x] for d in daily] for x in "hlc")
    a = e.adx(h, l, c, 14)
    dk = bot.daily_lookup(bars, daily)
    return [None if k is None or a[k] is None else _scale((a[k] - 15) / 30) for k in dk]


def ts3(bars, daily):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    m, at = bot.ema(c, 50), bot.atr(h, l, c, 14)
    out = [None] * len(bars)
    for k in range(10, len(bars)):
        if m[k] is not None and m[k - 10] is not None and at[k]:
            out[k] = _scale((m[k] - m[k - 10]) / at[k] / 4)
    return out


VARIANTS = {"TS1: 4H ADX": {"risk_mult": ts1}, "TS2: daily ADX": {"risk_mult": ts2}, "TS3: 4H EMA50 slope": {"risk_mult": ts3}}
