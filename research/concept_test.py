"""
Concept test: do Brad's Smart Money Concepts actually lead to price going up?

For every coin, on 4H candles, find each time a concept shows up (bullish side only,
because the bots trade spot / long only). Then look at what price did 1, 2 and 4 days
later, and compare it to an ordinary candle on the same coin over the same time.

  edge  = average move after the concept  -  average move after any candle
  up %  = how often price was higher afterwards

Skeptic check: the test is split into two halves (Mar 2024 - Jun 2025 and Jul 2025 - now).
A concept only counts as real if its edge is positive in BOTH halves.

Run inside the Freqtrade docker image (needs pandas + pyarrow):
  python research/concept_test.py <data_dir> <out_file>
"""
import glob
import math
import os
import sys

import pandas as pd

START = pd.Timestamp("2024-03-01", tz="UTC")
SPLIT = pd.Timestamp("2025-07-01", tz="UTC")
HORIZONS = [6, 12, 24]          # 4H candles: 1 day, 2 days, 4 days
PIVOT = 5                       # swing strength (bars each side)
LOOKBACK = 30                   # FVG / order block must be retested within this many bars
COINS = ["BTC", "ETH", "SOL", "XRP", "DOGE", "SUI", "BNB", "AVAX", "ADA"]


def load(data_dir, coin, tf):
    for ext, reader in ((".feather", pd.read_feather), (".parquet", pd.read_parquet),
                        (".json", lambda p: pd.read_json(p))):
        hits = glob.glob(os.path.join(data_dir, f"{coin}_USDT-{tf}{ext}"))
        if hits:
            df = reader(hits[0])
            if "date" not in df.columns:  # json format: list of lists
                df.columns = ["date", "open", "high", "low", "close", "volume"]
                df["date"] = pd.to_datetime(df["date"], unit="ms", utc=True)
            df["date"] = pd.to_datetime(df["date"], utc=True)
            return df.sort_values("date").reset_index(drop=True)
    return None


def pivots(series, L):
    """Swing point confirmed L bars later (no peeking ahead)."""
    v = series.tolist()
    out = [None] * len(v)
    for i in range(2 * L, len(v)):
        c = v[i - L]
        win = v[i - 2 * L:i + 1]
        out[i] = c if c == max(win) else None
    return out


def pivots_low(series, L):
    v = series.tolist()
    out = [None] * len(v)
    for i in range(2 * L, len(v)):
        c = v[i - L]
        win = v[i - 2 * L:i + 1]
        out[i] = c if c == min(win) else None
    return out


def find_events(df, daily):
    o, h, l, c = (df[k].tolist() for k in ("open", "high", "low", "close"))
    n = len(df)
    ph, pl = pivots(df["high"], PIVOT), pivots_low(df["low"], PIVOT)

    # daily trend filter (last COMPLETED day): close above 50-day EMA
    d = daily.copy()
    d["ema50"] = d["close"].ewm(span=50, adjust=False).mean()
    d["up"] = d["close"] > d["ema50"]
    d["day"] = d["date"].dt.floor("D")
    up_by_day = dict(zip(d["day"] + pd.Timedelta(days=1), d["up"]))  # usable the next day
    day_up = [bool(up_by_day.get(t.floor("D"), False)) for t in df["date"]]

    ev = {k: [] for k in ("Break of structure", "Market shift", "Liquidity sweep",
                          "FVG retest", "Order block retest", "Discount zone (uptrend)",
                          "BOS + daily uptrend")}
    highs, lows = [], []          # confirmed swing points so far
    last_ph = last_pl = None
    fvgs, obs = [], []            # open zones waiting for a retest: (top, bottom, made_at)
    for i in range(1, n):
        if ph[i] is not None:
            highs.append(ph[i]); last_ph = ph[i]
        if pl[i] is not None:
            lows.append(pl[i]); last_pl = pl[i]

        # break of structure: close crosses above the last swing high
        if last_ph is not None and c[i] > last_ph >= c[i - 1]:
            ev["Break of structure"].append(i)
            if day_up[i]:
                ev["BOS + daily uptrend"].append(i)
            # market shift: the break happens after lower highs and lower lows (downtrend)
            if len(highs) >= 2 and len(lows) >= 2 and highs[-1] < highs[-2] and lows[-1] < lows[-2]:
                ev["Market shift"].append(i)
            # order block = last down candle before the break
            for k in range(1, 11):
                if i - k >= 0 and c[i - k] < o[i - k]:
                    obs.append((h[i - k], l[i - k], i))
                    break

        # liquidity sweep: wick under the last swing low, close back above it
        if last_pl is not None and l[i] < last_pl < c[i]:
            ev["Liquidity sweep"].append(i)

        # bullish fair value gap
        if i >= 2 and l[i] > h[i - 2]:
            fvgs.append((l[i], h[i - 2], i))

        # first retest of an open FVG / order block that holds (closes inside or above it)
        for zones, name in ((fvgs, "FVG retest"), (obs, "Order block retest")):
            keep = []
            for top, bot, made in zones:
                if i - made > LOOKBACK:
                    continue
                if i > made and l[i] <= top and c[i] >= bot:
                    ev[name].append(i)
                    continue          # used up
                if c[i] < bot:
                    continue          # zone broken
                keep.append((top, bot, made))
            zones[:] = keep

        # discount zone: lower half of the last swing range, while the daily trend is up
        if day_up[i] and last_ph is not None and last_pl is not None and last_ph > last_pl:
            mid = (last_ph + last_pl) / 2
            if c[i] < mid <= c[i - 1]:
                ev["Discount zone (uptrend)"].append(i)
    return ev


