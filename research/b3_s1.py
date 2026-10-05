"""
B3 spot-only pairs (daily) and S1 Fear & Greed filter on v4 and Trend Rider.
Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/b3_s1.py        # writes research/B3_PAIRS.md and research/S1_SENTIMENT.md
"""
import datetime as dt
import json
import math
import os
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import b_boxes as bb  # noqa: E402
import engine as e  # noqa: E402
import long_history as lh  # noqa: E402

UTC = dt.timezone.utc


# ───────── B3 pairs ─────────
def load_daily(coins):
    """Daily candles used as the bars; BTC is always included (it's the other leg)."""
    out = {}
    for c in set(coins) | {"BTC"}:
        daily = lh.load(c)[1]
        out[c] = (daily, daily)
    return out


def zscores(data, coin, n):
    a = {d["ts"]: d["c"] for d in data[coin][0]}
    b = {d["ts"]: d["c"] for d in data["BTC"][0]}
    days = sorted(set(a) & set(b))
    sp = [math.log(a[d] / b[d]) for d in days]
    z = {}
    for i in range(n, len(days)):
        w = sp[i - n:i]
        m = sum(w) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / (n - 1))
        if sd > 0:
            z[days[i]] = (sp[i] - m) / sd
    return z


def pair_entries(alts, n, ent, data):
    """(entries_fn, z-scores) for the pairs bot; also used to check the live bot gives the same signals."""
    zs = {c: zscores(data, c, n) for c in alts}

    def entries(coin, bars, daily):
        h, l, c = ([b[x] for b in bars] for x in "hlc")
        at = bot.atr(h, l, c, 14)
        out = [None] * len(bars)
        for k, b in enumerate(bars):
            if at[k] is None:
                continue
            for alt in alts:
                z = zs[alt].get(b["ts"])
                if z is None:
                    continue
                if (coin == alt and z < -ent) or (coin == "BTC" and z > ent):
                    out[k] = {"stop": c[k] - 2 * at[k], "target": None, "max_bars": 30, "tag": alt}
                    break
        return out
    return entries, zs


def pairs_sim(alts, n, ent, data, t0, t1):
    entries, zs = pair_entries(alts, n, ent, data)

    def manage(p, bars, k):
        z = zs[p["tag"]].get(bars[k]["ts"])
        return "exit" if z is not None and abs(z) < 0.5 else None

    return e.trade_sim(list(alts) + ["BTC"], data, entries, t0, t1, manage=manage)


def b3():
    variants = {}
    for name, n, ent in (("P1: 60 days, z 2", 60, 2.0), ("P2: 30 days, z 2", 30, 2.0), ("P3: 60 days, z 2.5", 60, 2.5)):
        variants[name] = ((lambda n, ent: lambda data, t0, t1: pairs_sim(["ETH", "XRP"], n, ent, data, t0, t1))(n, ent),
                          (lambda n, ent: lambda coin, data, t0, t1: pairs_sim([coin], n, ent, data, t0, t1))(n, ent))
    rows, verdicts, best = e.evaluate(variants, loader=load_daily)
    lines = ["# B3 spot-only pairs (daily)", "", "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. "
             "Design pairs ETH/BTC and XRP/BTC on one shared $1,000; never-seen coins vs BTC, alone, pooled. 0.5% risk, "
             "0.1% fee each side. Script: research/b3_s1.py.", ""] + bb.report("Results", rows, verdicts, best)
    with open(os.path.join(HERE, "B3_PAIRS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


# ───────── S1 sentiment ─────────
def fear_greed():
    path = os.path.join(lh.CACHE, "fng.json")
    if not os.path.exists(path):
        raw = urllib.request.urlopen("https://api.alternative.me/fng/?limit=0&format=json", timeout=60).read()
        with open(path, "wb") as f:
            f.write(raw)
    with open(path) as f:
        return {bot.day_of(int(x["timestamp"]) * 1000): int(x["value"]) for x in json.load(f)["data"]}


def filtered(analyse, fng, lo, hi):
    """Drop entries when yesterday's index is <= lo or >= hi (None = no limit on that side)."""
    def fn(bars, daily):
        a = analyse(bars, daily)
        sig = list(a["signal"])
        for k, b in enumerate(bars):
            if sig[k]:
                v = fng.get(bot.day_of(b["ts"]) - 1)
                if v is None or (hi is not None and v >= hi) or (lo is not None and v <= lo):
                    sig[k] = False
        return {**a, "signal": sig}
    return fn


def s1():
    fng = fear_greed()
    v4_coins = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "v4-okx")["coins"]]
    bots = {
        "SP-12 v4": ("v4", v4_coins, lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), None),
        "Trend Rider": ("tr", e.TR_COINS, lambda b, d: bot.analyse_tr(b, d, 5), lambda x: {"hi": x["c"]}),
    }
    versions = {"no filter": (None, None), "F1: skip when >= 75": (None, 75), "F2: skip when <= 25": (25, None),
                "F3: both": (25, 75)}
    lines = ["# S1 Fear & Greed filter on v4 and Trend Rider", "",
             "Variants and pass rules fixed beforehand in research/NEWBOTS_PLAN.md. Index: alternative.me, last completed "
             "day. Bots as they trade (shared $1,000, max 3 open). Script: research/b3_s1.py.", "",
             "| Bot | Version | Half | Trades | Return | Max DD | Return/DD | PF | Pass? |", "|---|---|---|---|---|---|---|---|---|"]
    verdicts = []
    for bname, (strat, coins, an, extra) in bots.items():
        data = e.load(coins)
        res = {}
        for vname, (lo, hi) in versions.items():
            fn = an if vname == "no filter" else filtered(an, fng, lo, hi)
            res[vname] = {h: e.bot_sim(strat, coins, data, fn, t0, t1, extra=extra) for h, t0, t1 in e.HALVES}
        for vname in versions:
            ok = vname != "no filter" and all(
                (res[vname][h]["ret"] / -res[vname][h]["dd"] if res[vname][h]["dd"] else 0) >
                (res["no filter"][h]["ret"] / -res["no filter"][h]["dd"] if res["no filter"][h]["dd"] else 0)
                and res[vname][h]["pf"] >= res["no filter"][h]["pf"] for h in res[vname])
            for h, _, _ in e.HALVES:
                r = res[vname][h]
                rd = r["ret"] / -r["dd"] if r["dd"] else float("inf")
                lines.append(f"| {bname} | {vname} | {h} | {r['trades']} | {r['ret']:+.1f}% | {r['dd']:.1f}% | {rd:.2f} | "
                             f"{r['pf']:.2f} | {'-' if vname == 'no filter' else ('PASS' if ok else 'fail')} |")
            if vname != "no filter":
                verdicts.append(f"- {bname}, {vname}: {'PASS' if ok else 'fail'}")
        print(f"done {bname}", flush=True)
    lines += [""] + verdicts
    with open(os.path.join(HERE, "S1_SENTIMENT.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    b3()
    s1()
