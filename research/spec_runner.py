"""
Spec runner for the Scout research loop (L1). The Scout never invents or tunes anything: it runs pre-written spec
files from research/specs/ that are queued in research/ideas/IDEAS.md ("Scout queue"), applies the standard rules,
writes research/specs/results/<id>.md, marks the queue, and adds every tested variant to research/specs/LEDGER.md
(a running count, to keep data-mining honest).

Spec kinds:
- "overlay": changes an existing bot (v4 or Trend Rider, as they trade). A variant may give "risk_mult(bars, daily)"
  (a per-candle multiplier on the 0.5% risk, None = 1) and / or "filter(bars, daily)" (per-candle True = entry allowed).
  Pass for a bot: in BOTH halves (2018-05 to 2021 and the 2022-now holdout) return / max DD higher, PF not lower,
  max DD within 10%; AND on never-seen coins (alone, per market period, pooled) P/L and PF not lower in both halves.
- "newbot": variants give "entries(coin, bars, daily)" (+ optional "manage") for engine.trade_sim; judged by the
  common new-bot rules (engine.evaluate: both halves, 10% DD, never-seen coins, diversification).
A pass only makes a PAPER candidate, and only with Jeff's OK.

Run by hand:  python research/spec_runner.py [max_specs]
"""
import datetime as dt
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import bot  # noqa: E402
import engine as e  # noqa: E402
import long_history as lh  # noqa: E402

IDEAS = os.path.join(HERE, "ideas", "IDEAS.md")
LEDGER = os.path.join(HERE, "specs", "LEDGER.md")
RESULTS = os.path.join(HERE, "specs", "results")


def load_spec(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], os.path.join(ROOT, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fear():
    if "v" not in bot._fng or len(bot._fng["v"]) < 100:
        import b3_s1
        bot._fng["v"] = b3_s1.fear_greed()


def bot_setup(which):
    """(strat, coins, analyse, extra) for an existing bot as it trades now."""
    if which == "v4":
        coins = [c.split("-")[0] for c in next(b for b in bot.BOTS if b["id"] == "v4-okx")["coins"]]
        return "v4", coins, lambda b, d: bot.analyse_sp(b, d, bot.SP_SETTINGS["v4"]), None
    trb = next(b for b in bot.BOTS if b["id"] == "tr-okx")
    coins = [c.split("-")[0] for c in trb["coins"]]
    _fear()

    def an(bars, daily):
        a = bot.analyse_tr(bars, daily, trb.get("pivot", 5))
        return {**a, "signal": [s and not bot.fear_blocks(trb, x) for s, x in zip(a["signal"], bars)]}
    return "tr", coins, an, lambda x: {"hi": x["c"]}


def overlay_run(which, variant, coins, t0, t1):
    strat, _, analyse, extra = bot_setup(which)
    data = e.load(coins)
    mults, used = {}, []
    filt = variant.get("filter") if variant else None
    rm = variant.get("risk_mult") if variant else None

    def an(bars, daily):
        a = analyse(bars, daily)
        if rm:
            mults[id(bars)] = rm(bars, daily)
        if filt:
            ok = filt(bars, daily)
            a = {**a, "signal": [s and bool(o) for s, o in zip(a["signal"], ok)]}
        return a

    def risk_mult(ctx, name, coin, bars, k):
        m = mults.get(id(bars), [None] * (k + 1))[k] if rm else None
        m = 1.0 if m is None else m
        used.append(m)
        return m
    r = e.multi_sim([(which, strat, coins, data, an, extra)], t0, t1, risk_mult=risk_mult)
    s = r["bots"][which]
    ret, dd, rd = e.ret_dd(s["curve"]) if s["curve"] else (0.0, 0.0, 0.0)
    return {"n": s["trades"], "ret": ret, "dd": dd, "rd": rd, "pf": s["pf"], "won": s["won"], "lost": s["lost"],
            "pnl": s["pnl"], "avg_risk": (sum(used) / len(used) * bot.RISK_PCT * 100) if used else None}


def overlay_unseen(which, variant, coins_traded):
    out = {h: {"won": 0.0, "lost": 0.0, "pnl": 0.0} for h in ("1st half", "2nd half")}
    for c in [x for x in e.UNSEEN if x not in coins_traded]:
        bars = lh.load(c)[0]
        for p, t0, t1 in lh.PERIODS:
            t0 = max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, dt.timezone.utc))
            t1 = t1 or e.now()
            if t0 >= t1 or bars[-1]["ts"] < e.ms(t0):
                continue
            r = overlay_run(which, variant, [c], t0, t1)
            h = out["1st half" if t0 < e.CUT else "2nd half"]
            for k in ("won", "lost", "pnl"):
                h[k] += r[k]
    for h in out.values():
        h["pf"] = h["won"] / h["lost"] if h["lost"] else 0.0
    return out


