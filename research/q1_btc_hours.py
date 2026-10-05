"""
Q1: Bitcoin 21:00-23:00 UTC seasonality (Quantpedia). Rules fixed beforehand in research/IDEAS_PLAN.md.

Run:
  python research/q1_btc_hours.py        # writes research/Q1_BTC_HOURS.md
"""
import datetime as dt
import math
import os
import sys
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import engine as e  # noqa: E402
import hourly as hr  # noqa: E402

UTC = dt.timezone.utc
DAY = 86400000
OOS = dt.datetime(2023, 7, 1, tzinfo=UTC)


def vol_ok(bars):
    """{day ms: True if the 30-day volatility of daily returns (days before) is above its 1-year median}."""
    close = {}
    for b in bars:
        close[b["ts"] - b["ts"] % DAY] = b["c"]
    days = sorted(close)
    rets = [math.log(close[days[i]] / close[days[i - 1]]) for i in range(1, len(days))]
    vol = [None] * len(days)
    for i in range(31, len(days)):
        w = rets[i - 31:i - 1]
        m = sum(w) / 30
        vol[i] = math.sqrt(sum((x - m) ** 2 for x in w) / 29)
    out = {}
    for i in range(len(days)):
        hist = [v for v in vol[max(0, i - 365):i] if v is not None]
        out[days[i]] = vol[i] is not None and len(hist) >= 180 and vol[i] > median(hist)
    return out


def sim(bars, t0, t1, fee, mode):
    t1 = t1 or e.now()
    vok = vol_ok(bars) if mode == "Q1b" else None
    idx = {b["ts"]: k for k, b in enumerate(bars)}
    eq, curve, trades = 1000.0, [], []
    for k, b in enumerate(bars):
        if not (e.ms(t0) <= b["ts"] < e.ms(t1)):
            continue
        d = dt.datetime.fromtimestamp(b["ts"] / 1000, UTC)
        curve.append((b["ts"], eq))
        if d.hour != 21:
            continue
        if mode == "Q1c" and d.weekday() not in (3, 4):
            continue
        if mode == "Q1b" and not vok.get(b["ts"] - b["ts"] % DAY - DAY, False):
            continue
        k2 = idx.get(b["ts"] + 3600000)
        if k2 is None:
            continue
        units = eq / (1 + fee) / b["o"]
        curve.append((b["ts"] + 1, units * b["c"] * (1 - fee)))  # mark to market after the first hour
        out = units * bars[k2]["c"] * (1 - fee)
        trades.append({"pnl": out - eq})
        eq = out
    won = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    lost = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    curve.append((e.ms(t1), eq))
    ret, dd, rd = e.ret_dd(curve)
    return {"trades": len(trades), "ret": ret, "dd": dd, "pf": won / lost if lost else float("inf"), "won": won,
            "lost": lost, "pnl": eq - 1000, "curve": curve,
            "win": sum(t["pnl"] > 0 for t in trades) / len(trades) * 100 if trades else 0}


def main():
    data = {c: hr.hourly(c) for c in ("BTC", "ETH", "XRP")}
    base = e.baseline()
    b_ret, b_dd, b_rd = e.ret_dd(base["mix"])
    periods = [("1st half (2018-05 to 2021)", e.START, e.CUT), ("2nd half (2022-now)", e.CUT, None),
               ("never published (2023-07 to now)", OOS, None)]
    lines = ["# Q1 Bitcoin 21:00-23:00 UTC seasonality", "", "Rules fixed beforehand in research/IDEAS_PLAN.md. Binance 1H, "
             "full balance for 2 hours a day. Script: research/q1_btc_hours.py.", "",
             "| Variant | Cost each side | Period | Trades | Win % | Return | Max DD | PF |", "|---|---|---|---|---|---|---|---|"]
    verdicts = []
    for mode, label in (("Q1a", "Q1a every day"), ("Q1b", "Q1b high volatility only"), ("Q1c", "Q1c Thu + Fri only")):
        why = []
        for fee in (0.001, 0.0002):
            for pname, t0, t1 in periods:
                r = sim(data["BTC"], t0, t1, fee, mode)
                lines.append(f"| {label} | {fee * 100:g}% | {pname} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | "
                             f"{r['dd']:.1f}% | {r['pf']:.2f} |")
                if fee == 0.001:
                    if r["pnl"] <= 0:
                        why.append(f"loses in {pname}")
                    if r["dd"] < -10 and not pname.startswith("never"):
                        why.append(f"DD {r['dd']:.1f}% in {pname}")
        for pname, t0, t1 in periods[:2]:
            rs = [sim(data[c], t0, t1, 0.001, mode) for c in ("ETH", "XRP")]
            won, lost = sum(r["won"] for r in rs), sum(r["lost"] for r in rs)
            pf = won / lost if lost else float("inf")
            lines.append(f"| {label} | 0.1% | ETH + XRP pooled, {pname} | {sum(r['trades'] for r in rs)} | | "
                         f"P/L {sum(r['pnl'] for r in rs):+.0f} USD | worst {min(r['dd'] for r in rs):.1f}% | {pf:.2f} |")
            if not pf > 1:
                why.append(f"ETH + XRP PF {pf:.2f} in {pname}")
        full = sim(data["BTC"], e.START, None, 0.001, mode)
        cr = e.corr(e.monthly(full["curve"]), e.monthly(base["mix"]))
        n_ret, n_dd, n_rd = e.ret_dd(e.combine([base["v4"], base["tr"], full["curve"]], [1 / 3] * 3))
        if not cr < 0.5:
            why.append(f"correlation {cr:.2f}")
        if not n_rd > b_rd:
            why.append(f"portfolio return/DD {n_rd:.2f} not above {b_rd:.2f}")
        verdicts.append(f"- {label}: correlation {cr:.2f}, portfolio return/DD {n_rd:.2f} vs {b_rd:.2f}. "
                        + ("PASS" if not why else "fail: " + "; ".join(why)))
        print(f"done {label}", flush=True)
    lines += [""] + verdicts
    with open(os.path.join(HERE, "Q1_BTC_HOURS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
