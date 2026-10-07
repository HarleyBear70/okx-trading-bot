"""
F34: two published ideas on Jeff's live bots (Trend Rider, Donchian), live settings, real fee 0.35% a side.
  V  Volatility-managed sizing (Moreira & Muir 2017): each new trade's risk is scaled by
     (coin's median 20-day daily volatility over the past year) / (its 20-day volatility now), clipped to 0.5x-1.5x.
     Calm market = bigger, wild market = smaller. Entries and exits unchanged.
  R  Relative-strength filter (momentum): a non-BTC buy only counts if the coin's 30-day return beats BTC's
     (both measured up to the previous daily close). BTC's own signals are unchanged.
  VR both together.
Research only.
"""
import bisect
import math
import engine as e
import bot
import f29_coins as f29

VOL_N, RS_N, CLIP = 20, 30, (0.5, 1.5)


def day_key(ts):
    return ts // 86400000


def daily_maps(daily):
    """day -> (vol multiplier, 30-day return), using only closes before that day."""
    c = [d["c"] for d in daily]
    days = [day_key(d["ts"]) for d in daily]
    rets = [None] + [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    vol = [None] * len(c)
    for i in range(VOL_N, len(c)):
        w = rets[i - VOL_N + 1:i + 1]
        m = sum(w) / VOL_N
        vol[i] = math.sqrt(sum((x - m) ** 2 for x in w) / VOL_N)
    mult, r30 = {}, {}
    for i in range(1, len(c)):
        j = i - 1  # information up to the previous close
        hist = [v for v in vol[max(0, j - 364):j + 1] if v]
        if vol[j] and len(hist) >= 120:
            med = sorted(hist)[len(hist) // 2]
            mult[days[i]] = min(max(med / vol[j], CLIP[0]), CLIP[1])
        if j >= RS_N:
            r30[days[i]] = c[j] / c[j - RS_N] - 1
    return mult, r30


def run(which, t0, t1, coins_bot, strat):
    data = e.load(coins_bot + ["BTC"])
    maps = {c: daily_maps(data[c][1]) for c in data}
    btc_r = maps["BTC"][1]
    use_v, use_r = "V" in which, "R" in which

    def rs_ok(coin, ts):
        if coin == "BTC" or not use_r:
            return True
        d = day_key(ts)
        a, b = maps[coin][1].get(d), btc_r.get(d)
        return a is not None and b is not None and a > b

    cur = {"m": 1.0}
    o_open, o_risk = bot.open_position, bot.risk_pct

    def open_wrap(api, b, bs, coin, bar, inf, extra):
        c = coin.split("-")[0] if "-" in coin else coin
        if not rs_ok(c, bar["ts"]):
            return
        cur["m"] = maps[c][0].get(day_key(bar["ts"]), 1.0) if use_v else 1.0
        try:
            return o_open(api, b, bs, coin, bar, inf, extra)
        finally:
            cur["m"] = 1.0
    bot.open_position = open_wrap
    bot.risk_pct = lambda b, bs: o_risk(b, bs) * cur["m"]
    try:
        if strat == "tr":
            return f29.tr_run(coins_bot)(t0, t1)
        return f29.dc_run(coins_bot)(t0, t1)
    finally:
        bot.open_position, bot.risk_pct = o_open, o_risk


def main():
    print("| Bot | Variant | 2018-now return / DD / PF (trades) | 1st half (2018-21) | 2nd half (2022-now) | Return/DD |")
    print("|---|---|---|---|---|---|")
    for name, strat, coins in (("Trend Rider", "tr", f29.coins("tr-okx")), ("Donchian", "dc", f29.coins("dc-okx"))):
        for which, lab in (("", "as live"), ("V", "V vol sizing"), ("R", "R rel. strength"), ("VR", "V + R")):
            cells, full = [], None
            for _, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
                r = run(which, t0, t1, coins, strat)
                full = full or r
                cells.append(f"{r['ret']:+.1f}% / {r['dd']:.1f}% / {r['pf']:.2f} ({r['trades']})")
            print(f"| {name} | {lab} | " + " | ".join(cells) + f" | {full['ret'] / abs(full['dd']):.1f} |", flush=True)


if __name__ == "__main__":
    main()
