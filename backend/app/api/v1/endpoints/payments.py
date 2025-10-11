"""
AuraQuant - API Endpoints for Payments and Webhooks
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app import crud
from app.api import deps
from app.models.user import User
from app.models.subscription import SubscriptionStatus
from app.models.payment import PaymentStatus
from app.schemas.payment import PaymentInitiate, PaymentInitiateResponse, PaymentCreate
from app.schemas.subscription import SubscriptionCreate
from app.services.payment_service import payment_factory

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post("/initiate", response_model=PaymentInitiateResponse)
async def initiate_payment(
        *,
        db: AsyncSession = Depends(deps.get_db),
        payment_in: PaymentInitiate,
        current_user: User = Depends(deps.get_current_active_user),
):
    """
    Initiate a payment for a subscription plan.
    """
    plan = await crud.crud_plan.get(db, id=payment_in.plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(status_code=404, detail="Plan not found or is not active.")

    payment_service = payment_factory.get_service(payment_in.provider)
    if not payment_service:
        raise HTTPException(status_code=400, detail="Invalid payment provider.")

    try:
        init_data = await payment_service.initialize_payment(
            user=current_user,
            plan=plan,
            interval=payment_in.interval,
            success_url=payment_in.success_url,
            cancel_url=payment_in.cancel_url
        )
        return PaymentInitiateResponse(
            provider=payment_in.provider,
            authorization_url=init_data["authorization_url"],
            reference=init_data["reference"]
        )
    except Exception as e:
        logger.error(f"Payment initiation failed for provider {payment_in.provider}: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate payment. Please try again later.")


@router.get("/verify/{provider}/{reference}", status_code=status.HTTP_200_OK)
async def verify_payment_and_create_subscription(
        provider: str,
        reference: str,
        db: AsyncSession = Depends(deps.get_db),
        current_user: User = Depends(deps.get_current_active_user),
):
    """
    Verify a payment transaction and create/update the user's subscription.
    This is the endpoint the user is redirected to after a successful payment.
    """
    payment_service = payment_factory.get_service(provider)
    if not payment_service:
        raise HTTPException(status_code=400, detail="Invalid payment provider.")

    try:
        verified_data = await payment_service.verify_payment(reference)

        # --- Simple verification logic (can be made more robust) ---
        # For Paystack, status is 'success'. For PayPal, it's 'COMPLETED'.
        payment_status = verified_data.get("status", "").lower()
        is_successful = payment_status in ["success", "completed"]

        if not is_successful:
            raise HTTPException(status_code=400, detail="Payment verification failed.")

        # Extract details to create our internal records
        # This part will need to be adapted based on the exact response structure of each provider
        if provider == "paystack":
            amount = verified_data["amount"] / 100
            currency = verified_data["currency"]
            transaction_id = verified_data["reference"]
            metadata = verified_data.get("metadata", {})
            plan_id = metadata.get("plan_id")
            interval = metadata.get("interval")
        elif provider == "paypal":
            capture = verified_data["purchase_units"][0]["payments"]["captures"][0]
            amount = float(capture["amount"]["value"])
            currency = capture["amount"]["currency_code"]
            transaction_id = capture["id"]
            custom_id_parts = verified_data["purchase_units"][0].get("custom_id", "").split(',')
            metadata = {part.split(':')[0]: part.split(':')[1] for part in custom_id_parts}
            plan_id = int(metadata.get("plan_id"))
            interval = metadata.get("interval")
        else:
            raise HTTPException(status_code=400, detail="Provider not implemented for verification.")

        # Check if we have already processed this transaction
        existing_payment = await crud.crud_payment.get_by_provider_transaction_id(db, provider=provider,
                                                                                  provider_transaction_id=transaction_id)
        if existing_payment:
            logger.warning(f"Attempted to process an already existing transaction: {provider} - {transaction_id}")
            return {"status": "success", "message": "Subscription already active."}

        # --- Create Payment Record ---
        payment_obj = await crud.crud_payment.create(db, obj_in=PaymentCreate(
            user_id=current_user.id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.COMPLETED,
            provider=provider,
            provider_transaction_id=transaction_id
        ))

        # --- Create/Update Subscription Record ---
        # For simplicity, we create a new subscription. A real system might update an existing one.
        days = 365 if interval == "yearly" else 30
        end_date = datetime.utcnow() + timedelta(days=days)

        subscription_obj = await crud.crud_subscription.create(db, obj_in=SubscriptionCreate(
            user_id=current_user.id,
            plan_id=plan_id,
            status=SubscriptionStatus.ACTIVE,
            provider=provider,
            provider_subscription_id=transaction_id,
            # For simple one-off payments. Real recurring would have a subscription ID.
            current_period_start=datetime.utcnow(),
            current_period_end=end_date,
        ))

        # Link payment to the new subscription
        payment_obj.subscription_id = subscription_obj.id
        db.add(payment_obj)
        await db.commit()

        return {"status": "success", "message": "Your subscription has been activated."}

    except Exception as e:
        logger.error(f"Payment verification failed for {provider} with ref {reference}: {e}")
        raise HTTPException(status_code=500, detail="Failed to verify payment. Please contact support.")


@router.post("/webhook/{provider}", status_code=status.HTTP_200_OK)
async def payment_webhook(
        provider: str,
        request: Request,
):
    """
    Handle incoming webhooks from payment providers.
    This is crucial for managing recurring payments, cancellations, etc.
    """
    # IMPORTANT: In a production system, you MUST verify the webhook signature
    # to ensure the request is genuinely from the payment provider.
    # Each provider has a different way of doing this (e.g., checking a hash in the headers).

    payload = await request.json()
    logger.info(f"Received webhook from {provider}: {payload}")

    # Add logic here to parse the webhook payload and update subscription statuses.
    # For example, for a `charge.success` from Paystack, you would find the
    # user and extend their subscription. For a `subscription.canceled` event,
    # you would update their status in your database.

    return Response(status_code=status.HTTP_200_OK)