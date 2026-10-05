"""
H3 news guard: no new trades whose 4H decision candle closes near a US high-impact event (FOMC, CPI,
Non-Farm Payrolls). Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md.
Event list: research/events_us.json (sources inside the file).

Run:
  python research/h3_news.py        # writes research/H3_NEWS.md
"""
import bisect
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402
import engine as e  # noqa: E402

H = 3600 * 1000


def events():
    with open(os.path.join(HERE, "events_us.json")) as f:
        return sorted(int(dt.datetime.fromisoformat(x["utc"]).replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
                      for x in json.load(f)["events"])


def guarded_specs(before_h, after_h):
    ev = events()

    def blocked(close_ms):
        # an event between close - after and close + before blocks the entry
        i = bisect.bisect_left(ev, close_ms - after_h * H)
        return i < len(ev) and ev[i] <= close_ms + before_h * H

    specs = []
    for name, strat, coins, data, analyse, extra in e.demo_specs():
        def an(bars, daily, analyse=analyse):
            a = analyse(bars, daily)
            if before_h is None:
                return a
            return {**a, "signal": [s and not blocked(b["ts"] + bot.H4_MS) for s, b in zip(a["signal"], bars)]}
        specs.append((name, strat, coins, data, an, extra))
    return specs


def main():
    versions = {"no guard": (None, None), "G1: 4h before to 4h after": (4, 4), "G2: 12h before to 12h after": (12, 12),
                "G3: 24h before to 4h after": (24, 4)}
    res = {}
    for name, (b, a) in versions.items():
        specs = guarded_specs(b, a)
        res[name] = {}
        for h, t0, t1 in e.HALVES:
            r = e.multi_sim(specs, t0, t1)
            ret, dd, rd = e.ret_dd(r["combined"])
            res[name][h] = {"ret": ret, "dd": dd, "rd": rd, "n": sum(x["trades"] for x in r["bots"].values())}
        print(f"done {name}", flush=True)
    base = res["no guard"]
    lines = ["# H3 news guard", "", "Variants and pass rules fixed beforehand in research/HELPERS_PLAN.md. v4 + Trend Rider "
             "as they trade, $1,000 each. Events: research/events_us.json (FOMC, CPI, NFP since 2018). "
             "Script: research/h3_news.py.", "",
             "| Version | Half | Trades | Combined return | Combined max DD | Return/DD | Pass? |", "|---|---|---|---|---|---|---|"]
    for name in versions:
        ok = name != "no guard" and all(res[name][h]["rd"] > base[h]["rd"] and res[name][h]["ret"] >= 0.9 * base[h]["ret"]
                                        for h in base)
        for h, _, _ in e.HALVES:
            r = res[name][h]
            lines.append(f"| {name} | {h} | {r['n']} | {r['ret']:+.1f}% | {r['dd']:.1f}% | {r['rd']:.2f} | "
                         f"{'-' if name == 'no guard' else ('PASS' if ok else 'fail')} |")
    with open(os.path.join(HERE, "H3_NEWS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
