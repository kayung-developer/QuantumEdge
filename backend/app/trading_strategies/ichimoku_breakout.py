"""
AuraQuant - Ichimoku Cloud Breakout Strategy (Self-Contained)
This version has no external 'pandas_ta' dependency.
"""
import pandas as pd
from typing import Dict, Any

from .strategy_base import Strategy

class IchimokuBreakout(Strategy):
    """
    A trend-following strategy based on the Ichimoku Kinko Hyo indicator.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        tenkan_len = self.get_parameter("tenkan", 9)
        kijun_len = self.get_parameter("kijun", 26)
        senkou_len = self.get_parameter("senkou", 52)
        chikou_len = kijun_len # Chikou is typically the same as Kijun
        
        # --- REPLACED PANDAS_TA LOGIC ---
        # Tenkan-sen (Conversion Line)
        tenkan_high = self.data['high'].rolling(window=tenkan_len).max()
        tenkan_low = self.data['low'].rolling(window=tenkan_len).min()
        self.data['tenkan_sen'] = (tenkan_high + tenkan_low) / 2

        # Kijun-sen (Base Line)
        kijun_high = self.data['high'].rolling(window=kijun_len).max()
        kijun_low = self.data['low'].rolling(window=kijun_len).min()
        self.data['kijun_sen'] = (kijun_high + kijun_low) / 2

        # Senkou Span A (Leading Span A)
        self.data['senkou_a'] = ((self.data['tenkan_sen'] + self.data['kijun_sen']) / 2).shift(kijun_len)

        # Senkou Span B (Leading Span B)
        senkou_high = self.data['high'].rolling(window=senkou_len).max()
        senkou_low = self.data['low'].rolling(window=senkou_len).min()
        self.data['senkou_b'] = ((senkou_high + senkou_low) / 2).shift(kijun_len)

        # Chikou Span (Lagging Span)
        self.data['chikou_span'] = self.data['close'].shift(-chikou_len)
        # --- END OF REPLACEMENT ---
        
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        """
        The core logic of this method remains exactly the same.
        """
        if self.index < 26: # Need enough past data for Chikou comparison
            return

        curr_close = self.data['close'][self.index]
        tenkan = self.data['tenkan_sen'][self.index]
        kijun = self.data['kijun_sen'][self.index]
        senkou_a = self.data['senkou_a'][self.index]
        senkou_b = self.data['senkou_b'][self.index]
        chikou = self.data['chikou_span'][self.index]

        kumo_top = max(senkou_a, senkou_b)
        kumo_bottom = min(senkou_a, senkou_b)

        is_bullish_trend = (
            curr_close > kumo_top and tenkan > kijun and
            chikou > self.data['close'][self.index]
        )
        is_bearish_trend = (
            curr_close < kumo_bottom and tenkan < kijun and
            chikou < self.data['close'][self.index]
        )

        prev_tenkan = self.data['tenkan_sen'][self.index - 1]
        prev_kijun = self.data['kijun_sen'][self.index - 1]
        tenkan_crosses_below_kijun = prev_tenkan > prev_kijun and tenkan < kijun
        tenkan_crosses_above_kijun = prev_tenkan < prev_kijun and tenkan > kijun
        
        if not self.is_in_position:
            if is_bullish_trend:
                stop_loss = kumo_bottom
                take_profit = curr_close + (curr_close - stop_loss) * 1.5
                self.buy(sl=stop_loss, tp=take_profit)
            
            elif is_bearish_trend:
                stop_loss = kumo_top
                take_profit = curr_close - (stop_loss - curr_close) * 1.5
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and tenkan_crosses_below_kijun:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and tenkan_crosses_above_kijun:
                    self.close_position()
