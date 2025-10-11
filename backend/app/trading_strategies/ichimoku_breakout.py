"""
AuraQuant - Ichimoku Cloud Breakout Strategy
"""
import pandas_ta as ta
import pandas as pd
from typing import Dict, Any

from .strategy_base import Strategy


class IchimokuBreakout(Strategy):
    """
    A trend-following strategy based on the Ichimoku Kinko Hyo indicator.

    Rules:
    - Bullish Trend Confirmation:
        1. Price is above the Kumo Cloud (Senkou Span A and B).
        2. Tenkan-sen is above Kijun-sen.
        3. Chikou Span is above the price from 26 periods ago.
    - Bearish Trend Confirmation:
        1. Price is below the Kumo Cloud.
        2. Tenkan-sen is below Kijun-sen.
        3. Chikou Span is below the price from 26 periods ago.

    - Long Entry: A strong bullish trend is confirmed.
    - Short Entry: A strong bearish trend is confirmed.
    - Exit: When the Tenkan-sen crosses the Kijun-sen in the opposite direction.
    - Risk Management: Stop Loss is placed on the other side of the Kumo Cloud.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        tenkan_len = self.get_parameter("tenkan", 9)
        kijun_len = self.get_parameter("kijun", 26)
        senkou_len = self.get_parameter("senkou", 52)

        # Calculate the full Ichimoku indicator set
        self.data.ta.ichimoku(
            tenkan=tenkan_len,
            kijun=kijun_len,
            senkou=senkou_len,
            append=True
        )

        # pandas_ta creates columns like 'ITS_9', 'IKS_26', 'ISA_9_26_52', 'ISB_9_26_52', 'ICS_26'
        # Let's rename them for clarity
        self.data.rename(columns={
            f'ITS_{tenkan_len}': 'tenkan_sen',
            f'IKS_{kijun_len}': 'kijun_sen',
            f'ISA_{tenkan_len}_{kijun_len}_{senkou_len}': 'senkou_a',
            f'ISB_{kijun_len}': 'senkou_b',  # Note: pandas_ta ISB uses kijun length
            f'ICS_{kijun_len}': 'chikou_span'
        }, inplace=True)

        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        if self.index < 1:
            return

        # --- Get current indicator values ---
        curr_close = self.data['close'][self.index]
        tenkan = self.data['tenkan_sen'][self.index]
        kijun = self.data['kijun_sen'][self.index]
        senkou_a = self.data['senkou_a'][self.index]
        senkou_b = self.data['senkou_b'][self.index]
        chikou = self.data['chikou_span'][self.index]

        # Kumo Cloud boundaries
        kumo_top = max(senkou_a, senkou_b)
        kumo_bottom = min(senkou_a, senkou_b)

        # --- Define Trend Conditions ---
        is_bullish_trend = (
                curr_close > kumo_top and
                tenkan > kijun and
                chikou > self.data['close'][self.index - 26]  # Chikou vs price 26 periods ago
        )
        is_bearish_trend = (
                curr_close < kumo_bottom and
                tenkan < kijun and
                chikou < self.data['close'][self.index - 26]
        )

        # --- Crossover for Exits ---
        prev_tenkan = self.data['tenkan_sen'][self.index - 1]
        prev_kijun = self.data['kijun_sen'][self.index - 1]
        tenkan_crosses_below_kijun = prev_tenkan > prev_kijun and tenkan < kijun
        tenkan_crosses_above_kijun = prev_tenkan < prev_kijun and tenkan > kijun

        if not self.is_in_position:
            # --- Long Entry ---
            if is_bullish_trend:
                stop_loss = kumo_bottom  # Place SL on the other side of the cloud
                take_profit = curr_close + (curr_close - stop_loss) * 1.5  # 1.5 R:R
                self.buy(sl=stop_loss, tp=take_profit)

            # --- Short Entry ---
            elif is_bearish_trend:
                stop_loss = kumo_top  # Place SL on the other side of the cloud
                take_profit = curr_close - (stop_loss - curr_close) * 1.5
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            # --- Exit Logic ---
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and tenkan_crosses_below_kijun:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and tenkan_crosses_above_kijun:
                    self.close_position()