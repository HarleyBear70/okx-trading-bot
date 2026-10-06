"""
F1: the bots at the user's real OKX fees (research/FEES_PLAN.md). Research only, bot.py is not changed.

Runs one (bot, variant, fee setup) per call so they can go in parallel:
  python research/fees_test.py <bot> <variant> <T|M>
and prints one JSON line. research/fees_report.py (or Claude) collects them into research/FEES.md.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402

FEES = {"T": (0.0035, 0.0035), "M": (0.0020, 0.0035)}  # (buy, sell)


def set_fees(fin, fout):
    """Paper fills use bot.FEE on both sides; switch it to the buy fee only while a position opens."""
    bot.FEE, bot.BE_BUFFER = fout, fin + fout
    orig = bot.open_position

    def open_position(*a, **k):
        bot.FEE = fin
        try:
            return orig(*a, **k)
        finally:
            bot.FEE = fout
    bot.open_position = open_position


def coins(bid):
    return [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == bid)["coins"]]


def settings(bid):
    b = next(b for b in bot.BOTS if b["id"] == bid)
    return {k: b[k] for k in ("risk", "half_at_2r") if k in b}


def v4_analyse(cfg_over=None, min_score=2):
    cfg = {**bot.SP_SETTINGS["v4"], **(cfg_over or {})}

    def run(b, d):
        a = bot.analyse_sp(b, d, cfg)
        if min_score > 2:
            a["signal"] = [s and a["info"][i]["score"] >= min_score for i, s in enumerate(a["signal"])]
        return a
    return run


def runner(name, variant):
    if name == "v4":
        an = {"base": v4_analyse(), "V1": v4_analyse({"min_risk": 2.0}),
              "V2": v4_analyse({"min_risk": 3.0, "max_risk": 6.0}), "V3": v4_analyse(min_score=3)}[variant]
        c = coins("v4-okx")
        d = e.load(c)
        return lambda t0, t1: e.bot_sim("v4", c, d, an, t0, t1, settings=settings("v4-okx"))
    risk = {"R04": 0.004, "R075": 0.0075, "R10": 0.01}.get(variant)  # risk-size variants (F1b)
    if name == "tr":
        c = coins("tr-okx")
        d = e.load(c)
        st = {**settings("tr-okx"), **({"risk": risk} if risk else {})}
        return lambda t0, t1: e.bot_sim("tr", c, d, lambda b, dd: bot.analyse_tr(b, dd, 5), t0, t1,
                                        extra=lambda x: {"hi": x["c"]}, settings=st)
    if name == "nnfx":
        dn = {c: (daily, daily) for c, (_, daily) in e.load(["BTC", "ETH", "XRP"]).items()}
        return lambda t0, t1: e.bot_sim("nnfx", ["BTC", "ETH", "XRP"], dn, lambda b, d: bot.analyse_nnfx(b), t0, t1,
                                        settings={"risk": risk} if risk else None)
    if name == "b3":
        import b3_s1 as b3
        dd = b3.load_daily(e.DESIGN)
        return lambda t0, t1: b3.pairs_sim(["ETH", "XRP"], 60, 2.5, dd, t0, t1)
    if name == "b1":
        import b_boxes as bb
        d1h = bb.load_1h(e.DESIGN)
        return lambda t0, t1: e.trade_sim(e.DESIGN, d1h, bb.b1_entries(2.0, 60), t0, t1)
    raise SystemExit("unknown bot " + name)


def main():
    name, variant, fee = sys.argv[1:4]
    set_fees(*FEES[fee])
    run = runner(name, variant)
    out = {"bot": name, "variant": variant, "fee": fee}
    for lab, t0, t1 in [("full", e.START, None)] + list(e.HALVES):
        r = run(t0, t1)
        out[lab] = {"ret": round(r["ret"], 1), "dd": round(r["dd"], 1), "pf": round(r["pf"], 2), "trades": r["trades"],
                    "win": round(r["win"]), "monthly": e.monthly(r["curve"]) if lab == "full" else None}
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    main()
