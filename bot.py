"""
SP-12 v4 SAR demo bot for OKX (spot, DEMO ONLY).

A Python copy of the TradingView strategy "Structure Pullback (12-Check) v4 SAR"
using its default settings:
  4H candles, Tuned scoring (net score >= 2), swing strength 7,
  Propulsion trend filter (EMA 8 > 21 > 55), price above daily VWAP,
  stop = lowest low of 10 candles (1%..4% away), target = 3R (2%..15%),
  Parabolic SAR trailing stop once price has gone +1R (target removed),
  close the trade after 120 candles.
  Size: 1% risk of the bot's own $1,000 virtual account (like the
  strategy's initial_capital=1000), never more than the whole account.

GitHub Actions runs this every hour. It needs no libraries beyond Python.

Every private OKX request is sent with the demo header
"x-simulated-trading: 1", so this file cannot trade real money.
"""

import base64
import csv
import datetime as dt
import hashlib
import hmac
import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# ───────── Settings ─────────
COINS = [c.strip() for c in os.environ.get("BOT_COINS", "BTC-USDT,ETH-USDT,SOL-USDT,XRP-USDT").split(",") if c.strip()]
BASE_URL = os.environ.get("OKX_BASE_URL", "").strip() or "https://us.okx.com"
START_EQUITY = 1000.0      # strategy initial_capital
MIN_TUNED = 2              # Tuned: minimum net score
PIVOT_LEN = 7              # swing strength
RISK_PCT = 1.0             # risk per trade, % of bot equity
MAX_RISK = 4.0             # max stop distance %
MIN_RISK = 1.0             # min stop distance %
RR = 3.0                   # reward : risk
TP_MIN, TP_MAX = 2.0, 15.0 # take profit bounds %
MAX_BARS = 120             # time stop in candles
SAR_START, SAR_INC, SAR_MAX = 0.02, 0.02, 0.2
ORDER_PREFIX = "gh4"       # client order id prefix (Claude's old bot used "v4")

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
TRADES_FILE = os.path.join(HERE, "trades.csv")
H4_MS = 4 * 3600 * 1000


def log(*a):
    print(*a, flush=True)


# ───────── OKX REST ─────────
class OKX:
    def __init__(self, key, secret, passphrase, base=BASE_URL):
        self.key, self.secret, self.passphrase, self.base = key, secret, passphrase, base.rstrip("/")

    def _req(self, method, path, params=None, body=None, private=False):
        if params:
            path = path + "?" + urllib.parse.urlencode(params)
        data = json.dumps(body) if body is not None else ""
        headers = {"Content-Type": "application/json", "User-Agent": "sp12-bot"}
        if private:
            ts = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.") + \
                f"{dt.datetime.now(dt.timezone.utc).microsecond // 1000:03d}Z"
            sign = base64.b64encode(hmac.new(self.secret.encode(), (ts + method + path + data).encode(),
                                             hashlib.sha256).digest()).decode()
            headers.update({"OK-ACCESS-KEY": self.key, "OK-ACCESS-SIGN": sign,
                            "OK-ACCESS-TIMESTAMP": ts, "OK-ACCESS-PASSPHRASE": self.passphrase})
            headers["x-simulated-trading"] = "1"   # DEMO ONLY — never remove
        # (public candle data is the live market, same as the TradingView chart)
        for attempt in range(4):
            req = urllib.request.Request(self.base + path, data=data.encode() if data else None,
                                         headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    out = json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                txt = e.read().decode(errors="replace")
                if e.code == 429 and attempt < 3:
                    time.sleep(2 + attempt * 2)
                    continue
                raise RuntimeError(f"OKX HTTP {e.code} on {path}: {txt[:300]}")
            if out.get("code") not in ("0", 0):
                raise RuntimeError(f"OKX error on {path}: {json.dumps(out)[:400]}")
            return out["data"]
        raise RuntimeError(f"OKX rate limited on {path}")

    def get(self, path, params=None, private=False):
        return self._req("GET", path, params=params, private=private)

    def post(self, path, body):
        return self._req("POST", path, body=body, private=True)

    def candles(self, inst, bar, want):
        """Oldest->newest list of dicts. Includes the still-forming candle (confirm=False) at the end."""
        rows = self.get("/api/v5/market/candles", {"instId": inst, "bar": bar, "limit": 300})
        while len(rows) < want:
            more = self.get("/api/v5/market/history-candles",
                            {"instId": inst, "bar": bar, "after": rows[-1][0], "limit": 100})
            if not more:
                break
            rows += more
            time.sleep(0.15)
        out = [{"ts": int(r[0]), "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]),
                "v": float(r[5]), "confirm": r[8] == "1"} for r in rows]
        out.sort(key=lambda x: x["ts"])
        return out


# ───────── Pine-style indicators (lists, None = na) ─────────
def sma(src, n):
    out = [None] * len(src)
    for i in range(n - 1, len(src)):
        w = src[i - n + 1:i + 1]
        if None not in w:
            out[i] = sum(w) / n
    return out


def ema(src, n):
    out, a, prev = [None] * len(src), 2 / (n + 1), None
    for i in range(len(src)):
        if prev is None:
            if i >= n - 1 and None not in src[i - n + 1:i + 1]:
                prev = sum(src[i - n + 1:i + 1]) / n
                out[i] = prev
        else:
            prev = a * src[i] + (1 - a) * prev
            out[i] = prev
    return out


def rma(src, n):
    out, prev = [None] * len(src), None
    for i in range(len(src)):
        if prev is None:
            if i >= n - 1 and None not in src[i - n + 1:i + 1]:
                prev = sum(src[i - n + 1:i + 1]) / n
                out[i] = prev
        else:
            prev = (prev * (n - 1) + src[i]) / n
            out[i] = prev
    return out


def atr(h, l, c, n):
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, len(c))]
    return rma(tr, n)


