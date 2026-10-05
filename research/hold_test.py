"""
Hold pile test (covers H4): M3 rotation vs buy-and-hold vs weekly DCA vs dip-buying DCA.
Contenders and decision rules fixed beforehand in research/HOLD_PLAN.md.

Run:
  python research/hold_test.py        # writes research/HOLD.md
"""
import datetime as dt
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402
import n2_rotation as n2  # noqa: E402

DAY, FEE, WEEKLY = n2.DAY, 0.001, 10.0
UTC = dt.timezone.utc
PERIODS = [("2018-05 to now", e.START, None), ("1st half (2018-05 to 2021)", e.START, e.CUT),
           ("2nd half (2022 to now)", e.CUT, None)]


def days(D, t0, t1):
    first = e.ms(t0) // DAY * DAY
    while dt.datetime.fromtimestamp(first / 1000, UTC).weekday() != 0:
        first += DAY
    last = min(e.ms(t1 or e.now()), max(D.px["BTC"]), max(D.px["XRP"])) // DAY * DAY
    return list(range(first, last + 1, DAY))


def sma200(D, coin, day):
    cs = [D.px[coin].get(day - j * DAY) for j in range(200)]
    return None if None in cs else sum(cs) / 200


def hold_sim(D, t0, t1, weights, weekly=0.0, dip=False):
    """Buy-and-hold (weekly=0: $1,000 on day one) or weekly DCA (weekly dollars each Monday)."""
    units = {c: 0.0 for c in weights}
    spent = {c: 0.0 for c in weights}
    paid, nav_units, nav, last = 0.0, 0.0, [], {}

    def value(day):
        for c in units:
            p = D.px[c].get(day)
            if p is not None:
                last[c] = p
        return sum(units[c] * last.get(c, 0.0) for c in units)

    for i, day in enumerate(days(D, t0, t1)):
        is_monday = dt.datetime.fromtimestamp(day / 1000, UTC).weekday() == 0
        if (weekly and is_monday) or (not weekly and i == 0):
            sig = day - DAY
            v = value(sig)
            add = 0.0
            for c, w in weights.items():
                p = D.px[c].get(sig)
                if p is None:
                    continue
                amt = (w * weekly) if weekly else (w * 1000.0)
                if dip:
                    s = sma200(D, c, sig)
                    if s is not None and p <= 0.8 * s:
                        amt *= 2
                units[c] += amt / (1 + FEE) / p
                spent[c] += amt
                add += amt
            nav_units += add / (v / nav_units) if nav_units > 0 and v > 0 else add
            paid += add
        val = value(day)
        nav.append((day, val / nav_units if nav_units else 1.0))
    return {"nav": nav, "paid": paid, "final": val,
            "avg_px": {c: spent[c] / units[c] if units[c] else None for c in units}}


def metrics(nav):
    peak, dd, under, longest, run = nav[0][1], 0.0, 0, 0, 0
    years = {}
    for day, v in nav:
        peak = max(peak, v)
        dd = min(dd, v / peak - 1)
        if v < peak:
            under += 1
            run += 1
            longest = max(longest, run)
        else:
            run = 0
        years[dt.datetime.fromtimestamp(day / 1000, UTC).year] = v
    worst, start = None, nav[0][1]
    for y in sorted(years):
        r = years[y] / start - 1
        if worst is None or r < worst[0]:
            worst = (r, y)
        start = years[y]
    ret = nav[-1][1] / nav[0][1] - 1
    return {"ret": ret * 100, "dd": dd * 100, "worst": worst, "under": under / len(nav) * 100, "longest": longest,
            "rd": ret / -dd if dd else float("inf")}


