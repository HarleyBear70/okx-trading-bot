"""
Claude's own paper trader (Jeff, Oct 11 2026: "i want you trade and learn ... guessing only loses trades").
PAPER ONLY: never sends an order anywhere. Rules are CLAUDE'S, not Jeff's (built from his heartbeat structure and
Brad's top-down blueprint). Called from tools/heartbeat_watch.py every 15 min.

  Read top-down: 4H, 1H and 15m heartbeat legs all point the same way          -> bias
  Trigger:       the 5m makes a market shift (MS) in the bias direction          -> set a limit order
  Entry:         limit at the 50% of the new 5m leg (discount for a long, premium for a short)
  Stop:          past the 5m MUST HOLD (the new leg's start) + 0.05%
  Target:        2R
  Cancel:        price reaches the target first, the 5m shifts back the other way, the bias breaks, or 2 h unfilled
  One trade per coin. Costs at Binance.US: limit entry/target 0%, a stop pays 0.02% taker + 0.02% slippage.
  Paper account $1,000, risk 1% ($10) per trade. Shorts count as paper shorts (on Binance.US spot = selling held coins).

  Learning data saved with each trade: the bias, 1D direction, where the entry sat in the 15m leg (premium/discount),
  best and worst point in R, time in trade. journal/claude_hb_trades.csv, state in journal/claude_hb_state.json.
"""
import csv
import datetime as dt
import json
import os
import subprocess

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRADES = os.path.join(HERE, "journal", "claude_hb_trades.csv")
STATE = os.path.join(HERE, "journal", "claude_hb_state.json")
ET = dt.timezone(dt.timedelta(hours=-4))
START, RISK, GAP, TGT_R, STOP_COST, MAX_WAIT = 1000.0, 0.01, 0.0005, 2.0, 0.0004, 24
COLS = ["coin", "side", "signal_et", "fill_et", "exit_et", "entry", "stop", "target", "result", "result_R", "pnl_usd",
        "best_R", "worst_R", "hours", "bias_4H_1H_15m", "day_1D", "entry_in_15m", "note"]

try:
    with open(STATE) as f:
        st = json.load(f)
except (OSError, ValueError):
    st = {"balance": START, "coins": {}}
closed_now = []


def et(ms):
    return dt.datetime.fromtimestamp(ms / 1000, ET).strftime("%Y-%m-%d %H:%M")


def leg_at(state_at, run, t):
    s = state_at(run[1], t)
    return s.split()[0] if s else ""