def run_overlay(mod):
    lines, verdicts = [], []
    for which in mod.SPEC["bots"]:
        _, coins, _, _ = bot_setup(which)
        name = {"v4": "SP-12 v4", "tr": "Trend Rider"}[which]
        base = {h: overlay_run(which, None, coins, t0, t1) for h, t0, t1 in e.HALVES}
        base_un = overlay_unseen(which, None, coins)
        lines += [f"### {name} ({' '.join(coins)})", "", "| Version | Half | Trades | Return | Max DD | Return/DD | PF | "
                  "Avg risk | Never-seen P/L | Never-seen PF |", "|---|---|---|---|---|---|---|---|---|---|"]
        for h in base:
            b = base[h]
            lines.append(f"| as it trades | {h} | {b['n']} | {b['ret']:+.1f}% | {b['dd']:.1f}% | {b['rd']:.2f} | {b['pf']:.2f} | "
                         f"0.50% | {base_un[h]['pnl']:+.0f} | {base_un[h]['pf']:.2f} |")
        for vname, v in mod.VARIANTS.items():
            res = {h: overlay_run(which, v, coins, t0, t1) for h, t0, t1 in e.HALVES}
            un = overlay_unseen(which, v, coins)
            why = []
            for h in res:
                r, b = res[h], base[h]
                if not (r["rd"] > b["rd"] and r["pf"] >= b["pf"] and r["dd"] >= -10):
                    why.append(f"{h}: return/DD {r['rd']:.2f} vs {b['rd']:.2f}, PF {r['pf']:.2f} vs {b['pf']:.2f}, DD {r['dd']:.1f}%")
                if not (un[h]["pnl"] >= base_un[h]["pnl"] and un[h]["pf"] >= base_un[h]["pf"]):
                    why.append(f"never-seen {h}: P/L {un[h]['pnl']:+.0f} vs {base_un[h]['pnl']:+.0f}, PF {un[h]['pf']:.2f} vs "
                               f"{base_un[h]['pf']:.2f}")
                lines.append(f"| {vname} | {h} | {r['n']} | {r['ret']:+.1f}% | {r['dd']:.1f}% | {r['rd']:.2f} | {r['pf']:.2f} | "
                             f"{r['avg_risk']:.2f}% | {un[h]['pnl']:+.0f} | {un[h]['pf']:.2f} |")
            verdicts.append((f"{name} / {vname}", not why, "; ".join(why)))
        lines.append("")
        print(f"spec {mod.SPEC['id']}: done {name}", flush=True)
    return lines, verdicts


def run_newbot(mod):
    variants = {}
    for vname, v in mod.VARIANTS.items():
        fn, manage = v["entries"], v.get("manage")
        variants[vname] = ((lambda fn, manage: lambda data, t0, t1: e.trade_sim(e.DESIGN, data, fn, t0, t1, manage=manage))(fn, manage),
                           (lambda fn, manage: lambda coin, data, t0, t1: e.trade_sim([coin], data, fn, t0, t1, manage=manage))(fn, manage))
    rows, vlines, best = e.evaluate(variants)
    verdicts = []
    for vname in variants:
        line = next((x for x in vlines if x.startswith(f"- {vname}:")), "")
        nxt = vlines[vlines.index(line) + 1] if line in vlines else ""
        verdicts.append((vname, "PASS" in nxt, nxt.strip()))
    return rows + [""] + vlines, verdicts


