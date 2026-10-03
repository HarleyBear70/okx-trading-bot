"""
Jeff's demo trading bots, run by GitHub Actions every hour. No libraries needed beyond Python.

Bots (all settings copied from the strategies Jeff tested):
  SP-12 v4      OKX demo  BTC ETH SOL XRP   + PAPER on Kraken prices (BTC ETH SOL XRP)
  SP-12 v2      OKX demo  ETH SOL           + PAPER gold (XAUT, live OKX prices)
  Trend Rider   OKX demo  BTC ETH SOL       + PAPER gold (XAUT, swing strength 3)

"demo"  = real orders on the OKX DEMO account (every private request carries the
          "x-simulated-trading: 1" header, so real money can't be touched).
"paper" = no orders at all; the bot just records pretend trades in trades.csv.

Each bot only ever sells what it bought itself (tracked in state.json).
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

BASE_URL = os.environ.get("OKX_BASE_URL", "").strip() or "https://us.okx.com"
KRAKEN_URL = "https://api.kraken.com"
FEE = 0.001                 # 0.1% per side for paper trades (same as the backtests)
SAR_START, SAR_INC, SAR_MAX = 0.02, 0.02, 0.2
H4_MS = 4 * 3600 * 1000

BOTS = [
    {"id": "v4-okx", "name": "SP-12 v4", "strat": "v4", "venue": "okx", "mode": "demo", "prefix": "gh4",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT"], "equity": 1000.0},
    {"id": "v4-kraken", "name": "SP-12 v4 (Kraken paper)", "strat": "v4", "venue": "kraken", "mode": "paper",
     "coins": ["XBTUSD", "ETHUSD", "SOLUSD", "XRPUSD"], "equity": 1000.0},
    {"id": "v2-okx", "name": "SP-12 v2", "strat": "v2", "venue": "okx", "mode": "demo", "prefix": "ghS",
     "coins": ["ETH-USDT", "SOL-USDT"], "equity": 5000.0},
    {"id": "v2-gold", "name": "SP-12 v2 (gold paper)", "strat": "v2", "venue": "okx", "mode": "paper",
     "coins": ["XAUT-USDT"], "equity": 5000.0},
    {"id": "tr-okx", "name": "Trend Rider", "strat": "tr", "venue": "okx", "mode": "demo", "prefix": "ghT",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT"], "equity": 5000.0, "pivot": 5},
    {"id": "tr-gold", "name": "Trend Rider (gold paper)", "strat": "tr", "venue": "okx", "mode": "paper",
     "coins": ["XAUT-USDT"], "equity": 5000.0, "pivot": 3},
]

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
TRADES_FILE = os.path.join(HERE, "trades.csv")


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



def kraken_candles(pair, interval):
    """Kraken public OHLC (no key). interval in minutes. Last row is the forming candle."""
    url = f"{KRAKEN_URL}/0/public/OHLC?" + urllib.parse.urlencode({"pair": pair, "interval": interval})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "sp12-bot"}), timeout=20) as r:
                out = json.loads(r.read().decode())
            break
        except Exception as e:
            if attempt == 3:
                raise RuntimeError(f"Kraken {pair}: {e}")
            time.sleep(2 + attempt * 2)
    if out.get("error"):
        raise RuntimeError(f"Kraken {pair}: {out['error']}")
    rows = next(v for k, v in out["result"].items() if k != "last")
    bars = [{"ts": int(r[0]) * 1000, "o": float(r[1]), "h": float(r[2]), "l": float(r[3]), "c": float(r[4]),
             "v": float(r[6]), "confirm": True} for r in rows]
    if bars:
        bars[-1]["confirm"] = False
    return bars


def pivots_ge(src, L, high=True):
    """Swing point if it is the highest (lowest) of the L bars each side, ties allowed (as in Jeff's v2 / Trend Rider scripts)."""
    out = [None] * len(src)
    for i in range(2 * L, len(src)):
        w = src[i - 2 * L:i + 1]
        ctr = src[i - L]
        if (high and ctr >= max(w)) or (not high and ctr <= min(w)):
            out[i] = ctr
    return out


def daily_lookup(bars, daily):
    """For each 4H bar: index of the last COMPLETED daily candle before that bar's day."""
    didx = {day_of(d["ts"]): k for k, d in enumerate(daily)}
    return [didx.get(day_of(b["ts"]) - 1) for b in bars]


# ───────── SP-12 (v4 and v2 share the 12 checks) ─────────
SP_SETTINGS = {
    "v4": {"pivot": 7, "pivot_fn": "strict", "filters": True, "min_risk": 1.0, "max_risk": 4.0, "rr": 3.0,
           "tp_min": 2.0, "tp_max": 15.0, "max_bars": 120, "sar": True, "min_bars": 60},
    "v2": {"pivot": 5, "pivot_fn": "ge", "filters": False, "min_risk": 1.5, "max_risk": 4.0, "rr": 2.5,
           "tp_min": 3.0, "tp_max": 10.0, "max_bars": 60, "sar": False, "min_bars": 120},
}


def analyse_sp(bars, daily, cfg):
    o = [b["o"] for b in bars]; h = [b["h"] for b in bars]; l = [b["l"] for b in bars]
    c = [b["c"] for b in bars]; v = [b["v"] for b in bars]; n = len(bars)
    dc = [d["c"] for d in daily]
    de = ema(dc, 20)
    dk = daily_lookup(bars, daily)

    e50 = ema(c, 50)
    stdir = supertrend(h, l, c, 3, 10)
    e8, e21, e55 = ema(c, 8), ema(c, 21), ema(c, 55)
    m12, m26 = ema(c, 12), ema(c, 26)
    macd = [a - b if a is not None and b is not None else None for a, b in zip(m12, m26)]
    sig_src = [x for x in macd if x is not None]
    sig = [None] * (n - len(sig_src)) + ema(sig_src, 9)
    hist = [a - b if a is not None and b is not None else None for a, b in zip(macd, sig)]
    sar = psar(h, l, c, SAR_START, SAR_INC, SAR_MAX)
    low10 = lowest(l, 10)

    vwap, cum_pv, cum_v, cur_day = [None] * n, 0.0, 0.0, None
    for i in range(n):
        dday = day_of(bars[i]["ts"])
        if dday != cur_day:
            cum_pv, cum_v, cur_day = 0.0, 0.0, dday
        cum_pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        cum_v += v[i]
        vwap[i] = cum_pv / cum_v if cum_v else c[i]

    L = cfg["pivot"]
    if cfg["pivot_fn"] == "ge":
        ph, pl = pivots_ge(h, L, True), pivots_ge(l, L, False)
    else:
        ph, pl = pivots(h, L, True), pivots(l, L, False)
    last_ph = last_pl = None
    bos_bar = sweep_bar = ob_bar = fvg_bar = None
    ob_top = ob_bot = fvg_top = fvg_bot = None
    signal, info = [False] * n, [None] * n

    for i in range(n):
        if ph[i] is not None:
            last_ph = ph[i]
        if pl[i] is not None:
            last_pl = pl[i]
        if last_ph is not None and i > 0 and c[i] > last_ph and c[i - 1] <= last_ph:
            bos_bar, ob_top, ob_bot = i, None, None
            for k in range(1, 11):
                if i - k >= 0 and c[i - k] < o[i - k]:
                    ob_top, ob_bot, ob_bar = h[i - k], l[i - k], i
                    break
        if i >= 2 and l[i] > h[i - 2]:
            fvg_top, fvg_bot, fvg_bar = l[i], h[i - 2], i
        if last_pl is not None and l[i] < last_pl and c[i] > last_pl:
            sweep_bar = i

        if i < 1 or None in (e50[i - 1], stdir[i - 1], e55[i], hist[i], hist[i - 1], low10[i]):
            continue
        k = dk[i]
        c1 = bool(k is not None and k >= 1 and de[k] is not None and de[k - 1] is not None
                  and dc[k] > de[k] and de[k] > de[k - 1])
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

        filt = (e8[i] > e21[i] > e55[i] and c[i] > vwap[i]) if cfg["filters"] else True
        swing_stop = low10[i] * (1 - 0.001)
        raw_risk = (c[i] - swing_stop) / c[i] * 100
        risk_use = max(raw_risk, cfg["min_risk"])
        tp_pct = min(max(cfg["rr"] * risk_use, cfg["tp_min"]), cfg["tp_max"])
        signal[i] = bool(i + 1 >= cfg["min_bars"] and c2 and filt and score >= 2 and raw_risk <= cfg["max_risk"])
        info[i] = {"score": score, "raw_risk": raw_risk,
                   "sl": c[i] * (1 - risk_use / 100), "tp": c[i] * (1 + tp_pct / 100)}
    return {"signal": signal, "info": info, "sar": sar}


# ───────── Trend Rider ─────────
def analyse_tr(bars, daily, L):
    h = [b["h"] for b in bars]; l = [b["l"] for b in bars]; c = [b["c"] for b in bars]; n = len(bars)
    e50 = ema(c, 50)
    a = atr(h, l, c, 14)
    dc = [d["c"] for d in daily]
    de = ema(dc, 50)
    dk = daily_lookup(bars, daily)
    ph_l, pl_l = pivots_ge(h, L, True), pivots_ge(l, L, False)
    ph = pl = None
    signal, info = [False] * n, [None] * n
    for i in range(n):
        if ph_l[i] is not None:
            ph = ph_l[i]
        if pl_l[i] is not None:
            pl = pl_l[i]
        if i < 1 or a[i] is None or e50[i] is None:
            continue
        k = dk[i]
        daily_ok = bool(k is not None and de[k] is not None and dc[k] > de[k])
        bos = ph is not None and c[i] > ph and c[i - 1] <= ph
        sig = bool(i + 1 >= 61 and bos and c[i] > e50[i] and daily_ok)
        s = pl * 0.998 if pl is not None else c[i] - 2 * a[i]
        s = min(max(s, c[i] - 3 * a[i]), c[i] - 1 * a[i])
        signal[i] = sig
        info[i] = {"score": "BOS" if bos else "-", "raw_risk": (c[i] - s) / c[i] * 100, "sl": s, "tp": None}
    return {"signal": signal, "info": info, "atr": a}


# ───────── State & logging ─────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            s = json.load(f)
        if s.get("version") == 2:
            return s
    return {"version": 2, "bots": {}}


def bot_state(state, bot):
    return state["bots"].setdefault(bot["id"], {"equity": bot["equity"], "positions": {}, "last_bar": {}})


def save_state(s):
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=2, sort_keys=True)
        f.write("\n")


