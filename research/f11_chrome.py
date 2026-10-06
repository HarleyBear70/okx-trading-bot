"""
F11: Chrome's L1 (liquidity sweep bot), L2 (BTC leash), L3 (crowding filter) (research/F11_PLAN.md).
Research only, bot.py is not changed.

  python research/f11_chrome.py L1 <a|b|c>
  python research/f11_chrome.py <base|L2|L3> <tr|dc> [u]      u = never-seen coins
"""
import bisect
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE = 0.0035
bot.FEE, bot.BE_BUFFER = FEE, 2 * FEE
DAY = 86400000


def report(sim):
    out = {}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = sim(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"])}
    return out


# ───────── L1: liquidity sweep of the previous day's low, 1H ─────────
def l1(variant):
    import b_boxes as bb
    data = bb.load_1h(e.DESIGN)
    atrs = {}

    def entries(coin, bars, _daily):
        h, l, c = [x["h"] for x in bars], [x["l"] for x in bars], [x["c"] for x in bars]
        atr = bot.atr(h, l, c, 14)
        atrs[id(bars)] = atr
        dh, dl = {}, {}
        for x in bars:
            d = x["ts"] // DAY
            dh[d] = max(dh.get(d, x["h"]), x["h"])
            dl[d] = min(dl.get(d, x["l"]), x["l"])
        ph = bot.pivots(h, 3, True)  # value at the confirming candle
        out = [None] * len(bars)
        state, last_ph = 0, None
        for i in range(1, len(bars)):
            if ph[i] is not None:
                last_ph = ph[i]
            d = bars[i]["ts"] // DAY
            pdl, pdh = dl.get(d - 1), dh.get(d - 1)
            if state == 0:
                if pdl is not None and l[i] < pdl:
                    state, s_low, s_i, s_pdl, s_pdh = 1, l[i], i, pdl, pdh
            elif state == 1:  # swept: wait for a close back above the old low
                s_low = min(s_low, l[i])
                if c[i] > s_pdl:
                    state, r_i = 2, i
                elif i - s_i > 24:
                    state = 0
            elif state == 2:  # reclaimed: wait for a 1H break of structure
                if l[i] < s_low or i - r_i > 24:
                    state = 0
                elif last_ph is not None and c[i] > last_ph >= c[i - 1]:
                    stop = s_low * 0.998
                    if c[i] > stop:
                        tgt = {"a": s_pdh if s_pdh and s_pdh > c[i] else None, "b": c[i] + 2 * (c[i] - stop), "c": None}[variant]
                        if variant != "a" or tgt:
                            out[i] = {"stop": stop, "target": tgt, "max_bars": None}
                    state = 0
        return out

    def manage(p, bars, k):
        if variant != "c":
            return None
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None

    return lambda t0, t1: e.trade_sim(e.DESIGN, data, entries, t0, t1, risk=0.005, max_open=3, fee=FEE, manage=manage)


# ───────── overlays ─────────
def btc_leash(kind):
    """allow(coin, ts) for L2: BTC's own trend up (the bot's rule), non-BTC coins only."""
    b4, bd = e.load(["BTC"])["BTC"]
    c4 = [x["c"] for x in b4]
    e4 = bot.ema(c4, 50)
    up4 = {x["ts"]: e4[k] is not None and c4[k] > e4[k] for k, x in enumerate(b4)}
    cd = [x["c"] for x in bd]
    ed = bot.ema(cd, 50)
    upd = {bot.day_of(x["ts"]): ed[k] is not None and cd[k] > ed[k] for k, x in enumerate(bd)}

    def allow(coin, ts):
        if coin == "BTC":
            return True
        if kind == "tr":
            return up4.get(ts, False) and upd.get(bot.day_of(ts) - 1, False)
        return upd.get(bot.day_of(ts), False)  # daily bot: decides at the same daily close as BTC's
    return allow


def crowding():
    """allow(coin, ts) for L3: skip when BTC funding (last 3 prints) is in the top 10% of the prior 90 days."""
    rows = json.load(open(os.path.join(HERE, ".cache", "bitmex_funding_XBTUSD.json")))
    ts = [int(dt.datetime.fromisoformat(r["t"].replace("Z", "+00:00")).timestamp() * 1000) for r in rows]
    rate = [r["rate"] for r in rows]
    avg3 = [sum(rate[max(0, i - 2):i + 1]) / len(rate[max(0, i - 2):i + 1]) for i in range(len(rate))]
    crowded = []
    for i in range(len(avg3)):
        prior = sorted(avg3[max(0, i - 270):i])
        crowded.append(len(prior) >= 90 and avg3[i] > prior[int(len(prior) * 0.9) - 1])
    end = ts[-1] + DAY

    def allow(coin, t):
        if t > end:
            return True  # no BitMEX data after 2026-09-16: filter off
        j = bisect.bisect_right(ts, t) - 1
        return j < 0 or not crowded[j]
    return allow


def tr_sim(allow, unseen):
    cs = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "tr-okx")["coins"]]
    if unseen:
        cs = [c for c in e.UNSEEN + ["XRP"] if c not in cs]
    data = e.load(cs)
    atrs = {}

    def entries(coin, bars, daily):
        a = bot.analyse_tr(bars, daily, 5)
        atrs[id(bars)] = a["atr"]
        return [{"stop": a["info"][i]["sl"], "target": None, "max_bars": None}
                if s and (allow is None or allow(coin, bars[i]["ts"])) else None for i, s in enumerate(a["signal"])]

    def manage(p, bars, k):
        a = atrs[id(bars)][k]
        p["hi"] = max(p["hi"], bars[k]["c"])
        return p["hi"] - 3 * a if a is not None else None
    return lambda t0, t1: e.trade_sim(cs, data, entries, t0, t1, risk=0.004, max_open=3, fee=FEE, manage=manage)


def dc_sim(allow, unseen):
    b = next(b for b in bot.BOTS if b["id"] == "dc-okx")
    cs = [c.split("-")[0] for c in b["coins"]]
    if unseen:
        cs = [c for c in e.UNSEEN if c not in cs]
    data = {c: (d, d) for c, (_, d) in e.load(cs).items()}
    st = {k: b[k] for k in ("risk", "half_at_2r", "max_open", "pyramid") if k in b}
    coin_of = {id(data[c][0]): c for c in cs}

    def an(bars, _d):
        a = bot.analyse_donchian(bars)
        if allow is None:
            return a
        c = coin_of[id(bars)]
        return {**a, "signal": [s and allow(c, bars[k]["ts"]) for k, s in enumerate(a["signal"])]}
    return lambda t0, t1: e.bot_sim("donchian", cs, data, an, t0, t1, settings=st)


def main():
    a = sys.argv[1:]
    if a[0] == "L1":
        out = {"test": "L1" + a[1], **report(l1(a[1]))}
    else:
        test, which, unseen = a[0], a[1], len(a) > 2 and a[2] == "u"
        allow = None if test == "base" else btc_leash(which) if test == "L2" else crowding()
        sim = tr_sim(allow, unseen) if which == "tr" else dc_sim(allow, unseen)
        out = {"test": f"{test}-{which}{'-unseen' if unseen else ''}", **report(sim)}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
