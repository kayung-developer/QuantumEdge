"""
AuraQuant - Smart Money Concepts (SMC) Order Block Strategy
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

from .strategy_base import Strategy


class SMCOrderBlock(Strategy):
    """
    A strategy based on Smart Money Concepts, specifically trading order blocks
    after a Break of Structure (BOS).

    Core Logic:
    1. Identify Swings: Find significant swing highs and swing lows in the price action.
    2. Detect Break of Structure (BOS):
        - A bullish BOS occurs when price breaks above a recent significant swing high.
        - A bearish BOS occurs when price breaks below a recent significant swing low.
    3. Identify the Order Block:
        - For a bullish BOS, the order block is the last down-candle before the impulsive move up that caused the BOS.
        - For a bearish BOS, the order block is the last up-candle before the impulsive move down that caused the BOS.
    4. Entry Condition:
        - After a bullish BOS, wait for the price to "Return to Block" (RTB) - i.e., retrace back into the price range of the identified bullish order block. Enter a long trade.
        - After a bearish BOS, wait for price to RTB into the bearish order block. Enter a short trade.
    5. Risk Management:
        - For a long trade, the Stop Loss is placed just below the low of the bullish order block.
        - For a short trade, the Stop Loss is placed just above the high of the bearish order block.
        - Take Profit is set at a fixed risk-to-reward ratio.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)
        self.swing_highs = []
        self.swing_lows = []
        self.last_bos_up = None  # Stores info about the last bullish BOS and its order block
        self.last_bos_down = None  # Stores info about the last bearish BOS and its order block

    def init(self):
        """
        Identify all significant swing points in the data first.
        A simple swing point is a candle with lower/higher highs/lows on both sides.
        """
        lookback = self.get_parameter("swing_lookback", 5)

        for i in range(lookback, len(self.data) - lookback):
            # Swing High: A high with `lookback` lower highs on both sides
            is_swing_high = self.data['high'][i] == self.data['high'][i - lookback:i + lookback + 1].max()
            if is_swing_high:
                self.swing_highs.append({'index': i, 'price': self.data['high'][i]})

            # Swing Low: A low with `lookback` higher lows on both sides
            is_swing_low = self.data['low'][i] == self.data['low'][i - lookback:i + lookback + 1].min()
            if is_swing_low:
                self.swing_lows.append({'index': i, 'price': self.data['low'][i]})

    def _get_last_swing(self, swing_list: list):
        """Helper to find the most recent swing point relative to the current index."""
        relevant_swings = [s for s in swing_list if s['index'] < self.index]
        return relevant_swings[-1] if relevant_swings else None

    def next(self):
        risk_reward_ratio = self.get_parameter("risk_reward_ratio", 3.0)

        # --- 1. Identify most recent swing points ---
        last_swing_high = self._get_last_swing(self.swing_highs)
        last_swing_low = self._get_last_swing(self.swing_lows)

        if not last_swing_high or not last_swing_low:
            return

        curr_high = self.data['high'][self.index]
        curr_low = self.data['low'][self.index]
        curr_close = self.data['close'][self.index]

        # --- 2. Detect Break of Structure (BOS) ---

        # Bullish BOS: Price breaks a significant high
        if curr_high > last_swing_high['price']:
            # Find the impulse move that broke the structure
            impulse_start_index = self._get_last_swing(self.swing_lows)['index']

            # 3. Identify the Bullish Order Block (last down candle before the impulse)
            impulse_candles = self.data.iloc[impulse_start_index:last_swing_high['index']]
            down_candles = impulse_candles[impulse_candles['close'] < impulse_candles['open']]
            if not down_candles.empty:
                order_block_index = down_candles.index[-1]
                self.last_bos_up = {
                    'bos_index': self.index,
                    'ob_index': order_block_index,
                    'ob_high': self.data['high'][order_block_index],
                    'ob_low': self.data['low'][order_block_index]
                }
                self.last_bos_down = None  # Invalidate bearish setup

        # Bearish BOS: Price breaks a significant low
        elif curr_low < last_swing_low['price']:
            # Find the impulse move that broke the structure
            impulse_start_index = self._get_last_swing(self.swing_highs)['index']

            # 3. Identify the Bearish Order Block (last up candle before the impulse)
            impulse_candles = self.data.iloc[impulse_start_index:last_swing_low['index']]
            up_candles = impulse_candles[impulse_candles['close'] > impulse_candles['open']]
            if not up_candles.empty:
                order_block_index = up_candles.index[-1]
                self.last_bos_down = {
                    'bos_index': self.index,
                    'ob_index': order_block_index,
                    'ob_high': self.data['high'][order_block_index],
                    'ob_low': self.data['low'][order_block_index]
                }
                self.last_bos_up = None  # Invalidate bullish setup

        # --- 4. Check for Entry Condition (Return to Block) ---
        if not self.is_in_position:
            # Check for Bullish Entry
            if self.last_bos_up and curr_low <= self.last_bos_up['ob_high'] and curr_high >= self.last_bos_up['ob_low']:
                entry_price = self.last_bos_up['ob_high']  # Enter at the top of the block
                stop_loss = self.last_bos_up['ob_low']  # SL below the block
                take_profit = entry_price + (entry_price - stop_loss) * risk_reward_ratio

                self.buy(sl=stop_loss, tp=take_profit)
                self.last_bos_up = None  # Consume the setup

            # Check for Bearish Entry
            elif self.last_bos_down and curr_high >= self.last_bos_down['ob_low'] and curr_low <= self.last_bos_down[
                'ob_high']:
                entry_price = self.last_bos_down['ob_low']  # Enter at the bottom of the block
                stop_loss = self.last_bos_down['ob_high']  # SL above the block
                take_profit = entry_price - (stop_loss - entry_price) * risk_reward_ratio

                self.sell(sl=stop_loss, tp=take_profit)
                self.last_bos_down = None  # Consume the setup