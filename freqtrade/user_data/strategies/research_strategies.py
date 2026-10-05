"""
Research batch strategies: the common bot types sold by 3Commas / Bitsgap / HaasOnline,
rebuilt simply so they can be backtested on the same footing as Jeff's own bots.

DCABot     - 3Commas-style DCA: start a deal on an RSI dip, buy more ("safety orders")
             every 2.5% lower (each 1.5x bigger, up to 5), sell everything at +2% on the
             average price. Safety net stop at -30% (most DCA bots run with no stop).
FlashCrash - buy sharp drops (6%+ in 4 hours with RSI under 25), take +4%, give up
             after a day, stop at -6%.
"""
from pandas import DataFrame

from freqtrade.strategy import IStrategy


def rsi(close, n=14):
    d = close.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


class DCABot(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = False
    startup_candle_count = 50
    minimal_roi = {"0": 0.02}
    stoploss = -0.30
    use_exit_signal = False
    position_adjustment_enable = True
    max_entry_position_adjustment = 5

    STEP = 0.025      # next safety order every 2.5% below the first buy
    SCALE = 1.5       # each safety order 1.5x the one before
    UNITS = sum(1.5 ** k for k in range(6))   # base + 5 safety orders, in base-order units

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = rsi(dataframe["close"])
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe["rsi"] < 30, "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        return dataframe

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake,
                            max_stake, leverage, entry_tag, side, **kwargs) -> float:
        # keep enough money for every safety order of every open deal
        total = self.wallets.get_total_stake_amount()
        slots = self.config.get("max_open_trades", 3)
        return min(total / slots / self.UNITS, max_stake)

    def adjust_trade_position(self, trade, current_time, current_rate, current_profit,
                              min_stake, max_stake, **kwargs):
        filled = trade.select_filled_orders(trade.entry_side)
        count = trade.nr_of_successful_entries
        if not filled or count > self.max_entry_position_adjustment:
            return None
        first = filled[0]
        if current_rate > first.safe_price * (1 - self.STEP * count):
            return None
        stake = first.safe_filled * first.safe_price * (self.SCALE ** count)
        if min_stake and stake < min_stake:
            return None
        return min(stake, max_stake)


class FlashCrash(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "1h"
    can_short = False
    startup_candle_count = 50
    minimal_roi = {"0": 0.04, "720": 0.01, "1440": 0}
    stoploss = -0.06
    use_exit_signal = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["rsi"] = rsi(dataframe["close"])
        dataframe["drop4"] = dataframe["close"] / dataframe["close"].shift(4) - 1
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["drop4"] <= -0.06) & (dataframe["rsi"] < 25), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        return dataframe


def ut_bot(df, key=4.0, period=52, use_ha=True):
    """UT Bot Alerts (QuantNomad, TradingView). Returns (buy, sell) boolean lists.
    ATR from the real candles; signal source = Heikin Ashi close if use_ha."""
    o, h, l, c = (df[k].tolist() for k in ("open", "high", "low", "close"))
    n = len(c)
    tr = [h[0] - l[0]] + [max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1])) for i in range(1, n)]
    atr = [None] * n
    if n >= period:
        atr[period - 1] = sum(tr[:period]) / period
        for i in range(period, n):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period
    src = [(o[i] + h[i] + l[i] + c[i]) / 4 for i in range(n)] if use_ha else c
    stop = [0.0] * n
    buy, sell = [False] * n, [False] * n
    for i in range(1, n):
        if atr[i] is None:
            continue
        loss = key * atr[i]
        p = stop[i - 1]
        if src[i] > p and src[i - 1] > p:
            stop[i] = max(p, src[i] - loss)
        elif src[i] < p and src[i - 1] < p:
            stop[i] = min(p, src[i] + loss)
        elif src[i] > p:
            stop[i] = src[i] - loss
        else:
            stop[i] = src[i] + loss
        if atr[i - 1] is None:
            continue
        buy[i] = src[i] > stop[i] and src[i - 1] <= stop[i - 1]
        sell[i] = src[i] < stop[i] and src[i - 1] >= stop[i - 1]
    return buy, sell


