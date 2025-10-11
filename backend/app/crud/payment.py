"""
AuraQuant - CRUD Operations for the Payment Model
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate

class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    async def get_by_provider_transaction_id(
        self, db: AsyncSession, *, provider: str, provider_transaction_id: str
    ) -> Optional[Payment]:
        """
        Retrieve a payment by the payment provider's unique transaction ID.
        """
        result = await db.execute(
            select(self.model)
            .filter(
                Payment.provider == provider,
                Payment.provider_transaction_id == provider_transaction_id
            )
        )
        return result.scalars().first()

# Create a single instance
crud_payment = CRUDPayment(Payment)