"""
AuraQuant - Bollinger Band Mean Reversion Strategy (Self-Contained)
This version has no external 'pandas_ta' dependency.
"""
import pandas as pd
from typing import Dict, Any

from .strategy_base import Strategy

class BBMeanReversion(Strategy):
    """
    A mean-reversion strategy using Bollinger Bands.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        bb_len = self.get_parameter("bb_len", 20)
        bb_std = self.get_parameter("bb_std", 2.0)
        
        # --- REPLACED PANDAS_TA LOGIC ---
        # Calculate the Middle Band (Simple Moving Average)
        middle_band = self.data['close'].rolling(window=bb_len).mean()
        
        # Calculate the Standard Deviation
        std_dev = self.data['close'].rolling(window=bb_len).std()
        
        # Calculate the Upper and Lower Bands
        upper_band = middle_band + (std_dev * bb_std)
        lower_band = middle_band - (std_dev * bb_std)
        
        self.data['bb_lower'] = lower_band
        self.data['bb_middle'] = middle_band
        self.data['bb_upper'] = upper_band
        # --- END OF REPLACEMENT ---
        
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        """
        The core logic of this method remains exactly the same, as the
        DataFrame columns ('bb_lower', 'bb_middle', 'bb_upper') are named identically.
        """
        curr_close = self.data['close'][self.index]
        bb_lower = self.data['bb_lower'][self.index]
        bb_middle = self.data['bb_middle'][self.index]
        bb_upper = self.data['bb_upper'][self.index]

        if not self.is_in_position:
            if curr_close < bb_lower:
                stop_loss = bb_lower - (bb_middle - bb_lower) * 0.5
                take_profit = bb_middle
                self.buy(sl=stop_loss, tp=take_profit)

            elif curr_close > bb_upper:
                stop_loss = bb_upper + (bb_upper - bb_middle) * 0.5
                take_profit = bb_middle
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and curr_close > bb_middle:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and curr_close < bb_middle:
                    self.close_position()