def log_trade(bot, coin, side, qty, px, usdt, pnl, pnl_pct, reason, equity):
    new = not os.path.exists(TRADES_FILE)
    with open(TRADES_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "bot", "mode", "coin", "side", "qty", "price", "usdt",
                        "pnl_usdt", "pnl_pct", "reason", "bot_balance"])
        w.writerow([now_iso(), bot["name"], bot["mode"], coin, side, f"{qty:.8g}", f"{px:.8g}", round(usdt, 2),
                    "" if pnl is None else round(pnl, 2), "" if pnl_pct is None else round(pnl_pct, 2),
                    reason, round(equity, 2)])


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def ts_iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


# ───────── OKX demo orders ─────────
_inst_cache = {}


def inst_info(api, inst):
    if inst not in _inst_cache:
        d = api.get("/api/v5/public/instruments", {"instType": "SPOT", "instId": inst})[0]
        _inst_cache[inst] = (float(d["lotSz"]), float(d["minSz"]))
    return _inst_cache[inst]


def floor_to(x, step):
    return math.floor(x / step + 1e-9) * step


def wait_fill(api, inst, cl_id):
    o = None
    for _ in range(10):
        o = api.get("/api/v5/trade/order", {"instId": inst, "clOrdId": cl_id}, private=True)[0]
        if o["state"] in ("filled", "canceled", "mmp_canceled"):
            return o
        time.sleep(1)
    return o


