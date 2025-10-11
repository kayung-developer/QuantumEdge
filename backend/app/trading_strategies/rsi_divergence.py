"""
AuraQuant - RSI Divergence Trading Strategy
"""
import pandas_ta as ta
import pandas as pd
import numpy as np
from typing import Dict, Any

from .strategy_base import Strategy


class RSIDivergence(Strategy):
    """
    Identifies and trades on RSI divergences.

    - Bullish Divergence: Price makes a new low, but RSI makes a higher low.
    - Bearish Divergence: Price makes a new high, but RSI makes a lower high.
    This requires looking back over a certain period to identify peaks and troughs.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        rsi_len = self.get_parameter("rsi_len", 14)
        self.data.ta.rsi(length=rsi_len, append=True)
        self.data.rename(columns={f'RSI_{rsi_len}': 'rsi'}, inplace=True)
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def _find_peaks_troughs(self, series: pd.Series, lookback: int):
        """Helper to find the last significant peak or trough."""
        window = series[self.index - lookback: self.index]
        if len(window) == 0:
            return None, None

        peak_idx = window.idxmax()
        trough_idx = window.idxmin()
        return peak_idx, trough_idx

    def next(self):
        lookback_period = self.get_parameter("lookback", 30)
        risk_reward_ratio = self.get_parameter("risk_reward_ratio", 2.0)

        if self.index < lookback_period:
            return

        # --- Find recent peaks and troughs in price and RSI ---
        price_peak_idx, price_trough_idx = self._find_peaks_troughs(self.data['high'], lookback_period)
        _, price_trough_idx_low = self._find_peaks_troughs(self.data['low'], lookback_period)
        rsi_peak_idx, rsi_trough_idx = self._find_peaks_troughs(self.data['rsi'], lookback_period)

        curr_close = self.data['close'][self.index]
        curr_low = self.data['low'][self.index]
        curr_high = self.data['high'][self.index]

        if not self.is_in_position:
            # --- Bearish Divergence (Sell Signal) ---
            # Condition: Price makes a new high, but RSI makes a lower high.
            is_new_price_high = curr_high > self.data['high'][price_peak_idx]
            is_lower_rsi_high = self.data['rsi'][self.index] < self.data['rsi'][rsi_peak_idx]

            if is_new_price_high and is_lower_rsi_high:
                stop_loss = curr_high * 1.01  # SL 1% above the high
                take_profit = curr_close - (stop_loss - curr_close) * risk_reward_ratio
                self.sell(sl=stop_loss, tp=take_profit)
                return

            # --- Bullish Divergence (Buy Signal) ---
            # Condition: Price makes a new low, but RSI makes a higher low.
            is_new_price_low = curr_low < self.data['low'][price_trough_idx_low]
            is_higher_rsi_low = self.data['rsi'][self.index] > self.data['rsi'][rsi_trough_idx]

            if is_new_price_low and is_higher_rsi_low:
                stop_loss = curr_low * 0.99  # SL 1% below the low
                take_profit = curr_close + ((curr_close - stop_loss) * risk_reward_ratio)
                self.buy(sl=stop_loss, tp=take_profit)

        else:  # Is in position, look for an exit
            # For simplicity, we'll use a trailing stop or fixed exit.
            # A more advanced version would look for a reversal signal.
            self.close_position()  # Simple exit for demonstration