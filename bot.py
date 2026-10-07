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
FEE = 0.0035                # 0.35% per side: OKX spot Lv1 market orders, the real rate (was 0.1% until Oct 6 2026, research/FEES.md)
SAR_START, SAR_INC, SAR_MAX = 0.02, 0.02, 0.2
H4_MS = 4 * 3600 * 1000
RISK_PCT = 0.005  # every bot risks 0.5% of its balance per trade (was 1%; changed Oct 5 2026 to keep drawdown under 10%)
# "retired": True = failed its tests; skipped every hour once it has no open trade (its history stays in trades.csv).
# Per-bot settings in BOTS: "risk" overrides RISK_PCT; "half_at_2r": False turns off selling half at +2R
# (the switch: delete it or set True to sell half again). Both since Oct 5 2026, research/upside_test.py.
RISK_STEPS = [(0.50, 0.02), (0.25, 0.015), (0.10, 0.0125)]  # balance up 50% -> 2%, up 25% -> 1.5%, up 10% -> 1.25%
RISK_STEPS_ON = False  # stepping risk up is off for now (Oct 5 2026); set True to turn it back on
MAX_OPEN = 3  # no more than 3 trades open at once per bot (per-bot "max_open" overrides; Donchian Trend: 5, as tested)
FNG_URL = "https://api.alternative.me/fng/?limit=10&format=json"  # Crypto Fear & Greed Index (free, no key)
# Hold-pile buyer (Jeff, Oct 5 2026): every week buy BTC + XRP; double a coin's buy when its last daily close is
# 20%+ below its 200-day average. PAPER until Jeff goes live; he sets the real weekly amount then.
DCA = {"on": True, "mode": "paper", "weekly_usd": 10.0, "coins": {"BTC-USDT": 0.5, "XRP-USDT": 0.5},
       "dip_below_200d": 0.20, "dip_mult": 2.0}
# Profit sweeper (Jeff, Oct 5 2026): a share of every winning sale moves to the hold pile. OFF until real money.
SWEEP = {"on": False, "share": 0.25}
# Guard (Jeff, Oct 6 2026: Claude "hired" as risk manager). It can only block buys, never add risk or restart a bot.
# A bot whose closed balance falls max_dd below its best is halted: no new buys, open trades keep their stops.
# The halt sticks (state.json "halted") until Jeff says resume. Live BOTS only, so backtests are unaffected.
GUARD = {"on": True, "max_dd": 0.12, "skip_strats": ("hold",)}
BE_BUFFER = 2 * FEE  # breakeven stop sits just above entry so fees are covered

BOTS = [
    {"id": "v4-okx", "retired": True, "name": "SP-12 v4", "strat": "v4", "venue": "okx", "mode": "demo", "prefix": "gh4",
     "coins": ["BTC-USDT", "ETH-USDT", "XRP-USDT", "XLM-USDT", "BNB-USDT"], "equity": 1000.0,
     "risk": 0.004, "half_at_2r": False,  # Oct 5 2026 (Jeff, demo): no half sell, 0.4% keeps the 8-year drop under 10%
     "new_trades": False},  # paused Oct 6 2026: loses money at the real 0.35% fee, all 8 versions (research/FEES.md)
    # SOL dropped: lost money in backtest. XLM, BNB added Oct 5 2026 (passed pick + out-of-sample check, research/COINS.md)
    {"id": "v4-kraken", "retired": True, "name": "SP-12 v4 (Kraken paper)", "strat": "v4", "venue": "kraken", "mode": "paper",
     "coins": ["XBTUSD", "ETHUSD", "XRPUSD"], "equity": 1000.0,  # SOL dropped: lost money in backtest
     "risk": 0.004, "half_at_2r": False,  # same change as SP-12 v4 (Oct 5 2026)
     "new_trades": False},  # paused Oct 6 2026 with SP-12 v4 (research/FEES.md)
    {"id": "v2-okx", "retired": True, "name": "SP-12 v2", "strat": "v2", "venue": "okx", "mode": "demo", "prefix": "ghS",
     "coins": ["ETH-USDT", "SOL-USDT"], "equity": 1000.0,
     "new_trades": False},  # paused Oct 5 2026: no edge in long-history test, repair failed (research/REPAIR_v2.md)
    {"id": "v2-gold", "retired": True, "name": "SP-12 v2 (gold paper)", "strat": "v2", "venue": "okx", "mode": "paper",
     "coins": ["XAUT-USDT"], "equity": 1000.0, "new_trades": False},  # paused Oct 5 2026 with SP-12 v2
    {"id": "tr-okx", "name": "Trend Rider", "strat": "tr", "venue": "okx", "mode": "demo", "prefix": "ghT",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "SUI-USDT", "TRX-USDT"], "equity": 1000.0, "pivot": 5,
     "risk": 0.004,  # Oct 6 2026 (Jeff): 0.4% keeps the 8-year drop under 10% at the real 0.35% fee (research/FEES.md)
     "exchange_stops": True,  # Oct 6 2026 (Jeff): OKX holds the stop (EXCHANGE_STOPS_PLAN.md step 2, demo test)
     "half_at_2r": False,  # Oct 5 2026 (Jeff, demo): no half sell at +2R, the trailing stop handles the exit
     "fear_skip_at_or_below": 25},  # no new buys when Fear & Greed <= 25 (Oct 5 2026, research/S1_SENTIMENT.md)
    # Trend Rider coins: BNB, SUI added Oct 5 (passed backtest); TRX added Oct 5 (research/TRX.md)
    {"id": "b1-paper", "retired": True, "name": "B1c breakout retest (paper)", "strat": "b1", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT", "ETH-USDT", "XRP-USDT"], "equity": 1000.0,  # forward test from Oct 5 2026 (research/B_BOXES.md)
     "new_trades": False},  # paused Oct 6 2026: loses money at the real 0.35% fee (research/FEES.md)
    {"id": "b3-paper", "name": "B3 pairs (paper)", "strat": "pairs", "venue": "okx", "mode": "paper",
     "coins": ["ETH-USDT", "XRP-USDT", "BTC-USDT"], "equity": 1000.0,
     "pairs": ["ETH-USDT", "XRP-USDT"]},  # forward test from Oct 5 2026 (research/B3_PAIRS.md, variant P3)
    {"id": "nnfx-paper", "retired": True, "name": "NNFX Aroon (paper)", "strat": "nnfx", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT", "ETH-USDT", "XRP-USDT"], "equity": 1000.0,  # backup candidate from Oct 5 2026 (research/NNFX.md)
     "new_trades": False},  # moved to OKX demo as nnfx-okx on Oct 6 2026
    {"id": "nnfx-okx", "name": "NNFX Aroon", "strat": "nnfx", "venue": "okx", "mode": "demo", "prefix": "ghN",
     "coins": ["BTC-USDT", "ETH-USDT", "XRP-USDT"], "equity": 1000.0},  # Oct 6 2026 (Jeff): passed at the real fee, +45%, DD -7.6% (research/FEES.md)
    {"id": "dc-okx", "name": "Donchian Trend", "strat": "donchian", "venue": "okx", "mode": "demo", "prefix": "ghD",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT"], "equity": 1000.0, "risk": 0.0032,
     "max_open": 5, "half_at_2r": False,  # Oct 6 2026 (Jeff): daily 20-day breakout
     "pyramid": True,  # Oct 6 2026 (Jeff): one add-on at +1R, stop then >= entry; risk 0.35% -> 0.32% (research/F10.md)
     "btc_leash": True},  # Oct 6 2026 (Jeff): ETH SOL XRP BNB buy only when BTC's daily close > its daily 50 EMA (research/F11.md)
    # Donchian: daily 20-day breakout, passed at the real fee: +123%, DD -9.1% (research/F2.md)
    {"id": "hold-paper", "name": "BTC Protected Hold (paper)", "strat": "hold", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT"], "equity": 1000.0, "risk": 1.0, "half_at_2r": False},  # Oct 6 2026 (Jeff): all-in BTC above
    # its 100-day average, cash below. A hold, not a 0.5%-risk bot: drops of 35-40% still happen (research/F2.md, B3)
    {"id": "fl-paper", "name": "Follow Line (paper)", "strat": "followline", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT"], "equity": 1000.0, "risk": 0.003,
     "max_open": 5, "half_at_2r": False},  # Oct 6 2026 (Jeff): forward test of F13 #5 (+260% / DD -10.0%, research/F13.md)
    {"id": "db-paper", "name": "Double Bottom (paper)", "strat": "dbottom", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT"], "equity": 1000.0, "risk": 0.01,
     "max_open": 5, "half_at_2r": False},  # Oct 6 2026 (Jeff): forward test of F14 P1 (+60% / DD -7.5%, research/F14.md)
    {"id": "cr-paper", "name": "Confluence Rank (paper)", "strat": "confluence", "venue": "okx", "mode": "paper",
     "coins": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "XRP-USDT", "BNB-USDT"], "equity": 1000.0, "risk": 0.004,
     "max_open": 5, "half_at_2r": False},  # Oct 6 2026 (Jeff): forward test of his "my strat 2", F24 B1
    # (+37% / DD -5.7%; with Donchian return/DD 12.9 -> 16.6, research/F24.md)
    {"id": "tr-gold", "retired": True, "name": "Trend Rider (gold paper)", "strat": "tr", "venue": "okx", "mode": "paper",
     "coins": ["XAUT-USDT"], "equity": 1000.0, "pivot": 3, "half_at_2r": False,  # same change as Trend Rider
     "new_trades": False},  # paused Oct 5 2026: weak in long-history test, repair failed (research/REPAIR_gold.md)
]

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "state.json")
TRADES_FILE = os.path.join(HERE, "trades.csv")
HOLD_FILE = os.path.join(HERE, "hold_pile.csv")


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