def okx_buy(api, bot, inst, usdt, bar_ts):
    cl_id = f"{bot['prefix']}B{inst.split('-')[0]}{bar_ts // 1000}"[:32]
    api.post("/api/v5/trade/order", {"instId": inst, "tdMode": "cash", "side": "buy", "ordType": "market",
                                     "tgtCcy": "quote_ccy", "sz": f"{usdt:.2f}", "clOrdId": cl_id})
    o = wait_fill(api, inst, cl_id)
    filled = float(o.get("accFillSz") or 0)
    fee = float(o.get("fee") or 0)  # negative
    qty = filled + fee if o.get("feeCcy") == inst.split("-")[0] else filled
    px = float(o.get("avgPx") or 0)
    return qty, px, filled * px


def okx_sell(api, bot, inst, qty):
    base = inst.split("-")[0]
    lot, min_sz = inst_info(api, inst)
    bal = api.get("/api/v5/account/balance", {"ccy": base}, private=True)[0]["details"]
    avail = float(bal[0]["availBal"]) if bal else 0.0
    sz = floor_to(min(qty, avail), lot)
    if sz < min_sz:
        return 0.0, 0.0
    dec = max(0, -int(math.floor(math.log10(lot)))) if lot < 1 else 0
    cl_id = f"{bot['prefix']}S{base}{int(time.time())}"[:32]
    api.post("/api/v5/trade/order", {"instId": inst, "tdMode": "cash", "side": "sell", "ordType": "market",
                                     "sz": f"{sz:.{dec}f}", "clOrdId": cl_id})
    o = wait_fill(api, inst, cl_id)
    filled = float(o.get("accFillSz") or 0)
    px = float(o.get("avgPx") or 0)
    fee = float(o.get("fee") or 0)  # negative, in quote
    return filled, filled * px + fee


