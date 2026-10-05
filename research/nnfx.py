"""
NNFX-style daily system, built one slot at a time (C1 -> baseline -> volume -> exit), every choice made on the
SELECTION period only, the finished system judged once on the later period and on never-seen markets.
Plan and pass rules fixed beforehand in research/IDEAS_PLAN.md (NNFX section).

Run:
  python research/nnfx.py        # writes research/NNFX.md
"""
import datetime as dt
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import forex_dxy as fx  # noqa: E402
import long_history as lh  # noqa: E402

UTC = dt.timezone.utc


def d(y, m=1, day=1):
    return dt.datetime(y, m, day, tzinfo=UTC)


FX_COST, CR_COST, RISK, MAX_OPEN = 0.0005, 0.001, 0.005, 3
GROUPS = {
    "forex": {"markets": ["EURUSD", "GBPUSD", "USDJPY"], "short": True, "cost": FX_COST,
              "select": (d(2012), d(2019)), "judge": (d(2019), None)},
    "crypto": {"markets": ["BTC", "ETH", "XRP"], "short": False, "cost": CR_COST,
               "select": (d(2018, 5), d(2022)), "judge": (d(2022), None)},
}
UNSEEN = {"forex": ["AUDUSD", "NZDUSD", "USDCAD", "USDCHF"],
          "crypto": ["SOL", "LTC", "DOGE", "XLM", "ADA", "BNB", "LINK", "BCH", "AVAX", "SUI"]}