# ───────── B1c breakout retest (1H candles, paper forward test) ─────────
B1_SETTINGS = {"box": 60, "h_min": 0.03, "h_max": 0.12, "retest_4h": 12, "near": 0.002, "inside": 0.25,
               "rr": 2.0, "max_bars": 48}


def to_4h(bars):
    """Complete 4H candles (UTC) built from 1H candles."""
    out = {}
    for b in bars:
        k = b["ts"] - b["ts"] % H4_MS
        x = out.setdefault(k, {"ts": k, "o": b["o"], "h": b["h"], "l": b["l"], "c": b["c"], "n": 0})
        x["h"], x["l"], x["c"], x["n"] = max(x["h"], b["h"]), min(x["l"], b["l"]), b["c"], x["n"] + 1
    return [x for x in sorted(out.values(), key=lambda x: x["ts"]) if x["n"] == 4]


def analyse_b1(bars):
    """4H box of the last 60 candles; after a 4H close above the box high, buy the first 1H candle (within
    12 4H candles) that dips to within 0.2% of the old box high and closes back above it. Stop 25% back
    inside the box, target 2R. `bars` are 1H candles."""
    cfg = B1_SETTINGS
    b4 = to_4h(bars)
    h4, l4, c4 = [x["h"] for x in b4], [x["l"] for x in b4], [x["c"] for x in b4]
    idx = {b["ts"]: k for k, b in enumerate(bars)}
    n = len(bars)
    signal, info = [False] * n, [None] * n
    for j in range(cfg["box"] + 1, len(b4)):
        hi, lo = max(h4[j - cfg["box"]:j]), min(l4[j - cfg["box"]:j])
        if lo <= 0 or not (cfg["h_min"] <= (hi - lo) / lo <= cfg["h_max"]) or not (c4[j] > hi >= c4[j - 1]):
            continue
        start = b4[j]["ts"] + H4_MS
        for t in range(start, start + cfg["retest_4h"] * H4_MS, 3600 * 1000):
            k = idx.get(t)
            if k is None:
                continue
            x = bars[k]
            if x["l"] <= hi * (1 + cfg["near"]) and x["c"] > hi:
                sl = hi - cfg["inside"] * (hi - lo)
                signal[k] = True
                info[k] = {"score": "retest", "raw_risk": (x["c"] - sl) / x["c"] * 100, "sl": sl,
                           "tp": x["c"] + cfg["rr"] * (x["c"] - sl)}
                break
    return {"signal": signal, "info": info}


# ───────── B3 pairs (daily candles, paper forward test) ─────────
PAIRS_SETTINGS = {"n": 60, "entry": 2.5, "exit": 0.5, "max_bars": 30, "atr_mult": 2.0}


def pair_z(alt_daily, btc_daily, n):
    """{day ts: z-score of log(alt / BTC) vs its previous n days}."""
    a = {d["ts"]: d["c"] for d in alt_daily}
    b = {d["ts"]: d["c"] for d in btc_daily}
    days = sorted(set(a) & set(b))
    sp = [math.log(a[d] / b[d]) for d in days]
    z = {}
    for i in range(n, len(days)):
        w = sp[i - n:i]
        m = sum(w) / n
        sd = math.sqrt(sum((x - m) ** 2 for x in w) / (n - 1))
        if sd > 0:
            z[days[i]] = (sp[i] - m) / sd
    return z


def analyse_pairs(coin, bars, btc_daily, alt_dailies):
    """Hold the lagging leg: buy the alt when its spread vs BTC is 2.5 sd below normal, buy BTC when an alt's
    spread is 2.5 sd above. Exit when the spread is back within 0.5 sd (a["exit"][alt][i]), after 30 days,
    or at a 2 x daily ATR stop. `bars` are this coin's daily candles; alt_dailies = {alt: daily candles}."""
    cfg = PAIRS_SETTINGS
    zs = {alt: pair_z(d, btc_daily, cfg["n"]) for alt, d in alt_dailies.items()}
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    at = atr(h, l, c, 14)
    n = len(bars)
    signal, info = [False] * n, [None] * n
    exit_ = {alt: [False] * n for alt in zs}
    for k, b in enumerate(bars):
        for alt, z in zs.items():
            v = z.get(b["ts"])
            exit_[alt][k] = v is not None and abs(v) < cfg["exit"]
        if at[k] is None:
            continue
        for alt, z in zs.items():
            v = z.get(b["ts"])
            if v is None:
                continue
            if (coin == alt and v < -cfg["entry"]) or (coin != alt and coin not in zs and v > cfg["entry"]):
                sl = c[k] - cfg["atr_mult"] * at[k]
                signal[k] = True
                info[k] = {"score": f"z {v:+.2f} {alt.split('-')[0]}/BTC", "raw_risk": (c[k] - sl) / c[k] * 100,
                           "sl": sl, "tp": None, "tag": alt}
                break
    return {"signal": signal, "info": info, "exit": exit_}


# ───────── NNFX Aroon (daily candles, paper backup candidate) ─────────
NNFX_SETTINGS = {"aroon": 25, "stop_atr": 1.5, "half_atr": 1.0}


def aroon_dir(h, l, n=25):
    """+1 when Aroon up > Aroon down, -1 when down > up (unchanged on a tie)."""
    out = [0] * len(h)
    for i in range(n, len(h)):
        wh, wl = h[i - n:i + 1], l[i - n:i + 1]
        up = 100 * (n - wh[::-1].index(max(wh))) / n
        dn = 100 * (n - wl[::-1].index(min(wl))) / n
        out[i] = 1 if up > dn else (-1 if dn > up else out[i - 1])
    return out


