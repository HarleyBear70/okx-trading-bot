"""
W1 Wyckoff volume as a filter on v4, Trend Rider and B1c entries. Variants and rules fixed beforehand in
research/IDEAS_PLAN.md.

Run:
  python research/w1_volume.py        # writes research/W1_VOLUME.md
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import b3_s1 as b3  # noqa: E402
import b_boxes as bb  # noqa: E402
import engine as e  # noqa: E402


def prev_avg(src, k, n=20):
    return sum(src[k - n:k]) / n if k >= n else None


def vol_ok(bars, k, mode):
    """Is the decision candle k OK under WV1 / WV2 / WV3?"""
    h, l, c, v = ([b[x] for b in bars] for x in "hlcv")
    va = prev_avg(v, k)
    if va is None:
        return False
    if mode == "WV1":
        return v[k] > va
    if mode == "WV2":
        ra = prev_avg([a - b for a, b in zip(h, l)], k)
        return v[k] > va and ra is not None and h[k] - l[k] > ra
    for m in range(max(21, k - 10), k):  # WV3: a spring in the last 10 candles
        low20 = min(l[m - 20:m])
        vm = prev_avg(v, m)
        if l[m] < low20 and c[m] > low20 and vm is not None and v[m] > vm:
            return True
    return False


def masked(analyse, mode):
    def fn(bars, daily):
        a = analyse(bars, daily)
        if mode is None:
            return a
        return {**a, "signal": [s and vol_ok(bars, k, mode) for k, s in enumerate(a["signal"])]}
    return fn


def b1_entries(mode):
    """B1c entries (same rules as bot.analyse_b1), filtered on the 4H breakout candle."""
    cfg = bot.B1_SETTINGS

    def fn(coin, bars, daily):
        b4 = bot.to_4h(bars)
        # volume for the 4H candles
        vol = {}
        for b in bars:
            k = b["ts"] - b["ts"] % bot.H4_MS
            vol[k] = vol.get(k, 0.0) + b["v"]
        for x in b4:
            x["v"] = vol[x["ts"]]
        h4, l4, c4 = [x["h"] for x in b4], [x["l"] for x in b4], [x["c"] for x in b4]
        idx = {b["ts"]: k for k, b in enumerate(bars)}
        out = [None] * len(bars)
        for j in range(cfg["box"] + 1, len(b4)):
            hi, lo = max(h4[j - cfg["box"]:j]), min(l4[j - cfg["box"]:j])
            if lo <= 0 or not (cfg["h_min"] <= (hi - lo) / lo <= cfg["h_max"]) or not (c4[j] > hi >= c4[j - 1]):
                continue
            if mode is not None and not vol_ok(b4, j, mode):
                continue
            start = b4[j]["ts"] + bot.H4_MS
            for t in range(start, start + cfg["retest_4h"] * bot.H4_MS, 3600 * 1000):
                k = idx.get(t)
                if k is None:
                    continue
                x = bars[k]
                if x["l"] <= hi * (1 + cfg["near"]) and x["c"] > hi:
                    sl = hi - cfg["inside"] * (hi - lo)
                    out[k] = {"stop": sl, "target": x["c"] + cfg["rr"] * (x["c"] - sl), "max_bars": cfg["max_bars"]}
                    break
        return out
    return fn


def main():
    bot._fng["v"] = b3.fear_greed()
    v4c = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "v4-okx")["coins"]]
    trb = next(b for b in bot.BOTS if b["id"] == "tr-okx")
    trc = [c.split("-")[0] for c in trb["coins"]]
    d4, dtr, d1h = e.load(v4c), e.load(trc), bb.load_1h(e.DESIGN)

    def tr_an(bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        return {**a, "signal": [s and not bot.fear_blocks(trb, b) for s, b in zip(a["signal"], bars)]}

    runners = {
        "SP-12 v4": lambda mode, t0, t1: e.bot_sim("v4", v4c, d4, masked(lambda b, d: bot.analyse_sp(
            b, d, bot.SP_SETTINGS["v4"]), mode), t0, t1),
        "Trend Rider (with fear filter)": lambda mode, t0, t1: e.bot_sim("tr", trc, dtr, masked(tr_an, mode), t0, t1,
                                                                         extra=lambda x: {"hi": x["c"]}),
        "B1c": lambda mode, t0, t1: e.trade_sim(e.DESIGN, d1h, b1_entries(mode), t0, t1),
    }
    # sanity: B1c with no filter must equal the live bot's entries
    for c in e.DESIGN:
        live = bot.analyse_b1(d1h[c][0])
        mine = b1_entries(None)(c, d1h[c][0], None)
        assert [x is not None for x in mine] == live["signal"], f"B1c copy differs on {c}"
    lines = ["# W1 Wyckoff volume as a filter", "", "Variants and rules fixed beforehand in research/IDEAS_PLAN.md. Each bot "
             "as it trades; only entries are filtered. Script: research/w1_volume.py.", "",
             "| Bot | Version | Half | Trades | Return | Max DD | Return/DD | PF | Pass? |", "|---|---|---|---|---|---|---|---|---|"]
    verdicts = []
    for name, run in runners.items():
        res = {}
        for mode in (None, "WV1", "WV2", "WV3"):
            res[mode] = {}
            for h, t0, t1 in e.HALVES:
                r = run(mode, t0, t1)
                ret, dd, rd = e.ret_dd(r["curve"])
                res[mode][h] = {"n": r["trades"], "ret": ret, "dd": dd, "rd": rd, "pf": r["pf"]}
        for mode in res:
            ok = mode is not None and all(res[mode][h]["rd"] > res[None][h]["rd"] and res[mode][h]["pf"] >= res[None][h]["pf"]
                                          for h in res[mode])
            for h, _, _ in e.HALVES:
                r = res[mode][h]
                lines.append(f"| {name} | {mode or 'no filter'} | {h} | {r['n']} | {r['ret']:+.1f}% | {r['dd']:.1f}% | "
                             f"{r['rd']:.2f} | {r['pf']:.2f} | {'-' if mode is None else ('PASS' if ok else 'fail')} |")
            if mode:
                verdicts.append(f"- {name}, {mode}: {'PASS' if ok else 'fail'}")
        print(f"done {name}", flush=True)
    lines += [""] + verdicts
    with open(os.path.join(HERE, "W1_VOLUME.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
