"""
AuraQuant - High-Fidelity Backtesting Engine (with Regime Analysis)
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Type
import logging

from app.trading_strategies.strategy_base import Strategy
from app.services.regime_service import regime_service
from hmmlearn.hmm import GaussianHMM # For type hinting

logger = logging.getLogger(__name__)

class BacktestingService:
    """
    A powerful engine for simulating trading strategies against historical data,
    fully integrated with market regime analysis.
    """

    def __init__(
        self,
        strategy_class: Type[Strategy],
        data: pd.DataFrame,
        params: Dict[str, Any],
        symbol: str, # Symbol is now required for regime model loading
        initial_capital: float = 10000.0,
        commission_pct: float = 0.001
    ):
        self.strategy_class = strategy_class
        self.data = data.copy()
        self.params = params
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.commission_pct = commission_pct

    def _calculate_performance_metrics(self, trades: list, equity_curve: list) -> Dict[str, Any]:
        if not trades:
            return {
                "net_profit": 0, "total_trades": 0, "win_rate_pct": 0,
                "profit_factor": 0, "max_drawdown_pct": 0, "sharpe_ratio": 0,
                "regime_performance": {}, "error": "No trades were executed."
            }

        df_trades = pd.DataFrame(trades)
        # Simplified profit in USD, can be replaced with a more complex calculation
        # involving lot size, point value, etc.
        df_trades['profit_usd'] = df_trades['profit'] * 100

        total_trades = len(df_trades)
        winning_trades = df_trades[df_trades['profit_usd'] > 0]
        losing_trades = df_trades[df_trades['profit_usd'] <= 0]

        win_rate = (len(winning_trades) / total_trades) * 100 if total_trades > 0 else 0
        gross_profit = winning_trades['profit_usd'].sum()
        gross_loss = abs(losing_trades['profit_usd'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        net_profit = gross_profit - gross_loss

        equity_series = pd.Series(equity_curve)
        high_water_mark = equity_series.cummax()
        drawdown = (equity_series - high_water_mark) / high_water_mark
        max_drawdown = abs(drawdown.min()) * 100

        daily_returns = equity_series.pct_change().dropna()
        if daily_returns.std() > 0 and not daily_returns.empty:
            sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0.0

        # --- NEW: Regime-Specific Performance Analysis ---
        regime_performance = {}
        if 'regime' in df_trades.columns:
            for regime_id, group in df_trades.groupby('regime'):
                if pd.isna(regime_id): continue
                regime_id_str = str(int(regime_id))

                r_total_trades = len(group)
                r_net_profit = group['profit_usd'].sum()
                r_win_rate = (group['profit_usd'] > 0).sum() / r_total_trades * 100 if r_total_trades > 0 else 0

                regime_performance[regime_id_str] = {
                    "total_trades": r_total_trades,
                    "net_profit": r_net_profit,
                    "win_rate_pct": r_win_rate
                }

        return {
            "start_period": df_trades['entry_time'].min().strftime('%Y-%m-%d') if not df_trades.empty else None,
            "end_period": df_trades['exit_time'].max().strftime('%Y-%m-%d') if not df_trades.empty else None,
            "initial_capital": self.initial_capital,
            "net_profit": net_profit,
            "ending_equity": self.initial_capital + net_profit,
            "total_trades": total_trades,
            "win_rate_pct": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown_pct": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "average_win_usd": winning_trades['profit_usd'].mean() if not winning_trades.empty else 0,
            "average_loss_usd": losing_trades['profit_usd'].mean() if not losing_trades.empty else 0,
            "regime_performance": regime_performance,
        }

    def run(self) -> Dict[str, Any]:
        self.data['time'] = pd.to_datetime(self.data['time'])
        self.data.set_index('time', inplace=True, drop=False)

        # --- NEW: Predict Regimes for the Entire Historical Dataset ---
        regime_model: Optional[GaussianHMM] = regime_service._models.get(self.symbol.upper())
        if regime_model:
            logger.info(f"Regime model found for {self.symbol}. Predicting historical regimes...")
            # We need to rename columns temporarily to match the feature calculation function
            temp_data = self.data.rename(columns={"close": "Close"})
            features = regime_service._calculate_features_for_prediction.__self__._calculate_features(temp_data)

            if not features.empty:
                predicted_regimes = regime_model.predict(features)
                # Align the regimes with the original dataframe index
                self.data['regime'] = np.nan
                self.data.loc[features.index, 'regime'] = predicted_regimes
                # Forward-fill to handle non-trading days or missing feature data
                self.data['regime'].ffill(inplace=True)
                logger.info("Historical regime prediction complete.")
        else:
            logger.warning(f"No regime model found for {self.symbol}. Backtest will run without regime analysis.")

        # Instantiate the Strategy, now passing the full data with regime info
        strategy = self.strategy_class(data=self.data.reset_index(drop=True), params=self.params)
        strategy.init()

        equity_curve = [self.initial_capital]
        current_equity = self.initial_capital

        # 3. Main Event Loop - Iterate through each candle
        for i in range(len(self.data)):
            strategy.index = i

            # --- Check for SL/TP on the current open position ---
            if strategy.is_in_position:
                open_trade = next((t for t in strategy.trades if t['status'] == 'OPEN'), None)
                current_low = self.data['low'][i]
                current_high = self.data['high'][i]

                if open_trade:
                    # Check Stop Loss
                    if open_trade['type'] == 'BUY' and current_low <= open_trade['sl']:
                        open_trade['exit_price'] = open_trade['sl']
                        open_trade['exit_time'] = self.data['time'][i]
                        open_trade['status'] = 'CLOSED_SL'
                        strategy.is_in_position = False
                    elif open_trade['type'] == 'SELL' and current_high >= open_trade['sl']:
                        open_trade['exit_price'] = open_trade['sl']
                        open_trade['exit_time'] = self.data['time'][i]
                        open_trade['status'] = 'CLOSED_SL'
                        strategy.is_in_position = False

                    # Check Take Profit
                    elif open_trade['type'] == 'BUY' and current_high >= open_trade['tp']:
                        open_trade['exit_price'] = open_trade['tp']
                        open_trade['exit_time'] = self.data['time'][i]
                        open_trade['status'] = 'CLOSED_TP'
                        strategy.is_in_position = False
                    elif open_trade['type'] == 'SELL' and current_low <= open_trade['tp']:
                        open_trade['exit_price'] = open_trade['tp']
                        open_trade['exit_time'] = self.data['time'][i]
                        open_trade['status'] = 'CLOSED_TP'
                        strategy.is_in_position = False

            # 4. Execute the strategy's core logic for the current candle
            strategy.next()

            # --- Calculate Equity Curve ---
            # Simplified: Update equity only when a trade closes.
            # A more complex backtester would calculate unrealized P/L every bar.
            last_trade = strategy.trades[-1] if strategy.trades else None
            if last_trade and last_trade['status'] != 'OPEN' and last_trade.get('accounted') is None:
                profit_points = last_trade['exit_price'] - last_trade['entry_price']
                if last_trade['type'] == 'SELL':
                    profit_points = last_trade['entry_price'] - last_trade['exit_price']

                # Simplified profit in USD, assuming 1 lot size
                profit_usd = profit_points * 100
                commission = (last_trade['entry_price'] * 100) * self.commission_pct
                net_profit_usd = profit_usd - commission

                last_trade['profit'] = net_profit_usd
                current_equity += net_profit_usd
                last_trade['accounted'] = True

            equity_curve.append(current_equity)

        # 5. Generate Performance Report
        performance_metrics = self._calculate_performance_metrics(strategy.trades, equity_curve)

        return {
            "performance": performance_metrics,
            "trades": strategy.trades,
            "equity_curve": pd.Series(equity_curve, index=self.data.index).to_dict(),
            "parameters": self.params
        }


# Create a single instance
backtesting_service = BacktestingService