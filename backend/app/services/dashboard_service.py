"""
AuraQuant - Dashboard Aggregation Service
"""
from typing import Optional
from datetime import datetime, timedelta
import random  # For mock portfolio data generation

from .market_data_service import market_data_service
from .trade_service import trade_service
from app.schemas.dashboard import DashboardSummary, PortfolioTimeSeriesData


class DashboardService:
    """
    Service to aggregate data from various sources for the main dashboard.
    """

    def _generate_mock_portfolio_history(self, initial_equity: float) -> list[PortfolioTimeSeriesData]:
        """
        Generates a realistic-looking but simulated time series for the portfolio chart.
        In a real system, this data would be derived from a ledger of historical
        account equity snapshots.
        """
        history = []
        current_value = initial_equity
        now = datetime.utcnow()
        for i in range(90):  # 90 days of history
            date = now - timedelta(days=i)
            # Introduce some random walk and a slight upward drift
            change_percent = (random.random() - 0.48) / 100  # small daily fluctuation
            current_value *= (1 + change_percent)
            history.append(PortfolioTimeSeriesData(time=date, value=round(current_value, 2)))

        return history[::-1]  # Return in chronological order

    def get_dashboard_summary(self) -> Optional[DashboardSummary]:
        """
        Gathers and returns the aggregated dashboard summary.
        """
        if not market_data_service.is_ready() or not trade_service.is_ready():
            return None

        # 1. Get Market & Account Status
        market_status = market_data_service.get_market_status()
        if not market_status:
            return None

        # 2. Get Open Positions
        open_positions = trade_service.get_open_positions()

        # 3. Calculate Aggregates
        open_positions_count = len(open_positions)
        total_profit_loss = sum(p.profit for p in open_positions)

        # 4. Get Recent Positions (show up to 5 most recent)
        recent_positions = sorted(open_positions, key=lambda p: p.time, reverse=True)[:5]

        # 5. Get Portfolio History (Simulated)
        portfolio_history = self._generate_mock_portfolio_history(market_status.account_equity)

        return DashboardSummary(
            market_status=market_status,
            open_positions_count=open_positions_count,
            total_profit_loss=round(total_profit_loss, 2),
            recent_positions=recent_positions,
            portfolio_history=portfolio_history,
        )


# Create a single instance of the service
dashboard_service = DashboardService()