"""
Exchange-side stop orders (EXCHANGE_STOPS_PLAN.md) against a fake OKX: no network, no real or demo orders.

Run: python tests/test_exchange_stops.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bot  # noqa: E402


class FakeOKX:
    """Just enough of OKX's API: instruments, market orders, algo (conditional stop) orders."""

    def __init__(self):
        self.calls, self.algos, self.coin_bal, self.next_id = [], {}, 0.0, 1

    def get(self, path, params=None, private=False):
        self.calls.append(("GET", path, params))
        if path == "/api/v5/public/instruments":
            return [{"lotSz": "0.0001", "minSz": "0.0001", "tickSz": "0.1"}]
        if path == "/api/v5/account/balance":
            return [{"details": [{"availBal": str(self.coin_bal)}]}]
        if path == "/api/v5/trade/order":
            if "ordId" in params:  # the order a triggered stop created
                return [{"state": "filled", "accFillSz": "0.0100", "avgPx": "95.0", "fee": "-0.0033"}]
            return [{"state": "filled", "accFillSz": "0.0100", "avgPx": "100.0", "fee": "0"}]
        if path == "/api/v5/trade/orders-algo-pending":
            a = self.algos.get(params["algoId"])
            return [a] if a and a["state"] == "live" else []
        if path == "/api/v5/trade/orders-algo-history":
            a = self.algos.get(params["algoId"])
            return [a] if a and a["state"] != "live" else []
        raise AssertionError(path)

    def post(self, path, body):
        self.calls.append(("POST", path, body))
        if path == "/api/v5/trade/order":
            self.coin_bal = 0.01 if body["side"] == "buy" else 0.0
            return [{}]
        if path == "/api/v5/trade/order-algo":
            aid = f"A{self.next_id}"
            self.next_id += 1
            self.algos[aid] = {"algoId": aid, "state": "live", "sz": body["sz"], "slTriggerPx": body["slTriggerPx"]}
            return [{"algoId": aid}]
        if path == "/api/v5/trade/amend-algos":
            a = self.algos[body["algoId"]]
            a["slTriggerPx"] = body["newSlTriggerPx"]
            a["sz"] = body.get("newSz", a["sz"])
            return [{}]
        if path == "/api/v5/trade/cancel-algos":
            for x in body:
                self.algos[x["algoId"]]["state"] = "canceled"
            return [{}]
        raise AssertionError(path)


def setup():
    api = FakeOKX()
    b = {"id": "t", "name": "Test", "strat": "tr", "venue": "okx", "mode": "demo", "prefix": "ghT", "coins": ["BTC-USDT"],
         "equity": 1000.0, "exchange_stops": True}
    bs = {"equity": 1000.0, "positions": {}, "last_bar": {}}
    rows = []
    bot.log_trade = lambda *a: rows.append(a)
    bot.log = lambda *a: None
    bot.wait_fill = lambda api_, inst, cl: api_.get("/api/v5/trade/order", {"instId": inst, "clOrdId": cl}, True)[0]
    bar = {"ts": 0, "o": 100, "h": 101, "l": 99, "c": 100}
    bot.open_position(api, b, bs, "BTC-USDT", bar, {"sl": 96.0, "tp": None, "score": "BOS"}, {"hi": 100})
    return api, b, bs, rows


def test_place_amend_and_exchange_fill():
    api, b, bs, rows = setup()
    pos = bs["positions"]["BTC-USDT"]
    aid = pos["algo_id"]
    assert api.algos[aid]["slTriggerPx"] == "96.0" and api.algos[aid]["sz"] == "0.0100", api.algos[aid]
    pos["stop"] = 98.0  # trail moved up
    bot.stop_sync(api, b, "BTC-USDT", pos)
    assert api.algos[aid]["slTriggerPx"] == "98.0"
    n = len(api.calls)
    pos["stop"] = 98.05  # tiny move (< 0.1%): no amend call
    bot.stop_sync(api, b, "BTC-USDT", pos)
    assert not any(c[1] == "/api/v5/trade/amend-algos" for c in api.calls[n:])
    api.algos[aid].update({"state": "effective", "ordId": "O9"})  # price fell through the stop between runs
    assert bot.stop_check(api, b, bs, "BTC-USDT") is True
    assert "BTC-USDT" not in bs["positions"]
    sell = rows[-1]
    assert sell[2] == "sell" and sell[8] == "stop (exchange)" and abs(sell[4] - (0.01 * 95 - 0.0033) / 0.01) < 1e-9, sell


def test_bot_exit_cancels_first():
    api, b, bs, rows = setup()
    aid = bs["positions"]["BTC-USDT"]["algo_id"]
    bot.close_position(api, b, bs, "BTC-USDT", "Aroon flipped down", 0)
    paths = [c[1] for c in api.calls]
    i_cancel = paths.index("/api/v5/trade/cancel-algos")
    i_sell = max(i for i, c in enumerate(api.calls) if c[1] == "/api/v5/trade/order" and c[0] == "POST")
    assert i_cancel < i_sell and api.algos[aid]["state"] == "canceled"


def test_resize_after_add_on():
    api, b, bs, rows = setup()
    pos = bs["positions"]["BTC-USDT"]
    pos["qty"] += 0.005  # pyramid add-on
    bot.stop_sync(api, b, "BTC-USDT", pos)
    assert api.algos[pos["algo_id"]]["sz"] == "0.0150"


def test_switch_off_means_no_algo_calls():
    api, b, bs, rows = setup()
    api2 = FakeOKX()
    b2 = {**b, "exchange_stops": False}
    bs2 = {"equity": 1000.0, "positions": {}, "last_bar": {}}
    bot.open_position(api2, b2, bs2, "BTC-USDT", {"ts": 0, "o": 100, "h": 101, "l": 99, "c": 100},
                      {"sl": 96.0, "tp": None, "score": "BOS"}, {"hi": 100})
    assert not any("algo" in c[1] for c in api2.calls)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
