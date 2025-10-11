"""
AuraQuant - Trade Forensics and Risk Attribution Service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import pandas as pd
import pandas_ta as ta

from app.crud.order import crud_order
from app.services.market_service import unified_market_service


class ForensicsService:
    """
    Provides detailed, post-trade analysis for a single executed trade.
    """

    async def get_trade_forensics(self, db: AsyncSession, order_id: UUID) -> Dict[str, Any]:
        """
        Enriches a filled order with contextual market data from its execution period.
        """
        order = await crud_order.get(db, id=order_id)
        if not order or order.status != OrderStatus.FILLED:
            raise ValueError("Forensics can only be run on filled orders.")

        # 1. Fetch market data for the period the trade was open
        start_dt = order.created_at
        end_dt = order.filled_at

        # Fetch slightly more data for indicator context
        context_start_dt = start_dt - timedelta(days=5)

        klines = await unified_market_service.get_historical_klines(
            exchange_name=order.exchange, symbol=order.symbol, timeframe="1H",
            start_dt=context_start_dt, end_dt=end_dt
        )
        if not klines:
            return {"error": "Could not retrieve market data for the trade period."}

        df = pd.DataFrame([k.model_dump() for k in klines])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True)

        # 2. Calculate key indicators at the time of entry
        df.ta.rsi(length=14, append=True, col_names=('rsi',))
        df.ta.macd(append=True, col_names=('macd', 'macdh', 'macds'))

        entry_data = df.iloc[df.index.get_loc(start_dt, method='nearest')]

        # 3. Calculate trade performance metrics
        profit = (order.average_fill_price - order.price) * order.quantity_filled if order.side == "BUY" else (
                                                                                                                          order.price - order.average_fill_price) * order.quantity_filled

        # Calculate Maximum Favorable Excursion (MFE) and Maximum Adverse Excursion (MAE)
        trade_period_df = df.loc[start_dt:end_dt]
        if order.side == "BUY":
            mfe = trade_period_df['high'].max() - order.price
            mae = order.price - trade_period_df['low'].min()
        else:  # SELL
            mfe = order.price - trade_period_df['low'].min()
            mae = trade_period_df['high'].max() - order.price

        return {
            "order_details": order,
            "performance": {
                "profit": profit,
                "return_pct": (profit / (order.price * order.quantity_filled)) * 100,
                "mfe": mfe,  # Max potential profit
                "mae": mae,  # Max potential loss
            },
            "market_context_at_entry": {
                "rsi": entry_data.get('rsi'),
                "macd_histogram": entry_data.get('macdh'),
                "volume": entry_data.get('volume'),
            }
        }


forensics_service = ForensicsService()