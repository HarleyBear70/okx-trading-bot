"""
Binance.US live bots (mode "live") against a fake Binance.US: no network, no real orders.

Run: python tests/test_binanceus_live.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402

bot.TRADES_FILE = os.path.join(tempfile.mkdtemp(), "trades.csv")  # never touch the real trade log
LIVE_TR = next(b for b in bot.BOTS if b["id"] == "tr-live")


class FakeBNUS:
    """Just enough of Binance.US: balances, rules, market orders (fee taken in the coin on buys), STOP_LOSS orders."""

    def __init__(self, usd=100.0, px=100.0):
        self.bal = {"USD": usd, "BTC": 0.0}
        self.locked = 0.0
        self.px, self.orders, self.calls, self.next_id, self.trades = px, {}, [], 1, []

    def balances(self):
        return {"USD": (self.bal["USD"], 0.0), "BTC": (self.bal["BTC"] - self.locked, self.locked)}

    def rules(self, symbol):
        return {"step": 0.00001, "tick": 0.01, "min_notional": 1.0, "types": ["MARKET", "STOP_LOSS"]}

    def price(self, symbol):
        return self.px

    def order(self, test=False, **p):
        self.calls.append(("order", p))
        oid = self.next_id
        self.next_id += 1
        if p["type"] == "STOP_LOSS":
            q = float(p["quantity"])
            assert q <= self.bal["BTC"] - self.locked + 1e-12, "stop for more than the free coins"
            self.locked += q
            self.orders[oid] = {"orderId": oid, "status": "NEW", "qty": q, "stopPrice": float(p["stopPrice"])}
            return {"orderId": oid}
        if p["side"] == "BUY":
            usd = float(p["quoteOrderQty"])
            assert usd <= self.bal["USD"]
            q = round(usd / self.px, 5)
            fee = q * bot.BINANCEUS_FEE
            self.bal["USD"] -= q * self.px
            self.bal["BTC"] += q - fee
            return {"orderId": oid, "status": "FILLED", "executedQty": str(q),
                    "fills": [{"qty": str(q), "price": str(self.px), "commission": str(fee), "commissionAsset": "BTC"}]}
        q = float(p["quantity"])
        assert q <= self.bal["BTC"] - self.locked + 1e-12, "sold more than the free coins"
        fee = q * self.px * bot.BINANCEUS_FEE
        self.bal["BTC"] -= q
        self.bal["USD"] += q * self.px - fee
        return {"orderId": oid, "status": "FILLED", "executedQty": str(q),
                "fills": [{"qty": str(q), "price": str(self.px), "commission": str(fee), "commissionAsset": "USD"}]}

    def cancel(self, symbol, oid):
        self.calls.append(("cancel", oid))
        o = self.orders[oid]
        assert o["status"] == "NEW"
        o["status"] = "CANCELED"
        self.locked -= o["qty"]
        return {"status": "CANCELED"}

    def get_order(self, symbol, oid):
        o = self.orders[oid]
        return {"orderId": oid, "status": o["status"], "executedQty": str(o["qty"] if o["status"] == "FILLED" else 0),
                "cummulativeQuoteQty": str(o["qty"] * o["stopPrice"] if o["status"] == "FILLED" else 0)}

    def fire(self, oid):
        o = self.orders[oid]
        o["status"] = "FILLED"
        self.locked -= o["qty"]
        self.bal["BTC"] -= o["qty"]
        self.bal["USD"] += o["qty"] * o["stopPrice"]

    def _req(self, method, path, params=None, signed=False):
        assert path == "/api/v3/myTrades"
        return self.trades


def setup(usd=100.0):
    fake = FakeBNUS(usd)
    bot._bnus, bot._bnus_rules = fake, {}
    bs = {"equity": 50.0, "positions": {}, "last_bar": {}}
    return fake, bs


def open_btc(bs, stop=95.0):
    bar = {"ts": 1_700_000_000_000, "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.0}
    bot.open_position(None, LIVE_TR, bs, "BTC-USDT", bar, {"sl": stop, "tp": None, "score": "t"}, {"hi": 100.0})
    return bs["positions"].get("BTC-USDT")


def test_buy_places_real_order_and_exchange_stop():
    fake, bs = setup()
    pos = open_btc(bs)
    assert pos, "live bot should have bought"
    buy = [p for k, p in fake.calls if k == "order" and p["side"] == "BUY"]
    assert len(buy) == 1 and buy[0]["type"] == "MARKET"
    # 0.5% of $50 = $0.25 risk over a $5 stop distance -> 0.05 BTC... capped by $50 equity -> about $5 order at px 100
    assert 4.9 <= float(buy[0]["quoteOrderQty"]) <= 5.01, buy[0]
    stops = [p for k, p in fake.calls if k == "order" and p["type"] == "STOP_LOSS"]
    assert len(stops) == 1 and float(stops[0]["stopPrice"]) == 95.0
    assert pos["algo_id"] and fake.orders[pos["algo_id"]]["status"] == "NEW"


def test_stop_moves_by_cancel_and_replace():
    fake, bs = setup()
    pos = open_btc(bs)
    old = pos["algo_id"]
    pos["stop"] = 98.0
    bot.stop_sync(None, LIVE_TR, "BTC-USDT", pos)
    assert fake.orders[old]["status"] == "CANCELED"
    assert fake.orders[pos["algo_id"]]["stopPrice"] == 98.0 and fake.orders[pos["algo_id"]]["status"] == "NEW"
    n = len(fake.calls)
    bot.stop_sync(None, LIVE_TR, "BTC-USDT", pos)  # nothing changed -> no orders
    assert len(fake.calls) == n


def test_fired_stop_is_recorded():
    fake, bs = setup()
    pos = open_btc(bs)
    fake.fire(pos["algo_id"])
    assert bot.stop_check(None, LIVE_TR, bs, "BTC-USDT") is True
    assert "BTC-USDT" not in bs["positions"]
    assert 49.6 < bs["equity"] < 50.0, bs["equity"]  # lost about 5% of a $5 trade


def test_bot_sale_cancels_stop_first_and_sells_everything():
    fake, bs = setup()
    pos = open_btc(bs)
    sid = pos["algo_id"]
    bot.close_position(None, LIVE_TR, bs, "BTC-USDT", "trailing stop", 100.0)
    assert fake.orders[sid]["status"] == "CANCELED"
    sells = [p for k, p in fake.calls if k == "order" and p["side"] == "SELL" and p["type"] == "MARKET"]
    assert len(sells) == 1
    assert fake.bal["BTC"] < 0.00001 + 1e-12, fake.bal  # less than one step of dust left
    assert "BTC-USDT" not in bs["positions"]


def test_switch_off_blocks_new_buys():
    fake, bs = setup()
    bot.LIVE["on"] = False
    try:
        assert open_btc(bs) is None
        assert not fake.calls
    finally:
        bot.LIVE["on"] = True


def test_no_cash_no_order():
    fake, bs = setup(usd=0.5)
    assert open_btc(bs) is None
    assert not [c for c in fake.calls if c[0] == "order"]


def test_guard_blocks_live_bot():
    fake, bs = setup()
    bs["peak"], bs["equity"] = 50.0, 43.0
    assert open_btc(bs) is None and bs.get("halted")
    assert not fake.calls


def test_daily_loss_limit_blocks_buys():
    fake, bs = setup()
    bot.add_day_pnl(bs, -1.6)  # more than 3% of $50 lost today
    assert open_btc(bs) is None and not fake.calls


def test_no_exchange_stop_means_sell_straight_away():
    fake, bs = setup()
    real = fake.order

    def no_stops(test=False, **p):
        if p["type"] == "STOP_LOSS":
            raise RuntimeError("Binance.US said no")
        return real(test=test, **p)
    fake.order = no_stops
    assert open_btc(bs) is None
    assert fake.bal["BTC"] < 0.00001 + 1e-12  # bought, then sold again
    assert len([p for k, p in fake.calls if k == "order" and p["side"] == "SELL"]) == 1


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
    print("all Binance.US live tests passed")
