"""
T1b trend-strength sizing, CALIBRATED (follow-up to T1, which failed partly because its mapping averaged 0.31-0.47%
risk instead of about 0.5%). Written by Terminal Claude on 2026-10-05 BEFORE any run; queued for the Scout.

The mapping is centred on each coin's own MEDIAN trend strength, measured only on candles before 2022 (so the
2022-now holdout plays no part in the calibration). Risk = 0.5% x clamp(strength / median, 0.5, 1.5), i.e. 0.25% to
0.75%, about 0.5% at a typical candle. Applied to v4 and Trend Rider as they trade; exits untouched.
- TS1b: 4H ADX(14) / its pre-2022 median.
- TS2b: last completed daily ADX(14) / its pre-2022 median.
- TS3b: 4H EMA50 slope over 10 candles in ATR units / its pre-2022 median of positive slopes (negative slope -> 0.25%).
Pass: spec_runner overlay rules (both halves incl. the 2022-now holdout, DD within 10%, never-seen coins not worse).
"""
import statistics

import bot
import engine as e

SPEC = {"id": "T1b", "title": "Trend-strength sizing, calibrated on pre-2022 data", "written": "2026-10-05",
        "author": "Terminal Claude", "kind": "overlay", "bots": ["v4", "tr"]}
CUT = e.ms(e.CUT)


def _map(vals, ts):
    pre = [v for v, t in zip(vals, ts) if v is not None and v > 0 and t < CUT]
    if len(pre) < 50:
        return [None] * len(vals)
    med = statistics.median(pre)
    return [None if v is None else max(0.5, min(1.5, v / med)) for v in vals]


def ts1b(bars, daily):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    return _map(e.adx(h, l, c, 14), [b["ts"] for b in bars])


def ts2b(bars, daily):
    h, l, c = ([d[x] for d in daily] for x in "hlc")
    a = e.adx(h, l, c, 14)
    per_day = _map(a, [d["ts"] for d in daily])
    return [None if k is None else per_day[k] for k in bot.daily_lookup(bars, daily)]


def ts3b(bars, daily):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    m, at = bot.ema(c, 50), bot.atr(h, l, c, 14)
    slope = [None] * len(bars)
    for k in range(10, len(bars)):
        if m[k] is not None and m[k - 10] is not None and at[k]:
            slope[k] = (m[k] - m[k - 10]) / at[k]
    mapped = _map(slope, [b["ts"] for b in bars])
    return [0.5 if s is not None and s <= 0 else v for s, v in zip(slope, mapped)]


VARIANTS = {"TS1b: 4H ADX vs its median": {"risk_mult": ts1b}, "TS2b: daily ADX vs its median": {"risk_mult": ts2b},
            "TS3b: EMA50 slope vs its median": {"risk_mult": ts3b}}