class UTBot(IStrategy):
    """UT Bot Alerts, Jeff's settings: Heikin Ashi signals, ATR period 52, key value 4.
    Buys on the Buy signal, sells on the Sell signal, at REAL prices (next candle open)."""
    INTERFACE_VERSION = 3
    timeframe = "4h"
    can_short = False
    startup_candle_count = 200
    minimal_roi = {"0": 100}
    stoploss = -0.25          # safety net only; UT Bot itself has no stop besides the Sell signal
    use_exit_signal = True
    key, period, use_ha, daily_filter = 4.0, 52, True, False

    def informative_pairs(self):
        return [(p, "1d") for p in self.dp.current_whitelist()] if self.daily_filter else []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        buy, sell = ut_bot(dataframe, self.key, self.period, self.use_ha)
        dataframe["ut_buy"], dataframe["ut_sell"] = buy, sell
        dataframe["day_up"] = True
        if self.daily_filter:
            d = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe="1d").copy()
            d["up"] = d["close"] > d["close"].ewm(span=50, adjust=False).mean()
            up = dict(zip(d["date"].dt.floor("D") + __import__("pandas").Timedelta(days=1), d["up"]))
            dataframe["day_up"] = [bool(up.get(t.floor("D"), False)) for t in dataframe["date"]]
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe["ut_buy"] & dataframe["day_up"], "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe["ut_sell"], "exit_long"] = 1
        return dataframe


class UTBotRegular(UTBot):
    """Same, but signals from regular candles (for comparison)."""
    use_ha = False


class UTBot1h(UTBot):
    timeframe = "1h"


class UTBotTrend(UTBot):
    """Jeff's UT Bot settings, but only buys when the daily trend is up."""
    daily_filter = True


def _wma(s, n):
    import numpy as np
    w = np.arange(1, n + 1)
    return s.rolling(n).apply(lambda x: (x * w).sum() / w.sum(), raw=True)


def hma(s, n):
    return _wma(2 * _wma(s, max(n // 2, 1)) - _wma(s, n), max(int(n ** 0.5), 1))


class SSLHybrid(IStrategy):
    """SSL Hybrid (Mihkel00) baseline signal: HMA(60) baseline with a band of 0.2 x EMA(60) of true range.
    Baseline turns blue when price closes above the band (buy), red when it closes below (sell).
    The ATR period 28 / EMA smoothing settings only change the ATR bands drawn on the chart."""
    INTERFACE_VERSION = 3
    timeframe = "4h"
    can_short = False
    startup_candle_count = 200
    minimal_roi = {"0": 100}
    stoploss = -0.25
    use_exit_signal = True
    length, mult, daily_filter = 60, 0.2, False

    def informative_pairs(self):
        return [(p, "1d") for p in self.dp.current_whitelist()] if self.daily_filter else []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        import pandas as pd
        c = dataframe["close"]
        tr = pd.concat([dataframe["high"] - dataframe["low"], (dataframe["high"] - c.shift()).abs(),
                        (dataframe["low"] - c.shift()).abs()], axis=1).max(axis=1)
        base = hma(c, self.length)
        rng = tr.ewm(span=self.length, adjust=False).mean()
        dataframe["blue"] = c > base + rng * self.mult
        dataframe["red"] = c < base - rng * self.mult
        dataframe["day_up"] = True
        if self.daily_filter:
            d = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe="1d").copy()
            d["up"] = d["close"] > d["close"].ewm(span=50, adjust=False).mean()
            up = dict(zip(d["date"].dt.floor("D") + pd.Timedelta(days=1), d["up"]))
            dataframe["day_up"] = [bool(up.get(t.floor("D"), False)) for t in dataframe["date"]]
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        turned_blue = dataframe["blue"] & ~dataframe["blue"].shift(1, fill_value=False)
        dataframe.loc[turned_blue & dataframe["day_up"], "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe["red"], "exit_long"] = 1
        return dataframe


class SSLHybrid1h(SSLHybrid):
    timeframe = "1h"


class SSLHybridTrend(SSLHybrid):
    daily_filter = True
