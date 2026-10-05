"""
N2 rotation bot: each Monday hold the strongest K coins of the top 10 (as listed at the time) by momentum;
cash when BTC is below its 200-day average. Variants and rules fixed beforehand in research/NEWBOTS_PLAN.md.

Run:
  python research/n2_rotation.py        # writes research/N2_ROTATION.md
"""
import bisect
import datetime as dt
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import universe as u  # noqa: E402

DAY, FEE, K = u.DAY, 0.001, 3
UTC = dt.timezone.utc


class Data:
    def __init__(self):
        self.snaps = sorted((int(dt.datetime.fromisoformat(d).replace(tzinfo=UTC).timestamp() * 1000), s)
                            for d, s in u.snapshots().items())
        self.snap_days = [d for d, _ in self.snaps]
        self.px = {s: u.daily(s) for s in u.all_symbols()}
        self.px["BTC"] = self.px.get("BTC") or u.daily("BTC")

    def universe(self, day, lo, hi):
        i = bisect.bisect_right(self.snap_days, day) - 1
        return u.ranked(self.snaps[i][1], lo, hi) if i >= 0 else []

    def price(self, sym, day):
        return self.px.get(sym, {}).get(day)


def sim(D, lo, hi, lookback, vol_scaled, t0, t1=None):
    t1 = t1 or e.now()
    first = e.ms(t0) // DAY * DAY
    while dt.datetime.fromtimestamp(first / 1000, UTC).weekday() != 0:
        first += DAY
    last_day = min(e.ms(t1), max(D.px["BTC"])) // DAY * DAY
    cash, units, last_px = 1000.0, {}, {}
    episodes, open_ep = [], {}
    curve, skipped, seen = [], 0, 0
    btc = D.px["BTC"]

    def value(day):
        tot = cash
        for s, q in units.items():
            p = D.price(s, day)
            if p is not None:
                last_px[s] = p
            tot += q * last_px.get(s, 0.0)
        return tot

    day = first
    while day <= last_day:
        if dt.datetime.fromtimestamp(day / 1000, UTC).weekday() == 0:
            sig = day - DAY  # Sunday close, traded at Monday 00:00
            closes = [btc.get(sig - j * DAY) for j in range(200)]
            on = None not in closes and closes[0] > sum(closes) / 200
            targets = {}
            if on:
                cands = []
                for s in D.universe(sig, lo, hi):
                    seen += 1
                    p0, p1 = D.price(s, sig - lookback * DAY), D.price(s, sig)
                    if p0 is None or p1 is None:
                        skipped += 1
                        continue
                    if p1 / p0 - 1 > 0:
                        cands.append((p1 / p0 - 1, s))
                for _, s in sorted(cands, reverse=True)[:K]:
                    w = 1 / K
                    if vol_scaled:
                        r = [D.price(s, sig - j * DAY) for j in range(21)]
                        if None in r:
                            continue
                        lr = [math.log(r[j] / r[j + 1]) for j in range(20)]
                        m = sum(lr) / 20
                        sd = math.sqrt(sum((x - m) ** 2 for x in lr) / 19)
                        w *= min(1.0, 0.02 / sd) if sd > 0 else 1.0
                    targets[s] = w
            eq = value(sig)
            # all sells first (frees cash), then buys
            plan = []
            for s_ in set(units) | set(targets):
                p = D.price(s_, sig) or last_px.get(s_)
                if p:
                    plan.append((s_, p, units.get(s_, 0.0) * p, targets.get(s_, 0.0) * eq))
            for s_, p, cur, want in plan:
                if want < cur - 1e-9:
                    q = units[s_] if s_ not in targets else (cur - want) / p
                    proceeds = q * p * (1 - FEE)
                    cash += proceeds
                    units[s_] -= q
                    open_ep[s_]["flow"] += proceeds
                    if s_ not in targets or units[s_] <= 1e-12:
                        units.pop(s_, None)
                        episodes.append({"coin": s_, "pnl": open_ep.pop(s_)["flow"]})
            for s_, p, cur, want in plan:
                if want > cur + 1e-9:
                    spend = min(want - cur, cash)
                    if spend < 1:
                        continue
                    cash -= spend
                    units[s_] = units.get(s_, 0.0) + spend / (1 + FEE) / p
                    open_ep.setdefault(s_, {"flow": 0.0})["flow"] -= spend
        curve.append((day, value(day)))
        day += DAY
    for s_ in list(units):
        proceeds = units.pop(s_) * last_px.get(s_, 0.0) * (1 - FEE)
        cash += proceeds
        episodes.append({"coin": s_, "pnl": open_ep.pop(s_)["flow"] + proceeds})
    r = e._stats(episodes, curve, cash)
    r["skipped"], r["seen"] = skipped, seen
    return r