# ───────── Opening / closing (demo or paper) ─────────
def open_position(api, bot, bs, coin, bar, inf, extra):
    close = bar["c"]
    sl = inf["sl"]
    if close <= sl:
        return
    if bot["strat"] == "v4":
        eq = bs["equity"]
        qty = min(eq * 0.01 / (close - sl), eq / close)
    else:
        qty = min(50.0 / (close - sl), 5000.0 / close)
    usdt = qty * close
    if usdt < 5:
        log(f"  {coin}: signal but order too small ({usdt:.2f})")
        return
    if bot["mode"] == "demo":
        got, px, cost = okx_buy(api, bot, coin, usdt, bar["ts"])
        if got <= 0:
            log(f"  {coin}: buy did not fill")
            return
    else:
        got, px, cost = qty, close, usdt * (1 + FEE)
    pos = {"entry_ts": bar["ts"], "entry_px": px or close, "qty": got, "cost": cost, "sl": sl, "tp": inf["tp"],
           "stop": sl, "limit": inf["tp"], "trail": False, "hi": None}
    pos.update(extra)
    bs["positions"][coin] = pos
    tp_txt = f" TP {inf['tp']:.6g}" if inf["tp"] else " (trailing stop)"
    log(f"  BUY {coin} {got:.8g} @ {px:.6g} for {cost:.2f} | SL {sl:.6g}{tp_txt} | {inf['score']}")
    log_trade(bot, coin, "buy", got, px, cost, None, None, f"score {inf['score']}", bs["equity"])


def close_position(api, bot, bs, coin, reason, paper_px):
    pos = bs["positions"][coin]
    if bot["mode"] == "demo":
        filled, proceeds = okx_sell(api, bot, coin, pos["qty"])
        if filled <= 0:
            log(f"  {coin}: nothing left to sell — clearing position")
            bs["positions"].pop(coin)
            return
        px = proceeds / filled
    else:
        filled, px = pos["qty"], paper_px
        proceeds = filled * px * (1 - FEE)
    pnl = proceeds - pos["cost"]
    bs["equity"] = round(bs["equity"] + pnl, 4)
    pct = pnl / pos["cost"] * 100 if pos["cost"] else 0
    log(f"  SELL {coin} {filled:.8g} @ {px:.6g} ({reason}) P/L {pnl:+.2f} ({pct:+.2f}%)")
    log_trade(bot, coin, "sell", filled, px, proceeds, pnl, pct, reason, bs["equity"])
    bs["positions"].pop(coin)


def check_hit(api, bot, bs, coin, bar):
    """Did this candle touch the resting stop / target? Returns True if the trade was closed."""
    pos = bs["positions"][coin]
    if bar["l"] <= pos["stop"]:
        reason = "trailing stop" if pos.get("trail") or bot["strat"] == "tr" and pos["stop"] > pos["sl"] else "stop"
        close_position(api, bot, bs, coin, reason, min(pos["stop"], bar["o"]))
        return True
    if pos.get("limit") and bar["h"] >= pos["limit"]:
        close_position(api, bot, bs, coin, "take profit", max(pos["limit"], bar["o"]))
        return True
    return False


def manage_on_close(api, bot, bs, coin, a, i, bar, bars_in):
    """Update stop/target at a candle close, like the TradingView strategy. True if closed."""
    pos = bs["positions"][coin]
    if bot["strat"] == "v4":
        pos["hi"] = max(pos["hi"] or bar["h"], bar["h"])
        one_r = pos["entry_px"] - pos["sl"]
        trail = pos["hi"] >= pos["entry_px"] + one_r
        s = a["sar"][i]
        pos["trail"] = trail
        pos["stop"] = max(pos["sl"], s) if trail and s is not None and s < bar["c"] else pos["sl"]
        pos["limit"] = None if trail else pos["tp"]
    elif bot["strat"] == "tr":
        pos["hi"] = max(pos["hi"] or bar["c"], bar["c"])
        if a["atr"][i] is not None:
            pos["stop"] = max(pos["stop"], pos["hi"] - 3 * a["atr"][i])
    max_bars = SP_SETTINGS.get(bot["strat"], {}).get("max_bars")
    if max_bars and bars_in >= max_bars:
        close_position(api, bot, bs, coin, "time exit", bar["c"])
        return True
    return False