def rsi(c, n=14):
    up = [None] + [max(c[i] - c[i - 1], 0) for i in range(1, len(c))]
    dn = [None] + [max(c[i - 1] - c[i], 0) for i in range(1, len(c))]
    ru, rd = rma(up[1:], n), rma(dn[1:], n)
    out = [None]
    for u, d in zip(ru, rd):
        if u is None:
            out.append(None)
        elif d == 0:
            out.append(100.0)
        elif u == 0:
            out.append(0.0)
        else:
            out.append(100 - 100 / (1 + u / d))
    return out


def supertrend(h, l, c, factor=3, period=10):
    """Returns direction list: -1 = up trend, 1 = down trend (TradingView convention)."""
    a = atr(h, l, c, period)
    n = len(c)
    lower, upper, st, d = [None] * n, [None] * n, [None] * n, [None] * n
    for i in range(n):
        if a[i] is None:
            continue
        src = (h[i] + l[i]) / 2
        lb, ub = src - factor * a[i], src + factor * a[i]
        pl = lower[i - 1] or 0.0 if i > 0 else 0.0
        pu = upper[i - 1] or 0.0 if i > 0 else 0.0
        lb = lb if (lb > pl or (i > 0 and c[i - 1] < pl)) else pl
        ub = ub if (ub < pu or (i > 0 and c[i - 1] > pu)) else pu
        lower[i], upper[i] = lb, ub
        if i == 0 or a[i - 1] is None:
            d[i] = 1
        elif st[i - 1] == pu:
            d[i] = -1 if c[i] > ub else 1
        else:
            d[i] = 1 if c[i] < lb else -1
        st[i] = lb if d[i] == -1 else ub
    return d