def analyse_nnfx(bars):
    """Daily, long only: buy when Aroon(25) flips up; stop 1.5 ATR; half off at +1 ATR, then breakeven;
    the rest leaves when Aroon flips down (a["exit"])."""
    cfg = NNFX_SETTINGS
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    a, d = atr(h, l, c, 14), aroon_dir(h, l, cfg["aroon"])
    n = len(bars)
    signal, info = [False] * n, [None] * n
    for k in range(1, n):
        if d[k] == 1 and d[k - 1] != 1 and a[k] is not None:
            sl = c[k] - cfg["stop_atr"] * a[k]
            signal[k] = True
            info[k] = {"score": "Aroon flipped up", "raw_risk": (c[k] - sl) / c[k] * 100, "sl": sl, "tp": None,
                       "half_at": c[k] + cfg["half_atr"] * a[k]}
    return {"signal": signal, "info": info, "exit": [x == -1 for x in d]}


# ───────── Donchian Trend and BTC Protected Hold (Oct 6 2026, research/F2.md) ─────────
DONCHIAN_SETTINGS = {"entry": 20, "exit": 10, "stop_atr": 2.0, "atr": 20}
HOLD_SETTINGS = {"sma": 100}


def analyse_donchian(bars):
    """Daily, long only: buy on a close above the prior 20-day high; first stop 2 ATR(20) under the close, then the
    stop trails at the lowest low of the last 10 days (a["trail"]). No target, no half sell, no breakeven step."""
    cfg = DONCHIAN_SETTINGS
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    a = atr(h, l, c, cfg["atr"])
    n = len(bars)
    signal, info, trail = [False] * n, [None] * n, [None] * n
    for k in range(n):
        if k >= cfg["exit"] - 1:
            trail[k] = min(l[k - cfg["exit"] + 1:k + 1])
        if k >= cfg["entry"] and a[k] is not None and c[k] > max(h[k - cfg["entry"]:k]):
            sl = c[k] - cfg["stop_atr"] * a[k]
            signal[k] = True
            info[k] = {"score": f"{cfg['entry']}-day high", "raw_risk": (c[k] - sl) / c[k] * 100, "sl": sl, "tp": None}
    return {"signal": signal, "info": info, "trail": trail}


def btc_leash(bars, btc_daily, coin):
    """BTC leash (research/F11.md, L2): for a non-BTC coin, a daily signal counts only if BTC's close on the same day
    is above BTC's daily 50 EMA. Returns a list of True/False per bar (all True for BTC itself)."""
    if coin.startswith("BTC"):
        return [True] * len(bars)
    c = [d["c"] for d in btc_daily]
    e50 = ema(c, 50)
    up = {day_of(d["ts"]): e50[k] is not None and c[k] > e50[k] for k, d in enumerate(btc_daily)}
    return [up.get(day_of(b["ts"]), False) for b in bars]


def analyse_followline(bars):
    """Follow Line, quick-flip variant (research/F13.md #5), daily, long only. A trend line from Bollinger(21, 1) and
    ATR(5): above the upper band it sits at low - ATR (and only rises while the trend is up), below the lower band at
    high + ATR (only falls while down). Buy when it turns up; a["exit"] when it turns down. First stop 2 ATR(14)."""
    import math
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    a5, a14, m = atr(h, l, c, 5), atr(h, l, c, 14), sma(c, 21)
    n = len(bars)
    line, trend = [None] * n, [0] * n
    signal, info, ex = [False] * n, [None] * n, [False] * n
    for k in range(21, n):
        if a5[k] is None or m[k] is None:
            continue
        sd = math.sqrt(sum((x - m[k]) ** 2 for x in c[k - 20:k + 1]) / 21)
        prev = line[k - 1] if line[k - 1] is not None else c[k]
        if c[k] > m[k] + sd:
            line[k] = max(l[k] - a5[k], prev) if trend[k - 1] == 1 else l[k] - a5[k]
        elif c[k] < m[k] - sd:
            line[k] = min(h[k] + a5[k], prev) if trend[k - 1] == -1 else h[k] + a5[k]
        else:
            line[k] = prev
        trend[k] = 1 if line[k] > prev else -1 if line[k] < prev else trend[k - 1]
        ex[k] = trend[k] == -1 and trend[k - 1] == 1
        if trend[k] == 1 and trend[k - 1] != 1 and a14[k]:
            sl = c[k] - 2 * a14[k]
            signal[k] = True
            info[k] = {"score": "Follow Line turned up", "raw_risk": (c[k] - sl) / c[k] * 100, "sl": sl, "tp": None}
    return {"signal": signal, "info": info, "exit": ex}


def analyse_confluence(bars):
    """Confluence Rank Trend (Jeff's "my strat 2", research/F24.md B1), daily, long only. A 0-100 score from five
    20-point parts: trend (close and EMA 55 vs EMA 233), RSI(14) from 50 to 70, efficiency ratio (20 days, full at
    0.40), ATR(14) percentile over 200 days (full between 20 and 85) and up-day volume vs its 20-day average.
    Buy when the score crosses up through 85; stop 3 ATR(14) under the close, trailing 3 ATR under each close
    (a["trail"]); a["exit"] when the score falls below 35. Needs ~800 daily candles (EMA 233 + 200-day rank)."""
    o, h, l, c, v = ([b[f] for b in bars] for f in "ohlcv")
    ef, es, r, a = ema(c, 55), ema(c, 233), rsi(c, 14), atr(h, l, c, 14)
    vm = sma(v, 20)
    n = len(bars)
    score = [None] * n
    signal, info, ex, trail = [False] * n, [None] * n, [False] * n, [None] * n
    clamp = lambda x: max(0.0, min(1.0, x))  # noqa: E731
    for k in range(234, n):
        if a[k] is not None:
            trail[k] = c[k] - 3 * a[k]
        if None in (es[k], r[k], a[k], vm[k]) or any(x is None for x in a[k - 200:k]):
            continue
        pr = sum(a[k - j] <= a[k] for j in range(1, 201)) / 2
        chg = c[k] - c[k - 20]
        path = sum(abs(c[i] - c[i - 1]) for i in range(k - 19, k + 1))
        er = abs(chg) / path if path > 0 else 0.0
        trend = (10 if c[k] > es[k] else 0) + (10 if ef[k] > es[k] else 0)
        mom = 20 * clamp((r[k] - 50) / 20)
        eff = 20 * clamp(er / 0.4) if chg > 0 else 0.0
        vol = pr if pr < 20 else 20 * clamp((100 - pr) / 15) if pr > 85 else 20.0
        part = (20 * clamp(v[k] / vm[k] - 0.5) if c[k] > o[k] else 0.0) if vm[k] > 0 else 10.0
        score[k] = trend + mom + eff + vol + part
        ex[k] = score[k] < 35
        if score[k - 1] is not None and score[k] >= 85 > score[k - 1]:
            sl = c[k] - 3 * a[k]
            signal[k] = True
            info[k] = {"score": f"Confluence score {score[k]:.0f}", "raw_risk": (c[k] - sl) / c[k] * 100, "sl": sl,
                       "tp": None}
    return {"signal": signal, "info": info, "exit": ex, "trail": trail, "score": score}


def analyse_dbottom(bars):
    """Double bottom breakout (research/F14.md P1), daily, long only. Two swing lows (lowest of 5 days each side)
    within 3% of each other, 10-60 days apart, with a peak between them 5%+ above the higher low (the neckline).
    Buy on the first close above the neckline within 20 days of the second low. Stop under the lower low x 0.998,
    held 1-3 ATR(14) below the close; then trail at the 10-day low (a["trail"])."""
    h, l, c = [b["h"] for b in bars], [b["l"] for b in bars], [b["c"] for b in bars]
    a = atr(h, l, c, 14)
    n = len(bars)
    signal, info, trail = [False] * n, [None] * n, [None] * n
    last_sig = -99
    for k in range(n):
        if k >= 9:
            trail[k] = min(l[k - 9:k + 1])
        if k < 60 or a[k] is None:
            continue
        low = None
        for j2 in range(k - 20, k - 4):
            if l[j2] != min(l[j2 - 5:j2 + 6]):
                continue
            for j1 in range(j2 - 60, j2 - 9):
                if j1 < 5 or l[j1] != min(l[j1 - 5:j1 + 6]) or abs(l[j1] / l[j2] - 1) > 0.03:
                    continue
                neck = max(h[j1:j2 + 1])
                if neck >= max(l[j1], l[j2]) * 1.05 and c[k] > neck and max(c[j2:k]) <= neck:
                    low = min(l[j1], l[j2])
                    break
            if low:
                break
        if low is not None and k - last_sig > 1:
            sl = min(max(low * 0.998, c[k] - 3 * a[k]), c[k] - a[k])
            if c[k] > sl:
                signal[k] = True
                info[k] = {"score": "double bottom breakout", "raw_risk": (c[k] - sl) / c[k] * 100, "sl": sl, "tp": None}
                last_sig = k
    return {"signal": signal, "info": info, "trail": trail}