_cache = {}
FX_PAIRS = {"EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "NZDUSD", "USDCAD", "USDCHF"}


def daily(m):
    if m not in _cache:
        _cache[m] = fx.fx_daily(fx.fxcm(m)) if m in FX_PAIRS else lh.load(m)[1]
    return _cache[m]


# ───────── indicators (all return one value per day) ─────────
def wma(src, n):
    out = [None] * len(src)
    w = list(range(1, n + 1))
    for i in range(n - 1, len(src)):
        win = src[i - n + 1:i + 1]
        if None not in win:
            out[i] = sum(a * b for a, b in zip(win, w)) / sum(w)
    return out


def hma(c, n=30):
    a, b = wma(c, n // 2), wma(c, n)
    diff = [2 * x - y if x is not None and y is not None else None for x, y in zip(a, b)]
    return wma(diff, int(math.sqrt(n)))


def kama(c, n=10, fast=2, slow=30):
    out = [None] * len(c)
    fs, ss = 2 / (fast + 1), 2 / (slow + 1)
    for i in range(n, len(c)):
        change = abs(c[i] - c[i - n])
        vol = sum(abs(c[j] - c[j - 1]) for j in range(i - n + 1, i + 1))
        er = change / vol if vol else 0
        sc = (er * (fs - ss) + ss) ** 2
        prev = out[i - 1] if out[i - 1] is not None else c[i - 1]
        out[i] = prev + sc * (c[i] - prev)
    return out


def kijun(h, l, n=26):
    hh, ll = bot.highest(h, n), bot.lowest(l, n)
    return [(a + b) / 2 if a is not None else None for a, b in zip(hh, ll)]


def aroon_dir(h, l, n=25):
    out = [0] * len(h)
    for i in range(n, len(h)):
        wh, wl = h[i - n:i + 1], l[i - n:i + 1]
        up = 100 * (n - wh[::-1].index(max(wh))) / n
        dn = 100 * (n - wl[::-1].index(min(wl))) / n
        out[i] = 1 if up > dn else (-1 if dn > up else out[i - 1])
    return out


def vortex_dir(h, l, c, n=14):
    out = [0] * len(c)
    for i in range(n + 1, len(c)):
        vp = sum(abs(h[j] - l[j - 1]) for j in range(i - n + 1, i + 1))
        vm = sum(abs(l[j] - h[j - 1]) for j in range(i - n + 1, i + 1))
        out[i] = 1 if vp > vm else (-1 if vm > vp else out[i - 1])
    return out


def ssl_dir(h, l, c, n=10):
    sh, sl = bot.sma(h, n), bot.sma(l, n)
    out = [0] * len(c)
    for i in range(len(c)):
        if sh[i] is None:
            continue
        out[i] = 1 if c[i] > sh[i] else (-1 if c[i] < sl[i] else out[i - 1])
    return out


def psar_dir(h, l, c):
    s = bot.psar(h, l, c, 0.02, 0.02, 0.2)
    return [0 if v is None else (1 if c[i] > v else -1) for i, v in enumerate(s)]


C1 = {"Aroon(25)": lambda h, l, c: aroon_dir(h, l), "Vortex(14)": lambda h, l, c: vortex_dir(h, l, c),
      "SSL(10)": lambda h, l, c: ssl_dir(h, l, c)}
BASE = {"Kijun(26)": lambda h, l, c: kijun(h, l), "HMA(30)": lambda h, l, c: hma(c), "KAMA(10,2,30)": lambda h, l, c: kama(c)}


def adx_gt(h, l, c):
    a = e.adx(h, l, c, 14)
    return [x is not None and x > 20 for x in a]


def adx_rising(h, l, c):
    a = e.adx(h, l, c, 14)
    return [i >= 3 and a[i] is not None and a[i - 3] is not None and a[i] > a[i - 3] for i in range(len(a))]


def atr_above(h, l, c):
    a = bot.atr(h, l, c, 14)
    m = bot.sma(a, 50)
    return [x is not None and y is not None and x > y for x, y in zip(a, m)]


VOL = {"ADX(14) > 20": adx_gt, "ADX(14) rising": adx_rising, "ATR(14) above its 50-day average": atr_above}


# ───────── system simulator ─────────
def signals(bars, cfg):
    h, l, c = ([b[x] for b in bars] for x in "hlc")
    s = {"atr": bot.atr(h, l, c, 14), "c1": C1[cfg["c1"]](h, l, c)}
    s["base"] = BASE[cfg["base"]](h, l, c) if cfg.get("base") else None
    s["vol"] = VOL[cfg["vol"]](h, l, c) if cfg.get("vol") else None
    s["psar"] = psar_dir(h, l, c) if cfg.get("exit") == "PSAR flip" else None
    return s


def run_group(markets, cfg, t0, t1, short, cost):
    """One $1,000 balance across `markets`, daily, NNFX money management. Returns stats incl. curve."""
    t1 = t1 or e.now()
    per = {}
    for m in markets:
        bars = daily(m)
        if not bars:
            continue
        per[m] = (bars, signals(bars, cfg), {b["ts"]: k for k, b in enumerate(bars)})
    times = sorted({b["ts"] for bars, _, _ in per.values() for b in bars if e.ms(t0) <= b["ts"] < e.ms(t1)})
    eq, pos, trades, curve = 1000.0, {}, [], []

    def settle(p, qty, px):
        return (px - p["entry"]) * qty * p["side"] - (p["entry"] + px) * qty * cost

    def close_all(m, px):
        nonlocal eq
        p = pos.pop(m)
        pnl = settle(p, p["qty"], px)
        eq += pnl
        p["pnl"] += pnl
        trades.append(p["pnl"])

    for ts in times:
        for m, (bars, s, idx) in per.items():
            k = idx.get(ts)
            if k is None or k < 1:
                continue
            b = bars[k]
            if m in pos:
                p = pos[m]
                side = p["side"]
                if (b["l"] <= p["stop"]) if side == 1 else (b["h"] >= p["stop"]):
                    close_all(m, min(p["stop"], b["o"]) if side == 1 else max(p["stop"], b["o"]))
                    continue
                if not p["tp_done"] and ((b["h"] >= p["tp"]) if side == 1 else (b["l"] <= p["tp"])):
                    px = max(p["tp"], b["o"]) if side == 1 else min(p["tp"], b["o"])
                    half = p["qty"] / 2
                    pnl = settle(p, half, px)
                    eq += pnl
                    p["pnl"] += pnl
                    p["qty"] -= half
                    p["tp_done"] = True
                    p["stop"] = p["entry"]  # breakeven for the runner
                ex = cfg.get("exit", "opposite C1 flip")
                if ex == "opposite C1 flip":
                    out = s["c1"][k] == -side
                elif ex == "baseline cross":
                    out = s["base"][k] is not None and (b["c"] - s["base"][k]) * side < 0
                else:
                    out = s["psar"][k] == -side
                if out:
                    close_all(m, b["c"])
                continue
            # new entry at the close on a C1 flip
            d_ = s["c1"][k]
            if d_ == 0 or d_ == s["c1"][k - 1] or (d_ == -1 and not short) or s["atr"][k] is None:
                continue
            if s["base"] is not None and (s["base"][k] is None or (b["c"] - s["base"][k]) * d_ <= 0):
                continue
            if s["vol"] is not None and not s["vol"][k]:
                continue
            if len(pos) >= MAX_OPEN:
                continue
            a = s["atr"][k]
            stop = b["c"] - 1.5 * a * d_
            in_use = sum(p["qty"] * p["entry"] for p in pos.values())
            qty = min(eq * RISK / (1.5 * a), max(eq - in_use, 0.0) / b["c"])
            if qty * b["c"] < 5:
                continue
            pos[m] = {"side": d_, "entry": b["c"], "qty": qty, "stop": stop, "tp": b["c"] + a * d_, "tp_done": False,
                      "pnl": 0.0}
        mtm = eq
        for m, p in pos.items():
            bars, _, idx = per[m]
            k = idx.get(ts)
            if k is not None:
                mtm += settle(p, p["qty"], bars[k]["c"])
        curve.append((ts, mtm))
    for m in list(pos):
        bars = per[m][0]
        close_all(m, [b for b in bars if b["ts"] < e.ms(t1)][-1]["c"])
    won, lost = sum(x for x in trades if x > 0), -sum(x for x in trades if x < 0)
    ret, dd, _ = e.ret_dd(curve) if curve else (0.0, 0.0, 0.0)
    return {"trades": len(trades), "won": won, "lost": lost, "pnl": eq - 1000, "ret": eq / 10 - 100, "dd": dd,
            "pf": won / lost if lost else (float("inf") if won else 0.0), "curve": curve,
            "win": sum(x > 0 for x in trades) / len(trades) * 100 if trades else 0.0}


def score(cfg, period="select"):
    """Pooled PF over both groups' design markets in the given period."""
    rs = {g: run_group(v["markets"], cfg, *v[period], v["short"], v["cost"]) for g, v in GROUPS.items()}
    won, lost = sum(r["won"] for r in rs.values()), sum(r["lost"] for r in rs.values())
    return (won / lost if lost else 0.0), rs


def unseen(cfg, g):
    """Never-seen markets, each alone, later period, pooled."""
    v = GROUPS[g]
    rs = [run_group([m], cfg, *v["judge"], v["short"], v["cost"]) for m in UNSEEN[g]]
    won, lost = sum(r["won"] for r in rs), sum(r["lost"] for r in rs)
    return {"pf": won / lost if lost else 0.0, "pnl": sum(r["pnl"] for r in rs), "trades": sum(r["trades"] for r in rs),
            "worst": min(r["dd"] for r in rs)}


def row(label, pf, rs):
    return (f"| {label} | {pf:.2f} | {rs['forex']['trades']} / {rs['forex']['ret']:+.1f}% / {rs['forex']['pf']:.2f} | "
            f"{rs['crypto']['trades']} / {rs['crypto']['ret']:+.1f}% / {rs['crypto']['pf']:.2f} |")


def main():
    head = ["| Candidate | Pooled PF | Forex trades / return / PF | Crypto trades / return / PF |", "|---|---|---|---|"]
    lines = ["# NNFX-style daily system", "", "Plan and rules fixed beforehand in research/IDEAS_PLAN.md. Choices made on the "
             "SELECTION period only (forex 2012-2018 long+short, crypto 2018-05 to 2021 long only); the finished system is "
             "judged once on the later period. Script: research/nnfx.py.", ""]
    # 1. C1
    lines += ["## Step 1: C1 confirmation (selection period)", ""] + head
    best = None
    for name in C1:
        pf, rs = score({"c1": name})
        lines.append(row(name, pf, rs))
        if best is None or pf > best[1]:
            best = (name, pf)
    cfg, cur = {"c1": best[0]}, best[1]
    lines += ["", f"Kept: **{best[0]}** (pooled PF {cur:.2f}).", ""]
    print("step 1", cfg, flush=True)
    # 2. baseline
    lines += ["## Step 2: baseline", ""] + head
    best = None
    for name in BASE:
        pf, rs = score({**cfg, "base": name})
        lines.append(row(f"{cfg['c1']} + {name}", pf, rs))
        if best is None or pf > best[1]:
            best = (name, pf)
    if best[1] > cur:
        cfg["base"], cur = best[0], best[1]
        lines += ["", f"Kept: **{best[0]}** (pooled PF {cur:.2f}).", ""]
    else:
        lines += ["", f"No baseline beats C1 alone ({cur:.2f}); none kept.", ""]
    print("step 2", cfg, flush=True)
    # 3. volume
    lines += ["## Step 3: volume / strength filter", ""] + head
    best = None
    for name in VOL:
        pf, rs = score({**cfg, "vol": name})
        lines.append(row(f"... + {name}", pf, rs))
        if best is None or pf > best[1]:
            best = (name, pf)
    if best[1] > cur:
        cfg["vol"], cur = best[0], best[1]
        lines += ["", f"Kept: **{best[0]}** (pooled PF {cur:.2f}).", ""]
    else:
        lines += ["", f"No filter beats step 2 ({cur:.2f}); none kept.", ""]
    print("step 3", cfg, flush=True)
    # 4. exit
    lines += ["## Step 4: exit indicator for the runner half", ""] + head
    exits = ["opposite C1 flip"] + (["baseline cross"] if cfg.get("base") else []) + ["PSAR flip"]
    best = None
    for name in exits:
        pf, rs = score({**cfg, "exit": name})
        lines.append(row(f"... exit: {name}", pf, rs))
        if best is None or pf > best[1]:
            best = (name, pf)
    cfg["exit"] = best[0]
    lines += ["", f"Kept: **{best[0]}** (pooled PF {best[1]:.2f}).", "", f"Finished system: {cfg}", ""]
    print("step 4", cfg, flush=True)
    # judge once on the later period
    pf, rs = score(cfg, "judge")
    lines += ["## The finished system on the LATER period (judged once)", "", "| Group | Period | Trades | Win % | Return | "
              "Max DD | PF |", "|---|---|---|---|---|---|---|"]
    why = []
    for g, r in rs.items():
        p0 = GROUPS[g]["judge"][0]
        lines.append(f"| {g} ({'long+short' if GROUPS[g]['short'] else 'long only'}) | {p0:%Y}-now | {r['trades']} | "
                     f"{r['win']:.0f}% | {r['ret']:+.1f}% | {r['dd']:.1f}% | {r['pf']:.2f} |")
        if not (r["pf"] > 1 and r["pnl"] > 0):
            why.append(f"{g} not profitable")
        if r["dd"] < -10:
            why.append(f"{g} DD {r['dd']:.1f}%")
    for g in GROUPS:
        u = unseen(cfg, g)
        lines.append(f"| never-seen {g} ({', '.join(UNSEEN[g])}) | later period | {u['trades']} | | P/L {u['pnl']:+.0f} USD | "
                     f"worst {u['worst']:.1f}% | {u['pf']:.2f} |")
        if not u["pf"] > 1:
            why.append(f"never-seen {g} PF {u['pf']:.2f}")
    base = e.baseline()
    full = run_group(GROUPS["crypto"]["markets"], cfg, e.START, None, False, CR_COST)
    cr = e.corr(e.monthly(full["curve"]), e.monthly(base["mix"]))
    n_ret, n_dd, n_rd = e.ret_dd(e.combine([base["v4"], base["tr"], full["curve"]], [1 / 3] * 3))
    b_ret, b_dd, b_rd = e.ret_dd(base["mix"])
    if not cr < 0.5:
        why.append(f"crypto correlation {cr:.2f}")
    if not n_rd > b_rd:
        why.append(f"portfolio return/DD {n_rd:.2f} not above {b_rd:.2f}")
    lines += ["", f"Crypto version 2018-05 to now: {full['ret']:+.1f}% / DD {full['dd']:.1f}% / PF {full['pf']:.2f}; "
              f"correlation with v4+TR {cr:.2f}; portfolio return/DD {n_rd:.2f} vs v4+TR {b_rd:.2f}.", "",
              f"Result: {'PASS' if not why else 'FAIL - ' + '; '.join(why)}"]
    with open(os.path.join(HERE, "NNFX.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
