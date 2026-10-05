"""
Job 2b: long-history stress test and out-of-sample check.

Every bot strategy (SP-12 v4, SP-12 v2, Trend Rider) on every coin, as far back as free
public 4H data goes, using bot.py as it is now (0.5% risk, 0.1% fee each side) and bot.py's
own paper-mode functions bar by bar. Each coin is tested on its own with a fresh $1,000 in
each market period, so periods and coins don't leak into each other.

Data (one source per coin, whichever goes back furthest; 4H candles, daily built from them):
  Bitfinex public API      api-pub.bitfinex.com  (USD pairs; hours with no trades are filled
                                                  with flat candles at the last close)
  Binance public archive   data.binance.vision   (USDT pairs, monthly files, keeps delisted coins)
Downloads are cached in research/.cache/ (not committed).

Run:
  python research/long_history.py            # writes research/LONG_HISTORY.md
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402

CACHE = os.path.join(HERE, ".cache")
H4 = bot.H4_MS
UTC = dt.timezone.utc

# coin -> (source, symbol)
SOURCES = {
    "BTC": ("bitfinex", "tBTCUSD"), "ETH": ("bitfinex", "tETHUSD"), "XRP": ("bitfinex", "tXRPUSD"),
    "LTC": ("bitfinex", "tLTCUSD"), "XLM": ("bitfinex", "tXLMUSD"), "AVAX": ("bitfinex", "tAVAX:USD"),
    "SUI": ("bitfinex", "tSUIUSD"), "XAUT": ("bitfinex", "tXAUT:USD"),
    "SOL": ("binance", "SOLUSDT"), "BNB": ("binance", "BNBUSDT"), "DOGE": ("binance", "DOGEUSDT"),
    "ADA": ("binance", "ADAUSDT"), "LINK": ("binance", "LINKUSDT"), "BCH": ("binance", "BCHUSDT"),
    "LUNA": ("binance", "LUNAUSDT"), "FTT": ("binance", "FTTUSDT"),
}

# strategy -> (label, coins the live bot trades (in-sample), how to analyse, extra position fields)
STRATS = {
    "v4": ("SP-12 v4", ["BTC", "ETH", "XRP", "SOL"],  # SOL was tested and dropped, so it counts as seen
           lambda bars, daily: bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v4"]), lambda x: {}),
    "v2": ("SP-12 v2", ["ETH", "SOL", "XAUT"],
           lambda bars, daily: bot.analyse_sp(bars, daily, bot.SP_SETTINGS["v2"]), lambda x: {}),
    "tr": ("Trend Rider", ["BTC", "ETH", "SOL", "BNB", "SUI"],
           lambda bars, daily: bot.analyse_tr(bars, daily, 5), lambda x: {"hi": x["c"]}),
    "tr3": ("Trend Rider (gold, pivot 3)", ["XAUT"],
            lambda bars, daily: bot.analyse_tr(bars, daily, 3), lambda x: {"hi": x["c"]}),
}
# Binance reused LUNAUSDT for the new Terra 2.0 coin from 2022-05-31; stop at the old coin's death
END = {"LUNA": "2022-05-13"}

CURRENT = {"v4": ["BTC", "ETH", "XRP"], "v2": ["ETH", "SOL", "XAUT"], "tr": ["BTC", "ETH", "SOL", "BNB", "SUI"],
           "tr3": ["XAUT"]}
OUT_OF_SAMPLE = ["LTC", "DOGE", "XLM", "ADA", "BNB", "LINK", "BCH", "AVAX", "SUI", "LUNA", "FTT"]


def d(y, m=1, day=1):
    return dt.datetime(y, m, day, tzinfo=UTC)


PERIODS = [("2013-14 bubble + crash", d(2013), d(2015)), ("2015-17 bull", d(2015), d(2018)),
           ("2018 crash", d(2018), d(2019)), ("2019-21 bull", d(2019), d(2022)),
           ("2022 crash", d(2022), d(2023)), ("2023-now", d(2023), None)]


def ms(x):
    return int(x.timestamp() * 1000)


# ───────── data ─────────
def http(url, tries=10):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research"}),
                                        timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(65 if e.code == 429 else 5 * (k + 1))  # Bitfinex: about 30 candle requests a minute
        except Exception:
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"download failed: {url}")


def bitfinex(sym):
    rows, start = [], 1356998400000  # 2013-01-01
    while True:
        raw = json.loads(http(f"https://api-pub.bitfinex.com/v2/candles/trade:4h:{sym}/hist"
                              f"?limit=10000&sort=1&start={start}"))
        if raw and raw[0] == "error":  # rate limit
            time.sleep(30)
            continue
        if not raw:
            break
        rows += [{"ts": x[0], "o": x[1], "c": x[2], "h": x[3], "l": x[4], "v": x[5]} for x in raw]
        if len(raw) < 10000:
            break
        start = raw[-1][0] + 1
        time.sleep(4)
    time.sleep(4)
    return rows


def binance(sym):
    rows, y, m = [], 2017, 7
    now = dt.datetime.now(UTC)
    while (y, m) < (now.year, now.month):
        blob = http(f"https://data.binance.vision/data/spot/monthly/klines/{sym}/4h/{sym}-4h-{y}-{m:02d}.zip")
        if blob:
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                for x in csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))):
                    if not x[0].isdigit():
                        continue
                    ts = int(x[0])
                    ts = ts // 1000 if ts > 10 ** 14 else ts  # newer files use microseconds
                    rows.append({"ts": ts, "o": float(x[1]), "h": float(x[2]), "l": float(x[3]),
                                 "c": float(x[4]), "v": float(x[5])})
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return rows


def fill_gaps(rows):
    """One candle every 4 hours; a missing candle (no trades) becomes a flat one at the last close."""
    rows = sorted({r["ts"]: r for r in rows}.values(), key=lambda r: r["ts"])
    out = []
    for r in rows:
        while out and r["ts"] - out[-1]["ts"] > H4:
            p = out[-1]["c"]
            out.append({"ts": out[-1]["ts"] + H4, "o": p, "h": p, "l": p, "c": p, "v": 0.0})
        out.append(r)
    for r in out:
        r["confirm"] = True
    return out


def to_daily(bars):
    days = {}
    for b in bars:
        k = b["ts"] - b["ts"] % 86400000
        if k not in days:
            days[k] = {"ts": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "v": b["v"], "n": 1}
        else:
            x = days[k]
            x["h"], x["l"], x["c"], x["v"], x["n"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"], x["v"] + b["v"], x["n"] + 1
    out = [x for x in days.values() if x["n"] == 6]
    for x in out:
        x["confirm"] = True
    return sorted(out, key=lambda x: x["ts"])


def load(coin):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"{coin}.json")
    if os.path.exists(path):
        with open(path) as f:
            bars = json.load(f)
    else:
        src, sym = SOURCES[coin]
        print(f"downloading {coin} from {src} ...", flush=True)
        bars = fill_gaps(bitfinex(sym) if src == "bitfinex" else binance(sym))
        # drop the still-forming candle
        bars = [b for b in bars if b["ts"] + H4 <= time.time() * 1000]
        with open(path, "w") as f:
            json.dump(bars, f)
    # listing glitches: drop leading candles whose open / high is far from their close (SUI opened at 10,000)
    while bars and (bars[0]["o"] > 3 * bars[0]["c"] or bars[0]["h"] > 3 * bars[0]["c"]
                    or bars[0]["o"] < bars[0]["c"] / 3):
        bars = bars[1:]
    if coin in END:
        cut = ms(dt.datetime.fromisoformat(END[coin]).replace(tzinfo=UTC))
        bars = [b for b in bars if b["ts"] < cut]
    return bars, to_daily(bars)


# ───────── simulation ─────────
def simulate(strat, bars, a, t0, t1):
    """One coin, its own $1,000, trades opened in [t0, t1); an open trade is closed at t1."""
    b = {"id": "lh", "name": "lh", "strat": "v2" if strat == "v2" else ("tr" if strat.startswith("tr") else "v4"),
         "venue": "okx", "mode": "paper", "coins": ["X"], "equity": 1000.0}
    bs = {"equity": 1000.0, "positions": {}, "last_bar": {}}
    extra = STRATS[strat][3]
    trades, cur = [], {}

    def log_trade(_bot, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
        if side == "buy":
            cur["t"] = {"pnl": 0.0, "entry": cur["ts"]}
            trades.append(cur["t"])
        else:
            cur["t"]["pnl"] += pnl
            cur["t"]["exit"] = cur["ts"]
    bot.log_trade, bot.log = log_trade, lambda *x: None

    ks = [k for k, x in enumerate(bars) if ms(t0) <= x["ts"] < ms(t1)]
    if not ks:
        return None
    peak, low, low_ts, mtm = 1000.0, 0.0, None, 1000.0
    entry_k = None
    for k in ks:
        x = bars[k]
        cur["ts"] = x["ts"]
        if "X" in bs["positions"] and x["ts"] > bs["positions"]["X"]["entry_ts"]:
            if not bot.check_hit(None, b, bs, "X", x):
                bot.manage_on_close(None, b, bs, "X", a, k, x, k - entry_k)
        if "X" not in bs["positions"] and a["signal"][k]:
            bot.open_position(None, b, bs, "X", x, a["info"][k], extra(x))
            entry_k = k
        mtm = bs["equity"]
        if "X" in bs["positions"]:
            p = bs["positions"]["X"]
            mtm += p["qty"] * x["c"] * (1 - bot.FEE) - p["cost"]
        if mtm > peak:
            peak = mtm
        if mtm / peak - 1 < low:
            low, low_ts = mtm / peak - 1, x["ts"]
    if "X" in bs["positions"]:
        cur["ts"] = bars[ks[-1]]["ts"]
        bot.close_position(None, b, bs, "X", "end of test", bars[ks[-1]]["c"])

    first, last = bars[ks[0]], bars[ks[-1]]
    hpeak, hdd = 0.0, 0.0
    for k in ks:
        hpeak = max(hpeak, bars[k]["c"])
        hdd = min(hdd, bars[k]["c"] / hpeak - 1)
    won = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    lost = -sum(t["pnl"] for t in trades if t["pnl"] < 0)
    total = bs["equity"] - 1000
    month = defaultdict(float)
    for t in trades:
        month[bot.ts_iso(t.get("exit", t["entry"]))[:7]] += t["pnl"]
    best_m = max(month.items(), key=lambda kv: kv[1]) if month else (None, 0)
    streak = run = 0
    for t in trades:
        run = run + 1 if t["pnl"] <= 0 else 0
        streak = max(streak, run)
    return {"trades": len(trades), "win": sum(t["pnl"] > 0 for t in trades) / len(trades) * 100 if trades else 0,
            "ret": total / 10, "dd": low * 100, "dd_when": bot.ts_iso(low_ts)[:7] if low_ts else "",
            "pf": won / lost if lost else (float("inf") if won else 0),
            "bh": last["c"] / first["o"] * 100 - 100, "bh_dd": hdd * 100,
            "best_share": best_m[1] / total * 100 if total > 0 else None, "best_month": best_m[0],
            "streak": streak, "from": bot.ts_iso(first["ts"])[:10], "won": won, "lost": lost, "pnl": total,
            "trade_pnls": [t["pnl"] for t in trades]}


def fmt_row(label, coin, pname, r):
    pf = "inf" if r["pf"] == float("inf") else f"{r['pf']:.2f}"
    best = f"{r['best_share']:.0f}% ({r['best_month']})" if r["best_share"] is not None else "-"
    flag = " **>10%**" if r["dd"] < -10 else ""
    return (f"| {label} | {coin} | {pname} | {r['trades']} | {r['win']:.0f}% | {r['ret']:+.1f}% | "
            f"{r['dd']:.1f}%{flag} | {pf} | {r['bh']:+.0f}% | {r['bh_dd']:.0f}% | {best} | {r['streak']} |")


HEAD = ("| Bot | Coin | Period | Trades | Win % | Return | Max DD | PF | B&H return | B&H DD | "
        "Best month share of profit | Longest losing streak |\n|---|---|---|---|---|---|---|---|---|---|---|---|")


def main():
    coins = sorted(set(SOURCES))
    data = {}
    for c in coins:
        bars, daily = load(c)
        if bars:
            data[c] = (bars, daily)
    now = dt.datetime.now(UTC)
    results = {}  # (strat, coin, period) -> result
    for strat, (label, seen, analyse, _) in STRATS.items():
        test_coins = ["XAUT"] if strat == "tr3" else [c for c in coins if c != "XAUT" or strat == "v2"]
        for c in test_coins:
            if c not in data:
                continue
            bars, daily = data[c]
            a = analyse(bars, daily)
            for pname, t0, t1 in PERIODS:
                t1 = t1 or now
                if bars[0]["ts"] >= ms(t1) or bars[-1]["ts"] < ms(t0):
                    continue
                r = simulate(strat, bars, a, max(t0, dt.datetime.fromtimestamp(bars[0]["ts"] / 1000, UTC)), t1)
                if r and r["trades"]:
                    results[(strat, c, pname)] = r
                elif r:
                    results[(strat, c, pname)] = r
        print(f"done {label}", flush=True)

    out = ["# Long-history stress test (job 2b)", "",
           f"Run {now:%Y-%m-%d}. bot.py as it is now: {bot.RISK_PCT * 100:g}% risk per trade, 0.1% fee each side, "
           "bot.py's own paper-mode functions bar by bar. One coin at a time, fresh $1,000 each period. "
           "Max DD is mark-to-market at each 4H close. Script: research/long_history.py.", "",
           "## Data", "", "| Coin | Source | Pair | First 4H candle | Last |", "|---|---|---|---|---|"]
    for c in coins:
        if c in data:
            src, sym = SOURCES[c]
            out.append(f"| {c} | {src} | {sym} | {bot.ts_iso(data[c][0][0]['ts'])[:10]} | "
                       f"{bot.ts_iso(data[c][0][-1]['ts'])[:10]} |")
    out += ["", "LUNA is the original Terra coin only, cut at 2022-05-13 (Binance later reused the ticker "
            "for Terra 2.0). Binance coins end at the last full month. SUI's first Bitfinex candle (open 10,000) "
            "was dropped as a listing glitch.", "",
            "A period that starts before a coin's first candle starts at that first candle (see the B&H "
            "return for that partial period). Early years are thin, wild markets: a stress test, not proof.", ""]

    def table(title, keys):
        rows = [fmt_row(STRATS[s][0], c, p, results[(s, c, p)]) for s, c, p in keys if (s, c, p) in results]
        return [f"## {title}", "", HEAD] + rows + [""]

    cur_keys = [(s, c, p) for s in STRATS for c in CURRENT[s] for p, _, _ in PERIODS]
    oos_keys = [(s, c, p) for s in ("v4", "v2", "tr") for c in OUT_OF_SAMPLE if c not in STRATS[s][1]
                for p, _, _ in PERIODS]
    out += table("Coins the bots trade now (in-sample)", cur_keys)
    out += table("Coins the bots were never built for (out-of-sample)", oos_keys)

    # roll-ups
    def roll(keys):
        rs = [results[k] for k in keys if k in results and results[k]["trades"]]
        if not rs:
            return "no trades"
        pos = sum(r["ret"] > 0 for r in rs)
        brk = sum(r["dd"] < -10 for r in rs)
        med = sorted(r["ret"] for r in rs)[len(rs) // 2]
        pfs = sorted(r["pf"] for r in rs)[len(rs) // 2]
        return (f"{len(rs)} coin-periods, {pos} profitable ({pos / len(rs) * 100:.0f}%), median return {med:+.1f}%, "
                f"median PF {pfs:.2f}, {brk} broke 10% DD")
    out += ["## Roll-up", ""]
    for s in ("v4", "v2", "tr", "tr3"):
        out.append(f"- {STRATS[s][0]}, in-sample: " + roll([k for k in cur_keys if k[0] == s]))
        if s != "tr3":
            out.append(f"- {STRATS[s][0]}, out-of-sample: " + roll([k for k in oos_keys if k[0] == s]))
    out.append("")
    for s in ("v4", "v2", "tr"):
        for p, _, _ in PERIODS:
            ins = roll([k for k in cur_keys if k[0] == s and k[2] == p])
            oos = roll([k for k in oos_keys if k[0] == s and k[2] == p])
            out.append(f"- {STRATS[s][0]} {p}: in-sample {ins}; out-of-sample {oos}")
    with open(os.path.join(HERE, "LONG_HISTORY.md"), "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out[-40:]))


if __name__ == "__main__":
    main()