def analyse_hold(bars):
    """Daily: in BTC while the close is above its 100-day average, out (cash) when it closes below (a["exit"]).
    The 1%-of-price "stop" is never meant to be hit; with risk 1.0 the bot buys with all of its free balance."""
    c = [b["c"] for b in bars]
    m = sma(c, HOLD_SETTINGS["sma"])
    n = len(bars)
    signal, info = [False] * n, [None] * n
    for k in range(n):
        if m[k] is not None and c[k] > m[k]:
            signal[k] = True
            info[k] = {"score": f"above {HOLD_SETTINGS['sma']}-day average", "raw_risk": 99.0, "sl": c[k] * 0.01, "tp": None}
    return {"signal": signal, "info": info, "exit": [m[k] is not None and c[k] < m[k] for k in range(n)]}


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


def migrate_budget(state):
    """One time: bots that started on $5,000 switch to the same $1,000 practice balance as SP-12 v4.
    The balance keeps its % gain/loss, and trades already open count at 1/5 size."""
    if state.get("budget") == 1000:
        return state
    for b in BOTS:
        bs = state["bots"].get(b["id"])
        if bs and bs.get("equity", 0) > 2500:
            bs["equity"] = round(bs["equity"] * 0.2, 4)
            for pos in bs["positions"].values():
                pos["pnl_scale"] = pos.get("pnl_scale", 1.0) * 0.2
    state["budget"] = 1000
    return state

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


# ───────── Execution log (journal/executions-YYYY-MM.jsonl): data only, never changes a trade ─────────
_last_fill = {}
RECORD = False  # main() turns it on for a real "run"; backtests, replays and tests that reuse these functions never write


def record(kind, bot=None, coin=None, **fields):
    """One JSON line per event: buy / sell / half / add / skip / stop_* / run. Failures here never stop trading."""
    if not RECORD:
        return
    try:
        rec = {"utc": now_iso(), "kind": kind, **({"bot_id": bot["id"], "bot": bot["name"], "mode": bot["mode"]} if bot else {}),
               **({"coin": coin} if coin else {}), **fields}
        jdir = os.path.join(HERE, "journal")
        os.makedirs(jdir, exist_ok=True)
        with open(os.path.join(jdir, f"executions-{dt.datetime.now(dt.timezone.utc):%Y-%m}.jsonl"), "a") as f:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":"), default=str) + "\n")
    except Exception as e:
        log(f"  (execution log failed: {e})")


def pct_diff(a, b):
    return round((a / b - 1) * 100, 4) if a and b else None


def okx_buy(api, bot, inst, usdt, bar_ts):
    cl_id = f"{bot['prefix']}B{inst.split('-')[0]}{bar_ts // 1000}"[:32]
    api.post("/api/v5/trade/order", {"instId": inst, "tdMode": "cash", "side": "buy", "ordType": "market",
                                     "tgtCcy": "quote_ccy", "sz": f"{usdt:.2f}", "clOrdId": cl_id})
    o = wait_fill(api, inst, cl_id)
    filled = float(o.get("accFillSz") or 0)
    fee = float(o.get("fee") or 0)  # negative
    qty = filled + fee if o.get("feeCcy") == inst.split("-")[0] else filled
    px = float(o.get("avgPx") or 0)
    _last_fill.update({"avg_px": px, "fee_usdt": round(abs(fee) * (px if o.get("feeCcy") == inst.split("-")[0] else 1), 6),
                       "fee_ccy": o.get("feeCcy"), "ord_id": o.get("ordId"), "state": o.get("state")})
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
    _last_fill.update({"avg_px": px, "fee_usdt": round(abs(fee), 6), "fee_ccy": o.get("feeCcy"), "ord_id": o.get("ordId"),
                       "state": o.get("state")})
    return filled, filled * px + fee


# ───────── Exchange-side stop orders (EXCHANGE_STOPS_PLAN.md) ─────────
# Per-bot switch "exchange_stops": True (demo only for now). OKX then holds a conditional market sell at the stop, so it
# fires the moment price touches it, 24/7. Rules: cancel the bot's stop before ANY sell the bot makes itself; re-sync
# (place / amend) at the end of every run; if the exchange stop fired between runs, record OKX's real fill.
_tick_cache = {}


def exch_stops(bot):
    return bool(bot.get("exchange_stops")) and bot["mode"] == "demo"


def tick_size(api, inst):
    if inst not in _tick_cache:
        d = api.get("/api/v5/public/instruments", {"instType": "SPOT", "instId": inst})[0]
        _tick_cache[inst] = float(d["tickSz"])
    return _tick_cache[inst]


def fmt_step(x, step):
    dec = max(0, -int(math.floor(math.log10(step)))) if step < 1 else 0
    return f"{floor_to(x, step):.{dec}f}"


def stop_place(api, bot, coin, pos):
    lot, _ = inst_info(api, coin)
    tick = tick_size(api, coin)
    sz = floor_to(pos["qty"], lot)
    body = {"instId": coin, "tdMode": "cash", "side": "sell", "ordType": "conditional", "sz": fmt_step(sz, lot),
            "slTriggerPx": fmt_step(pos["stop"], tick), "slOrdPx": "-1", "slTriggerPxType": "last",
            "algoClOrdId": f"{bot['prefix']}X{coin.split('-')[0]}{int(time.time())}"[:32]}
    d = api.post("/api/v5/trade/order-algo", body)[0]
    pos["algo_id"], pos["algo_px"], pos["algo_sz"] = d["algoId"], pos["stop"], sz
    log(f"  {coin}: exchange stop placed at {pos['stop']:.6g} for {sz:.8g} (algo {d['algoId']})")
    record("stop_placed", bot, coin, stop=pos["stop"], qty=sz, algo_id=d["algoId"])


def stop_cancel(api, bot, coin, pos):
    """Cancel this position's exchange stop before the bot sells by itself (so OKX can't sell the same coins too)."""
    if not pos.get("algo_id"):
        return
    try:
        api.post("/api/v5/trade/cancel-algos", [{"algoId": pos["algo_id"], "instId": coin}])
        log(f"  {coin}: exchange stop cancelled (algo {pos['algo_id']})")
        record("stop_cancelled", bot, coin, algo_id=pos["algo_id"])
    except Exception as e:
        log(f"  {coin}: ATTENTION could not cancel exchange stop {pos['algo_id']}: {e}")
    pos["algo_id"] = None


def stop_sync(api, bot, coin, pos):
    """End of run: make OKX's stop match the bot's (place it if missing, amend if the stop rose or the size changed)."""
    try:
        if not pos.get("algo_id"):
            stop_place(api, bot, coin, pos)
            return
        lot, _ = inst_info(api, coin)
        sz = floor_to(pos["qty"], lot)
        moved = pos["stop"] > pos["algo_px"] * 1.001
        resized = abs(sz - pos["algo_sz"]) >= lot
        if moved or resized:
            body = {"instId": coin, "algoId": pos["algo_id"], "newSlTriggerPx": fmt_step(pos["stop"], tick_size(api, coin)),
                    "newSlOrdPx": "-1"}
            if resized:
                body["newSz"] = fmt_step(sz, lot)
            api.post("/api/v5/trade/amend-algos", body)
            pos["algo_px"], pos["algo_sz"] = pos["stop"], sz
            log(f"  {coin}: exchange stop moved to {pos['stop']:.6g}" + (f", size {sz:.8g}" if resized else ""))
            record("stop_moved", bot, coin, stop=pos["stop"], qty=sz, algo_id=pos["algo_id"])
    except Exception as e:
        log(f"  {coin}: ATTENTION exchange stop not in sync ({e}); the hourly check still guards this trade")


