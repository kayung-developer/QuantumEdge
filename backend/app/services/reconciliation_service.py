"""
AuraQuant - Trade Reconciliation Service
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.db.session import AsyncSessionLocal
from app.core.connections import connection_manager
from app.crud.order import crud_order
from app.crud.reconciliation import crud_reconciliation_report  # Assumes this is created
from app.models.order import OrchestratedOrder, OrderStatus
from app.models.reconciliation import ReconciliationStatus, ReconciliationReport
from app.services.audit_service import audit_service
from app.schemas.audit import AuditLogCreate, AuditAction

logger = logging.getLogger(__name__)


class ReconciliationService:
    def __init__(self):
        self._worker_task: Optional[asyncio.Task] = None
        self.run_interval_seconds = 3600  # Run every hour

    async def _run_single_reconciliation(self, exchange_name: str, start_dt: datetime, end_dt: datetime):
        """
        Performs a full reconciliation for a single exchange over a given period.
        """
        report = ReconciliationReport(
            exchange_name=exchange_name, status=ReconciliationStatus.RUNNING,
            start_time=datetime.now(timezone.utc), internal_trades_checked=0,
            external_trades_fetched=0, matched_trades=0, mismatched_trades=0,
            missing_internal=0, missing_external=0
        )

        try:
            adapter = connection_manager.get_adapter(exchange_name)
            if not adapter:
                raise ConnectionError(f"Adapter for {exchange_name} is not active.")

            async with AsyncSessionLocal() as db:
                # 1. Fetch internal filled orders from our database
                internal_orders = await crud_order.get_filled_in_range(db, exchange_name, start_dt, end_dt)
                internal_map = {o.exchange_order_id: o for o in internal_orders}
                report.internal_trades_checked = len(internal_orders)

                # 2. Fetch external trade history from the exchange
                external_trades = await adapter.get_trade_history(start_dt, end_dt)
                external_map = {str(t.order): t for t in external_trades}
                report.external_trades_fetched = len(external_trades)

                discrepancies = []

                # 3. Compare internal records against external records
                for internal_id, internal_order in internal_map.items():
                    external_trade = external_map.pop(internal_id, None)
                    if external_trade:
                        # --- Match Found: Compare key fields ---
                        is_mismatched = False
                        mismatch_details = {}

                        # Compare volume (handle potential floating point issues)
                        if not np.isclose(internal_order.quantity_filled, external_trade.volume):
                            is_mismatched = True
                            mismatch_details['volume'] = {'internal': internal_order.quantity_filled,
                                                          'external': external_trade.volume}

                        # Compare price
                        if not np.isclose(internal_order.average_fill_price, external_trade.price):
                            is_mismatched = True
                            mismatch_details['price'] = {'internal': internal_order.average_fill_price,
                                                         'external': external_trade.price}

                        if is_mismatched:
                            report.mismatched_trades += 1
                            discrepancies.append({
                                'type': 'mismatch', 'order_id': internal_id, 'details': mismatch_details
                            })
                        else:
                            report.matched_trades += 1
                    else:
                        # --- Missing External ---
                        report.missing_external += 1
                        discrepancies.append({'type': 'missing_external', 'order_id': internal_id})

                # 4. Any remaining trades in the external_map are missing from our internal records
                for external_id, _ in external_map.items():
                    report.missing_internal += 1
                    discrepancies.append({'type': 'missing_internal', 'order_id': external_id})

                # 5. Finalize Report
                report.discrepancies = discrepancies
                if report.mismatched_trades > 0 or report.missing_internal > 0 or report.missing_external > 0:
                    report.status = ReconciliationStatus.FAILURE if report.missing_internal > 0 else ReconciliationStatus.WARNING
                else:
                    report.status = ReconciliationStatus.SUCCESS

        except Exception as e:
            logger.error(f"Reconciliation for {exchange_name} failed: {e}", exc_info=True)
            report.status = ReconciliationStatus.FAILURE
            report.discrepancies = [{"type": "error", "message": str(e)}]
        finally:
            report.end_time = datetime.now(timezone.utc)
            report.duration_seconds = (report.end_time - report.start_time).total_seconds()

            async with AsyncSessionLocal() as db:
                await crud_reconciliation_report.create(db, obj_in=report)
                if report.status != ReconciliationStatus.SUCCESS:
                    # Send a critical alert if reconciliation fails
                    await alerting_service.dispatch(
                        message=f"Reconciliation for {exchange_name} completed with status: {report.status}. {report.mismatched_trades} mismatches, {report.missing_internal} missing internal records.",
                        level=AlertLevel.CRITICAL
                    )

    async def run_worker(self):
        """The main loop for the reconciliation background worker."""
        logger.info("Reconciliation Service worker is running...")
        while True:
            active_adapters = connection_manager.get_all_active_adapters()
            end_dt = datetime.now(timezone.utc)
            start_dt = end_dt - timedelta(seconds=self.run_interval_seconds)

            for adapter in active_adapters:
                logger.info(f"Starting reconciliation job for {adapter.exchange_name}...")
                await self._run_single_reconciliation(adapter.exchange_name, start_dt, end_dt)

            await asyncio.sleep(self.run_interval_seconds)

    def start(self):
        if not self._worker_task or self._worker_task.done():
            self._worker_task = asyncio.create_task(self.run_worker())

    def stop(self):
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None


reconciliation_service = ReconciliationService()