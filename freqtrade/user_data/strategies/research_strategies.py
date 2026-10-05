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