# ───────── queue + ledger ─────────
QUEUE_ROW = re.compile(r"^\| *(\d+) *\| *(\S+\.py) *\| *([^|]+?) *\| *([^|]*?) *\|$")


def queued():
    with open(IDEAS) as f:
        rows = [QUEUE_ROW.match(x.strip()) for x in f]
    return [(m.group(1), m.group(2), m.group(3)) for m in rows if m and m.group(3).lower() == "queued"]


def mark(spec_path, status, result):
    with open(IDEAS) as f:
        lines = f.read().split("\n")
    for i, x in enumerate(lines):
        m = QUEUE_ROW.match(x.strip())
        if m and m.group(2) == spec_path:
            lines[i] = f"| {m.group(1)} | {spec_path} | {status} | {result} |"
    with open(IDEAS, "w") as f:
        f.write("\n".join(lines))


def ledger_add(spec_id, verdicts, when):
    with open(LEDGER) as f:
        text = f.read()
    rows = [f"| {when} | {spec_id} | {v} | {'PASS' if ok else 'fail'} |" for v, ok, _ in verdicts]
    head, table = text.split("<!-- rows -->")
    table = table.rstrip("\n") + "\n" + "\n".join(rows) + "\n"
    n_total = int(re.search(r"Variants tested so far: (\d+)", head).group(1)) + len(verdicts)
    n_pass = int(re.search(r"Rule passes so far: (\d+)", head).group(1)) + sum(1 for _, ok, _ in verdicts if ok)
    head = re.sub(r"Variants tested so far: \d+", f"Variants tested so far: {n_total}", head)
    head = re.sub(r"Rule passes so far: \d+", f"Rule passes so far: {n_pass}", head)
    head = re.sub(r"expected lucky passes at a 5% false-pass rate: about \d+",
                  f"expected lucky passes at a 5% false-pass rate: about {round(n_total * 0.05)}", head)
    with open(LEDGER, "w") as f:
        f.write(head + "<!-- rows -->" + table)
    return n_total, n_pass


def run_queue(max_specs=3):
    """Run up to max_specs queued specs. Returns Markdown lines for the weekly report."""
    out = ["## 4. Research queue (spec files run by the Scout)", ""]
    todo = queued()[:max_specs]
    if not todo:
        return out + ["Nothing queued. New ideas go in as spec files (research/specs/) + a 'queued' row in "
                      "research/ideas/IDEAS.md.", ""]
    when = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    for order, path, _ in todo:
        mod = load_spec(path)
        sid = mod.SPEC["id"]
        try:
            lines, verdicts = run_overlay(mod) if mod.SPEC["kind"] == "overlay" else run_newbot(mod)
        except Exception as ex:
            mark(path, "error", str(ex)[:80])
            out += [f"### {sid}: error", "", f"`{ex}`", ""]
            continue
        n_total, n_pass = ledger_add(sid, verdicts, when)
        passed = [v for v, ok, _ in verdicts if ok]
        res = os.path.join(RESULTS, f"{sid}.md")
        with open(res, "w") as f:
            f.write("\n".join([f"# {sid}: {mod.SPEC['title']}", "", f"Run {when} by the spec runner (research/spec_runner.py) "
                               f"from {path} (written {mod.SPEC['written']} by {mod.SPEC['author']}).", ""] + lines + [
                "## Verdicts", ""] + [f"- {v}: {'PASS' if ok else 'fail'}{'' if ok else ' - ' + why}" for v, ok, why in verdicts]) + "\n")
        status = ("PASS (paper candidate, needs Jeff's OK): " + ", ".join(passed)) if passed else "fail"
        mark(path, status, f"research/specs/results/{sid}.md")
        out += [f"### {sid}: {mod.SPEC['title']}: {'PASS - ' + ', '.join(passed) if passed else 'fail'}", "",
                f"Full table: research/specs/results/{sid}.md. Ledger: {n_total} variants tested so far, {n_pass} rule "
                f"passes (about {round(n_total * 0.05)} would pass by luck alone at a 5% false-pass rate).", ""]
    return out


if __name__ == "__main__":
    print("\n".join(run_queue(int(sys.argv[1]) if len(sys.argv) > 1 else 3)))