def main():
    D = Data()
    variants = {"M1: top 3, 28-day momentum": (28, False), "M2: top 3, 90-day momentum": (90, False),
                "M3: top 3, 28-day, volatility-scaled": (28, True)}
    base = e.baseline()
    b_ret, b_dd, b_rd = e.ret_dd(base["mix"])
    rows = ["| Variant | Universe | Half | Holdings | Win % | Return | Max DD | PF |", "|---|---|---|---|---|---|---|---|"]
    verdicts, best = [], (None, 0.0)
    for name, (lb, vs) in variants.items():
        why = []
        for uni, (lo, hi) in (("top 10", (1, 10)), ("ranks 11-20", (11, 20))):
            for h, t0, t1 in e.HALVES:
                r = sim(D, lo, hi, lb, vs, t0, t1)
                rows.append(f"| {name} | {uni} | {h} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | "
                            f"{r['dd']:.1f}% | {r['pf']:.2f} |")
                if uni == "top 10":
                    if not (r["pf"] > 1.0 and r["pnl"] > 0):
                        why.append(f"top-10 {h} not profitable")
                    if r["dd"] < -10:
                        why.append(f"top-10 {h} DD {r['dd']:.1f}%")
                elif not r["pf"] > 1.0:
                    why.append(f"ranks 11-20 {h} PF {r['pf']:.2f}")
        full = sim(D, 1, 10, lb, vs, e.START)
        cr = e.corr(e.monthly(full["curve"]), e.monthly(base["mix"]))
        n_ret, n_dd, n_rd = e.ret_dd(e.combine([base["v4"], base["tr"], full["curve"]], [1 / 3] * 3))
        if not cr < 0.5:
            why.append(f"correlation {cr:.2f}")
        if not n_rd > b_rd:
            why.append(f"portfolio return/DD {n_rd:.2f} not above {b_rd:.2f}")
        verdicts.append(f"- {name}: own 2018-05 to now {full['ret']:+.0f}% / DD {full['dd']:.1f}%; correlation with "
                        f"v4+TR {cr:.2f}; portfolio return/DD {n_rd:.2f} ({n_ret:+.0f}% / {n_dd:.1f}%) vs v4+TR "
                        f"{b_rd:.2f} ({b_ret:+.0f}% / {b_dd:.1f}%); top-10 coins skipped for no data: "
                        f"{full['skipped']} of {full['seen']}")
        verdicts.append(f"  {'PASS' if not why else 'fail: ' + '; '.join(why)}")
        if not why and n_rd - b_rd > best[1]:
            best = (name, n_rd - b_rd)
        print(f"done {name}", flush=True)
    lines = ["# N2 rotation bot", "", "Variants and rules fixed beforehand in research/NEWBOTS_PLAN.md. Universe = "
             "CoinMarketCap top 10 (or ranks 11-20) as listed at the time, stablecoins removed. Weekly, 0.1% fee. "
             "Script: research/n2_rotation.py.", ""] + rows + [""] + verdicts + [
             "", f"Result: {'PASS - ' + best[0] if best[0] else 'no variant passes'}"]
    with open(os.path.join(HERE, "N2_ROTATION.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
