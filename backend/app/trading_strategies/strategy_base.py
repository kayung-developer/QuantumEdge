"""
AuraQuant - Abstract Base Class for Trading Strategies
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd


class Strategy(ABC):
    """
    Abstract Base Class for all trading strategies.

    This class defines the standard interface that all strategies must implement.
    The execution engines (backtester, live trader) will interact with strategies
    through this common interface.

    Attributes:
        params (Dict[str, Any]): A dictionary of parameters that customize the
                                 strategy's behavior (e.g., moving average lengths).
        data (pd.DataFrame): The historical market data (OHLCV) for the asset,
                             provided by the execution engine.
    """

    def __init__(self, data: pd.DataFrame, params: Dict[str, Any]):
        """
        Initializes the strategy instance.

        Args:
            data: A pandas DataFrame containing the historical OHLCV data.
                  The DataFrame must have columns: ['time', 'open', 'high', 'low', 'close', 'volume'].
                  'time' should be a datetime object.
            params: A dictionary of parameters to configure the strategy.
        """
        if not all(col in data.columns for col in ['time', 'open', 'high', 'low', 'close', 'volume']):
            raise ValueError("Input DataFrame is missing required OHLCV columns.")

        self.params = params
        self.data = data
        self.index = 0  # The current data point (candle) being processed
        self.trades = []  # A log of all trades executed by the strategy
        self.is_in_position = False

    @abstractmethod
    def init(self):
        """
        Initialize the strategy.

        This method is called once before the main event loop (`next`). It should
        be used to perform any pre-calculations or to set up indicators on the
        entire dataset. For example, calculating moving averages for all data points.
        """
        pass

    @abstractmethod
    def next(self):
        """
        The core logic of the strategy, executed for each data point.

        This method is called sequentially for each row in the `data` DataFrame.
        It should contain the logic to decide whether to enter, exit, or hold a
        position based on the current and past data.
        """
        pass

    # --- Helper methods available to all strategies ---

    def buy(self, sl: float, tp: float):
        """
        Places a buy order at the current data point.
        In a backtest, this records a trade. In live trading, it would execute a real order.
        """

        if not self.is_in_position:
            entry_price = self.data['close'][self.index]
            current_regime = self.data['regime'][self.index] if 'regime' in self.data.columns else None
            self.trades.append({
                'type': 'BUY',
                'entry_time': self.data['time'][self.index],
                'entry_price': entry_price,
                'exit_time': None,
                'exit_price': None,
                'sl': sl,
                'tp': tp,
                'profit': 0,
                'status': 'OPEN',
                'regime': current_regime

            })
            self.is_in_position = True

    def sell(self, sl: float, tp: float):
        """
        Places a sell order at the current data point.
        """
        if not self.is_in_position:
            entry_price = self.data['close'][self.index]
            current_regime = self.data['regime'][self.index] if 'regime' in self.data.columns else None
            self.trades.append({
                'type': 'SELL',
                'entry_time': self.data['time'][self.index],
                'entry_price': entry_price,
                'exit_time': None,
                'exit_price': None,
                'sl': sl,
                'tp': tp,
                'profit': 0,
                'status': 'OPEN',
                'regime': current_regime
            })
            self.is_in_position = True

    def close_position(self):
        """
        Closes the current open position.
        """
        if self.is_in_position:
            open_trade = next((t for t in self.trades if t['status'] == 'OPEN'), None)
            if open_trade:
                exit_price = self.data['close'][self.index]
                open_trade['exit_price'] = exit_price
                open_trade['exit_time'] = self.data['time'][self.index]
                open_trade['status'] = 'CLOSED'

                profit_points = exit_price - open_trade['entry_price']
                if open_trade['type'] == 'SELL':
                    profit_points = open_trade['entry_price'] - exit_price

                # A simplified profit calculation. A real system would include lot size, commission, etc.
                open_trade['profit'] = profit_points
                self.is_in_position = False

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a parameter from the params dictionary.
        """
        return self.params.get(key, default)