def finish(coin, o, ms, kind, px):
    side = 1 if o["side"] == "long" else -1
    r = abs(o["entry"] - o["stop"])
    res = side * (px - o["entry"]) / r - (STOP_COST * px / r if kind == "stop" else 0)
    usd = res * RISK * st["balance"]
    st["balance"] += usd
    row = {"coin": coin, "side": o["side"], "signal_et": et(o["sig"]), "fill_et": et(o["fill"]), "exit_et": et(ms),
           "entry": o["entry"], "stop": o["stop"], "target": o["target"], "result": "WIN" if kind == "target" else "LOSS",
           "result_R": f"{res:+.2f}", "pnl_usd": f"{usd:+.2f}", "best_R": f"{o['best']:.2f}", "worst_R": f"{o['worst']:.2f}",
           "hours": f"{(ms - o['fill']) / 3.6e6:.1f}", "bias_4H_1H_15m": o["bias"], "day_1D": o["day"],
           "entry_in_15m": o["z15"], "note": ""}
    exists = os.path.exists(TRADES)
    with open(TRADES, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if not exists:
            w.writeheader()
        w.writerow(row)
    closed_now.append(row)


def step(coin, runs, state_at):
    if not all(k in runs for k in ("4H", "1H", "15m", "5m")):
        return []
    evs, _, _, _, d = runs["5m"]
    cs = st["coins"].setdefault(coin, {"last": 0, "order": None})
    size = 300000
    if not cs["last"]:  # first run: start from the newest candle, no back-filling
        cs["last"] = int(d[-1][0]) + size
    ev_at = {t: (e, c, s) for t, e, c, s in evs}
    for r in d:
        t = int(r[0]) + size
        if t <= cs["last"]:
            continue
        h, l = float(r[2]), float(r[3])
        o = cs["order"]
        bias = [leg_at(state_at, runs[x], t) for x in ("4H", "1H", "15m")]
        if o:
            up = o["side"] == "long"
            if o["fill"] is None:
                want = "UP" if up else "DOWN"
                if (l <= o["entry"]) if up else (h >= o["entry"]):
                    o["fill"] = t - size
                elif ((h >= o["target"]) if up else (l <= o["target"])) or any(b != want for b in bias) \
                        or (t - o["sig"]) / size > MAX_WAIT:
                    cs["order"] = o = None
            if o and o["fill"] is not None:
                r1 = abs(o["entry"] - o["stop"])
                fav, adv = ((h - o["entry"]), (o["entry"] - l)) if up else ((o["entry"] - l), (h - o["entry"]))
                o["best"], o["worst"] = max(o["best"], fav / r1), max(o["worst"], adv / r1)
                if (l <= o["stop"]) if up else (h >= o["stop"]):
                    finish(coin, o, t, "stop", o["stop"])
                    cs["order"] = o = None
                elif (h >= o["target"]) if up else (l <= o["target"]):
                    finish(coin, o, t, "target", o["target"])
                    cs["order"] = o = None
        x = ev_at.get(t)
        if x and x[0] in ("MS UP", "MS DOWN"):
            e, c, (leg, strong, weak) = x
            want = "UP" if e == "MS UP" else "DOWN"
            if o and o["fill"] is None and o["side"] != ("long" if want == "UP" else "short"):
                cs["order"] = o = None  # the 5m shifted back the other way: cancel the waiting order
            if not o and all(b == want for b in bias):
                up = want == "UP"
                entry = (strong + weak) / 2
                stop = strong * (1 - GAP) if up else strong * (1 + GAP)
                risk = abs(entry - stop)
                if risk > 0:
                    s15 = runs["15m"]
                    st15 = state_at(s15[1], t)
                    z = ""
                    i = max(k for k, y in enumerate(s15[1]) if y[0] <= t) if any(y[0] <= t for y in s15[1]) else None
                    if i is not None:
                        lg, sg, wk = s15[1][i][1]
                        lo, hi = (sg, wk) if lg == "UP" else (wk, sg)
                        z = "premium" if entry > (lo + hi) / 2 else "discount"
                    cs["order"] = {"side": "long" if up else "short", "sig": t, "fill": None, "entry": round(entry, 8),
                                   "stop": round(stop, 8), "target": round(entry + (TGT_R if up else -TGT_R) * risk, 8),
                                   "best": 0.0, "worst": 0.0, "bias": want, "day": leg_at(state_at, runs["1D"], t) if "1D" in runs else "",
                                   "z15": z, "ctx15": st15}
        cs["last"] = t
    o = cs["order"]
    if not o:
        return [f"Claude's paper trade: none open on {coin}.", ""]
    what = "waiting to fill" if o["fill"] is None else f"OPEN since {et(o['fill'])} ET, best {o['best']:.2f}R, worst {o['worst']:.2f}R"
    return [f"Claude's paper trade on {coin}: {o['side']} limit {o['entry']}, stop {o['stop']}, target {o['target']} "
            f"(signal {et(o['sig'])} ET), {what}.", ""]


def save():
    with open(STATE, "w") as f:
        json.dump(st, f, indent=1)
    if closed_now and os.environ.get("GH_TOKEN"):
        msg = "From terminal Claude: my own heartbeat paper trades (Claude's rules, paper only):\n" + "\n".join(
            f"- {r['coin']} {r['side']} {r['entry']} -> {r['result']} {r['result_R']}R (${r['pnl_usd']}), "
            f"{r['hours']} h, best {r['best_R']}R; bias {r['bias_4H_1H_15m']}, 1D {r['day_1D']}, entry in 15m {r['entry_in_15m']}"
            for r in closed_now) + f"\nPaper balance ${st['balance']:.2f} (started $1,000)."
        subprocess.run(["gh", "issue", "comment", "4", "--body", msg], check=False)