def exchange_sold_since(api, coin, since_ms):
    """OKX sells of this coin since since_ms (e.g. a fired exchange stop the bot missed): (qty, proceeds net of fees)
    or None. Proceeds are in USDT; sell fees are charged in USDT (negative)."""
    try:
        fills = api.get("/api/v5/trade/fills", {"instType": "SPOT", "instId": coin}, private=True)
    except Exception as e:
        log(f"  {coin}: could not read OKX fills ({e})")
        return None
    sells = [f for f in fills if f.get("side") == "sell" and int(f.get("ts", 0)) >= since_ms]
    qty = sum(float(f["fillSz"]) for f in sells)
    if qty <= 0:
        return None
    gross = sum(float(f["fillSz"]) * float(f["fillPx"]) for f in sells)
    fees = sum(float(f.get("fee") or 0) for f in sells if f.get("feeCcy", "USDT") != coin.split("-")[0])
    _last_fill.update({"avg_px": gross / qty, "fee_usdt": round(abs(fees), 6), "ord_id": sells[0].get("ordId")})
    return qty, gross + fees


def stop_check(api, bot, bs, coin):
    """Start of run: did OKX's stop fire since the last run? If so, record OKX's real fill and return True."""
    pos = bs["positions"].get(coin)
    if not pos or not pos.get("algo_id"):
        return False
    try:
        pending = api.get("/api/v5/trade/orders-algo-pending", {"ordType": "conditional", "algoId": pos["algo_id"]},
                          private=True)
    except Exception as e:
        # Once a stop has fired, OKX can answer "order does not exist" here instead of an empty list (Oct 7 2026:
        # Trend Rider's SUI stop filled, this raised, and the trade was dropped unrecorded). Go on to the history.
        log(f"  {coin}: exchange stop not pending ({str(e)[:120]}); checking its history")
        pending = None
    if pending:
        return False
    try:
        h = api.get("/api/v5/trade/orders-algo-history", {"ordType": "conditional", "algoId": pos["algo_id"]}, private=True)
    except Exception as e:
        log(f"  {coin}: could not check exchange stop ({e})")
        return False
    state = h[0].get("state") if h else None
    ord_id = (h[0].get("ordId") or (h[0].get("ordIdList") or [None])[0]) if h else None
    if state == "effective" and ord_id:
        o = api.get("/api/v5/trade/order", {"instId": coin, "ordId": ord_id}, private=True)[0]
        filled = float(o.get("accFillSz") or 0)
        px = float(o.get("avgPx") or 0)
        fee = float(o.get("fee") or 0)  # negative, in quote
        if filled > 0:
            pos["algo_id"] = None
            _last_fill.update({"avg_px": px, "fee_usdt": round(abs(fee), 6), "ord_id": h[0].get("ordId")})
            close_position(api, bot, bs, coin, "stop (exchange)", pos["stop"], done=(filled, filled * px + fee))
            return True
    log(f"  {coin}: ATTENTION exchange stop {pos['algo_id']} is {state or 'missing'}; it will be placed again")
    record("stop_problem", bot, coin, algo_id=pos["algo_id"], state=state)
    pos["algo_id"] = None
    return False


# ───────── Opening / closing (demo or paper) ─────────
def risk_pct(bot, bs):
    """The bot's base risk (its "risk" setting, else RISK_PCT). If RISK_STEPS_ON, risk a bit more per trade as the
    practice balance grows so it grows faster, dropping straight back to base if the balance falls 5% from its best."""
    base = bot.get("risk", RISK_PCT)
    eq = bs["equity"]
    bs["peak"] = max(bs.get("peak", eq), eq)
    if not RISK_STEPS_ON or eq < bs["peak"] * 0.95:
        return base
    gain = eq / bot["equity"] - 1
    for need, pct in RISK_STEPS:
        if gain >= need:
            return pct
    return base

def guard_block(bot, bs):
    """GUARD: reason this live bot may not buy, or None. Sets the sticky bs["halted"] on a drawdown breach."""
    if not GUARD["on"] or bot.get("strat") in GUARD["skip_strats"] or bot.get("id") not in {b["id"] for b in BOTS}:
        return None
    if bs.get("halted"):
        return bs["halted"]
    eq = bs["equity"]
    bs["peak"] = max(bs.get("peak", eq), eq)
    if eq < bs["peak"] * (1 - GUARD["max_dd"]):
        bs["halted"] = (f"guard: balance {eq:.2f} is {(1 - eq / bs['peak']) * 100:.1f}% below its best {bs['peak']:.2f} "
                        f"(limit {GUARD['max_dd'] * 100:.0f}%) - halted {ts_iso(time.time() * 1000)}")
        log(f"  GUARD halted {bot['name']}: {bs['halted']}")
        return bs["halted"]
    return None

def open_position(api, bot, bs, coin, bar, inf, extra):
    close = bar["c"]
    sl = inf["sl"]
    if close <= sl:
        return
    why = guard_block(bot, bs)
    if why:
        log(f"  {coin}: signal but {bot['name']} is halted ({why})")
        record("skip", bot, coin, why="halted by guard", detail=why, signal_px=close)
        return
    max_open = bot.get("max_open", MAX_OPEN)
    if len(bs["positions"]) >= max_open:
        log(f"  {coin}: signal but {max_open} trades already open")
        record("skip", bot, coin, why="max open trades", open=len(bs["positions"]), signal_px=close)
        return
    eq = bs["equity"]
    in_use = sum(p["cost"] * p.get("pnl_scale", 1.0) for p in bs["positions"].values())
    free = max(eq - in_use, 0.0)
    qty = min(eq * risk_pct(bot, bs) / (close - sl), free / close)
    usdt = qty * close
    if usdt < 5:
        log(f"  {coin}: signal but order too small ({usdt:.2f})")
        record("skip", bot, coin, why="order too small", usdt=round(usdt, 2), signal_px=close)
        return
    if bot["mode"] == "demo":
        got, px, cost = okx_buy(api, bot, coin, usdt, bar["ts"])
        if got <= 0:
            log(f"  {coin}: buy did not fill")
            record("skip", bot, coin, why="buy did not fill", usdt=round(usdt, 2), signal_px=close)
            return
    else:
        got, px, cost = qty, close, usdt * (1 + FEE)
    pos = {"entry_ts": bar["ts"], "entry_px": px or close, "qty": got, "cost": cost, "sl": sl, "tp": inf["tp"],
           "stop": sl, "limit": inf["tp"], "trail": False, "hi": None}
    pos.update(extra)
    pos["risk_usd"] = round(got * ((px or close) - sl), 4)
    bs["positions"][coin] = pos
    fg = None
    try:
        fg = fear_greed().get(day_of(bar["ts"]) - 1)
    except Exception:
        pass
    record("buy", bot, coin, signal_px=close, fill_px=px or close, slip_pct=pct_diff(px or close, close), qty=got,
           cost=round(cost, 4), fee_usdt=_last_fill.get("fee_usdt") if bot["mode"] == "demo" else round(usdt * FEE, 4),
           stop=sl, stop_dist_pct=round((close - sl) / close * 100, 3), target=inf["tp"], score=inf["score"],
           risk_pct=round(risk_pct(bot, bs) * 100, 3), risk_usd=pos["risk_usd"], equity=bs["equity"],
           open_after=len(bs["positions"]), candle_utc=ts_iso(bar["ts"]), fear_greed=fg,
           order_id=_last_fill.get("ord_id") if bot["mode"] == "demo" else None)
    if exch_stops(bot):
        stop_sync(api, bot, coin, pos)
    tp_txt = f" TP {inf['tp']:.6g}" if inf["tp"] else " (trailing stop)"
    log(f"  BUY {coin} {got:.8g} @ {px:.6g} for {cost:.2f} | SL {sl:.6g}{tp_txt} | {inf['score']}")
    log_trade(bot, coin, "buy", got, px, cost, None, None, f"score {inf['score']}", bs["equity"])


