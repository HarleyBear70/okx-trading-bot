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
  - sell half at +2R, the rest keeps running with its stop (bot.take_half)
Position size uses bot.risk_pct(): RISK_PCT of the balance, stepping up by RISK_STEPS as the balance
grows when step-ups are on. Step-ups follow bot.RISK_STEPS_ON unless JEFF_RISK_STEPS=on/off is set,
so the backtest can be run both ways. JEFF_TAKE_HALF=off turns off selling half at +2R.
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

from pandas import DataFrame

from freqtrade.exchange import timeframe_to_minutes
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_absolute

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
import bot  # noqa: E402  (Jeff's bot.py at the repo root)

FOUR_H = timedelta(hours=4)
BE_BUFFER = 0.002  # breakeven stop sits just above entry so fees are covered
HALF_TAG = "half profit +2R"

_steps = os.environ.get("JEFF_RISK_STEPS", "").strip().lower()
if _steps in ("on", "off"):
    bot.RISK_STEPS_ON = _steps == "on"
TAKE_HALF = os.environ.get("JEFF_TAKE_HALF", "").strip().lower() != "off"


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
    use_exit_signal = True        # needed so custom_exit (take profit, time exit) runs; exit_long is never set
    position_adjustment_enable = True  # needed so adjust_trade_position can sell half at +2R

    strat = "v4"                  # v4, v2 or tr
    pivot = 5                     # Trend Rider swing strength
    take_half = TAKE_HALF         # sell half at +2R, like the live bots

    def bot_start(self, **kwargs) -> None:
        self._bs = {}             # balance and peak, the same fields bot.risk_pct() reads

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
        sig = df[df["date"] <= opened - timedelta(minutes=timeframe_to_minutes(self.timeframe))]
        if sig.empty:
            return df, None, None
        since = df[df["date"] >= opened]
        return df, sig.iloc[-1], since

    def _two_r(self, trade):
        _, sig, _ = self._frames(trade.pair, trade)
        if sig is None:
            return None
        entry, sl = trade.open_rate, float(sig["sl"])
        return entry + 2 * (entry - sl) if entry > sl else None

    # ---------- position size: bot.risk_pct() ----------
    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake,
                            max_stake, leverage, entry_tag, side, **kwargs) -> float:
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or df.empty:
            return proposed_stake
        last = df.iloc[-1]
        sl = last.get("sl")
        if sl is None or not (current_rate > sl):
            return proposed_stake
        start = float(self.config["dry_run_wallet"])
        equity = (start + Trade.get_total_closed_profit()
                  + sum(t.realized_profit for t in Trade.get_trades_proxy(is_open=True)))
        self._bs["equity"] = equity
        risk = bot.risk_pct({"equity": start}, self._bs)
        stake = equity * risk / (current_rate - sl) * current_rate
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

    # ---------- sell half at +2R ----------
    def adjust_trade_position(self, trade, current_time, current_rate, current_profit, min_stake,
                              max_stake, current_entry_rate, current_exit_rate, current_entry_profit,
                              current_exit_profit, **kwargs):
        """Keeps a limit sell for half the position resting at +2R until it fills. A stop, target or
        time exit on the same candle replaces it, so the stop is checked first, as in bot.check_hit."""
        if not self.take_half or trade.nr_of_successful_exits > 0:
            return None
        if self._two_r(trade) is None:
            return None
        return -(trade.stake_amount / 2), HALF_TAG

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
        if exit_tag == HALF_TAG:
            two_r = self._two_r(trade)
            if two_r is not None:
                return max(two_r, proposed_rate)
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


class TrendRider1h(JeffBase):
    """Trend Rider on 1-hour candles (daily trend filter unchanged). Run with --timeframe 1h."""
    strat = "tr"
    pivot = 5
    timeframe = "1h"
    startup_candle_count = 400


class JeffFixedTP(JeffBase):
    """Trend Rider entries with Jeff's manual exits: fixed 1% stop, 2.5% take profit."""
    strat = "tr"
    pivot = 5
    use_custom_stoploss = False
    stoploss = -0.01
    minimal_roi = {"0": 0.025}
    take_half = False

    def custom_stake_amount(self, pair, current_time, current_rate, proposed_stake, min_stake,
                            max_stake, leverage, entry_tag, side, **kwargs) -> float:
        return proposed_stake
