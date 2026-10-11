"""
Checks Jeff's own paper trades (journal/jeff_paper_trades.csv) against real candles: did the stop or the target get hit?
Read-only: it never trades. Prices = OKX 5m candles (what Jeff's TradingView chart shows). Results are scored at
Binance.US costs (Jeff trades there): limit entry and target 0%, a stop-out pays 0.02% taker + 0.02% slippage.

  open trade          -> stop or target hit? (both inside one 5m candle = counted as the stop, the safe way)
  "limit waiting"     -> filled once price trades to the entry, then checked like an open trade
When a trade closes it fills in status / exit / result_R and writes the details (time in trade, best and worst point
in R) to the lesson column, then posts a note on issue #4 (GH_TOKEN set, GitHub Actions only).

  python tools/jeff_paper_check.py
"""
import csv
import datetime as dt
import json
import os
import subprocess
import sys
import urllib.request

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "journal", "jeff_paper_trades.csv")
ET = dt.timezone(dt.timedelta(hours=-4))  # EDT (Oct 2026)
STOP_COST = 0.0004
BARS = {"5m": "5m", "15m": "15m", "1H": "1H", "4H": "4H"}
sys.path.insert(0, os.path.join(HERE, "research"))


def candles(inst, since_ms):
    """confirmed 5m candles from since_ms to now, oldest first: (ts, h, l, c)"""
    out, after = {}, ""
    for _ in range(40):
        url = f"https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar=5m&limit=100{after}"
        req = urllib.request.Request(url, headers={"User-Agent": "jeff-paper-check"})
        data = json.load(urllib.request.urlopen(req, timeout=20))["data"]
        if not data:
            break
        for r in data:
            if r[8] == "1":
                out[int(r[0])] = (int(r[0]), float(r[2]), float(r[3]), float(r[4]))
        oldest = min(int(r[0]) for r in data)
        if oldest <= since_ms:
            break
        after = f"&after={oldest}"
    return [out[k] for k in sorted(out) if k >= since_ms]


def code_view(t):
    """what the structure code (research/jeff_struct.py, swing 1) saw on the trade's chart when Jeff entered"""
    from jeff_struct import Heart
    inst = t["coin"] if t["coin"].endswith("USDT") else t["coin"] + "T"
    start = dt.datetime.strptime(t["date_et"].replace("~", ""), "%Y-%m-%d %H:%M").replace(tzinfo=ET)
    t0 = int(start.timestamp() * 1000)
    rows, after = {}, f"&after={t0}"  # only candles that had closed before Jeff entered
    for _ in range(3):
        url = f"https://www.okx.com/api/v5/market/history-candles?instId={inst}&bar={BARS[t['tf']]}&limit=100{after}"
        data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "x"}), timeout=20))["data"]
        if not data:
            break
        for r in data:
            rows[int(r[0])] = r
        after = f"&after={min(int(r[0]) for r in data)}"
    d = [rows[k] for k in sorted(rows)]
    h, l, c = ([float(r[i]) for r in d] for i in (2, 3, 4))
    s, evs = Heart(h, l, c, 1), []
    for k in range(len(d)):
        ev = s.step(k)
        if ev and ev.split()[0] in ("BOS", "MS", "sweep", "fuel", "start"):
            evs.append(f"{ev} {dt.datetime.fromtimestamp(int(d[k][0]) / 1000, ET):%m-%d %H:%M}")
    if not s.trend:
        return "code: no structure yet"
    lo, hi = s.rng
    mid, e = (lo + hi) / 2, float(t["entry"])
    zone = "premium" if e > mid else "discount"
    return (f"code at entry ({t['tf']}): leg {'UP' if s.trend == 1 else 'DOWN'}, MUST HOLD {s.strong}, leg {'high' if s.trend == 1 else 'low'} "
            f"{s.weak}, 50% {mid:.6g}, entry in {zone}; last events: " + "; ".join(evs[-3:]))


def check(t):
    side = 1 if t["side"] == "long" else -1
    e, stop, tgt = float(t["entry"]), float(t["stop"]), float(t["target"])
    r = abs(e - stop)
    start = dt.datetime.strptime(t["date_et"].replace("~", ""), "%Y-%m-%d %H:%M").replace(tzinfo=ET)
    inst = t["coin"] if t["coin"].endswith("USDT") else t["coin"] + "T"  # Bitstamp ETH-USD -> OKX ETH-USDT (close enough)
    bars = candles(inst, int(start.timestamp() * 1000) - 300000)
    filled = not t["status"].startswith("sell limit") and not t["status"].startswith("buy limit")
    best = worst = 0.0
    for ts, h, l, c in bars:
        if not filled:
            if (side == -1 and h >= e) or (side == 1 and l <= e):
                filled, fill_ts = True, ts
            else:
                continue
        fav = (e - l) if side == -1 else (h - e)
        adv = (h - e) if side == -1 else (e - l)
        best, worst = max(best, fav / r), max(worst, adv / r)
        hit_stop = h >= stop if side == -1 else l <= stop
        hit_tgt = l <= tgt if side == -1 else h >= tgt
        if hit_stop or hit_tgt:
            win = hit_tgt and not hit_stop
            res = abs(tgt - e) / r if win else -1 - STOP_COST * stop / r
            when = dt.datetime.fromtimestamp(ts / 1000, ET)
            hours = (ts - int(start.timestamp() * 1000)) / 3.6e6
            return {"status": f"{'target' if win else 'stopped'} {when:%m-%d %H:%M} ET", "exit": tgt if win else stop,
                    "result_R": f"{res:+.2f}",
                    "detail": f"{'WIN' if win else 'LOSS'} after {hours:.1f} h; best point {best:.2f}R, worst {worst:.2f}R"
                              + ("" if win else f"; price got {best:.2f}R toward the target before the stop")}
    if filled and t["status"].startswith(("sell limit", "buy limit")):
        return {"status": "open (limit filled)"}
    return None


def main():
    with open(CSV, newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys()) if rows else []
    closed = []
    if "code_view" not in fields:
        fields.append("code_view")
    for t in rows:
        if not t.get("code_view"):
            try:
                t["code_view"] = code_view(t)
            except Exception as ex:
                print(f"code view failed: {ex}")
        if not (t["status"].startswith("open") or "limit" in t["status"]):
            continue
        try:
            upd = check(t)
        except Exception as ex:  # network etc: try again next run
            print(f"{t['coin']} {t['date_et']}: check failed ({ex})")
            continue
        if not upd:
            print(f"{t['coin']} {t['side']} {t['date_et']}: still {t['status']}")
            continue
        t["status"] = upd["status"]
        if "exit" in upd:
            t["exit"], t["result_R"] = upd["exit"], upd["result_R"]
            t["lesson"] = (t["lesson"] + " | " if t["lesson"] else "") + upd["detail"]
            closed.append(t)
        print(f"{t['coin']} {t['side']} {t['date_et']}: {t['status']} {t.get('result_R', '')}")
    with open(CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    if closed and os.environ.get("GH_TOKEN"):
        msg = "Jeff's paper trade check (read-only, Binance.US costs):\n" + "\n".join(
            f"- {t['coin']} {t['tf']} {t['side']} from {t['date_et']} ET: {t['status']}, {t['result_R']}R. {t['lesson'].split(' | ')[-1]}"
            for t in closed)
        subprocess.run(["gh", "issue", "comment", "4", "--body", msg], check=False)


if __name__ == "__main__":
    main()