def main():
    D = n2.Data()
    lines = ["# Hold pile test (M3 rotation vs buy-and-hold vs DCA vs dip DCA; covers H4)", "",
             "Contenders and decision rules fixed beforehand in research/HOLD_PLAN.md. Daily closes, Monday trades, "
             "0.1% fee. Return, max DD, worst year and time underwater are on a time-weighted unit value, so weekly "
             "deposits don't count as gains. Script: research/hold_test.py.", ""]
    res = {}
    for pname, t0, t1 in PERIODS:
        rows = {
            "Buy-and-hold BTC ($1,000)": hold_sim(D, t0, t1, {"BTC": 1.0}),
            "Buy-and-hold 50/50 BTC+XRP ($1,000)": hold_sim(D, t0, t1, {"BTC": 0.5, "XRP": 0.5}),
            "M3 rotation ($1,000)": n2.sim(D, 1, 10, 28, True, t0, t1),
            "Plain DCA $5 BTC + $5 XRP weekly": hold_sim(D, t0, t1, {"BTC": 0.5, "XRP": 0.5}, WEEKLY),
            "Dip DCA (2x when 20% below 200-day)": hold_sim(D, t0, t1, {"BTC": 0.5, "XRP": 0.5}, WEEKLY, dip=True),
            "M3 rotation, $10 weekly": n2.sim(D, 1, 10, 28, True, t0, t1, contrib=WEEKLY, start_cash=0.0),
        }
        res[pname] = {}
        lines += [f"## {pname}", "", "| Contender | Return | Max DD | Return / DD | Worst year | Days underwater | "
                  "Longest underwater | Paid in | Final value | Value / paid | Avg price BTC | Avg price XRP |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for name, r in rows.items():
            m = metrics(r["nav"])
            res[pname][name] = (m, r)
            weekly = abs(r["paid"] - 1000.0) > 1e-6
            ap = r.get("avg_px", {})
            lines.append(f"| {name} | {m['ret']:+.0f}% | {m['dd']:.0f}% | {m['rd']:.2f} | {m['worst'][0] * 100:+.0f}% "
                         f"({m['worst'][1]}) | {m['under']:.0f}% | {m['longest']} days | "
                         f"{'$%.0f' % r['paid'] if weekly else '$1,000'} | ${r['final']:,.0f} | "
                         f"{r['final'] / r['paid']:.2f} | "
                         f"{('$%.0f' % ap['BTC']) if ap.get('BTC') else '-'} | {('$%.3f' % ap['XRP']) if ap.get('XRP') else '-'} |")
        lines.append("")
        print(f"done {pname}", flush=True)

    halves = [p for p, _, _ in PERIODS[1:]]
    m3_ok = all(res[h]["M3 rotation ($1,000)"][0]["dd"] > res[h]["Buy-and-hold BTC ($1,000)"][0]["dd"] and
                res[h]["M3 rotation ($1,000)"][0]["rd"] > res[h]["Buy-and-hold BTC ($1,000)"][0]["rd"] for h in halves)
    dip_ok = all(all(res[h]["Dip DCA (2x when 20% below 200-day)"][1]["avg_px"][c] <
                     res[h]["Plain DCA $5 BTC + $5 XRP weekly"][1]["avg_px"][c] for c in ("BTC", "XRP")) and
                 res[h]["Dip DCA (2x when 20% below 200-day)"][1]["final"] / res[h]["Dip DCA (2x when 20% below 200-day)"][1]["paid"] >=
                 res[h]["Plain DCA $5 BTC + $5 XRP weekly"][1]["final"] / res[h]["Plain DCA $5 BTC + $5 XRP weekly"][1]["paid"]
                 for h in halves)
    lines += ["## Verdicts (rules from HOLD_PLAN.md)", "",
              f"- M3 for the hold pile: {'RECOMMENDED' if m3_ok else 'not recommended'} (needs a smaller max DD than "
              "buy-and-hold BTC and a higher return / DD in both halves)",
              f"- Dip DCA over plain DCA: {'RECOMMENDED' if dip_ok else 'not recommended'} (needs a lower average price "
              "for BTC and XRP and no lower value / paid in, in both halves)"]
    with open(os.path.join(HERE, "HOLD.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
