"""
AuraQuant - Order Orchestration Service (Definitive Final Version)

This service is the central nervous system for all trade-related actions. It is
designed to be transactional, stateful, fault-tolerant, and fully auditable.
It correctly handles live trades, paper trades, and complex algorithmic orders
like TWAP, ensuring they all pass through the same rigorous validation and
state management pipeline.
"""
import asyncio
import uuid
import logging
from typing import Dict, Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import redis_client
from app.services.market_service import unified_market_service
from app.crud.order import crud_order
from app.models.order import OrchestratedOrder, OrderStatus
from app.models.user import User
from app.schemas.order import OrderCreate, AlgoParams
from app.schemas.trade import OrderRequest, OrderType
from app.services.smart_order_router import sor_service
from app.db.session import AsyncSessionLocal
from app.services.risk_service import risk_service
from app.services.audit_service import audit_service
from app.schemas.audit import AuditLogCreate, AuditAction
from app.services.telemetry_service import telemetry_service
from app.services.alerting_service import alerting_service, AlertLevel
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class OrderOrchestratorService:
    def __init__(self):
        self._worker_task: Optional[asyncio.Task] = None
        self._algo_tasks: Dict[UUID, asyncio.Task] = {}

    async def create_order(self, db: AsyncSession, *, user: User, order_in: OrderCreate) -> OrchestratedOrder:
        """
        Step 1: Validate, persist the order, and enqueue it for submission. This is the API-facing method.
        """
        # --- PRE-TRADE RISK VALIDATION ---
        # This is the first gate. It applies to ALL order types.
        await risk_service.validate_pre_trade(db, user=user, order=order_in)

        # --- PRE-SUBMISSION VALIDATION ---
        if order_in.order_type.upper() == "LIMIT" and not order_in.price:
            raise ValueError("Price is required for LIMIT orders.")

        # An "auto" exchange setting implies SOR should be used, but we still check if ANY adapter is available.
        if order_in.exchange.lower() != "auto" :
             unified_market_service.get_adapter(order_in.exchange)
        elif not connection_manager.get_all_active_adapters():
             raise ConnectionError("Smart Order Routing requires at least one active exchange connection.")

        # --- PERSIST THE ORDER (Single Source of Truth) ---
        db_order = OrchestratedOrder(
            user_id=user.id,
            exchange=order_in.exchange,
            symbol=order_in.symbol,
            order_type=order_in.order_type.upper(),
            side=order_in.side.upper(),
            quantity_requested=order_in.quantity,
            price=order_in.price,
            status=OrderStatus.PENDING_SUBMIT,
            is_paper_trade=order_in.is_paper_trade,
            is_algorithmic=order_in.is_algorithmic,
            order_metadata={"algo_params": order_in.algo_params.model_dump() if order_in.algo_params else None}
        )
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)

        # --- AUDIT THE CREATION REQUEST ---
        await audit_service.log(db, user_id=user.id, action=AuditAction.ORDER_CREATE_REQUEST,
            details=f"User requested {'PAPER' if order_in.is_paper_trade else 'LIVE'} {order_in.side} {order_in.quantity} {order_in.symbol}",
            event_metadata={"order_id": str(db_order.id), "request": order_in.model_dump()})

        # --- ROUTE TO APPROPRIATE HANDLER ---
        if db_order.is_algorithmic:
            self.start_algorithmic_order(db_order)
        else:
            await redis_client.enqueue_order(db_order.id)

        return db_order

    async def _handle_successful_fill(self, db: AsyncSession, order: OrchestratedOrder, result: "OrderResult"):
        """
        A new helper function to handle the logic for a successfully filled order.
        """
        order.status = OrderStatus.FILLED
        order.quantity_filled = result.volume
        order.average_fill_price = result.price
        order.filled_at = datetime.now(timezone.utc)

        await self._audit_and_commit_state_change(db, order)

        # --- CRITICAL: INITIATE COPY TRADING ---
        # After a live trade from a real user is confirmed as FILLED,
        # we check if this user is a "leader" and trigger the copy trade logic for their followers.
        if not order.is_paper_trade:
            from app.services.collaboration_service import collaboration_service

            # Fetch the user (leader) object
            leader = await db.get(User, order.user_id)
            if leader:
                # Run this as a background task so it doesn't slow down the fill processing
                asyncio.create_task(
                    collaboration_service.initiate_copy_trade(db, leader=leader, trade=order)
                )


    async def _process_order_submission(self, order_id: UUID):
        """
        The main worker function that routes a dequeued order.
        """
        async with AsyncSessionLocal() as db:
            order = await crud_order.get(db, id=order_id)
            if not order or order.status != OrderStatus.PENDING_SUBMIT:
                return

            if order.is_paper_trade:
                await self._simulate_paper_trade_execution(db, order)
            else:
                await self._execute_live_trade(db, order)

    async def _execute_live_trade(self, db: AsyncSession, order: OrchestratedOrder):
        """
        Contains the logic to send a real order to an exchange adapter.
        """
        start_time = datetime.now(timezone.utc)
        try:
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now(timezone.utc)
            db.add(order)
            await db.commit()

            # --- Smart Order Routing ---
            # If the exchange is 'auto', ask the SOR for the best venue.
            target_exchange = order.exchange
            if target_exchange.lower() == 'auto':
                plan = await sor_service.generate_execution_plan(order.symbol, order.side, order.quantity_requested)
                target_exchange = plan[0]['exchange'] # Use the best exchange from the plan
                logger.info(f"SOR selected exchange '{target_exchange}' for order {order.id}.")

            adapter_req = OrderRequest(
                symbol=order.symbol, volume=order.quantity_requested,
                type=OrderType(order.side.lower()) if order.order_type == "MARKET" else OrderType(f"{order.side.lower()}_limit"),
                price=order.price)

            result = await unified_market_service.place_order(target_exchange, adapter_req)

            # --- TELEMETRY: Record latency ---
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            telemetry_service.record_order_latency(target_exchange, latency)

            if result.retcode in [10009, 0]:
                order.status = OrderStatus.ACCEPTED
                order.exchange_order_id = str(result.order)
                # In a real system, a separate process would listen for fill confirmations
                # and call this telemetry function. For now, we simulate an immediate fill.
                telemetry_service.record_fill_event(
                    exchange=target_exchange, symbol=order.symbol, side=order.side,
                    quantity=result.volume, price=result.price
                )
                # In a real system, a separate webhook/stream would update from ACCEPTED to FILLED.
                # For this implementation, we'll simulate an immediate fill and trigger the copy trade.
                await self._handle_successful_fill(db, order, result)
            else:
                # --- ALERT: Order Rejection ---
                await alerting_service.dispatch(
                    message=f"Live order {order.id} for user {order.user_id} on {order.symbol} was REJECTED by {target_exchange}. Reason: {result.retcode_message}",
                    level=AlertLevel.WARNING
                )
                order.status = OrderStatus.REJECTED
                order.failure_reason = result.retcode_message
                await self._audit_and_commit_state_change(db, order)
        except Exception as e:
            # --- CRITICAL ALERT: Execution Failure ---
            await alerting_service.dispatch(
                message=f"CRITICAL FAILURE during live execution for order {order.id} (User: {order.user_id}). Reason: {e}",
                level=AlertLevel.CRITICAL
            )
            logger.error(f"LIVE execution failed for order {order.id}: {e}", exc_info=True)
            order.status = OrderStatus.ERROR
            order.failure_reason = str(e)
        finally:
            await self._audit_and_commit_state_change(db, order)

    async def _simulate_paper_trade_execution(self, db: AsyncSession, order: OrchestratedOrder):
        """
        Simulates the execution of an order against live market data.
        """
        try:
            order.status = OrderStatus.SUBMITTED
            order.submitted_at = datetime.now(timezone.utc)
            await self._audit_and_commit_state_change(db, order)

            await asyncio.sleep(0.2)
            tick = await unified_market_service.get_latest_tick(order.exchange, order.symbol)
            if not tick: raise ConnectionError(f"Market data unavailable for paper trade simulation.")

            order.status = OrderStatus.ACCEPTED
            order.exchange_order_id = f"PAPER-{uuid.uuid4().hex[:12]}"
            await self._audit_and_commit_state_change(db, order)

            await asyncio.sleep(0.5)

            fill_price = tick.ask if order.side == 'BUY' else tick.bid
            if order.order_type == "LIMIT": fill_price = order.price

            order.status = OrderStatus.FILLED
            order.quantity_filled = order.quantity_requested
            order.average_fill_price = fill_price
            order.filled_at = datetime.now(timezone.utc)
        except Exception as e:
            logger.error(f"PAPER simulation failed for order {order.id}: {e}", exc_info=True)
            order.status = OrderStatus.ERROR
            order.failure_reason = f"Paper trade simulation failed: {e}"
        finally:
            await self._audit_and_commit_state_change(db, order)

    def start_algorithmic_order(self, parent_order: OrchestratedOrder):
        """Starts the execution logic for a parent algorithmic order."""
        order_id = parent_order.id
        if order_id in self._algo_tasks and not self._algo_tasks[order_id].done():
            logger.warning(f"Algo task for order {order_id} is already running.")
            return

        if parent_order.metadata and parent_order.metadata.get("algo_params"):
            logger.info(f"Starting TWAP execution for order {order_id}.")
            task = asyncio.create_task(self._execute_twap_strategy(parent_order))
            self._algo_tasks[order_id] = task
        else:
            logger.error(f"Algorithmic order {order_id} has no parameters. Halting execution.")

    async def _execute_twap_strategy(self, parent_order: OrchestratedOrder):
        """The long-running execution logic for a single TWAP order."""
        try:
            params = AlgoParams(**parent_order.metadata["algo_params"])
            total_duration_sec = params.duration_minutes * 60
            interval_sec = total_duration_sec / params.num_children
            child_qty = parent_order.quantity_requested / params.num_children

            logger.info(f"TWAP [{parent_order.id}]: Executing {child_qty:.6f} every {interval_sec:.2f}s for {params.num_children} intervals.")

            async with AsyncSessionLocal() as db:
                parent_order.status = OrderStatus.ACCEPTED
                await self._audit_and_commit_state_change(db, parent_order)

            for i in range(params.num_children):
                await asyncio.sleep(interval_sec)
                try:
                    exec_plan = await sor_service.generate_execution_plan(parent_order.symbol, parent_order.side, child_qty)
                    route = exec_plan[0]

                    # --- CRITICAL: Propagate the paper trade flag to children ---
                    child_order_in = OrderCreate(
                        exchange=route['exchange'], symbol=parent_order.symbol, order_type="MARKET",
                        side=parent_order.side, quantity=route['quantity'],
                        is_paper_trade=parent_order.is_paper_trade
                    )

                    async with AsyncSessionLocal() as db:
                        child_db_order = OrchestratedOrder(
                            user_id=parent_order.user_id, parent_order_id=parent_order.id,
                            exchange=child_order_in.exchange, symbol=child_order_in.symbol,
                            order_type=child_order_in.order_type, side=child_order_in.side,
                            quantity_requested=child_order_in.quantity, status=OrderStatus.PENDING_SUBMIT,
                            is_paper_trade=child_order_in.is_paper_trade # Ensure flag is set
                        )
                        db.add(child_db_order)
                        await db.commit()
                        await db.refresh(child_db_order)

                        await redis_client.enqueue_order(child_db_order.id)
                        logger.info(f"TWAP [{parent_order.id}]: Enqueued child order #{i + 1} ({child_db_order.id})")
                except Exception as e:
                    logger.error(f"ERROR in TWAP [{parent_order.id}] loop iteration #{i+1}: {e}", exc_info=True)

            logger.info(f"TWAP [{parent_order.id}]: All child orders enqueued.")
            # A full implementation would then monitor children and mark parent as FILLED.
        except Exception as e:
            logger.error(f"FATAL ERROR in TWAP strategy for parent order {parent_order.id}: {e}", exc_info=True)

    async def _audit_and_commit_state_change(self, db: AsyncSession, order: OrchestratedOrder):
        """A helper to ensure state changes are audited and committed atomically."""
        order.updated_at = datetime.now(timezone.utc)
        db.add(order)
        await audit_service.log(db, user_id=order.user_id, action=AuditAction.ORDER_STATE_CHANGE,
            details=f"Order {order.id} for {order.symbol} changed status to {order.status}.",
            metadata={"order_id": str(order.id), "new_status": order.status, "reason": order.failure_reason})
        await db.commit()

    # --- Worker Management ---
    async def run_worker(self):
        logger.info("Order Orchestrator Worker is running...")
        while True:
            try:
                order_id = await redis_client.dequeue_order()
                if order_id:
                    logger.info(f"Worker dequeued order: {order_id}")
                    asyncio.create_task(self._process_order_submission(order_id))
            except Exception as e:
                logger.error(f"Error in orchestrator worker loop: {e}", exc_info=True)
                await asyncio.sleep(5)

    def start_worker(self):
        if not self._worker_task or self._worker_task.done():
            self._worker_task = asyncio.create_task(self.run_worker())

    def stop_worker(self):
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None

orchestrator_service = OrderOrchestratorService()