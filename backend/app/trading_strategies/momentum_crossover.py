"""
AuraQuant - Momentum Crossover Trading Strategy
"""
import pandas_ta as ta
import pandas as pd
from typing import Dict, Any

from .strategy_base import Strategy


class MomentumCrossover(Strategy):
    """
    A trend-following and momentum strategy.

    Rules:
    - Long Entry: Fast EMA crosses above Slow EMA AND RSI is above a certain threshold (e.g., 50).
    - Short Entry: Fast EMA crosses below Slow EMA AND RSI is below a certain threshold (e.g., 50).
    - Exit: Position is closed when a crossover in the opposite direction occurs.
    - Risk Management: Stop Loss is set using the ATR, Take Profit is a multiple of the SL.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        super().__init__(data, params)

    def init(self):
        """
        Pre-calculate all indicators using the pandas_ta library for efficiency.
        """
        fast_ema_len = self.get_parameter("fast_ema", 20)
        slow_ema_len = self.get_parameter("slow_ema", 50)
        rsi_len = self.get_parameter("rsi_len", 14)
        atr_len = self.get_parameter("atr_len", 14)

        # Use pandas_ta to efficiently calculate indicators for the entire dataset
        self.data.ta.ema(length=fast_ema_len, append=True)
        self.data.ta.ema(length=slow_ema_len, append=True)
        self.data.ta.rsi(length=rsi_len, append=True)
        self.data.ta.atr(length=atr_len, append=True)

        # Clean up column names for easier access
        self.data.rename(columns={
            f'EMA_{fast_ema_len}': 'fast_ema',
            f'EMA_{slow_ema_len}': 'slow_ema',
            f'RSI_{rsi_len}': 'rsi',
            f'ATRr_{atr_len}': 'atr'
        }, inplace=True)

        # Drop rows with NaN values resulting from indicator calculations
        self.data.dropna(inplace=True)
        self.data.reset_index(drop=True, inplace=True)

    def next(self):
        """
        Define the logic for each candle (data point).
        """
        if self.index < 1:  # Ensure we have a previous candle to check for crossovers
            return

        # --- Get parameters ---
        rsi_buy_threshold = self.get_parameter("rsi_buy_threshold", 50)
        rsi_sell_threshold = self.get_parameter("rsi_sell_threshold", 50)
        atr_multiplier_sl = self.get_parameter("atr_multiplier_sl", 2.0)
        risk_reward_ratio = self.get_parameter("risk_reward_ratio", 1.5)

        # --- Get current and previous candle data for crossover detection ---
        prev_fast_ema = self.data['fast_ema'][self.index - 1]
        prev_slow_ema = self.data['slow_ema'][self.index - 1]
        curr_fast_ema = self.data['fast_ema'][self.index]
        curr_slow_ema = self.data['slow_ema'][self.index]
        curr_rsi = self.data['rsi'][self.index]
        curr_atr = self.data['atr'][self.index]
        curr_close = self.data['close'][self.index]

        # --- Define Crossover Conditions ---
        bullish_crossover = prev_fast_ema < prev_slow_ema and curr_fast_ema > curr_slow_ema
        bearish_crossover = prev_fast_ema > prev_slow_ema and curr_fast_ema < curr_slow_ema

        # --- Position Management ---
        if not self.is_in_position:
            # --- Long Entry Condition ---
            if bullish_crossover and curr_rsi > rsi_buy_threshold:
                stop_loss = curr_close - (curr_atr * atr_multiplier_sl)
                take_profit = curr_close + ((curr_close - stop_loss) * risk_reward_ratio)
                self.buy(sl=stop_loss, tp=take_profit)

            # --- Short Entry Condition ---
            elif bearish_crossover and curr_rsi < rsi_sell_threshold:
                stop_loss = curr_close + (curr_atr * atr_multiplier_sl)
                take_profit = curr_close - ((stop_loss - curr_close) * risk_reward_ratio)
                self.sell(sl=stop_loss, tp=take_profit)
        else:
            # --- Exit Condition ---
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                if open_trade['type'] == 'BUY' and bearish_crossover:
                    self.close_position()
                elif open_trade['type'] == 'SELL' and bullish_crossover:
                    self.close_position()