def add_piece(api, bot, bs, coin, bar):
    """Pyramid (Turtle style, research/F10.md): the trade is up 1R at a close, so buy one more piece that risks the
    bot's normal % down to the current stop, then lift the shared stop to at least the first entry. Once per trade."""
    pos = bs["positions"][coin]
    pos["added"] = True
    close = bar["c"]
    if close <= pos["stop"]:
        return
    eq = bs["equity"]
    in_use = sum(p["cost"] * p.get("pnl_scale", 1.0) for p in bs["positions"].values())
    qty = min(eq * risk_pct(bot, bs) / (close - pos["stop"]), max(eq - in_use, 0.0) / close)
    usdt = qty * close
    if usdt >= 5:
        if bot["mode"] == "demo":
            got, px, cost = okx_buy(api, bot, coin, usdt, bar["ts"])
        else:
            got, px, cost = qty, close, usdt * (1 + FEE)
        if got > 0:
            pos["qty"] += got
            pos["cost"] += cost
            pos["add_px"] = px or close
            log(f"  ADD {coin} {got:.8g} @ {px:.6g} for {cost:.2f} (up 1R) | stop now at least entry {pos['entry_px']:.6g}")
            log_trade(bot, coin, "buy", got, px, cost, None, None, "add-on +1R", bs["equity"])
            pos["risk_usd"] = round(pos.get("risk_usd", 0) + got * ((px or close) - pos["stop"]), 4)
            record("add", bot, coin, signal_px=close, fill_px=px or close, slip_pct=pct_diff(px or close, close), qty=got,
                   cost=round(cost, 4), stop=pos["stop"], entry_px=pos["entry_px"],
                   fee_usdt=_last_fill.get("fee_usdt") if bot["mode"] == "demo" else round(usdt * FEE, 4))
        else:
            log(f"  {coin}: add-on buy did not fill")
    else:
        log(f"  {coin}: up 1R but add-on too small ({usdt:.2f})")
    pos["stop"] = max(pos["stop"], pos["entry_px"])


def close_position(api, bot, bs, coin, reason, paper_px, done=None):
    """done = (filled, proceeds) when OKX's own stop order already sold (stop_check)."""
    pos = bs["positions"][coin]
    if done:
        filled, proceeds = done
        px = proceeds / filled
    elif bot["mode"] == "demo":
        stop_cancel(api, bot, coin, pos)
        filled, proceeds = okx_sell(api, bot, coin, pos["qty"])
        if filled <= 0:
            # Nothing left to sell: something already sold these coins (almost always the exchange stop). Record
            # OKX's real sale instead of dropping the trade, so trades.csv, state.json and the balance stay right.
            got = exchange_sold_since(api, coin, pos["entry_ts"])
            if not got:
                log(f"  {coin}: ATTENTION nothing left to sell and no OKX sale found — clearing position unrecorded")
                record("vanished", bot, coin, entry_px=pos["entry_px"], qty=pos["qty"], stop=pos["stop"])
                bs["positions"].pop(coin)
                return
            filled, proceeds = got
            reason = "stop (exchange, found late)"
            log(f"  {coin}: coins were already sold on OKX ({filled:.8g} for {proceeds:.6g}) - recording that sale")
        px = proceeds / filled
    else:
        filled, px = pos["qty"], paper_px
        proceeds = filled * px * (1 - FEE)
    pnl = (proceeds - pos["cost"]) * pos.get("pnl_scale", 1.0)
    bs["equity"] = round(bs["equity"] + pnl, 4)
    pct = (proceeds - pos["cost"]) / pos["cost"] * 100 if pos["cost"] else 0
    log(f"  SELL {coin} {filled:.8g} @ {px:.6g} ({reason}) P/L {pnl:+.2f} ({pct:+.2f}%)")
    log_trade(bot, coin, "sell", filled, px, proceeds, pnl, pct, reason, bs["equity"])
    gross = _last_fill.get("avg_px") if bot["mode"] == "demo" else paper_px  # price before fees
    record("sell", bot, coin, reason=reason, by="exchange stop" if done else "bot", intended_px=paper_px, fill_px=gross,
           slip_pct=pct_diff(gross, paper_px), qty=filled, proceeds=round(proceeds, 4),
           fee_usdt=_last_fill.get("fee_usdt") if bot["mode"] == "demo" else round(filled * px * FEE, 4),
           entry_px=pos["entry_px"], stop=pos["stop"], first_stop=pos["sl"], pnl=round(pnl, 4), pnl_pct=round(pct, 3),
           r_multiple=round(pnl / pos["risk_usd"], 3) if pos.get("risk_usd") else None,
           held_hours=round((time.time() * 1000 - pos["entry_ts"]) / 3600000, 1), added=bool(pos.get("added")),
           half=bool(pos.get("half")), equity_after=bs["equity"])
    bs["positions"].pop(coin)
    sweep_profit(api, bot, bs, pnl)


def stop_reason(pos):
    if pos["stop"] <= pos["sl"]:
        return "stop"
    if pos["stop"] <= pos["entry_px"] * (1 + BE_BUFFER) * 1.0001:
        return "breakeven stop"
    return "trailing stop"

def take_half(api, bot, bs, coin, paper_px):
    """+2R reached: sell half to bank profit, the rest keeps running with its stop."""
    pos = bs["positions"][coin]
    pos["half"] = True
    if bot["mode"] == "demo":
        stop_cancel(api, bot, coin, pos)
        filled, proceeds = okx_sell(api, bot, coin, pos["qty"] / 2)
        if filled <= 0:
            log(f"  {coin}: +2R reached but half is too small to sell - letting it all run")
            return
        px = proceeds / filled
    else:
        filled, px = pos["qty"] / 2, paper_px
        proceeds = filled * px * (1 - FEE)
    part_cost = pos["cost"] * filled / pos["qty"]
    pnl = (proceeds - part_cost) * pos.get("pnl_scale", 1.0)
    bs["equity"] = round(bs["equity"] + pnl, 4)
    pct = (proceeds - part_cost) / part_cost * 100 if part_cost else 0
    pos["qty"] -= filled
    pos["cost"] -= part_cost
    log(f"  HALF {coin} {filled:.8g} @ {px:.6g} (+2R) P/L {pnl:+.2f} ({pct:+.2f}%)")
    record("half", bot, coin, intended_px=paper_px, fill_px=px, slip_pct=pct_diff(px, paper_px), qty=filled,
           pnl=round(pnl, 4), fee_usdt=_last_fill.get("fee_usdt") if bot["mode"] == "demo" else round(filled * px * FEE, 4))
    log_trade(bot, coin, "sell", filled, px, proceeds, pnl, pct, "half profit +2R", bs["equity"])
    sweep_profit(api, bot, bs, pnl)

def check_hit(api, bot, bs, coin, bar):
    """Did this candle touch the resting stop / target? Returns True if the trade was closed."""
    pos = bs["positions"][coin]
    if bar["l"] <= pos["stop"]:
        reason = stop_reason(pos)
        close_position(api, bot, bs, coin, reason, min(pos["stop"], bar["o"]))
        return True
    two_r = pos.get("half_at") or pos["entry_px"] + 2 * (pos["entry_px"] - pos["sl"])
    if (bot.get("half_at_2r", True) and not pos.get("half") and not pos.get("no_half") and pos["entry_px"] > pos["sl"]
            and bar["h"] >= two_r):
        take_half(api, bot, bs, coin, max(two_r, bar["o"]))
        if pos.get("be_after_half") and coin in bs["positions"]:
            pos["stop"] = max(pos["stop"], pos["entry_px"])  # NNFX: the runner's stop goes to breakeven
    if pos.get("limit") and bar["h"] >= pos["limit"]:
        close_position(api, bot, bs, coin, "take profit", max(pos["limit"], bar["o"]))
        return True
    return False


