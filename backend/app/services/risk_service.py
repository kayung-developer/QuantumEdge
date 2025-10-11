"""
AuraQuant - Real-Time Pre-Trade Risk Management Service (Complete Implementation)

This service is the gatekeeper for all trading activity. Its primary function,
`validate_pre_trade`, is called by the Order Orchestrator before any order is
created in the system. It performs a series of rigorous checks against a user's
risk profile. If any check fails, it raises an exception, immediately halting
the order process and creating a detailed audit log of the violation.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging

from app.models.user import User
from app.models.risk import UserRiskProfile
from app.crud.risk import crud_risk_profile
from app.schemas.order import OrderCreate
from app.schemas.trade import PositionInfo
from app.services.market_service import unified_market_service
from app.services.audit_service import audit_service
from app.schemas.audit import AuditLogCreate, AuditAction

logger = logging.getLogger(__name__)

class RiskManagementService:

    async def get_user_profile(self, db: AsyncSession, user_id: int) -> Optional[UserRiskProfile]:
        """Fetches a user's risk profile from the database via the CRUD layer."""
        return await crud_risk_profile.get_by_user_id(db, user_id=user_id)

    # --- INDIVIDUAL RISK CHECK IMPLEMENTATIONS ---

    def _check_trading_halted(self, profile: Optional[UserRiskProfile]):
        """RULE 1: Checks if the user's account has a manual trading halt (kill switch) enabled."""
        if profile and profile.trading_halted:
            raise PermissionError("Trading is currently halted for this account by an administrator.")

    def _check_max_order_value(self, profile: Optional[UserRiskProfile], order: OrderCreate, price: float):
        """RULE 2: Checks if the total value of the new order exceeds the user's configured limit."""
        if profile and profile.max_order_value_usd:
            order_value = order.quantity * price
            if order_value > profile.max_order_value_usd:
                raise ValueError(f"Order value ${order_value:,.2f} exceeds the maximum single order value of ${profile.max_order_value_usd:,.2f}.")

    def _check_max_open_positions(self, profile: Optional[UserRiskProfile], open_positions: List[PositionInfo]):
        """RULE 3: Checks if creating this new order would exceed the user's max concurrent positions limit."""
        if profile and profile.max_open_positions is not None:
            # We check >= because the new order will become a new position
            if len(open_positions) >= profile.max_open_positions:
                raise ValueError(f"Exceeds maximum of {profile.max_open_positions} open positions.")

    def _check_symbol_exposure(self, profile: Optional[UserRiskProfile], open_positions: List[PositionInfo], order: OrderCreate, price: float):
        """RULE 4: Calculates total exposure for the order's symbol and checks against the user's limit."""
        if profile and profile.max_exposure_per_symbol_usd:
            current_symbol_exposure = sum(
                pos.volume * pos.price_current
                for pos in open_positions
                if pos.symbol == order.symbol
            )
            new_order_value = order.quantity * price
            total_potential_exposure = current_symbol_exposure + new_order_value

            if total_potential_exposure > profile.max_exposure_per_symbol_usd:
                raise ValueError(f"Order for {order.symbol} would increase exposure to ${total_potential_exposure:,.2f}, exceeding the limit of ${profile.max_exposure_per_symbol_usd:,.2f}.")

    def _check_total_exposure(self, profile: Optional[UserRiskProfile], open_positions: List[PositionInfo], order: OrderCreate, price: float):
        """RULE 5: Calculates total account exposure across all symbols and checks against the user's limit."""
        if profile and profile.max_total_exposure_usd:
            current_total_exposure = sum(pos.volume * pos.price_current for pos in open_positions)
            new_order_value = order.quantity * price
            total_potential_exposure = current_total_exposure + new_order_value

            if total_potential_exposure > profile.max_total_exposure_usd:
                raise ValueError(f"Order would increase total account exposure to ${total_potential_exposure:,.2f}, exceeding the limit of ${profile.max_total_exposure_usd:,.2f}.")

    # --- MAIN VALIDATION ORCHESTRATOR ---

    async def validate_pre_trade(self, db: AsyncSession, *, user: User, order: OrderCreate) -> bool:
        """
        The main validation entry point. Runs all risk checks sequentially for a new order.
        This is the primary function consumed by other services.

        Returns:
            True if all checks pass.
        Raises:
            PermissionError or ValueError if any check fails.
        """
        # Step 1: Fetch the user's risk profile. If none exists, platform defaults apply (i.e., no checks fail).
        user_with_profile = await db.get(User, user.id, options=[selectinload(User.risk_profile)])
        profile = user_with_profile.risk_profile

        try:
            # CHECK 1: Trading Halt (Kill Switch) - The most important check, run first.
            self._check_trading_halted(profile)

            # Step 2: Gather live market data needed for calculations.
            # This is done once to be efficient.
            tick = await unified_market_service.get_latest_tick(order.exchange, order.symbol)
            if not tick:
                raise ConnectionError(f"Could not fetch live price for {order.symbol} to perform risk checks.")

            # Use the "ask" for buys and "bid" for sells to accurately calculate cost/value.
            price_for_calc = tick.ask if order.side.upper() == 'BUY' else tick.bid

            open_positions = await unified_market_service.get_open_positions(order.exchange)

            # --- RUN ALL CHECKS SEQUENTIALLY ---

            # CHECK 2: Max Order Value
            self._check_max_order_value(profile, order, price_for_calc)

            # CHECK 3: Max Open Positions
            self._check_max_open_positions(profile, open_positions)

            # CHECK 4: Per-Symbol Exposure
            self._check_symbol_exposure(profile, open_positions, order, price_for_calc)

            # CHECK 5: Total Account Exposure
            self._check_total_exposure(profile, open_positions, order, price_for_calc)

            # NOTE: Drawdown checks are more complex and would typically run on a slightly
            # delayed basis or against a cached daily high-water mark, as they are computationally
            # intensive. A pre-trade check for drawdown is an advanced topic often
            # handled by a separate, dedicated risk analysis service.

        except (PermissionError, ValueError, ConnectionError) as e:
            # --- CRITICAL: Log the Risk Violation to the Audit Trail ---
            logger.warning(f"RISK VIOLATION for user {user.id}: {e}")
            await audit_service.log(
                db,
                user_id=user.id,
                action=AuditAction.RISK_RULE_VIOLATION,
                details=f"Pre-trade risk check failed for {order.side} {order.quantity} {order.symbol}: {e}",
                event_metadata={
                    "order_request": order.model_dump(),
                    "check_failed": e.__class__.__name__,
                    "profile_rules_active": profile.model_dump() if profile else "default"
                }
            )

            # Re-raise the exception. This is what stops the order from proceeding
            # in the OrderOrchestratorService.
            raise e

        # If all checks pass without raising an exception, return True.
        logger.info(f"Pre-trade risk checks passed for user {user.id} for order on {order.symbol}.")
        return True

# Create a single, globally accessible instance of the service.
risk_service = RiskManagementService()