def psar(h, l, c, start, inc, mx):
    n = len(c)
    out = [None] * n
    result = max_min = acc = None
    is_below = None
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                is_below, max_min, result = True, h[1], l[0]
            else:
                is_below, max_min, result = False, l[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if is_below:
            if result > l[i]:
                first, is_below = True, False
                result, max_min, acc = max(h[i], max_min), l[i], start
        else:
            if result < h[i]:
                first, is_below = True, True
                result, max_min, acc = min(l[i], max_min), h[i], start
        if not first:
            if is_below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if l[i] < max_min:
                    max_min, acc = l[i], min(acc + inc, mx)
        if is_below:
            result = min(result, l[i - 1])
            if i > 1:
                result = min(result, l[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def highest(src, n):
    return [max(src[i - n + 1:i + 1]) if i >= n - 1 else None for i in range(len(src))]


def lowest(src, n):
    return [min(src[i - n + 1:i + 1]) if i >= n - 1 else None for i in range(len(src))]


def pivots(src, L, high=True):
    """Value is set at the bar where the pivot gets confirmed (L bars after it), like ta.pivothigh/low."""
    out = [None] * len(src)
    for i in range(2 * L, len(src)):
        ctr = src[i - L]
        left, right = src[i - 2 * L:i - L], src[i - L + 1:i + 1]
        if high and all(ctr >= x for x in left) and all(ctr > x for x in right):
            out[i] = ctr
        if not high and all(ctr <= x for x in left) and all(ctr < x for x in right):
            out[i] = ctr
    return out


def day_of(ts):
    return ts // 86400000


# ───────── The strategy ─────────
def analyse(bars, daily):
    """bars: confirmed 4H candles oldest->newest. daily: confirmed 1D (UTC) candles.
    Returns per-bar dict lists needed for entries/exits (evaluated on the last bar)."""
    o = [b["o"] for b in bars]; h = [b["h"] for b in bars]; l = [b["l"] for b in bars]
    c = [b["c"] for b in bars]; v = [b["v"] for b in bars]; n = len(bars)

    # Daily trend (previous completed day vs day before)
    dc = [d["c"] for d in daily]
    de = ema(dc, 20)
    didx = {day_of(d["ts"]): k for k, d in enumerate(daily)}

    def daily_up(i):
        k = didx.get(day_of(bars[i]["ts"]) - 1)
        if k is None or k < 1 or de[k] is None or de[k - 1] is None:
            return False
        return dc[k] > de[k] and de[k] > de[k - 1]

    e50 = ema(c, 50)
    stdir = supertrend(h, l, c, 3, 10)
    e8, e21, e55 = ema(c, 8), ema(c, 21), ema(c, 55)
    r = rsi(c, 14)
    m12, m26 = ema(c, 12), ema(c, 26)
    macd = [a - b if a is not None and b is not None else None for a, b in zip(m12, m26)]
    sig_src = [x for x in macd if x is not None]
    sig_part = ema(sig_src, 9)
    sig = [None] * (n - len(sig_src)) + sig_part
    hist = [a - b if a is not None and b is not None else None for a, b in zip(macd, sig)]
    sar = psar(h, l, c, SAR_START, SAR_INC, SAR_MAX)
    rng_hi, rng_lo = highest(h, 30), lowest(l, 30)
    low10 = lowest(l, 10)

    # daily-anchored VWAP of hlc3
    vwap, cum_pv, cum_v, cur_day = [None] * n, 0.0, 0.0, None
    for i in range(n):
        dday = day_of(bars[i]["ts"])
        if dday != cur_day:
            cum_pv, cum_v, cur_day = 0.0, 0.0, dday
        cum_pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        cum_v += v[i]
        vwap[i] = cum_pv / cum_v if cum_v else c[i]

    ph, pl = pivots(h, PIVOT_LEN, True), pivots(l, PIVOT_LEN, False)
    last_ph = last_pl = None
    bos_bar = sweep_bar = ob_bar = fvg_bar = None
    ob_top = ob_bot = fvg_top = fvg_bot = None
    signal = [False] * n
    info = [None] * n

    for i in range(n):
        if ph[i] is not None:
            last_ph = ph[i]
        if pl[i] is not None:
            last_pl = pl[i]
        bos_up = last_ph is not None and i > 0 and c[i] > last_ph and c[i - 1] <= last_ph
        if bos_up:
            bos_bar, ob_top, ob_bot = i, None, None
            for k in range(1, 11):
                if i - k >= 0 and c[i - k] < o[i - k]:
                    ob_top, ob_bot, ob_bar = h[i - k], l[i - k], i
                    break
        if i >= 2 and l[i] > h[i - 2]:
            fvg_top, fvg_bot, fvg_bar = l[i], h[i - 2], i
        if last_pl is not None and l[i] < last_pl and c[i] > last_pl:
            sweep_bar = i

        if i < 1 or None in (e50[i - 1], stdir[i - 1], e55[i], hist[i], hist[i - 1], low10[i], rng_hi[i]):
            continue

        c1 = daily_up(i)
        c2 = c[i - 1] > e50[i - 1] and stdir[i - 1] < 0
        c3 = bos_bar is not None and i - bos_bar <= 20
        c5 = fvg_bar is not None and i > fvg_bar and i - fvg_bar <= 30 and l[i] <= fvg_top and c[i] >= fvg_bot
        c6 = (ob_bar is not None and ob_top is not None and i > ob_bar and i - ob_bar <= 30
              and l[i] <= ob_top and c[i] >= ob_bot)
        c7 = sweep_bar is not None and i - sweep_bar <= 10
        body = abs(c[i] - o[i])
        lower_w = min(c[i], o[i]) - l[i]
        upper_w = h[i] - max(c[i], o[i])
        engulf = c[i] > o[i] and c[i - 1] < o[i - 1] and c[i] >= o[i - 1] and o[i] <= c[i - 1]
        hammer = body > 0 and lower_w >= 2 * body and upper_w <= body
        c10 = engulf or hammer
        c11 = stdir[i] < 0
        c12 = hist[i] > hist[i - 1]
        score = int(c1) + int(c7) + int(c11) + int(c12) - int(c3) - int(c5) - int(c6) - int(c10)

        prop_up = e8[i] > e21[i] > e55[i]
        vwap_ok = c[i] > vwap[i]
        swing_stop = low10[i] * (1 - 0.001)
        raw_risk = (c[i] - swing_stop) / c[i] * 100
        risk_use = max(raw_risk, MIN_RISK)
        tp_pct = min(max(RR * risk_use, TP_MIN), TP_MAX)

        signal[i] = bool(c2 and prop_up and vwap_ok and score >= MIN_TUNED and raw_risk <= MAX_RISK)
        info[i] = {"score": score, "risk_use": risk_use, "raw_risk": raw_risk, "tp_pct": tp_pct,
                   "checks": {"daily": c1, "h4": c2, "bos": c3, "fvg": c5, "ob": c6, "sweep": c7,
                              "candle": c10, "st": c11, "macd": c12, "prop": prop_up, "vwap": vwap_ok}}
    return {"signal": signal, "info": info, "sar": sar, "close": c, "high": h, "low": l}


# ───────── State & logging ─────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"equity": START_EQUITY, "positions": {}, "last_bar": {}}


def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2, sort_keys=True)
        f.write("\n")


def log_trade(row):
    new = not os.path.exists(TRADES_FILE)
    with open(TRADES_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "coin", "side", "qty", "price", "usdt", "pnl_usdt", "pnl_pct", "reason", "equity"])
        w.writerow(row)


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def ts_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


# ───────── Orders ─────────
def inst_info(api, inst):
    d = api.get("/api/v5/public/instruments", {"instType": "SPOT", "instId": inst})[0]
    return float(d["lotSz"]), float(d["minSz"])


def floor_to(x, step):
    return math.floor(x / step + 1e-9) * step


def wait_fill(api, inst, cl_id):
    for _ in range(10):
        o = api.get("/api/v5/trade/order", {"instId": inst, "clOrdId": cl_id}, private=True)[0]
        if o["state"] in ("filled", "canceled", "mmp_canceled"):
            return o
        time.sleep(1)
    return o


def buy(api, inst, usdt, bar_ts):
    cl_id = f"{ORDER_PREFIX}{inst.split('-')[0]}{bar_ts // 1000}"[:32]
    api.post("/api/v5/trade/order", {"instId": inst, "tdMode": "cash", "side": "buy", "ordType": "market",
                                     "tgtCcy": "quote_ccy", "sz": f"{usdt:.2f}", "clOrdId": cl_id})
    o = wait_fill(api, inst, cl_id)
    filled = float(o.get("accFillSz") or 0)
    fee = float(o.get("fee") or 0)  # negative number
    qty = filled + fee if o.get("feeCcy") == inst.split("-")[0] else filled
    px = float(o.get("avgPx") or 0)
    return cl_id, qty, px, filled * px


def sell(api, inst, qty, tag):
    base = inst.split("-")[0]
    lot, min_sz = inst_info(api, inst)
    bal = api.get("/api/v5/account/balance", {"ccy": base}, private=True)[0]["details"]
    avail = float(bal[0]["availBal"]) if bal else 0.0
    sz = floor_to(min(qty, avail), lot)
    if sz < min_sz:
        log(f"  {inst}: nothing to sell (size {sz})")
        return None, 0.0, 0.0
    cl_id = f"{ORDER_PREFIX}{tag}{base}{int(time.time())}"[:32]
    dec = max(0, -int(math.floor(math.log10(lot)))) if lot < 1 else 0
    api.post("/api/v5/trade/order", {"instId": inst, "tdMode": "cash", "side": "sell", "ordType": "market",
                                     "sz": f"{sz:.{dec}f}", "clOrdId": cl_id})
    o = wait_fill(api, inst, cl_id)
    filled = float(o.get("accFillSz") or 0)
    px = float(o.get("avgPx") or 0)
    fee = float(o.get("fee") or 0)  # negative, in USDT for a sell
    return cl_id, filled, filled * px + fee


# ───────── Main loop per coin ─────────
def close_position(api, state, inst, reason):
    pos = state["positions"][inst]
    cl_id, filled, proceeds = sell(api, inst, pos["qty"], "s")
    if cl_id is None:
        state["positions"].pop(inst)
        return
    pnl = proceeds - pos["cost"]
    state["equity"] = round(state["equity"] + pnl, 4)
    px = proceeds / filled if filled else 0
    log(f"  SELL {inst} {filled} @ {px:.6g} ({reason}) P/L {pnl:+.2f} USDT")
    log_trade([now_iso(), inst, "sell", filled, round(px, 8), round(proceeds, 2), round(pnl, 2),
               round(pnl / pos["cost"] * 100, 2) if pos["cost"] else 0, reason, round(state["equity"], 2)])
    state["positions"].pop(inst)


def run_coin(api, state, inst, trade=True):
    raw4 = api.candles(inst, "4H", 500)
    rawd = api.candles(inst, "1Dutc", 120)
    bars = [b for b in raw4 if b["confirm"]]
    forming = raw4[-1] if not raw4[-1]["confirm"] else None
    daily = [d for d in rawd if d["confirm"]]
    a = analyse(bars, daily)
    idx = {b["ts"]: i for i, b in enumerate(bars)}
    last_done = state["last_bar"].get(inst, 0)
    new_bars = [i for i, b in enumerate(bars) if b["ts"] > last_done]
    if last_done == 0:
        new_bars = new_bars[-1:]   # first run: only look at the latest closed candle

    i_last = len(bars) - 1
    inf = a["info"][i_last]
    log(f"{inst}: last 4H candle {ts_iso(bars[i_last]['ts'])} close {bars[i_last]['c']}"
        + (f" | score {inf['score']} risk {inf['raw_risk']:.2f}% signal={a['signal'][i_last]}" if inf else ""))
    if not trade:
        return

    for i in new_bars:
        b = bars[i]
        pos = state["positions"].get(inst)
        # 1) exit orders that were resting during this candle
        if pos and b["ts"] > pos["entry_ts"]:
            if b["l"] <= pos["stop"]:
                close_position(api, state, inst, "stop" if not pos.get("trail") else "SAR trail")
                pos = None
            elif pos.get("limit") and b["h"] >= pos["limit"]:
                close_position(api, state, inst, "take profit")
                pos = None
        # 2) update the position at this candle's close (SAR trail, time stop)
        if pos and b["ts"] > pos["entry_ts"]:
            pos["hi_since"] = max(pos.get("hi_since") or b["h"], b["h"])
            one_r = pos["entry_px"] - pos["sl"]
            trail = pos["hi_since"] >= pos["entry_px"] + one_r
            s = a["sar"][i]
            pos["trail"] = trail
            pos["stop"] = max(pos["sl"], s) if trail and s is not None and s < b["c"] else pos["sl"]
            pos["limit"] = None if trail else pos["tp"]
            bars_in = i - idx.get(pos["entry_ts"], i)
            if pos["entry_ts"] not in idx:
                bars_in = (b["ts"] - pos["entry_ts"]) // H4_MS
            if bars_in >= MAX_BARS:
                close_position(api, state, inst, "time exit")
                pos = None
        # 3) new entry at this candle's close (only acted on for the latest candle)
        if not pos and a["signal"][i] and i == i_last:
            inf = a["info"][i]
            close = b["c"]
            sl = close * (1 - inf["risk_use"] / 100)
            tp = close * (1 + inf["tp_pct"] / 100)
            eq = state["equity"]
            qty = min(eq * RISK_PCT / 100 / (close - sl), eq / close)
            usdt = qty * close
            if usdt < 5:
                log(f"  {inst}: signal but order too small ({usdt:.2f} USDT)")
            else:
                cl_id, got, px, cost = buy(api, inst, usdt, b["ts"])
                if got > 0:
                    state["positions"][inst] = {"entry_ts": b["ts"], "entry_px": px or close, "qty": got,
                                                "cost": cost, "sl": sl, "tp": tp, "stop": sl, "limit": tp,
                                                "trail": False, "hi_since": None, "clOrdId": cl_id}
                    log(f"  BUY {inst} {got} @ {px:.6g} for {cost:.2f} USDT | SL {sl:.6g} TP {tp:.6g} score {inf['score']}")
                    log_trade([now_iso(), inst, "buy", got, round(px, 8), round(cost, 2), "", "",
                               f"score {inf['score']}", round(state["equity"], 2)])
        state["last_bar"][inst] = b["ts"]

    # 4) check the candle that is still forming (hourly runs catch stops/targets early)
    pos = state["positions"].get(inst)
    if pos and forming and forming["ts"] > pos["entry_ts"]:
        if forming["l"] <= pos["stop"]:
            close_position(api, state, inst, "stop" if not pos.get("trail") else "SAR trail")
        elif pos.get("limit") and forming["h"] >= pos["limit"]:
            close_position(api, state, inst, "take profit")


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "run").lower()
    key, sec, pw = (os.environ.get(k, "") for k in ("OKX_API_KEY", "OKX_API_SECRET", "OKX_API_PASSPHRASE"))
    api = OKX(key, sec, pw)
    log(f"SP-12 v4 demo bot | mode={mode} | {BASE_URL} | {now_iso()} UTC")

    if mode == "check":
        for inst in COINS:
            run_coin(api, load_state(), inst, trade=False)
        if not (key and sec and pw):
            log("API key secrets are missing — public data works, but trading can't start yet.")
            sys.exit(1)
        bal = api.get("/api/v5/account/balance", {"ccy": "USDT"}, private=True)[0]["details"]
        log(f"Demo account connected. USDT available: {bal[0]['availBal'] if bal else 0}")
        return

    if not (key and sec and pw):
        log("Waiting for OKX_API_KEY / OKX_API_SECRET / OKX_API_PASSPHRASE secrets — not trading.")
        return
    state = load_state()
    errors = 0
    for inst in COINS:
        try:
            run_coin(api, state, inst, trade=True)
        except Exception as e:  # keep going with the other coins
            errors += 1
            log(f"  ERROR {inst}: {e}")
        save_state(state)
    log(f"Bot equity: {state['equity']:.2f} USDT | open: {', '.join(state['positions']) or 'none'}")
    if errors == len(COINS):
        sys.exit(1)


if __name__ == "__main__":
    main()