def fwd_returns(df, idx, hz):
    c = df["close"].tolist()
    return [(c[i + hz] / c[i] - 1) * 100 for i in idx if i + hz < len(c)]


def stats(vals):
    if not vals:
        return None
    m = sum(vals) / len(vals)
    up = sum(v > 0 for v in vals) / len(vals) * 100
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / max(len(vals) - 1, 1))
    return m, up, sd, len(vals)


def main():
    data_dir, out = sys.argv[1], sys.argv[2]
    halves = {"first half": (START, SPLIT), "second half": (SPLIT, None)}
    rows = {}          # (concept, horizon, half) -> list of returns
    base = {}          # (horizon, half) -> list of returns
    per_coin = {}      # (concept, coin) -> list of 2-day returns (full period)
    coins_used = []
    for coin in COINS:
        df4, d1 = load(data_dir, coin, "4h"), load(data_dir, coin, "1d")
        if df4 is None or d1 is None:
            continue
        coins_used.append(coin)
        ev = find_events(df4, d1)
        dates = df4["date"]
        for hname, (a, b) in halves.items():
            in_half = [(dates[i] >= a) and (b is None or dates[i] < b) for i in range(len(df4))]
            all_idx = [i for i in range(len(df4)) if in_half[i]]
            for hz in HORIZONS:
                base.setdefault((hz, hname), []).extend(fwd_returns(df4, all_idx, hz))
                for name, idx in ev.items():
                    sel = [i for i in idx if in_half[i]]
                    rows.setdefault((name, hz, hname), []).extend(fwd_returns(df4, sel, hz))
        for name, idx in ev.items():
            sel = [i for i in idx if dates[i] >= START]
            per_coin.setdefault((name, coin), []).extend(fwd_returns(df4, sel, 12))

    names = sorted({k[0] for k in rows})
    lines = ["# Concept test: do Brad's concepts work on your coins?", "",
             f"OKX 4H candles, {', '.join(coins_used)}. Bullish (buy) side only. "
             "Edge = average % move after the concept minus the average % move after any candle. "
             "**Real** means the 2-day edge was positive in both halves (Mar 2024 - Jun 2025 and Jul 2025 - now).",
             "", "## Summary (2-day move)", "",
             "| Concept | Times seen | Edge 1st half | Edge 2nd half | Up % (all) | Verdict |",
             "|---|---|---|---|---|---|"]
    verdicts = []
    for name in names:
        e = {}
        tot = []
        for hname in halves:
            s, b = stats(rows[(name, 12, hname)]), stats(base[(12, hname)])
            e[hname] = (s[0] - b[0]) if s and b else None
            tot += rows[(name, 12, hname)]
        st = stats(tot)
        a1, a2 = e["first half"], e["second half"]
        if a1 is None or a2 is None or st is None or st[3] < 30:
            verdict = "Not enough data"
        elif a1 > 0 and a2 > 0:
            se = st[2] / math.sqrt(st[3])
            verdict = "**Real**" if (a1 + a2) / 2 > se else "Weak (could be luck)"
        elif a1 > 0 or a2 > 0:
            verdict = "Mixed (works only part of the time)"
        else:
            verdict = "No edge"
        verdicts.append((name, verdict))
        fmt = lambda x: "-" if x is None else f"{x:+.2f}%"
        lines.append(f"| {name} | {st[3] if st else 0} | {fmt(a1)} | {fmt(a2)} | "
                     f"{st[1]:.0f}% | {verdict} |" if st else f"| {name} | 0 | - | - | - | Not enough data |")

    lines += ["", "## Detail by time after the signal", "",
              "| Concept | Half | +1 day edge | +2 day edge | +4 day edge | Up % at +2 days | Count |",
              "|---|---|---|---|---|---|---|"]
    for name in names:
        for hname in halves:
            cells = []
            for hz in HORIZONS:
                s, b = stats(rows[(name, hz, hname)]), stats(base[(hz, hname)])
                cells.append("-" if not s or not b else f"{s[0] - b[0]:+.2f}%")
            s2 = stats(rows[(name, 12, hname)])
            lines.append(f"| {name} | {hname} | {' | '.join(cells)} | "
                         f"{'-' if not s2 else f'{s2[1]:.0f}%'} | {0 if not s2 else s2[3]} |")
    for hname in halves:
        b = stats(base[(12, hname)])
        if b:
            lines.append(f"| *Any candle (baseline)* | {hname} | | {b[0]:+.2f}% avg | | {b[1]:.0f}% | {b[3]} |")

    lines += ["", "## By coin (average 2-day move after the concept, full period)", "",
              "| Concept | " + " | ".join(coins_used) + " |",
              "|---|" + "---|" * len(coins_used)]
    for name in names:
        cells = []
        for coin in coins_used:
            s = stats(per_coin.get((name, coin), []))
            cells.append("-" if not s else f"{s[0]:+.1f}%")
        lines.append(f"| {name} | " + " | ".join(cells) + " |")

    lines += ["", "## How to read this", "",
              "- A positive edge means price tended to rise more than usual after the concept appeared.",
              "- **Real** = positive in both halves and bigger than normal noise. **Mixed** = worked in one half only, "
              "which usually means luck or a change in the market.",
              "- This tests each concept on its own. A concept with no edge alone can still help as a filter "
              "together with others (that is what the bots do).", ""]
    with open(out, "w") as f:
        f.write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
