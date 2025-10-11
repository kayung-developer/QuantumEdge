"""
AuraQuant - AI Trading Signal Service
"""
import asyncio
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.signal import crud_signal  # Assumes this is created
from app.schemas.signal import SignalCreate, SignalAction  # Assumes these are created
from app.models.signal import AISignal, SignalStatus
from app.models.user import User
from app.services.cv_service import cv_service
from app.services.market_service import unified_market_service
from app.services.order_orchestrator import orchestrator_service
from app.schemas.order import OrderCreate


class SignalService:
    """
    Manages the creation, lifecycle, and execution of AI-generated trading signals.
    """

    async def generate_signal_from_cv_detection(
            self, db: AsyncSession, user: User, detection: dict
    ) -> Optional[AISignal]:
        """
        Translates a CV pattern detection into an actionable trading signal.
        """
        # --- This is where the "strategy" part of the AI lives ---
        # It defines HOW to trade a detected pattern.

        # Example logic for a Head and Shoulders pattern
        if detection['pattern_type'] == 'Head and Shoulders':
            symbol = detection['symbol']
            exchange = 'Binance'  # Should be dynamic

            # Fetch current price for SL/TP calculation
            tick = await unified_market_service.get_latest_tick(exchange, symbol)
            if not tick: return None

            entry_price = tick.bid  # Enter at market
            stop_loss = tick.ask * 1.01  # Simplistic SL 1% above
            take_profit = entry_price - (stop_loss - entry_price) * 2.0  # 2:1 R:R

            signal_in = SignalCreate(
                user_id=user.id,
                model_name="AuraQuant-Chart-Pattern-CNN-v1",
                model_version="1.0",  # This should be dynamic from the loaded model
                exchange=exchange,
                symbol=symbol,
                timeframe="1H",
                side="SELL",
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                confidence_score=detection['confidence_score'],
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                rationale=f"Detected a {detection['pattern_type']} pattern with {detection['confidence_score']:.2f} confidence."
            )

            new_signal = await crud_signal.create(db, obj_in=signal_in)

            # TODO: Send a real-time notification to the user (e.g., via WebSocket/SSE)
            print(f"NEW AI SIGNAL GENERATED for user {user.id}: {new_signal.id}")

            return new_signal
        return None

    async def run_cv_scanner_for_user(self, db: AsyncSession, user: User):
        """
        A background task that periodically scans markets for a user and generates signals.
        """
        # In a real system, this would scan the user's watchlist
        symbols_to_scan = ["BTCUSDT", "ETHUSDT"]
        for symbol in symbols_to_scan:
            klines = await unified_market_service.get_historical_klines(
                'Binance', symbol, '1H', datetime.now() - timedelta(days=10), datetime.now()
            )
            detections = cv_service.detect_patterns(klines)
            for detection in detections:
                detection_dict = detection.model_dump()
                detection_dict['symbol'] = symbol
                await self.generate_signal_from_cv_detection(db, user, detection_dict)

    async def action_signal(
            self, db: AsyncSession, *, signal_id: UUID, user: User, action: SignalAction
    ) -> AISignal:
        """
        Handles a user's action (approve/reject) on a signal.
        """
        signal = await crud_signal.get(db, id=signal_id)
        if not signal or signal.user_id != user.id:
            raise ValueError("Signal not found or user not authorized.")

        if signal.status != SignalStatus.GENERATED:
            raise ValueError(f"Signal is already in a terminal state ({signal.status}).")

        if action.action_type == "REJECT":
            signal.status = SignalStatus.REJECTED
            signal.actioned_by_user = True
            signal.actioned_at = datetime.now(timezone.utc)
            db.add(signal)
            await db.commit()
            return signal

        elif action.action_type == "APPROVE":
            signal.status = SignalStatus.EXECUTING
            signal.actioned_by_user = True
            signal.actioned_at = datetime.now(timezone.utc)

            # --- Trigger the Orchestrator ---
            order_in = OrderCreate(
                exchange=signal.exchange,
                symbol=signal.symbol,
                order_type="MARKET",  # AI signals could be limit too
                side=signal.side,
                quantity=0.01  # Quantity should be calculated based on risk rules
            )
            # This will run risk checks before creating the order
            created_order = await orchestrator_service.create_order(db, user=user, order_in=order_in)

            # Link the signal to the order
            signal.orchestrated_order_id = created_order.id
            db.add(signal)
            await db.commit()
            await db.refresh(signal)

            return signal

        raise ValueError("Invalid action type.")


signal_service = SignalService()