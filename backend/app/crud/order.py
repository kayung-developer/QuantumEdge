"""
AuraQuant - CRUD Operations for the OrchestratedOrder Model (with Reporting Query)
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.order import OrchestratedOrder, OrderStatus
from app.schemas.order import OrderCreate
from pydantic import BaseModel

class CRUDOrder(CRUDBase[OrchestratedOrder, OrderCreate, BaseModel]):
    async def get(self, db: AsyncSession, id: UUID) -> Optional[OrchestratedOrder]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_by_exchange_order_id(self, db: AsyncSession, *, exchange_order_id: str) -> Optional[OrchestratedOrder]:
        result = await db.execute(
            select(self.model).filter(OrchestratedOrder.exchange_order_id == exchange_order_id)
        )
        return result.scalars().first()

    async def get_all_active_orders(self, db: AsyncSession) -> List[OrchestratedOrder]:
        active_states = [OrderStatus.PENDING_SUBMIT, OrderStatus.SUBMITTED, OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED]
        result = await db.execute(
            select(self.model).filter(OrchestratedOrder.status.in_(active_states))
        )
        return result.scalars().all()

    # --- NEW METHOD FOR REPORTING ---
    async def get_all_filled_for_user_in_range(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> List[OrchestratedOrder]:
        """
        Retrieves all orders for a specific user within a date range that
        are in a 'FILLED' state. This is the primary query for generating
        tax and regulatory reports.

        Args:
            db: The SQLAlchemy async session.
            user_id: The ID of the user.
            start_date: The start of the time window.
            end_date: The end of the time window.

        Returns:
            A list of OrchestratedOrder objects.
        """
        result = await db.execute(
            select(self.model)
            .filter(
                OrchestratedOrder.user_id == user_id,
                OrchestratedOrder.status == OrderStatus.FILLED,
                OrchestratedOrder.filled_at >= start_date,
                OrchestratedOrder.filled_at <= end_date
            )
            .order_by(OrchestratedOrder.filled_at.asc())
        )
        return result.scalars().all()


# Create a single instance
crud_order = CRUDOrder(OrchestratedOrder)