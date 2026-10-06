"""F27: Jeff's DCA + trend plan vs plain DCA and the Hold pile (research/F27_PLAN.md). Research only.

  python research/f27_dca.py
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

FEE, MONTHLY = 0.0035, 300.0


def day(ts):
    return dt.datetime.fromtimestamp(ts / 1000, dt.timezone.utc)


def sim(bars, t0, t1, mode, rungs=(0.15, 0.20, 0.30)):
    """mode: "plain" | "holdpile" | "trend" (rungs=None: ladder off). Returns put_in, value, multiple, worst drop %."""
    c = [b["c"] for b in bars]
    s200 = bot.sma(c, 200)
    idx = [k for k, b in enumerate(bars) if e.ms(t0) <= b["ts"] < e.ms(t1) and s200[k] is not None]
    cash = units = put_in = 0.0
    pending = []  # (kind, usd) to fill at the next open
    safe = None
    was_crash = lump_fired = False
    exited = committed = 0.0
    fired = [False, False, False]
    run_high = None
    index, peak, worst, prev_v = 1.0, 1.0, 0.0, None

    def buy(usd, px):
        nonlocal cash, units
        usd = min(usd, cash)
        if usd > 1e-9:
            cash -= usd
            units += usd * (1 - FEE) / px

    for n, k in enumerate(idx):
        b = bars[k]
        for kind, usd in pending:  # fills at today's open
            if kind == "sell":
                cash += units * b["o"] * (1 - FEE)
                units = 0.0
            else:
                buy(usd, b["o"])
        pending = []
        contrib = 0.0
        new_month = n == 0 or day(b["ts"]).month != day(bars[idx[n - 1]]["ts"]).month
        if mode == "holdpile":  # same $ per month, spread weekly (Mondays), x2 when 20%+ under the 200-day
            if day(b["ts"]).weekday() == 0:
                usd = MONTHLY * 12 / 52 * (2 if c[k] <= 0.8 * s200[k] else 1)
                cash += usd
                contrib = usd
                pending.append(("buy", usd))
        elif new_month:
            cash += MONTHLY
            contrib = MONTHLY
            pending.append(("buy", MONTHLY))
        if mode == "trend":
            run_high = c[k] if run_high is None else max(run_high, c[k])
            was_safe = safe
            if safe is None:
                safe = c[k] > s200[k]
            elif c[k] > s200[k] * 1.02:
                safe = True
            elif c[k] < s200[k] * 0.98:
                safe = False
            crash = was_safe is True and not safe
            if crash and units > 0:
                exited = units * c[k]
                pending.insert(0, ("sell", 0))
                was_crash, lump_fired, committed, fired = True, False, 0.0, [False, False, False]
            if rungs and was_crash and not lump_fired and not safe and not crash:
                per = exited * 0.95 / len(rungs)
                for j, r in enumerate(rungs):
                    if not fired[j] and c[k] <= run_high * (1 - r):
                        pending.append(("buy", per))
                        fired[j] = True
                        committed += per
            if was_crash and not lump_fired and safe:
                lump = max(exited * 0.95 - committed, 0.0)
                if lump > 0:
                    pending.append(("buy", lump))
                lump_fired = True
        put_in += contrib
        v = cash + units * c[k]
        if prev_v and prev_v > 0:
            index *= (v - contrib) / prev_v
            peak = max(peak, index)
            worst = min(worst, index / peak - 1)
        prev_v = v
    return put_in, v, v / put_in if put_in else 0.0, worst * 100


def main():
    coins = ["BTC", "XRP", "ETH"]
    data = {c: d for c, (_, d) in e.load(coins).items()}
    modes = [("Plain monthly DCA", "plain", None), ("Hold pile rule (live)", "holdpile", None),
             ("E1 as written 15/20/30", "trend", (0.15, 0.20, 0.30)), ("E2 crypto ladder 40/55/70", "trend", (0.40, 0.55, 0.70)),
             ("E3 ladder off", "trend", ())]
    for lab, t0, t1 in [("full", e.START, None), *e.HALVES]:
        t1 = t1 or e.now()
        print(f"\n== {lab} ({t0:%Y-%m} to {t1:%Y-%m}) ==")
        for c in coins:
            for name, m, r in modes:
                p, v, mult, dd = sim(data[c], t0, t1, m, r if r is not None else (0.15, 0.20, 0.30))
                print(f"{c:4} {name:26} put in ${p:8,.0f}  now ${v:9,.0f}  x{mult:5.2f}  worst drop {dd:6.1f}%", flush=True)


if __name__ == "__main__":
    main()
