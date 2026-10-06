"""
F33: CFTC Commitments of Traders (Traders in Financial Futures) for CME Bitcoin futures as a BTC signal.
Data: publicreporting.cftc.gov dataset gpe5-46if (free), "BITCOIN - CHICAGO MERCANTILE EXCHANGE", weekly since 2017-12.
Positions are as of Tuesday and published Friday, so each report is used from the following Monday's close.
Signal: each group's net position (long - short) as a share of open interest, ranked against its own last 52 weeks.
Test: BTC's next-4-week return after high (top third) vs low (bottom third) readings, in both halves.
Research only.
"""
import bisect
import datetime as dt
import json
import urllib.request
import engine as e

URL = ("https://publicreporting.cftc.gov/resource/gpe5-46if.json?$limit=5000&$order=report_date_as_yyyy_mm_dd"
       "&market_and_exchange_names=BITCOIN%20-%20CHICAGO%20MERCANTILE%20EXCHANGE")


def cot():
    rows = json.load(urllib.request.urlopen(URL, timeout=60))
    out = []
    for r in rows:
        d = dt.datetime.fromisoformat(r["report_date_as_yyyy_mm_dd"][:10]).replace(tzinfo=e.UTC)
        oi = float(r["open_interest_all"])
        am = (float(r["asset_mgr_positions_long"]) - float(r["asset_mgr_positions_short"])) / oi
        lev = (float(r["lev_money_positions_long"]) - float(r["lev_money_positions_short"])) / oi
        out.append((d + dt.timedelta(days=6), am, lev))  # usable from Monday after the Friday release
    return out


def pct_rank(xs, i, n=52):
    w = xs[max(0, i - n + 1):i + 1]
    return sum(1 for x in w if x <= xs[i]) / len(w) if len(w) >= 26 else None


def main():
    data = cot()
    _, daily = e.load(["BTC"])["BTC"]
    days = [x["ts"] for x in daily]
    close = {x["ts"]: x["c"] for x in daily}

    def px_on_or_after(t):
        i = bisect.bisect_left(days, e.ms(t))
        return (days[i], close[days[i]]) if i < len(days) else (None, None)

    print(f"{len(data)} weekly reports, {data[0][0]:%Y-%m-%d} to {data[-1][0]:%Y-%m-%d}\n")
    print("| Group | Reading | Half | Weeks | Avg BTC next 4 weeks | Up % |")
    print("|---|---|---|---|---|---|")
    for gi, name in ((1, "Asset managers net"), (2, "Leveraged funds net")):
        xs = [r[gi] for r in data]
        buckets = {}
        for i, r in enumerate(data):
            p = pct_rank(xs, i)
            if p is None:
                continue
            t0, p0 = px_on_or_after(r[0])
            t1, p1 = px_on_or_after(r[0] + dt.timedelta(days=28))
            if p0 is None or p1 is None or t1 == t0:
                continue
            half = "2018-21" if r[0] < e.CUT else "2022-now"
            tier = "high (top third)" if p >= 2 / 3 else "low (bottom third)" if p <= 1 / 3 else "middle"
            buckets.setdefault((tier, half), []).append(p1 / p0 - 1)
            buckets.setdefault(("all weeks", half), []).append(p1 / p0 - 1)
        for tier in ("high (top third)", "middle", "low (bottom third)", "all weeks"):
            for half in ("2018-21", "2022-now"):
                v = buckets.get((tier, half), [])
                if v:
                    print(f"| {name} | {tier} | {half} | {len(v)} | {sum(v) / len(v) * 100:+.1f}% | "
                          f"{sum(1 for x in v if x > 0) / len(v) * 100:.0f}% |")


if __name__ == "__main__":
    main()
