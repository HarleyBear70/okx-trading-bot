"""
The Analyst's paper ledger (Oct 6 2026). The Analyst is Claude trading on judgment, on paper, to see whether it beats
the rule-based bots. Its risk rules live HERE, in code, so a judgment call can never break them:
  - paper only, long only, no leverage; coins: BTC ETH SOL XRP BNB LINK (OKX USDT prices)
  - every buy needs a stop below the price; risk per trade at most 0.5% of the balance (sized here, not by the Analyst)
  - at most 3 trades open, one per coin, never more than the free cash
  - stops can only be raised, never lowered
  - real fee 0.35% on every buy and sell
  - guard: 12% below the best balance -> no new buys until Jeff says resume (like bot.py GUARD)

Commands:
  python analyst/ledger.py status
  python analyst/ledger.py buy BTC --stop 84000 [--target 92000] [--risk 0.5] --why "..." --wrong "..."
  python analyst/ledger.py order BTC --above 87500 --stop 84900 [--hours 72] --why "..." --wrong "..."
  python analyst/ledger.py order LINK --below 13.55 --stop 12.9 --why "..." --wrong "..."
  python analyst/ledger.py cancel BTC
  python analyst/ledger.py stop BTC 85500
  python analyst/ledger.py sell BTC --why "..."
  python analyst/ledger.py check        # hourly (bot.yml): stops / targets hit by the 1H candles since the last check
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import bot  # noqa: E402

LEDGER = os.path.join(HERE, "ledger.json")
TRADES = os.path.join(HERE, "trades.csv")
ACCOUNTS = {"claude": HERE, "chrome": os.path.join(HERE, "chrome"),
            "terminal": os.path.join(HERE, "terminal")}  # same rules, separate balances
# "terminal" = terminal Claude's Brad-checklist contest account (Jeff, Oct 10 2026), fresh $1,000
COINS = ["BTC", "ETH", "SOL", "XRP", "BNB", "LINK"]
FEE = 0.0035
MAX_RISK = 0.005
MAX_OPEN = 3
MAX_DD = 0.12
START = 1000.0


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")


def load():
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            return json.load(f)
    return {"equity": START, "peak": START, "positions": {}, "last_check": None, "halted": None}


def save(led):
    with open(LEDGER, "w") as f:
        json.dump(led, f, indent=1)


def log_trade(row):
    new = not os.path.exists(TRADES)
    with open(TRADES, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["time_utc", "coin", "side", "qty", "price", "usdt", "pnl_usdt", "pnl_pct",
                                          "r_multiple", "reason", "balance"])
        if new:
            w.writeheader()
        w.writerow(row)


def candles(coin, tf="1H", n=100):
    return bot.OKX("", "", "").candles(f"{coin}-USDT", tf, n)


def price(coin):
    return candles(coin, "1H", 2)[-1]["c"]


def close_pos(led, coin, px, reason):
    p = led["positions"].pop(coin)
    proceeds = p["qty"] * px * (1 - FEE)
    pnl = proceeds - p["cost"]
    led["equity"] = round(led["equity"] + pnl, 4)
    led["peak"] = max(led["peak"], led["equity"])
    r = pnl / p["risk_usd"] if p["risk_usd"] else 0
    log_trade({"time_utc": now_iso(), "coin": coin, "side": "sell", "qty": p["qty"], "price": px,
               "usdt": round(proceeds, 2), "pnl_usdt": round(pnl, 2), "pnl_pct": round(pnl / p["cost"] * 100, 2),
               "r_multiple": round(r, 2), "reason": reason, "balance": led["equity"]})
    print(f"SOLD {coin} @ {px:g}: P/L {pnl:+.2f} ({r:+.2f}R) - {reason}. Balance {led['equity']:.2f}")


def cmd_status(led, _a):
    print(f"Balance {led['equity']:.2f} (best {led['peak']:.2f}){'  HALTED: ' + led['halted'] if led['halted'] else ''}")
    for c, p in led["positions"].items():
        px = price(c)
        upl = p["qty"] * px * (1 - FEE) - p["cost"]
        print(f"  {c}: {p['qty']:.6g} @ {p['entry']:g}, now {px:g}, stop {p['stop']:g}, target {p.get('target')}, "
              f"open P/L {upl:+.2f} ({upl / p['risk_usd']:+.2f}R) | why: {p['why']}")
    if not led["positions"]:
        print("  no open trades")
    for c, o in led.get("orders", {}).items():
        print(f"  ORDER {c}: buy {o['side']} {o['trigger']:g}, stop {o['stop']:g}, placed {o['placed']} | why: {o['why']}")


def open_trade(led, coin, px, stop, target, risk_pct, why, wrong, when=None):
    """Opens a trade at px if every rule allows it; returns an error text instead when not."""
    if led["halted"]:
        return f"halted ({led['halted']})"
    if led["equity"] < led["peak"] * (1 - MAX_DD):
        led["halted"] = f"balance {led['equity']:.2f} is over {MAX_DD * 100:.0f}% below its best {led['peak']:.2f}"
        return f"HALTED: {led['halted']}"
    if coin in led["positions"]:
        return f"{coin} already open"
    if len(led["positions"]) >= MAX_OPEN:
        return f"{MAX_OPEN} trades already open"
    if stop >= px:
        return f"stop {stop:g} is not below the price {px:g}"
    if target is not None and target <= px:
        return f"target {target:g} is not above the price {px:g}"
    risk = min(risk_pct / 100, MAX_RISK)
    free = led["equity"] - sum(p["cost"] for p in led["positions"].values())
    qty = min(led["equity"] * risk / (px - stop), free / (px * (1 + FEE)))
    if qty * px < 5:
        return f"order too small ({qty * px:.2f})"
    cost = qty * px * (1 + FEE)
    risk_usd = qty * (px - stop)
    when = when or now_iso()
    led["positions"][coin] = {"qty": qty, "entry": px, "cost": cost, "stop": stop, "first_stop": stop,
                              "target": target, "risk_usd": risk_usd, "opened": when, "why": why, "wrong": wrong}
    log_trade({"time_utc": when, "coin": coin, "side": "buy", "qty": qty, "price": px, "usdt": round(cost, 2),
               "pnl_usdt": "", "pnl_pct": "", "r_multiple": "", "reason": why, "balance": led["equity"]})
    print(f"BOUGHT {coin} {qty:.6g} @ {px:g} (${cost:.2f}), stop {stop:g} ({(px - stop) / px * 100:.2f}% away), "
          f"risk ${risk_usd:.2f} = {risk_usd / led['equity'] * 100:.2f}% of balance")
    return None


def cmd_buy(led, a):
    coin = a.coin.upper()
    if coin not in COINS:
        sys.exit(f"REFUSED: {coin} is not on the list {COINS}")
    if not a.why or not a.wrong:
        sys.exit("REFUSED: every trade needs --why and --wrong (what would prove it wrong)")
    err = open_trade(led, coin, price(coin), a.stop, a.target, a.risk, a.why, a.wrong)
    save(led)
    if err:
        sys.exit(f"REFUSED: {err}")


def cmd_order(led, a):
    """Resting order: buy when price trades above (breakout) or down to (dip) a level; filled by the hourly check."""
    coin = a.coin.upper()
    if coin not in COINS:
        sys.exit(f"REFUSED: {coin} is not on the list {COINS}")
    if not a.why or not a.wrong:
        sys.exit("REFUSED: every trade needs a why and a wrong (what would prove it wrong)")
    if (a.above is None) == (a.below is None):
        sys.exit("REFUSED: give exactly one of --above or --below")
    trig = a.above if a.above is not None else a.below
    if a.stop >= trig:
        sys.exit(f"REFUSED: stop {a.stop:g} is not below the trigger {trig:g}")
    px = price(coin)
    if (a.above is not None and px >= trig) or (a.below is not None and px <= trig):
        sys.exit(f"REFUSED: price {px:g} is already past the trigger {trig:g} (use buy)")
    led.setdefault("orders", {})[coin] = {
        "side": "above" if a.above is not None else "below", "trigger": trig, "stop": a.stop, "target": a.target,
        "risk": a.risk, "why": a.why, "wrong": a.wrong, "placed": now_iso(),
        "placed_ms": int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000),
        "expires_ms": int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000) + int(a.hours * 3600000)}
    save(led)
    print(f"ORDER {coin}: buy if price goes {'above' if a.above is not None else 'down to'} {trig:g}, stop {a.stop:g}, "
          f"expires in {a.hours:g}h")


def cmd_cancel(led, a):
    coin = a.coin.upper()
    if led.get("orders", {}).pop(coin, None) is None:
        sys.exit(f"REFUSED: no {coin} order")
    save(led)
    print(f"{coin} order cancelled")


def cmd_stop(led, a):
    coin = a.coin.upper()
    p = led["positions"].get(coin) or sys.exit(f"REFUSED: no open {coin} trade")
    if a.price <= p["stop"]:
        sys.exit(f"REFUSED: stops only move up (now {p['stop']:g})")
    if a.price >= price(coin):
        sys.exit("REFUSED: new stop is not below the current price (sell instead)")
    p["stop"] = a.price
    save(led)
    print(f"{coin} stop raised to {a.price:g}")


def cmd_sell(led, a):
    coin = a.coin.upper()
    if coin not in led["positions"]:
        sys.exit(f"REFUSED: no open {coin} trade")
    close_pos(led, coin, price(coin), a.why or "Analyst decision")
    save(led)


def cmd_check(led, _a):
    """Stops / targets hit since the last check, from closed 1H candles (stop first when both hit, like bot.py)."""
    since = led.get("last_check_ms") or 0
    latest = since
    now_ms = int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    for coin in list(led.get("orders", {})):
        o = led["orders"][coin]
        for b in candles(coin, "1H", 100):
            if not b["confirm"] or b["ts"] < o["placed_ms"] - 3600000 or b["ts"] + 3600000 <= max(since, o["placed_ms"]):
                continue  # 1H candles that ended after the order was placed, each checked once
            latest = max(latest, b["ts"])
            hit = b["h"] >= o["trigger"] if o["side"] == "above" else b["l"] <= o["trigger"]
            if hit:
                px = max(o["trigger"], b["o"]) if o["side"] == "above" else min(o["trigger"], b["o"])
                when = dt.datetime.fromtimestamp(b["ts"] / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
                err = open_trade(led, coin, px, o["stop"], o["target"], o["risk"], o["why"], o["wrong"], when)
                print(f"ORDER {coin} triggered @ {px:g}" + (f" but refused: {err}" if err else ""))
                del led["orders"][coin]
                if not err:  # same candle: the stop may already be hit after the fill
                    p = led["positions"][coin]
                    p["opened"] = dt.datetime.fromtimestamp((b["ts"] + 3600000) / 1000, dt.timezone.utc).strftime(
                        "%Y-%m-%d %H:%M")
                break
        else:
            if now_ms > o["expires_ms"]:
                print(f"ORDER {coin} expired unfilled")
                del led["orders"][coin]
    for coin in list(led["positions"]):
        p = led["positions"][coin]
        opened_ms = int(dt.datetime.strptime(p["opened"], "%Y-%m-%d %H:%M").replace(
            tzinfo=dt.timezone.utc).timestamp() * 1000)
        for b in candles(coin, "1H", 100):
            if not b["confirm"] or b["ts"] < opened_ms or b["ts"] <= since:
                continue  # only whole candles after the buy, each checked once
            latest = max(latest, b["ts"])
            if b["l"] <= p["stop"]:
                close_pos(led, coin, min(p["stop"], b["o"]), "stop" if p["stop"] <= p["first_stop"] else "trailing stop")
                break
            if p.get("target") and b["h"] >= p["target"]:
                close_pos(led, coin, max(p["target"], b["o"]), "target")
                break
    led["last_check_ms"] = latest or int(dt.datetime.now(dt.timezone.utc).timestamp() * 1000)
    led["last_check"] = now_iso()
    save(led)


def cmd_requests(led, _a):
    """Chrome Claude can't run Python: it writes lines in chrome/requests.md, and the hourly run carries them out.
    Pending lines start with "- [ ] ", for example:
      - [ ] ORDER SOL above 125.3 stop 118.5 hours 72 | why: ... | wrong: ...
      - [ ] ORDER LINK below 13.55 stop 12.85 | why: ... | wrong: ...
      - [ ] BUY BTC stop 84000 | why: ... | wrong: ...
      - [ ] STOP SOL 121.5
      - [ ] SELL SOL | why: ...
      - [ ] CANCEL SOL
    Each becomes "- [x] ... -> result" (done) or "- [!] ... -> REFUSED: reason"."""
    path = os.path.join(os.path.dirname(LEDGER), "requests.md")
    if not os.path.exists(path):
        return
    with open(path) as f:
        lines = f.read().split("\n")
    for i, line in enumerate(lines):
        if not line.startswith("- [ ] "):
            continue
        body, why, wrong = line[6:], None, None
        parts = [x.strip() for x in body.split("|")]
        for x in parts[1:]:
            if x.lower().startswith("why:"):
                why = x[4:].strip()
            elif x.lower().startswith("wrong:"):
                wrong = x[6:].strip()
        w = parts[0].split()
        out = []
        sys_out = sys.stdout

        class Cap:
            def write(self, t):
                out.append(t)

            def flush(self):
                pass
        sys.stdout = Cap()
        try:
            act = w[0].upper()
            kv = {w[j].lower(): w[j + 1] for j in range(2, len(w) - 1, 2)}
            ns = argparse.Namespace(coin=w[1], why=why, wrong=wrong, risk=float(kv.get("risk", 0.5)),
                                    target=float(kv["target"]) if "target" in kv else None)
            if act == "BUY":
                ns.stop = float(kv["stop"])
                cmd_buy(led, ns)
            elif act == "ORDER":
                ns.above = float(w[3]) if w[2].lower() == "above" else None
                ns.below = float(w[3]) if w[2].lower() == "below" else None
                kv = {w[j].lower(): w[j + 1] for j in range(4, len(w) - 1, 2)}
                ns.stop, ns.hours = float(kv["stop"]), float(kv.get("hours", 72))
                ns.target = float(kv["target"]) if "target" in kv else None
                ns.risk = float(kv.get("risk", 0.5))
                cmd_order(led, ns)
            elif act == "STOP":
                ns.price = float(w[2])
                cmd_stop(led, ns)
            elif act == "SELL":
                cmd_sell(led, ns)
            elif act == "CANCEL":
                cmd_cancel(led, ns)
            else:
                raise SystemExit(f"REFUSED: unknown action {act}")
            mark, res = "- [x] ", "".join(out).strip().replace("\n", " / ")
        except SystemExit as e:
            mark, res = "- [!] ", str(e)
        except Exception as e:
            mark, res = "- [!] ", f"REFUSED: could not read the line ({type(e).__name__}: {e})"
        finally:
            sys.stdout = sys_out
        led = load()  # commands save as they go
        lines[i] = f"{mark}{body} -> {now_iso()} UTC: {res}"
        print(lines[i])
    with open(path, "w") as f:
        f.write("\n".join(lines))


def main():
    global LEDGER, TRADES
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", choices=sorted(ACCOUNTS), default="claude")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("requests")
    sub.add_parser("status")
    sub.add_parser("check")
    b = sub.add_parser("buy")
    b.add_argument("coin")
    b.add_argument("--stop", type=float, required=True)
    b.add_argument("--target", type=float)
    b.add_argument("--risk", type=float, default=0.5, help="percent of balance, capped at 0.5")
    b.add_argument("--why", required=True)
    b.add_argument("--wrong", required=True)
    o = sub.add_parser("order")
    o.add_argument("coin")
    o.add_argument("--above", type=float)
    o.add_argument("--below", type=float)
    o.add_argument("--stop", type=float, required=True)
    o.add_argument("--target", type=float)
    o.add_argument("--risk", type=float, default=0.5)
    o.add_argument("--hours", type=float, default=72)
    o.add_argument("--why", required=True)
    o.add_argument("--wrong", required=True)
    c = sub.add_parser("cancel")
    c.add_argument("coin")
    s = sub.add_parser("stop")
    s.add_argument("coin")
    s.add_argument("price", type=float)
    se = sub.add_parser("sell")
    se.add_argument("coin")
    se.add_argument("--why")
    a = ap.parse_args()
    LEDGER = os.path.join(ACCOUNTS[a.account], "ledger.json")
    TRADES = os.path.join(ACCOUNTS[a.account], "trades.csv")
    led = load()
    {"status": cmd_status, "check": cmd_check, "buy": cmd_buy, "order": cmd_order, "cancel": cmd_cancel,
     "stop": cmd_stop, "sell": cmd_sell, "requests": cmd_requests}[a.cmd](led, a)


if __name__ == "__main__":
    main()
