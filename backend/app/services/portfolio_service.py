"""
AuraQuant - Advanced Portfolio Analysis and Optimization Service
"""
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from pypfopt import EfficientFrontier, risk_models, expected_returns, objective_functions

from app.crud.order import crud_order
from app.models.user import User


class PortfolioService:
    """
    Provides advanced analytics and optimization for a user's entire trading portfolio.
    """

    async def _get_and_process_trade_history(
            self, db: AsyncSession, user_id: int, start_date: datetime, end_date: datetime
    ) -> Optional[pd.DataFrame]:
        """
        Fetches all filled orders for a user and calculates daily P/L for each symbol.
        """
        orders = await crud_order.get_all_filled_for_user_in_range(
            db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        if not orders:
            return None

        trades = []
        for o in orders:
            # Simplified P/L calculation
            profit = (o.average_fill_price - o.price) * o.quantity_filled if o.side == "BUY" else (
                                                                                                              o.price - o.average_fill_price) * o.quantity_filled
            trades.append({
                "date": o.filled_at.date(),
                "symbol": o.symbol,
                "profit": profit
            })

        if not trades: return None

        df = pd.DataFrame(trades)
        # Pivot table to get daily P/L per symbol
        pnl_df = df.pivot_table(index='date', columns='symbol', values='profit', aggfunc='sum').fillna(0)
        return pnl_df

    async def run_portfolio_analysis(
            self, db: AsyncSession, user: User, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Performs a full analysis of the user's historical trading performance.
        """
        pnl_df = await self._get_and_process_trade_history(db, user.id, start_date, end_date)
        if pnl_df is None or pnl_df.empty:
            return {"error": "Not enough trade data for analysis in the selected period."}

        # --- Calculate Daily Portfolio Returns ---
        # Assume a constant starting capital for calculating returns
        initial_capital = 100_000
        daily_pnl = pnl_df.sum(axis=1)
        daily_capital = initial_capital + daily_pnl.cumsum()
        daily_returns = daily_capital.pct_change().fillna(0)

        # --- Risk/Return Metrics ---
        total_return = (daily_capital.iloc[-1] / initial_capital) - 1
        sharpe_ratio = (daily_returns.mean() * 252) / (
                    daily_returns.std() * np.sqrt(252)) if daily_returns.std() > 0 else 0

        # Volatility (Annualized)
        volatility = daily_returns.std() * np.sqrt(252)

        # Max Drawdown
        high_water_mark = daily_capital.cummax()
        drawdown = (daily_capital - high_water_mark) / high_water_mark
        max_drawdown = abs(drawdown.min())

        return {
            "total_return_pct": total_return * 100,
            "annualized_volatility_pct": volatility * 100,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_pct": max_drawdown * 100,
            "asset_returns_correlation": pnl_df.corr().to_dict(),
        }

    async def run_mean_variance_optimization(
            self, db: AsyncSession, user: User, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """
        Performs a classic Markowitz Mean-Variance Optimization to find the
        portfolio allocation that maximizes the Sharpe ratio.
        """
        pnl_df = await self._get_and_process_trade_history(db, user.id, start_date, end_date)
        if pnl_df is None or pnl_df.empty or len(pnl_df.columns) < 2:
            return {"error": "Optimization requires at least two traded assets with history."}

        # 1. Calculate expected annual returns for each asset
        mu = expected_returns.mean_historical_return(pnl_df, returns_data=True, frequency=252)

        # 2. Calculate the annualized sample covariance matrix of returns
        S = risk_models.sample_cov(pnl_df, returns_data=True, frequency=252)

        # 3. Optimize for maximal Sharpe ratio
        ef = EfficientFrontier(mu, S)
        # Add an objective to regularize weights to avoid extreme allocations
        ef.add_objective(objective_functions.L2_reg, gamma=0.1)

        ef.max_sharpe()

        cleaned_weights = ef.clean_weights()
        performance = ef.portfolio_performance(verbose=False)

        return {
            "optimal_weights": cleaned_weights,
            "expected_annual_return_pct": performance[0] * 100,
            "annual_volatility_pct": performance[1] * 100,
            "sharpe_ratio": performance[2],
        }


portfolio_service = PortfolioService()