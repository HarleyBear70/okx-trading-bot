"""
Trade journal for Jeff's bots. GitHub runs it right after bot.py, every hour.

It NEVER places or cancels orders. It reloads the same candles the bots used and writes
down, in detail, what each bot saw and why it did (or didn't) trade, so Claude can
review it and decide on changes.

Files it keeps (all inside the journal/ folder):
  decisions-YYYY-MM.jsonl  one line per bot + coin for every new 4H candle, plus a line for every buy/sell
  trades.json              every trade (open and closed) with entry reasons, exit reason,
                           best/worst price during the trade, R multiple, testing vs live
  summary.json             report card per bot and per coin, and what every bot sees right now
  state.json               bookkeeping (last candle journaled, trade rows already read)
  changes.json             hand-written log of every settings change (Claude adds to it, the journal
                           never edits it), copied into summary.json for before/after checks
"""

import csv
import datetime as dt
import json
import math
import os
import sys
import traceback

import bot

H4 = bot.H4_MS
HERE = os.path.dirname(os.path.abspath(__file__))
JDIR = os.path.join(HERE, "journal")
JSTATE = os.path.join(JDIR, "state.json")
CHART_COIN = {"XBTUSD": "BTC-USDT", "ETHUSD": "ETH-USDT", "SOLUSD": "SOL-USDT", "XRPUSD": "XRP-USDT"}
BOT_BY_NAME = {b["name"]: b for b in bot.BOTS}
BOT_BY_ID = {b["id"]: b for b in bot.BOTS}


