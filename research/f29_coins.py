"""
F29: Jeff's coin list (Oct 6 2026). He keeps BTC ETH SOL XRP BNB LINK on his charts and can drop DOGE AVAX ADA XAU SUI.
Question: should LINK be added to Trend Rider / Donchian / NNFX, and does Trend Rider need SUI (and TRX)?
Each bot runs with its live bot.py settings (risk, half sell, max open, pyramid, BTC leash) at the real 0.35% fee.
Research only, bot.py is not changed.
"""
import engine as e
import bot

LIVE = {b["id"]: b for b in bot.BOTS}


def settings(bid):
    return {k: v for k, v in LIVE[bid].items() if k not in ("id", "name", "strat", "venue", "mode", "coins", "equity", "prefix")}


def coins(bid):
    return [c.split("-")[0] for c in LIVE[bid]["coins"]]


def tr_run(cs):
    d = e.load(cs)
    return lambda t0, t1: e.bot_sim("tr", cs, d, lambda b, dd: bot.analyse_tr(b, dd, 5), t0, t1,
                                    extra=lambda x: {"hi": x["c"]}, settings=settings("tr-okx"))


def nnfx_run(cs):
    dn = {c: (daily, daily) for c, (_, daily) in e.load(cs).items()}
    return lambda t0, t1: e.bot_sim("nnfx", cs, dn, lambda b, d: bot.analyse_nnfx(b), t0, t1,
                                    extra=lambda x: {}, settings=settings("nnfx-okx"))


def dc_run(cs):
    dn = {c: (daily, daily) for c, (_, daily) in e.load(cs).items()}
    btc = e.load(["BTC"])["BTC"][1]
    per_coin = {}  # Donchian signals with the BTC leash applied, keyed by the coin's bar list
    for c in cs:
        a = bot.analyse_donchian(dn[c][1])
        ok = bot.btc_leash(dn[c][1], btc, c)
        a["signal"] = [s and o for s, o in zip(a["signal"], ok)]
        per_coin[id(dn[c][1])] = a
    return lambda t0, t1: e.bot_sim("donchian", cs, dn, lambda b, d: per_coin[id(b)], t0, t1,
                                    extra=lambda x: {"no_half": True}, settings=settings("dc-okx"))


def row(label, run):
    cells = []
    for _, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = run(t0, t1)
        cells.append(f"{r['ret']:+.1f}% / {r['dd']:.1f}% / {r['pf']:.2f} ({r['trades']})")
    print(f"| {label} | " + " | ".join(cells) + " |", flush=True)


def main():
    print("| Variant | 2018-now return / DD / PF (trades) | 1st half (2018-21) | 2nd half (2022-now) |")
    print("|---|---|---|---|")
    tr = coins("tr-okx")
    for label, cs in [("TR now " + " ".join(tr), tr), ("TR + LINK", tr + ["LINK"]),
                      ("TR - SUI", [c for c in tr if c != "SUI"]),
                      ("TR - SUI + LINK", [c for c in tr if c != "SUI"] + ["LINK"]),
                      ("TR - SUI - TRX + LINK", [c for c in tr if c not in ("SUI", "TRX")] + ["LINK"])]:
        row(label, tr_run(cs))
    dc = coins("dc-okx")
    for label, cs in [("DC now " + " ".join(dc), dc), ("DC + LINK", dc + ["LINK"])]:
        row(label, dc_run(cs))
    nn = coins("nnfx-okx")
    for label, cs in [("NNFX now " + " ".join(nn), nn), ("NNFX + LINK", nn + ["LINK"]),
                      ("NNFX + SOL BNB LINK", nn + ["SOL", "BNB", "LINK"])]:
        row(label, nnfx_run(cs))


if __name__ == "__main__":
    main()