def manage_on_close(api, bot, bs, coin, a, i, bar, bars_in):
    """Update stop/target at a candle close, like the TradingView strategy. True if closed."""
    pos = bs["positions"][coin]
    one_r = pos["entry_px"] - pos["sl"]
    if one_r > 0 and bar["h"] >= pos["entry_px"] + one_r:
        pos["be"] = True  # +1R reached: the stop never goes back below breakeven
    be_floor = max(pos["sl"], pos["entry_px"] * (1 + BE_BUFFER)) if pos.get("be") else pos["sl"]
    if bot["strat"] == "v4":
        pos["hi"] = max(pos["hi"] or bar["h"], bar["h"])
        trail = pos["hi"] >= pos["entry_px"] + one_r
        s = a["sar"][i]
        pos["trail"] = trail
        new = max(be_floor, s) if trail and s is not None and s < bar["c"] else be_floor
        pos["stop"] = max(pos["stop"], new)  # stops only ever move up
        pos["limit"] = None if trail else pos["tp"]
    elif bot["strat"] == "b1":
        pass  # fixed stop and target, as backtested
    elif bot["strat"] == "nnfx":
        if a["exit"][i]:
            close_position(api, bot, bs, coin, "Aroon flipped down", bar["c"])
            return True
        return False
    elif bot["strat"] == "donchian":
        if a["trail"][i] is not None:
            pos["stop"] = max(pos["stop"], a["trail"][i])  # trails at the 10-day low, only ever up
        if bot.get("pyramid") and not pos.get("added") and one_r > 0 and bar["c"] >= pos["entry_px"] + one_r:
            add_piece(api, bot, bs, coin, bar)
        return False
    elif bot["strat"] == "dbottom":
        if a["trail"][i] is not None:
            pos["stop"] = max(pos["stop"], a["trail"][i])  # trails at the 10-day low, only ever up
        return False
    elif bot["strat"] == "confluence":
        if a["exit"][i]:
            close_position(api, bot, bs, coin, f"score faded below 35 ({a['score'][i]:.0f})", bar["c"])
            return True
        if a["trail"][i] is not None:
            pos["stop"] = max(pos["stop"], a["trail"][i])  # 3 ATR under each close, only ever up
        return False
    elif bot["strat"] == "followline":
        if a["exit"][i]:
            close_position(api, bot, bs, coin, "Follow Line turned down", bar["c"])
            return True
        return False
    elif bot["strat"] == "hold":
        if a["exit"][i]:
            close_position(api, bot, bs, coin, f"closed below the {HOLD_SETTINGS['sma']}-day average", bar["c"])
            return True
        return False
    elif bot["strat"] == "pairs":
        if a["exit"].get(pos.get("tag"), [False] * (i + 1))[i]:
            close_position(api, bot, bs, coin, "spread back to normal", bar["c"])
            return True
    elif bot["strat"] == "tr":
        pos["hi"] = max(pos["hi"] or bar["c"], bar["c"])
        trail_stop = pos["hi"] - 3 * a["atr"][i] if a["atr"][i] is not None else be_floor
        pos["stop"] = max(pos["stop"], be_floor, trail_stop)
    else:
        pos["stop"] = max(pos["stop"], be_floor)
    max_bars = {"b1": B1_SETTINGS, "pairs": PAIRS_SETTINGS}.get(bot["strat"], SP_SETTINGS.get(bot["strat"], {})).get("max_bars")
    if max_bars and bars_in >= max_bars:
        close_position(api, bot, bs, coin, "time exit", bar["c"])
        return True
    return False


# ───────── Fear & Greed filter, hold-pile buyer, profit sweeper ─────────
_fng = {}


def fear_greed():
    """{day number: index value}, fetched once per run; {} if the API can't be reached."""
    if "v" not in _fng:
        try:
            with urllib.request.urlopen(urllib.request.Request(FNG_URL, headers={"User-Agent": "sp12-bot"}),
                                        timeout=20) as r:
                _fng["v"] = {day_of(int(x["timestamp"]) * 1000): int(x["value"]) for x in json.loads(r.read())["data"]}
        except Exception as e:
            log(f"Fear & Greed fetch failed: {e}")
            _fng["v"] = {}
    return _fng["v"]


def fear_blocks(bot, bar):
    """True if the bot has a fear filter and the previous day's index is at/below it (or unknown), as backtested."""
    limit = bot.get("fear_skip_at_or_below")
    if limit is None:
        return False
    v = fear_greed().get(day_of(bar["ts"]) - 1)
    return v is None or v <= limit


def hold_log(row):
    new = not os.path.exists(HOLD_FILE)
    with open(HOLD_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["time_utc", "mode", "kind", "coin", "usd", "price", "units", "dip", "sma200",
                        "coin_units_total", "coin_spent_total"])
        w.writerow(row)


def hold_buy(state, coin, usd, px, kind, dip=False, sma200=None):
    """Paper buy for the hold pile (fee included), logged to hold_pile.csv."""
    hp = state.setdefault("hold", {"units": {}, "spent": {}, "last_week": None})
    units = usd / (1 + FEE) / px
    hp["units"][coin] = hp["units"].get(coin, 0.0) + units
    hp["spent"][coin] = hp["spent"].get(coin, 0.0) + usd
    hold_log([now_iso(), DCA["mode"], kind, coin, round(usd, 2), f"{px:.8g}", f"{units:.8g}", dip,
              "" if sma200 is None else f"{sma200:.8g}", f"{hp['units'][coin]:.8g}", round(hp["spent"][coin], 2)])
    return units


def run_dca(api, state):
    """Once per ISO week (first run on or after Monday 00:00 UTC): buy each coin's share of the weekly amount at the
    last completed daily close; double it when that close is 20%+ below the 200-day average."""
    if not DCA["on"]:
        return
    week = dt.datetime.now(dt.timezone.utc).strftime("%G-W%V")
    hp = state.setdefault("hold", {"units": {}, "spent": {}, "last_week": None})
    if hp.get("last_week") == week:
        return
    for coin, w in DCA["coins"].items():
        daily = [d for d in api.candles(coin, "1Dutc", 210) if d["confirm"]]
        if len(daily) < 200:
            log(f"[Hold pile] {coin}: not enough daily candles for the 200-day average - skipped this week")
            continue
        px = daily[-1]["c"]
        sma200 = sum(d["c"] for d in daily[-200:]) / 200
        dip = px <= (1 - DCA["dip_below_200d"]) * sma200
        usd = DCA["weekly_usd"] * w * (DCA["dip_mult"] if dip else 1)
        units = hold_buy(state, coin, usd, px, "weekly DCA", dip, sma200)
        log(f"[Hold pile] {coin}: bought {units:.8g} for {usd:.2f} @ {px:.6g}{' (DIP x2)' if dip else ''} "
            f"| 200-day {sma200:.6g}")
    hp["last_week"] = week


def sweep_profit(api, bot, bs, pnl):
    """If SWEEP is on: move a share of a winning sale out of the bot's balance into the hold pile (paper)."""
    if not SWEEP["on"] or api is None or pnl is None or pnl <= 0 or "_state" not in _hold_ctx:
        return
    amt = SWEEP["share"] * pnl
    bs["equity"] = round(bs["equity"] - amt, 4)
    for coin, w in DCA["coins"].items():
        px = float(api.get("/api/v5/market/ticker", {"instId": coin})[0]["last"])
        hold_buy(_hold_ctx["_state"], coin, amt * w, px, f"sweep from {bot['name']}")
    log(f"  SWEEP {amt:.2f} of the {pnl:.2f} profit to the hold pile")


_hold_ctx = {}


# ───────── Market data (cached per run) ─────────
_data = {}


