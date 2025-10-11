"""
AuraQuant - Momentum Crossover Trading Strategy (Self-Contained)
This version has no external 'pandas_ta' dependency and calculates all
indicators directly using pandas for maximum robustness and reliability.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from .strategy_base import Strategy

class MomentumCrossover(Strategy):
    """
    A trend-following and momentum strategy.

    Rules:
    - Long Entry: Fast EMA crosses above Slow EMA AND RSI is above a certain threshold.
    - Short Entry: Fast EMA crosses below Slow EMA AND RSI is below a certain threshold.
    - Exit: Position is closed when a crossover in the opposite direction occurs.
    - Risk Management: Stop Loss is set using the ATR, Take Profit is a multiple of the SL.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    # --- NEW: Internal Indicator Calculation Methods ---

    def _calculate_ema(self, series: pd.Series, length: int) -> pd.Series:
        """Calculates the Exponential Moving Average using pandas."""
        return series.ewm(span=length, adjust=False).mean()

    def _calculate_rsi(self, series: pd.Series, length: int) -> pd.Series:
        """Calculates the Relative Strength Index using pandas."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=length).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> pd.Series:
        """Calculates the Average True Range using pandas."""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=length).mean()


    def init(self):
        """
        Pre-calculate all indicators using internal, robust methods.
        """
        fast_ema_len = self.get_parameter("fast_ema", 20)
        slow_ema_len = self.get_parameter("slow_ema", 50)
        rsi_len = self.get_parameter("rsi_len", 14)
        atr_len = self.get_parameter("atr_len", 14)

        # Use our internal, self-contained functions to calculate indicators
        self.data['fast_ema'] = self._calculate_ema(self.data['close'], fast_ema_len)
        self.data['slow_ema'] = self._calculate_ema(self.data['close'], slow_ema_len)
        self.data['rsi'] = self._calculate_rsi(self.data['close'], rsi_len)
        self.data['atr'] = self._calculate_atr(self.data['high'], self.data['low'], self.data['close'], atr_len)

        # Drop rows with NaN values resulting from indicator calculations
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        """
        The core logic of the strategy, executed for each data point.
        THIS METHOD REMAINS EXACTLY THE SAME as the logic is unchanged.
        """
        if self.index < 1:
            return

        rsi_buy_threshold = self.get_parameter("rsi_buy_threshold", 50)
        rsi_sell_threshold = self.get_parameter("rsi_sell_threshold", 50)
        atr_multiplier_sl = self.get_parameter("atr_multiplier_sl", 2.0)
        risk_reward_ratio = self.get_parameter("risk_reward_ratio", 1.5)

        prev_fast_ema = self.data['fast_ema'][self.index - 1]
        prev_slow_ema = self.data['slow_ema'][self.index - 1]
        curr_fast_ema = self.data['fast_ema'][self.index]
        curr_slow_ema = self.data['slow_ema'][self.index]
        curr_rsi = self.data['rsi'][self.index]
        curr_atr = self.data['atr'][self.index]
        curr_close = self.data['close'][self.index]

        bullish_crossover = prev_fast_ema < prev_slow_ema and curr_fast_ema > curr_slow_ema
        bearish_crossover = prev_fast_ema > prev_slow_ema and curr_fast_ema < curr_slow_ema

        if not self.is_in_position:
            if bullish_crossover and curr_rsi > rsi_buy_threshold:
                stop_loss = curr_close - (curr_atr * atr_multiplier_sl)
                take_profit = curr_close + ((curr_close - stop_loss) * risk_reward_ratio)
                self.buy(sl=stop_loss, tp=take_profit)

            elif bearish_crossover and curr_rsi < rsi_sell_threshold:
                stop_loss = curr_close + (curr_atr * atr_multiplier_sl)
                take_profit = curr_close - ((stop_loss - curr_close) * risk_reward_ratio)
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and bearish_crossover:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and bullish_crossover:
                    self.close_position()
