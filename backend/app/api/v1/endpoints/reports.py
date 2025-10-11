"""
AuraQuant - API Endpoints for Data Exports and Reporting
"""
import csv
import io
from datetime import datetime
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.crud.order import crud_order

router = APIRouter()


@router.get("/export/trade-history")
async def export_trade_history(
        start_date: datetime,
        end_date: datetime,
        db: AsyncSession = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Generates and streams a CSV file of the user's complete, filled trade
    history for a given date range.
    """
    # Fetch all filled orders for the user in the date range
    orders = await crud_order.get_all_filled_for_user_in_range(db, user_id=current_user.id, start_date=start_date,
                                                               end_date=end_date)

    # Use an in-memory text stream to build the CSV
    string_io = io.StringIO()
    writer = csv.writer(string_io)

    # Write the CSV header
    writer.writerow([
        "OrderID", "ExchangeOrderID", "Exchange", "Symbol", "Side", "Type",
        "QuantityRequested", "QuantityFilled", "AverageFillPrice",
        "Status", "FilledTimestamp", "IsPaperTrade"
    ])

    # Write the data rows
    for order in orders:
        writer.writerow([
            str(order.id), order.exchange_order_id, order.exchange, order.symbol,
            order.side, order.order_type, order.quantity_requested,
            order.quantity_filled, order.average_fill_price,
            order.status, order.filled_at.isoformat() if order.filled_at else None,
            order.is_paper_trade
        ])

    # Create a streaming response
    response = StreamingResponse(
        iter([string_io.getvalue()]),
        media_type="text/csv"
    )
    # Set the filename for the download
    response.headers[
        "Content-Disposition"] = f"attachment; filename=auraquant_trade_history_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv"

    return response