def get_data(api, venue, coin, tf="4H"):
    key = (venue, coin, tf)
    if key not in _data:
        if tf == "1H":
            raw4, rawd = api.candles(coin, "1H", 400), []
        elif tf in ("1D", "1DL"):  # 1DL: long daily history for Confluence Rank's 233 EMA + 200-day rank
            raw4 = api.candles(coin, "1Dutc", 800 if tf == "1DL" else 220)
            rawd = raw4
        elif venue == "kraken":
            raw4, rawd = kraken_candles(coin, 240), kraken_candles(coin, 1440)
        else:
            # 400 daily candles so the daily 50 EMA is fully warmed up (look-ahead audit, Oct 5 2026)
            raw4, rawd = api.candles(coin, "4H", 500), api.candles(coin, "1Dutc", 400)
        bars = [b for b in raw4 if b["confirm"]]
        forming = raw4[-1] if raw4 and not raw4[-1]["confirm"] else None
        daily = [d for d in rawd if d["confirm"]]
        _data[key] = (bars, forming, daily)
    return _data[key]


def bot_tf(bot):
    return {"b1": "1H", "pairs": "1D", "nnfx": "1D", "donchian": "1D", "hold": "1D", "followline": "1D", "dbottom": "1D",
            "confluence": "1DL"}.get(bot["strat"], "4H")


def analyse_for(api, bot, coin):
    """(timeframe, bars, forming candle, analysis) for one bot + coin, from the live market data."""
    tf = bot_tf(bot)
    bars, forming, daily = get_data(api, bot["venue"], coin, tf)
    if bot["strat"] == "b1":
        a = analyse_b1(bars)
    elif bot["strat"] == "nnfx":
        a = analyse_nnfx(bars)
    elif bot["strat"] == "donchian":
        a = analyse_donchian(bars)
        if bot.get("btc_leash"):
            ok = btc_leash(bars, get_data(api, bot["venue"], "BTC-USDT", "1D")[0], coin)
            a["leash_blocked"] = [s and not o for s, o in zip(a["signal"], ok)]
            a["signal"] = [s and o for s, o in zip(a["signal"], ok)]
    elif bot["strat"] == "hold":
        a = analyse_hold(bars)
    elif bot["strat"] == "followline":
        a = analyse_followline(bars)
    elif bot["strat"] == "dbottom":
        a = analyse_dbottom(bars)
    elif bot["strat"] == "confluence":
        a = analyse_confluence(bars)
    elif bot["strat"] == "pairs":
        btc = get_data(api, bot["venue"], "BTC-USDT", "1D")[0]
        a = analyse_pairs(coin, bars, btc, {alt: get_data(api, bot["venue"], alt, "1D")[0] for alt in bot["pairs"]})
    elif bot["strat"] == "tr":
        a = analyse_tr(bars, daily, bot.get("pivot", 5))
    else:
        a = analyse_sp(bars, daily, SP_SETTINGS[bot["strat"]])
    return tf, bars, forming, a


def entry_extra(bot, bar, inf):
    """Strategy-specific fields stored on a new position."""
    if bot["strat"] == "tr":
        return {"hi": bar["c"]}
    if bot["strat"] == "b1":
        return {"no_half": True}
    if bot["strat"] == "pairs":
        return {"no_half": True, "tag": inf["tag"]}
    if bot["strat"] == "nnfx":
        return {"half_at": inf["half_at"], "be_after_half": True}
    if bot["strat"] in ("donchian", "hold", "followline", "dbottom", "confluence"):
        return {"no_half": True}
    return {}


def run_bot_coin(api, state, bot, coin, trade=True):
    tf, bars, forming, a = analyse_for(api, bot, coin)
    bs = bot_state(state, bot)
    i_last = len(bars) - 1
    inf = a["info"][i_last]
    pos = bs["positions"].get(coin)
    log(f"[{bot['name']}] {coin}: {tf} {ts_iso(bars[i_last]['ts'])} close {bars[i_last]['c']:.6g}"
        + (f" | score {inf['score']} risk {inf['raw_risk']:.2f}% signal={a['signal'][i_last]}" if inf else "")
        + (f" | OPEN from {pos['entry_px']:.6g}, stop {pos['stop']:.6g}" if pos else ""))
    if not trade:
        return

    if exch_stops(bot) and stop_check(api, bot, bs, coin):
        log(f"  {coin}: closed by the exchange stop since the last run")
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
        if coin not in bs["positions"] and a["signal"][k] and k == i_last and bot.get("new_trades", True):
            if fear_blocks(bot, b):
                log(f"  {coin}: signal skipped - Fear & Greed at or below {bot['fear_skip_at_or_below']} (or unavailable)")
                record("skip", bot, coin, why="fear filter", signal_px=b["c"], candle_utc=ts_iso(b["ts"]),
                       fear_greed=fear_greed().get(day_of(b["ts"]) - 1))
            else:
                open_position(api, bot, bs, coin, b, a["info"][k], entry_extra(bot, b, a["info"][k]))
        if a.get("leash_blocked") and a["leash_blocked"][k] and k == i_last and coin not in bs["positions"]:
            record("skip", bot, coin, why="BTC leash (BTC below its daily 50 EMA)", signal_px=b["c"], candle_utc=ts_iso(b["ts"]))
        bs["last_bar"][coin] = b["ts"]

    if coin in bs["positions"] and forming and forming["ts"] > bs["positions"][coin]["entry_ts"]:
        check_hit(api, bot, bs, coin, forming)
    if exch_stops(bot) and coin in bs["positions"]:
        stop_sync(api, bot, coin, bs["positions"][coin])


def retired_and_flat(state, bot):
    """A retired bot keeps running only until its last open trade is closed."""
    return bool(bot.get("retired")) and not state["bots"].get(bot["id"], {}).get("positions")


def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "run").lower()
    key, sec, pw = (os.environ.get(k, "") for k in ("OKX_API_KEY", "OKX_API_SECRET", "OKX_API_PASSPHRASE"))
    api = OKX(key, sec, pw)
    log(f"Jeff's demo bots | mode={mode} | {BASE_URL} | {now_iso()} UTC")
    state = migrate_budget(load_state())

    if mode == "check":
        for bot in BOTS:
            if retired_and_flat(state, bot):
                continue
            for coin in bot["coins"]:
                try:
                    run_bot_coin(api, state, bot, coin, trade=False)
                except Exception as e:
                    log(f"[{bot['name']}] {coin}: ERROR {e}")
        bal = api.get("/api/v5/account/balance", {"ccy": "USDT"}, private=True)[0]["details"]
        log(f"Demo account connected. USDT available: {bal[0]['availBal'] if bal else 0}")
        return

    have_keys = bool(key and sec and pw)
    global RECORD
    RECORD = True
    _hold_ctx["_state"] = state
    try:
        run_dca(api, state)
    except Exception as e:
        log(f"[Hold pile] ERROR {e}")
    save_state(state)
    errors = total = 0
    for bot in BOTS:
        if retired_and_flat(state, bot):
            continue
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
    snap = {}
    for bot in BOTS:
        bs = state["bots"].get(bot["id"])
        if bs:
            log(f"{bot['name']}: balance {bs['equity']:.2f} | open: {', '.join(bs['positions']) or 'none'}")
            if not bot.get("retired") or bs["positions"]:
                snap[bot["id"]] = {"equity": bs["equity"], "open": {c: {"entry": p["entry_px"], "stop": p["stop"], "qty": p["qty"]}
                                                                    for c, p in bs["positions"].items()}}
    usdt = None
    if have_keys:
        try:
            d = api.get("/api/v5/account/balance", {"ccy": "USDT"}, private=True)[0]["details"]
            usdt = float(d[0]["availBal"]) if d else 0.0
        except Exception:
            pass
    record("run", bots=snap, demo_usdt_available=usdt, errors=errors, coin_runs=total)
    if total and errors == total:
        sys.exit(1)


if __name__ == "__main__":
    main()
