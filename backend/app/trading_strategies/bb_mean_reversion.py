"""
AuraQuant - Bollinger Band Mean Reversion Strategy
"""
import pandas_ta as ta
import pandas as pd
from typing import Dict, Any

from .strategy_base import Strategy


class BBMeanReversion(Strategy):
    """
    A mean-reversion strategy using Bollinger Bands.

    Rules:
    - Long Entry: Price closes below the lower Bollinger Band, suggesting it's oversold.
    - Short Entry: Price closes above the upper Bollinger Band, suggesting it's overbought.
    - Exit: The position is closed when the price crosses the middle band (the moving average).
    - Risk Management: Stop Loss is placed just outside the band, Take Profit is the middle band.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        bb_len = self.get_parameter("bb_len", 20)
        bb_std = self.get_parameter("bb_std", 2.0)

        # Calculate Bollinger Bands using pandas_ta
        self.data.ta.bbands(length=bb_len, std=bb_std, append=True)

        # Rename columns for clarity. pandas_ta names them BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
        self.data.rename(columns={
            f'BBL_{bb_len}_{bb_std}': 'bb_lower',
            f'BBM_{bb_len}_{bb_std}': 'bb_middle',
            f'BBU_{bb_len}_{bb_std}': 'bb_upper',
        }, inplace=True)

        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        curr_close = self.data['close'][self.index]
        curr_low = self.data['low'][self.index]
        curr_high = self.data['high'][self.index]
        bb_lower = self.data['bb_lower'][self.index]
        bb_middle = self.data['bb_middle'][self.index]
        bb_upper = self.data['bb_upper'][self.index]

        if not self.is_in_position:
            # --- Long Entry Condition ---
            if curr_close < bb_lower:
                stop_loss = bb_lower - (bb_middle - bb_lower) * 0.5  # SL is 50% of the band width below the lower band
                take_profit = bb_middle
                self.buy(sl=stop_loss, tp=take_profit)

            # --- Short Entry Condition ---
            elif curr_close > bb_upper:
                stop_loss = bb_upper + (bb_upper - bb_middle) * 0.5  # SL is 50% of the band width above the upper band
                take_profit = bb_middle
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            # --- Exit Condition ---
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and curr_close > bb_middle:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and curr_close < bb_middle:
                    self.close_position()