def iso(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def parse_iso(s):
    return int(dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def r(x, n=6):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return float(f"{x:.{n}g}")


def pct(a, b):
    return None if a is None or b in (None, 0) else round((a - b) / b * 100, 3)


def testing_or_live(mode):
    return "testing" if mode in ("demo", "paper") else "live"


def fmt(p):
    return "?" if p is None else f"{p:,.6g}"


# ───────── shared indicators for one coin ─────────
def base_indicators(bars, daily):
    o = [b["o"] for b in bars]; h = [b["h"] for b in bars]; l = [b["l"] for b in bars]
    c = [b["c"] for b in bars]; v = [b["v"] for b in bars]; n = len(bars)
    m12, m26 = bot.ema(c, 12), bot.ema(c, 26)
    macd = [a - b if a is not None and b is not None else None for a, b in zip(m12, m26)]
    sig_src = [x for x in macd if x is not None]
    sig = [None] * (n - len(sig_src)) + bot.ema(sig_src, 9)
    hist = [a - b if a is not None and b is not None else None for a, b in zip(macd, sig)]
    vwap, cum_pv, cum_v, cur_day = [None] * n, 0.0, 0.0, None
    for i in range(n):
        dday = bot.day_of(bars[i]["ts"])
        if dday != cur_day:
            cum_pv, cum_v, cur_day = 0.0, 0.0, dday
        cum_pv += (h[i] + l[i] + c[i]) / 3 * v[i]
        cum_v += v[i]
        vwap[i] = cum_pv / cum_v if cum_v else c[i]
    dc = [d["c"] for d in daily]
    return {
        "o": o, "h": h, "l": l, "c": c, "v": v, "n": n,
        "e8": bot.ema(c, 8), "e21": bot.ema(c, 21), "e50": bot.ema(c, 50), "e55": bot.ema(c, 55),
        "e200": bot.ema(c, 200), "rsi": bot.rsi(c, 14), "atr": bot.atr(h, l, c, 14),
        "stdir": bot.supertrend(h, l, c, 3, 10), "macd": macd, "hist": hist, "vwap": vwap,
        "vol20": bot.sma(v, 20), "sar": bot.psar(h, l, c, bot.SAR_START, bot.SAR_INC, bot.SAR_MAX),
        "low10": bot.lowest(l, 10), "dc": dc, "de20": bot.ema(dc, 20), "de50": bot.ema(dc, 50),
        "drsi": bot.rsi(dc, 14), "dk": bot.daily_lookup(bars, daily),
    }


def context(ind, i):
    """Everything worth knowing about one closed 4H candle, beyond the strategy's own checks."""
    c = ind["c"][i]
    k = ind["dk"][i]
    vol_ratio = ind["v"][i] / ind["vol20"][i] if ind["vol20"][i] else None
    atr_v = ind["atr"][i]
    return {
        "open": r(ind["o"][i]), "high": r(ind["h"][i]), "low": r(ind["l"][i]), "close": r(c),
        "candle_change_pct": pct(c, ind["o"][i]),
        "volume_vs_20avg": None if vol_ratio is None else round(vol_ratio, 2),
        "rsi14": None if ind["rsi"][i] is None else round(ind["rsi"][i], 1),
        "ema8": r(ind["e8"][i]), "ema21": r(ind["e21"][i]), "ema50": r(ind["e50"][i]),
        "ema55": r(ind["e55"][i]), "ema200": r(ind["e200"][i]),
        "pct_from_ema50": pct(c, ind["e50"][i]), "pct_from_ema200": pct(c, ind["e200"][i]),
        "supertrend": None if ind["stdir"][i] is None else ("green/up" if ind["stdir"][i] < 0 else "red/down"),
        "macd_hist": r(ind["hist"][i]), "macd_hist_prev": r(ind["hist"][i - 1]) if i else None,
        "vwap": r(ind["vwap"][i]), "atr14": r(atr_v), "atr_pct": pct(c + atr_v, c) if atr_v else None,
        "psar": r(ind["sar"][i]),
        "daily_close": r(ind["dc"][k]) if k is not None else None,
        "daily_ema20": r(ind["de20"][k]) if k is not None else None,
        "daily_ema50": r(ind["de50"][k]) if k is not None else None,
        "daily_rsi14": round(ind["drsi"][k], 1) if k is not None and ind["drsi"][k] is not None else None,
    }


# ───────── SP-12 (v4 / v2): same rules as bot.analyse_sp, but every check is kept ─────────
def detail_sp(bars, daily, cfg, ind, wanted):
    o, h, l, c = ind["o"], ind["h"], ind["l"], ind["c"]
    n = ind["n"]
    dc, de, dk = ind["dc"], ind["de20"], ind["dk"]
    e50, stdir, e8, e21, e55, hist = ind["e50"], ind["stdir"], ind["e8"], ind["e21"], ind["e55"], ind["hist"]
    low10, vwap = ind["low10"], ind["vwap"]
    L = cfg["pivot"]
    if cfg["pivot_fn"] == "ge":
        ph, pl = bot.pivots_ge(h, L, True), bot.pivots_ge(l, L, False)
    else:
        ph, pl = bot.pivots(h, L, True), bot.pivots(l, L, False)
    last_ph = last_pl = None
    bos_bar = sweep_bar = ob_bar = fvg_bar = None
    ob_top = ob_bot = fvg_top = fvg_bot = None
    out = {}
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
        if i not in wanted:
            continue
        if i < 1 or None in (e50[i - 1], stdir[i - 1], e55[i], hist[i], hist[i - 1], low10[i]):
            out[i] = {"ready": False}
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
        ema_stack = e8[i] > e21[i] > e55[i]
        above_vwap = c[i] > vwap[i]
        filt = (ema_stack and above_vwap) if cfg["filters"] else True
        swing_stop = low10[i] * (1 - 0.001)
        raw_risk = (c[i] - swing_stop) / c[i] * 100
        risk_use = max(raw_risk, cfg["min_risk"])
        tp_pct = min(max(cfg["rr"] * risk_use, cfg["tp_min"]), cfg["tp_max"])
        enough = i + 1 >= cfg["min_bars"]
        risk_ok = raw_risk <= cfg["max_risk"]
        signal = bool(enough and c2 and filt and score >= 2 and risk_ok)

        checks = [
            {"key": "daily_trend", "points": +1, "passed": c1,
             "plain": "Daily trend up: yesterday's daily close above a rising 20-day EMA"},
            {"key": "liquidity_sweep", "points": +1, "passed": c7,
             "plain": "Liquidity sweep in the last 10 candles: price dipped under a swing low and closed back above it"},
            {"key": "supertrend_green", "points": +1, "passed": c11, "plain": "Supertrend is green on this candle"},
            {"key": "macd_rising", "points": +1, "passed": c12, "plain": "MACD histogram rising (momentum picking up)"},
            {"key": "recent_bos", "points": -1, "passed": c3,
             "plain": "Break of structure in the last 20 candles (the tested settings count this AGAINST a buy)"},
            {"key": "in_fvg", "points": -1, "passed": c5,
             "plain": "Price dipping into a recent fair value gap (counted against)"},
            {"key": "in_order_block", "points": -1, "passed": c6,
             "plain": "Price retesting the order block before the last BOS (counted against)"},
            {"key": "reversal_candle", "points": -1, "passed": c10,
             "plain": "Bullish engulfing or hammer candle (counted against)"},
        ]
        gates = [
            {"key": "trend_gate", "passed": c2,
             "plain": "Required: previous candle closed above the 50 EMA with Supertrend green"},
            {"key": "score", "passed": score >= 2, "plain": f"Required: score of 2 or more (got {score})"},
            {"key": "risk", "passed": risk_ok,
             "plain": f"Required: stop no more than {cfg['max_risk']}% away (it was {raw_risk:.2f}%)"},
        ]
        if cfg["filters"]:
            gates.append({"key": "ema_stack", "passed": ema_stack,
                          "plain": "Required: EMAs stacked up (8 above 21 above 55)"})
            gates.append({"key": "above_vwap", "passed": above_vwap, "plain": "Required: price above daily VWAP"})
        if not enough:
            gates.append({"key": "history", "passed": False, "plain": "Not enough candle history yet"})

        failed = [g["plain"].replace("Required: ", "") for g in gates if not g["passed"]]
        plus = [x["plain"] for x in checks if x["passed"] and x["points"] > 0]
        minus = [x["plain"] for x in checks if x["passed"] and x["points"] < 0]
        if signal:
            why = (f"BUY signal. Score {score} (needed 2). Points for: {'; '.join(plus) or 'none'}."
                   + (f" Points against: {'; '.join(minus)}." if minus else "")
                   + f" Stop {raw_risk:.2f}% below, target {tp_pct:.2f}% above.")
        else:
            why = f"No buy. Missing: {'; '.join(failed)}. Score {score} (needed 2)."
            if plus:
                why += f" Points for: {'; '.join(plus)}."
            if minus:
                why += f" Points against: {'; '.join(minus)}."
        near_miss = (not signal) and len(failed) == 1
        out[i] = {
            "ready": True, "signal": signal, "score": score, "score_needed": 2,
            "checks": checks, "gates": gates, "near_miss": near_miss,
            "swing": {"last_swing_high": r(last_ph), "last_swing_low": r(last_pl),
                      "candles_since_bos": None if bos_bar is None else i - bos_bar,
                      "candles_since_sweep": None if sweep_bar is None else i - sweep_bar,
                      "fvg": None if fvg_bar is None else [r(fvg_bot), r(fvg_top)],
                      "order_block": None if ob_top is None else [r(ob_bot), r(ob_top)]},
            "risk": {"stop_distance_pct": round(raw_risk, 3), "stop_used_pct": round(risk_use, 3),
                     "target_pct": round(tp_pct, 3), "planned_stop": r(c[i] * (1 - risk_use / 100)),
                     "planned_target": r(c[i] * (1 + tp_pct / 100)), "reward_to_risk": round(tp_pct / risk_use, 2)},
            "why": why,
        }
    return out


# ───────── Trend Rider ─────────
def detail_tr(bars, daily, L, ind, wanted):
    h, l, c, n = ind["h"], ind["l"], ind["c"], ind["n"]
    e50, a = ind["e50"], ind["atr"]
    dc, de, dk = ind["dc"], ind["de50"], ind["dk"]
    ph_l, pl_l = bot.pivots_ge(h, L, True), bot.pivots_ge(l, L, False)
    ph = pl = None
    out = {}
    for i in range(n):
        if ph_l[i] is not None:
            ph = ph_l[i]
        if pl_l[i] is not None:
            pl = pl_l[i]
        if i not in wanted:
            continue
        if i < 1 or a[i] is None or e50[i] is None:
            out[i] = {"ready": False}
            continue
        k = dk[i]
        daily_ok = bool(k is not None and de[k] is not None and dc[k] > de[k])
        bos = ph is not None and c[i] > ph and c[i - 1] <= ph
        above = c[i] > e50[i]
        enough = i + 1 >= 61
        signal = bool(enough and bos and above and daily_ok)
        s = pl * 0.998 if pl is not None else c[i] - 2 * a[i]
        s = min(max(s, c[i] - 3 * a[i]), c[i] - 1 * a[i])
        risk = (c[i] - s) / c[i] * 100
        gates = [
            {"key": "daily_trend", "passed": daily_ok, "plain": "Required: daily close above the 50-day EMA"},
            {"key": "above_ema50", "passed": above, "plain": "Required: 4H close above the 50 EMA"},
            {"key": "bos", "passed": bos,
             "plain": f"Required: candle closes above the last swing high ({fmt(ph)}) - a break of structure"},
        ]
        if not enough:
            gates.append({"key": "history", "passed": False, "plain": "Not enough candle history yet"})
        failed = [g["plain"].replace("Required: ", "") for g in gates if not g["passed"]]
        if signal:
            why = (f"BUY signal: broke above the swing high {fmt(ph)} with the daily and 4H trend up. "
                   f"Stop {risk:.2f}% below at {fmt(s)}; no fixed target - a trailing stop 3 ATR under the "
                   f"highest close follows the trend.")
        else:
            why = f"No buy. Missing: {'; '.join(failed)}."
        out[i] = {
            "ready": True, "signal": signal, "score": "BOS" if bos else "-", "checks": [], "gates": gates,
            "near_miss": (not signal) and len(failed) == 1,
            "swing": {"last_swing_high": r(ph), "last_swing_low": r(pl),
                      "pct_to_swing_high": pct(ph, c[i]) if ph else None},
            "risk": {"stop_distance_pct": round(risk, 3), "planned_stop": r(s), "target_pct": None,
                     "trail": "3 x ATR below highest close"},
            "why": why,
        }
    return out


def compact(d):
    """Checks and gates as {key: passed}; their meanings are written once in summary.json."""
    d = dict(d)
    for k in ("checks", "gates"):
        for x in d.get(k, []):
            MEANINGS.setdefault(x["key"], {"meaning": x["plain"].split(" (got")[0].split(" (it was")[0],
                                           "points": x.get("points")})
        d[k] = {x["key"]: bool(x["passed"]) for x in d.get(k, [])}
    return d


MEANINGS = {}


# ───────── per bot + coin ─────────
_cache = {}


def coin_frame(api, b, coin):
    key = (b["venue"], coin)
    if key not in _cache:
        bars, forming, daily = bot.get_data(api, b["venue"], coin)
        _cache[key] = (bars, forming, daily, base_indicators(bars, daily))
    return _cache[key]


def detail_for(api, b, coin, wanted_idx):
    if b["strat"] not in ("tr", "v4", "v2"):
        return {}  # e.g. the B1c paper bot (1H candles): no per-candle notes, its trades are still journaled
    bars, forming, daily, ind = coin_frame(api, b, coin)
    if b["strat"] == "tr":
        d = detail_tr(bars, daily, b.get("pivot", 5), ind, set(wanted_idx))
    else:
        d = detail_sp(bars, daily, bot.SP_SETTINGS[b["strat"]], ind, set(wanted_idx))
    for i in wanted_idx:
        if i in d:
            d[i]["market"] = context(ind, i)
    return d


def bar_index(bars, ts):
    for k in range(len(bars) - 1, -1, -1):
        if bars[k]["ts"] == ts:
            return k
    return None


def entry_bar_for_time(ms):
    """A trade filled at time T was decided on the last 4H candle that had CLOSED by T."""
    return (ms // H4) * H4 - H4


# ───────── trades.csv ─────────
def read_trade_rows():
    if not os.path.exists(bot.TRADES_FILE):
        return []
    with open(bot.TRADES_FILE, newline="") as f:
        return list(csv.DictReader(f))


def fnum(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


EXIT_PLAIN = {
    "stop": "Price fell to the stop-loss, so the bot sold to cap the loss.",
    "trailing stop": "Price came back down to the trailing stop after moving up - the bot locked in what it could.",
    "take profit": "Price reached the profit target and the bot sold.",
    "half profit +2R": "Price reached 2x the risk, so the bot sold half to bank profit and let the rest run.",
    "breakeven stop": "Price reached +1R, then came back to the entry - the bot got out about even instead of taking a loss.",
    "time exit": "The trade ran out of time (held the maximum number of candles) and was closed at market.",
}


def build_trades(api, state):
    rows = read_trade_rows()
    trades, open_by = [], {}
    for n, row in enumerate(rows):
        b = BOT_BY_NAME.get(row["bot"])
        if not b:
            continue
        key = (b["id"], row["coin"])
        t = parse_iso(row["time_utc"])
        if row["side"] == "buy" and key in open_by and (row.get("reason") or "").startswith("add-on"):
            tr = open_by[key]  # pyramid add-on: same trade, one more piece
            tr["qty"] = (tr.get("qty") or 0) + (fnum(row["qty"]) or 0)
            tr["cost"] = (tr.get("cost") or 0) + (fnum(row["usdt"]) or 0)
            tr["add_time"], tr["add_px"] = row["time_utc"], fnum(row["price"])
        elif row["side"] == "buy":
            tr = {"id": f"{b['id']}|{row['coin']}|{row['time_utc']}", "bot_id": b["id"], "bot": b["name"],
                  "strategy": b["strat"], "mode": row.get("mode") or b["mode"],
                  "coin": row["coin"], "chart_coin": CHART_COIN.get(row["coin"], row["coin"]),
                  "entry_time": row["time_utc"], "entry_ms": t, "entry_px": fnum(row["price"]),
                  "qty": fnum(row["qty"]), "cost": fnum(row["usdt"]), "entry_note": row.get("reason"),
                  "status": "open", "csv_row": n}
            tr["side_group"] = testing_or_live(tr["mode"])
            trades.append(tr)
            open_by[key] = tr
        elif row["side"] == "sell" and key in open_by and (row.get("reason") or "").startswith("half"):
            tr = open_by[key]
            tr["half_pnl"] = (tr.get("half_pnl") or 0) + (fnum(row["pnl_usdt"]) or 0)
            tr["half_time"], tr["half_px"] = row["time_utc"], fnum(row["price"])
        elif row["side"] == "sell" and key in open_by:
            tr = open_by.pop(key)
            pnl = (fnum(row["pnl_usdt"]) or 0) + (tr.get("half_pnl") or 0)
            tr.update({"status": "closed", "exit_time": row["time_utc"], "exit_ms": t,
                       "exit_px": fnum(row["price"]), "proceeds": fnum(row["usdt"]), "pnl": pnl,
                       "pnl_pct": fnum(row["pnl_pct"]), "exit_reason": row["reason"],
                       "exit_plain": EXIT_PLAIN.get(row["reason"], row["reason"]),
                       "result": "win" if (pnl or 0) > 0 else "loss", "balance_after": fnum(row["bot_balance"])})

    for tr in trades:
        b = BOT_BY_ID[tr["bot_id"]]
        try:
            bars, forming, daily, ind = coin_frame(api, b, tr["coin"])
        except Exception as e:
            tr["journal_error"] = str(e)[:200]
            continue
        pos = state.get("bots", {}).get(b["id"], {}).get("positions", {}).get(tr["coin"])
        if tr["status"] == "open" and pos:
            tr.update({"entry_bar_ms": pos["entry_ts"], "stop_now": r(pos.get("stop")), "planned_stop": r(pos.get("sl")),
                       "planned_target": r(pos.get("tp")), "trailing_on": bool(pos.get("trail"))})
        else:
            tr["entry_bar_ms"] = entry_bar_for_time(tr["entry_ms"])
        ei = bar_index(bars, tr["entry_bar_ms"])
        tr["entry_bar_time"] = iso(tr["entry_bar_ms"])
        if ei is not None:
            d = detail_for(api, b, tr["coin"], [ei]).get(ei, {})
            tr["entry_decision"] = d
            tr["why_entry"] = d.get("why")
            if "planned_stop" not in tr and d.get("risk"):
                tr["planned_stop"] = d["risk"].get("planned_stop")
                tr["planned_target"] = d["risk"].get("planned_target")
        end_ms = tr.get("exit_ms") or (bars[-1]["ts"] + H4)
        during = [x for x in bars + ([forming] if forming else []) if tr["entry_bar_ms"] < x["ts"] + H4 and x["ts"] <= end_ms]
        during = [x for x in during if x["ts"] > tr["entry_bar_ms"]]
        ep = tr["entry_px"]
        if during and ep:
            hi = max(x["h"] for x in during)
            lo = min(x["l"] for x in during)
            tr["best_pct"] = pct(hi, ep)
            tr["worst_pct"] = pct(lo, ep)
            tr["best_px"], tr["worst_px"] = r(hi), r(lo)
            tr["candles_held"] = len(during)
        if ep and tr.get("planned_stop") and ep > tr["planned_stop"]:
            risk_per = ep - tr["planned_stop"]
            tr["risk_pct"] = round(risk_per / ep * 100, 3)
            if tr["status"] == "closed" and tr.get("exit_px"):
                tr["r_multiple"] = round((tr["exit_px"] - ep) / risk_per, 2)
            if tr.get("best_px"):
                tr["best_r"] = round((tr["best_px"] - ep) / risk_per, 2)
        if tr["status"] == "open":
            last = (forming or bars[-1])["c"]
            tr["price_now"] = r(last)
            tr["unrealized_pct"] = pct(last, ep)
            tr["result"] = "open"
        if tr["status"] == "closed" and tr["result"] == "loss" and (tr.get("best_pct") or 0) >= 1:
            tr["note"] = f"This loser was up {tr['best_pct']:.2f}% at its best before turning around."
    return trades


# ───────── summary ─────────
def stats(ts):
    closed = [t for t in ts if t["status"] == "closed"]
    wins = [t for t in closed if t["result"] == "win"]
    losses = [t for t in closed if t["result"] == "loss"]
    gw = sum(t["pnl"] or 0 for t in wins)
    gl = -sum(t["pnl"] or 0 for t in losses)
    rs = [t["r_multiple"] for t in closed if t.get("r_multiple") is not None]
    held = [t["candles_held"] for t in closed if t.get("candles_held")]
    return {
        "trades": len(ts), "open": len(ts) - len(closed), "closed": len(closed),
        "wins": len(wins), "losses": len(losses),
        "win_rate_pct": round(len(wins) / len(closed) * 100, 1) if closed else None,
        "total_pnl": round(gw - gl, 2),
        "avg_win": round(gw / len(wins), 2) if wins else None,
        "avg_loss": round(-gl / len(losses), 2) if losses else None,
        "profit_factor": round(gw / gl, 2) if gl else None,
        "avg_r": round(sum(rs) / len(rs), 2) if rs else None,
        "avg_candles_held": round(sum(held) / len(held), 1) if held else None,
        "losers_that_were_green_first": sum(1 for t in losses if (t.get("best_pct") or 0) >= 1),
    }


def build_summary(trades, latest, state, signal_counts):
    by_bot = {}
    for b in bot.BOTS:
        mine = [t for t in trades if t["bot_id"] == b["id"]]
        bs = state.get("bots", {}).get(b["id"], {})
        by_bot[b["id"]] = {
            "name": b["name"], "mode": b["mode"], "group": testing_or_live(b["mode"]), "strategy": b["strat"],
            "start_balance": b["equity"], "balance": bs.get("equity", b["equity"]),
            "open_positions": list(bs.get("positions", {}).keys()),
            "all": stats(mine),
            "by_coin": {c: stats([t for t in mine if t["coin"] == c]) for c in b["coins"]},
            "signals_seen": signal_counts.get(b["id"], {}),
        }
    return {"updated_utc": bot.now_iso(), "bots": by_bot, "now": latest,
            "totals": {"testing": stats([t for t in trades if t["side_group"] == "testing"]),
                       "live": stats([t for t in trades if t["side_group"] == "live"])}}


# ───────── main ─────────
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def append_lines(recs):
    if not recs:
        return
    path = os.path.join(JDIR, f"decisions-{dt.datetime.now(dt.timezone.utc):%Y-%m}.jsonl")
    with open(path, "a") as f:
        for rec in recs:
            f.write(json.dumps(rec, sort_keys=True, separators=(",", ":")) + "\n")


def market_backdrop(api):
    """BTC's 4H and daily picture - most coins follow it."""
    try:
        b = {"venue": "okx"}
        bars, forming, daily, ind = coin_frame(api, b, "BTC-USDT")
        i = len(bars) - 1
        k = ind["dk"][i]
        return {"btc_close": r(ind["c"][i]), "btc_4h_supertrend": context(ind, i)["supertrend"],
                "btc_above_4h_ema50": ind["c"][i] > ind["e50"][i],
                "btc_above_daily_ema50": bool(k is not None and ind["de50"][k] and ind["dc"][k] > ind["de50"][k]),
                "btc_rsi14": context(ind, i)["rsi14"]}
    except Exception as e:
        return {"error": str(e)[:200]}


def main():
    os.makedirs(JDIR, exist_ok=True)
    api = bot.OKX(*(os.environ.get(k, "") for k in ("OKX_API_KEY", "OKX_API_SECRET", "OKX_API_PASSPHRASE")))
    jstate = load_json(JSTATE, {"last_bar": {}, "rows_seen": 0, "signal_counts": {}})
    state = load_json(bot.STATE_FILE, {"bots": {}})
    now = bot.now_iso()
    backdrop = market_backdrop(api)
    recs, latest, errors = [], {}, 0

    for b in bot.BOTS:
        bs = state.get("bots", {}).get(b["id"], {})
        for coin in b["coins"]:
            key = f"{b['id']}|{coin}"
            try:
                bars, forming, daily, ind = coin_frame(api, b, coin)
                last = jstate["last_bar"].get(key, 0)
                new_idx = [k for k, x in enumerate(bars) if x["ts"] > last][-6:]
                if not last:
                    new_idx = [len(bars) - 1]
                details = detail_for(api, b, coin, new_idx)
                pos = bs.get("positions", {}).get(coin)
                for i in new_idx:
                    d = details.get(i, {})
                    if not d.get("ready"):
                        continue
                    ts = bars[i]["ts"]
                    if pos and pos.get("entry_ts") == ts:
                        action = "BOUGHT"
                    elif pos and pos.get("entry_ts", 0) < ts:
                        action = "HOLDING"
                    elif d["signal"]:
                        action = "SIGNAL (no buy - already in a trade, order too small, or error; see bot log)"
                    else:
                        action = "NO TRADE"
                    rec = {"type": "candle", "logged_utc": now, "candle_utc": iso(ts), "candle_ms": ts,
                           "bot_id": b["id"], "bot": b["name"], "strategy": b["strat"], "mode": b["mode"],
                           "group": testing_or_live(b["mode"]), "coin": coin,
                           "chart_coin": CHART_COIN.get(coin, coin), "action": action, **compact(d), "btc": backdrop}
                    if pos:
                        rec["position"] = {"entry_px": r(pos["entry_px"]), "stop": r(pos.get("stop")),
                                           "target": r(pos.get("limit")), "trailing": bool(pos.get("trail")),
                                           "unrealized_pct": pct(bars[i]["c"], pos["entry_px"])}
                    recs.append(rec)
                    sc = jstate["signal_counts"].setdefault(b["id"], {"candles": 0, "signals": 0, "near_misses": 0})
                    sc["candles"] += 1
                    sc["signals"] += int(bool(d["signal"]))
                    sc["near_misses"] += int(bool(d.get("near_miss")))
                    latest[key] = {k: rec[k] for k in ("candle_utc", "bot", "coin", "chart_coin", "action", "why",
                                                       "score", "mode", "group") if k in rec}
                    latest[key]["close"] = rec["market"]["close"]
                    latest[key]["rsi14"] = rec["market"]["rsi14"]
                jstate["last_bar"][key] = bars[-1]["ts"]
            except Exception as e:
                errors += 1
                bot.log(f"[journal] {key}: ERROR {e}")
                traceback.print_exc()

    rows = read_trade_rows()
    for row in rows[jstate.get("rows_seen", 0):]:
        b = BOT_BY_NAME.get(row["bot"], {})
        recs.append({"type": "trade", "logged_utc": now, "bot_id": b.get("id"), "bot": row["bot"],
                     "mode": row.get("mode"), "group": testing_or_live(row.get("mode")), "coin": row["coin"],
                     "side": row["side"], "time_utc": row["time_utc"], "price": fnum(row["price"]),
                     "qty": fnum(row["qty"]), "usdt": fnum(row["usdt"]), "pnl": fnum(row.get("pnl_usdt")),
                     "pnl_pct": fnum(row.get("pnl_pct")), "reason": row.get("reason"),
                     "plain": EXIT_PLAIN.get(row.get("reason"), "Bot bought: " + (row.get("reason") or ""))})
    jstate["rows_seen"] = len(rows)

    trades = build_trades(api, state)
    append_lines(recs)
    write_json(os.path.join(JDIR, "trades.json"), trades)
    write_json(os.path.join(JDIR, "summary.json"),
               build_summary(trades, latest, state, jstate["signal_counts"]) | {"btc": backdrop, "check_meanings": MEANINGS,
               "changes": load_json(os.path.join(JDIR, "changes.json"), [])})
    write_json(JSTATE, jstate)
    bot.log(f"[journal] {len([x for x in recs if x['type'] == 'candle'])} candle notes, "
            f"{len([x for x in recs if x['type'] == 'trade'])} trade notes, {len(trades)} trades on file, {errors} errors")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(0)  # the journal must never make the bot's run fail
