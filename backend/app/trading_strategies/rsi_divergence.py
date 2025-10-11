"""
AuraQuant - RSI Divergence Trading Strategy (Self-Contained)
This version has no external 'pandas_ta' dependency.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from .strategy_base import Strategy

class RSIDivergence(Strategy):
    """
    Identifies and trades on RSI divergences.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def _calculate_rsi(self, series: pd.Series, length: int) -> pd.Series:
        """Calculates the Relative Strength Index using pandas."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/length, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/length, adjust=False).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def init(self):
        rsi_len = self.get_parameter("rsi_len", 14)

        # --- REPLACED PANDAS_TA LOGIC ---
        self.data['rsi'] = self._calculate_rsi(self.data['close'], rsi_len)
        # --- END OF REPLACEMENT ---

        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def _find_peaks_troughs(self, series: pd.Series, lookback: int):
        """Helper to find the last significant peak or trough."""
        window = series[self.index - lookback : self.index]
        if len(window) < lookback:
            return None, None
        
        peak_idx = window.idxmax()
        trough_idx = window.idxmin()
        return peak_idx, trough_idx

    def next(self):
        """
        The core logic of this method remains exactly the same.
        """
        lookback_period = self.get_parameter("lookback", 30)
        risk_reward_ratio = self.get_parameter("risk_reward_ratio", 2.0)
        
        if self.index < lookback_period:
            return

        price_peak_idx, _ = self._find_peaks_troughs(self.data['high'], lookback_period)
        _, price_trough_idx_low = self._find_peaks_troughs(self.data['low'], lookback_period)
        rsi_peak_idx, rsi_trough_idx = self._find_peaks_troughs(self.data['rsi'], lookback_period)

        if price_peak_idx is None or price_trough_idx_low is None or rsi_peak_idx is None or rsi_trough_idx is None:
            return

        curr_close = self.data['close'][self.index]
        curr_low = self.data['low'][self.index]
        curr_high = self.data['high'][self.index]
        
        if not self.is_in_position:
            is_new_price_high = curr_high > self.data['high'][price_peak_idx]
            is_lower_rsi_high = self.data['rsi'][self.index] < self.data['rsi'][rsi_peak_idx]

            if is_new_price_high and is_lower_rsi_high:
                stop_loss = curr_high * 1.01
                take_profit = curr_close - (stop_loss - curr_close) * risk_reward_ratio
                self.sell(sl=stop_loss, tp=take_profit)
                return

            is_new_price_low = curr_low < self.data['low'][price_trough_idx_low]
            is_higher_rsi_low = self.data['rsi'][self.index] > self.data['rsi'][rsi_trough_idx]
            
            if is_new_price_low and is_higher_rsi_low:
                stop_loss = curr_low * 0.99
                take_profit = curr_close + ((curr_close - stop_loss) * risk_reward_ratio)
                self.buy(sl=stop_loss, tp=take_profit)
        
        else:
            self.close_position()
