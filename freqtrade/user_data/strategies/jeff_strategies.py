"""
Jeff's strategies for Freqtrade backtesting.

Entries reuse the exact rule code in bot.py (analyse_sp / analyse_tr), so the
backtest tests the same signals the hourly GitHub bots trade.

Exits are copied as closely as Freqtrade allows:
  - starting stop under the swing low (from the signal candle)
  - stop moves to breakeven (+0.2% for fees) once the trade is up 1R
  - SP-12 v4: Parabolic SAR trail after +1R, target removed once trailing
  - Trend Rider: trail at highest close - 3 ATR
  - SP-12 v2 / v4: take-profit target and time exit
Not copied yet: selling half at +2R, and risk stepping up as the balance grows.
Every trade risks 1% of the balance.
"""
import sys
from datetime import timedelta
from pathlib import Path

from pandas import DataFrame

from freqtrade.strategy import IStrategy, stoploss_from_absolute

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
import bot  # noqa: E402  (Jeff's bot.py at the repo root)

FOUR_H = timedelta(hours=4)
BE_BUFFER = 0.002  # breakeven stop sits just above entry so fees are covered
RISK = 0.01        # 1% of the balance per trade


def to_bars(df: DataFrame) -> list:
    return [
        {"ts": int(d.timestamp() * 1000), "o": o, "h": h, "l": l, "c": c, "v": v, "confirm": True}
        for d, o, h, l, c, v in zip(df["date"], df["open"], df["high"], df["low"], df["close"], df["volume"])
    ]


class JeffBase(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "4h"
    can_short = False
    startup_candle_count = 200
    process_only_new_candles = True

    minimal_roi = {"0": 100}      # no fixed ROI; targets handled below
    stoploss = -0.15              # safety net only; the real stop is custom_stoploss
    use_custom_stoploss = True
    trailing_stop = False
    use_exit_signal = False

    strat = "v4"                  # v4, v2 or tr
    pivot = 5                     # Trend Rider swing strength

    def informative_pairs(self):
        return [(p, "1d") for p in self.dp.current_whitelist()]

    # ---------- signals ----------
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        daily_df = self.dp.get_pair_dataframe(pair=metadata["pair"], timeframe="1d")
        bars, daily = to_bars(dataframe), to_bars(daily_df)
        if self.strat == "tr":
            a = bot.analyse_tr(bars, daily, self.pivot)
            dataframe["atr"] = a["atr"]
        else:
            a = bot.analyse_sp(bars, daily, bot.SP_SETTINGS[self.strat])
            dataframe["sar"] = a["sar"]
        dataframe["signal"] = [1 if s else 0 for s in a["signal"]]
        dataframe["sl"] = [i["sl"] if i else None for i in a["info"]]
        dataframe["tp"] = [i["tp"] if i else None for i in a["info"]]
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe["signal"] == 1) & (dataframe["close"] > dataframe["sl"]), "enter_long"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        return dataframe

    # ---------- helpers ----------
    def _frames(self, pair, trade):
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return None, None, None
        opened = trade.open_date_utc
        sig = df[df["date"] <= opened - FOUR_H]
        if sig.empty:
            return df, None, None
        since = df[df["date"] >= opened]
        return df, sig.iloc[-1], since

    # ---------- position size: risk 1% ----------
    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake,
                            max_stake, leverage, entry_tag, side, **kwargs) -> float:
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return proposed_stake
        last = df.iloc[-1]
        sl = last.get("sl")
        if sl is None or not (current_rate > sl):
            return proposed_stake
        equity = self.wallets.get_total_stake_amount()
        stake = equity * RISK / (current_rate - sl) * current_rate
        stake = min(stake, max_stake)
        if min_stake and stake < min_stake:
            return 0
        return stake

    # ---------- stops ----------
    def custom_stoploss(self, pair, trade, current_time, current_rate, current_profit, after_fill,
                        **kwargs):
        df, sig, since = self._frames(pair, trade)
        if sig is None:
            return None
        entry, sl = trade.open_rate, float(sig["sl"])
        one_r = entry - sl
        stop = sl
        if one_r > 0 and since is not None and not since.empty:
            hi = float(since["high"].max())
            be_floor = max(sl, entry * (1 + BE_BUFFER)) if hi >= entry + one_r else sl
            last = df.iloc[-1]
            if self.strat == "v4":
                s = last.get("sar")
                if hi >= entry + one_r and s is not None and s < last["close"]:
                    stop = max(be_floor, float(s))
                else:
                    stop = be_floor
            elif self.strat == "tr":
                hi_close = max(float(since["close"].max()), entry)
                atr = last.get("atr")
                trail = hi_close - 3 * float(atr) if atr is not None else be_floor
                stop = max(sl, be_floor, trail)
            else:
                stop = be_floor
        return stoploss_from_absolute(stop, current_rate, is_short=trade.is_short)

    # ---------- target and time exit ----------
    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if self.strat == "tr":
            return None
        df, sig, since = self._frames(pair, trade)
        if sig is None:
            return None
        cfg = bot.SP_SETTINGS[self.strat]
        n_closed = 0 if since is None else len(since)
        if cfg.get("max_bars") and n_closed >= cfg["max_bars"]:
            return "time exit"
        tp = sig.get("tp")
        if tp is None:
            return None
        trailing = False
        if self.strat == "v4" and since is not None and not since.empty:
            one_r = trade.open_rate - float(sig["sl"])
            trailing = one_r > 0 and float(since["high"].max()) >= trade.open_rate + one_r
        if trailing:
            return None
        recent_high = float(since["high"].max()) if since is not None and not since.empty else 0
        if current_rate >= tp or recent_high >= tp:
            return "take profit"
        return None

    def custom_exit_price(self, pair, trade, current_time, proposed_rate, current_profit, exit_tag,
                          **kwargs):
        if exit_tag == "take profit":
            _, sig, _ = self._frames(pair, trade)
            if sig is not None and sig.get("tp") is not None:
                return max(float(sig["tp"]), proposed_rate)
        return proposed_rate


class SP12v4(JeffBase):
    strat = "v4"


class SP12v2(JeffBase):
    strat = "v2"


class TrendRider(JeffBase):
    strat = "tr"
    pivot = 5


class TrendRiderGold(JeffBase):
    strat = "tr"
    pivot = 3