# ───────── Market data (cached per run) ─────────
_data = {}


def get_data(api, venue, coin):
    key = (venue, coin)
    if key not in _data:
        if venue == "kraken":
            raw4, rawd = kraken_candles(coin, 240), kraken_candles(coin, 1440)
        else:
            raw4, rawd = api.candles(coin, "4H", 500), api.candles(coin, "1Dutc", 120)
        bars = [b for b in raw4 if b["confirm"]]
        forming = raw4[-1] if raw4 and not raw4[-1]["confirm"] else None
        daily = [d for d in rawd if d["confirm"]]
        _data[key] = (bars, forming, daily)
    return _data[key]


def run_bot_coin(api, state, bot, coin, trade=True):
    bars, forming, daily = get_data(api, bot["venue"], coin)
    if bot["strat"] == "tr":
        a = analyse_tr(bars, daily, bot.get("pivot", 5))
    else:
        a = analyse_sp(bars, daily, SP_SETTINGS[bot["strat"]])
    bs = bot_state(state, bot)
    i_last = len(bars) - 1
    inf = a["info"][i_last]
    pos = bs["positions"].get(coin)
    log(f"[{bot['name']}] {coin}: 4H {ts_iso(bars[i_last]['ts'])} close {bars[i_last]['c']:.6g}"
        + (f" | score {inf['score']} risk {inf['raw_risk']:.2f}% signal={a['signal'][i_last]}" if inf else "")
        + (f" | OPEN from {pos['entry_px']:.6g}, stop {pos['stop']:.6g}" if pos else ""))
    if not trade:
        return

    idx = {b["ts"]: k for k, b in enumerate(bars)}
    last_done = bs["last_bar"].get(coin, 0)
    new_bars = [k for k, b in enumerate(bars) if b["ts"] > last_done]
    if last_done == 0:
        new_bars = new_bars[-1:]

    for k in new_bars:
        b = bars[k]
        if coin in bs["positions"] and b["ts"] > bs["positions"][coin]["entry_ts"]:
            if not check_hit(api, bot, bs, coin, b):
                p = bs["positions"][coin]
                bars_in = k - idx[p["entry_ts"]] if p["entry_ts"] in idx else (b["ts"] - p["entry_ts"]) // H4_MS
                manage_on_close(api, bot, bs, coin, a, k, b, bars_in)
        if coin not in bs["positions"] and a["signal"][k] and k == i_last:
            extra = {"hi": b["c"]} if bot["strat"] == "tr" else {}
            open_position(api, bot, bs, coin, b, a["info"][k], extra)
        bs["last_bar"][coin] = b["ts"]

    if coin in bs["positions"] and forming and forming["ts"] > bs["positions"][coin]["entry_ts"]:
        check_hit(api, bot, bs, coin, forming)


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "run").lower()
    key, sec, pw = (os.environ.get(k, "") for k in ("OKX_API_KEY", "OKX_API_SECRET", "OKX_API_PASSPHRASE"))
    api = OKX(key, sec, pw)
    log(f"Jeff's demo bots | mode={mode} | {BASE_URL} | {now_iso()} UTC")
    state = load_state()

    if mode == "check":
        for bot in BOTS:
            for coin in bot["coins"]:
                try:
                    run_bot_coin(api, state, bot, coin, trade=False)
                except Exception as e:
                    log(f"[{bot['name']}] {coin}: ERROR {e}")
        bal = api.get("/api/v5/account/balance", {"ccy": "USDT"}, private=True)[0]["details"]
        log(f"Demo account connected. USDT available: {bal[0]['availBal'] if bal else 0}")
        return

    have_keys = bool(key and sec and pw)
    errors = total = 0
    for bot in BOTS:
        if bot["mode"] == "demo" and not have_keys:
            log(f"[{bot['name']}] waiting for OKX API key secrets — skipped")
            continue
        for coin in bot["coins"]:
            total += 1
            try:
                run_bot_coin(api, state, bot, coin, trade=True)
            except Exception as e:
                errors += 1
                log(f"[{bot['name']}] {coin}: ERROR {e}")
            save_state(state)
    for bot in BOTS:
        bs = state["bots"].get(bot["id"])
        if bs:
            log(f"{bot['name']}: balance {bs['equity']:.2f} | open: {', '.join(bs['positions']) or 'none'}")
    if total and errors == total:
        sys.exit(1)


if __name__ == "__main__":
    main()
