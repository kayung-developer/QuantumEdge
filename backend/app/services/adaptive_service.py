"""
AuraQuant - Adaptive Deployment Service (Live Engine)
"""
import asyncio
import logging
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.crud.adaptive import crud_adaptive_portfolio  # Assumes this is created
from app.services.regime_service import regime_service
from app.services.market_service import unified_market_service

logger = logging.getLogger(__name__)


class AdaptiveDeploymentService:
    def __init__(self, check_interval_seconds: int = 300):  # Check every 5 minutes
        self._worker_task: Optional[asyncio.Task] = None
        self.check_interval = check_interval_seconds
        # This dictionary will hold the last known active regime for each portfolio
        self._active_regime_state: Dict[int, int] = {}

    async def _tick(self):
        """
        A single run of the adaptive portfolio check.
        """
        logger.info("Adaptive worker ticking...")
        async with AsyncSessionLocal() as db:
            active_portfolios = await crud_adaptive_portfolio.get_all_active(db)

            for portfolio in active_portfolios:
                try:
                    # 1. Fetch data needed for regime prediction
                    # We need ~30 days of data for reliable feature calculation
                    end_dt = datetime.utcnow()
                    start_dt = end_dt - timedelta(days=30)
                    klines = await unified_market_service.get_historical_klines(
                        exchange_name="Binance",  # Should be dynamic from portfolio
                        symbol=portfolio.symbol,
                        timeframe="1D",  # Regimes are typically on daily timeframe
                        start_dt=start_dt,
                        end_dt=end_dt
                    )
                    if not klines: continue

                    data_df = pd.DataFrame([k.model_dump() for k in klines])
                    data_df.rename(columns={"close": "Close"}, inplace=True)

                    # 2. Predict the current regime
                    current_regime = regime_service.predict_current_regime(portfolio.symbol, data_df)

                    if current_regime is None: continue

                    last_known_regime = self._active_regime_state.get(portfolio.id)

                    # 3. Check if the regime has changed
                    if current_regime != last_known_regime:
                        logger.info(
                            f"REGIME CHANGE DETECTED for portfolio {portfolio.id} ({portfolio.symbol}): "
                            f"From {last_known_regime} -> {current_regime}"
                        )

                        # 4. Look up the new strategy to activate
                        new_strategy_id = portfolio.regime_strategy_map.get(str(current_regime))

                        if new_strategy_id:
                            # --- CRITICAL INTEGRATION POINT ---
                            # In a complete system, this is where you would signal a
                            # live trading execution engine.
                            logger.warning(
                                f"ACTION: Signal live engine to DEACTIVATE old strategy and "
                                f"ACTIVATE new strategy '{new_strategy_id}' for portfolio {portfolio.id}."
                            )
                            # Example: await live_trading_engine.switch_strategy(portfolio.id, new_strategy_id)
                        else:
                            logger.warning(
                                f"ACTION: No strategy defined for new regime {current_regime}. "
                                f"Signaling live engine to HALT ALL TRADING for portfolio {portfolio.id}."
                            )
                            # Example: await live_trading_engine.halt_portfolio(portfolio.id)

                        # 5. Update the state
                        self._active_regime_state[portfolio.id] = current_regime

                except Exception as e:
                    logger.error(f"Error processing adaptive portfolio {portfolio.id}: {e}")

    async def run_worker(self):
        """
        The main loop for the background worker.
        """
        logger.info("Adaptive Deployment Service worker is running...")
        while True:
            try:
                await self._tick()
            except Exception as e:
                logger.error(f"Error in adaptive worker main loop: {e}")
            await asyncio.sleep(self.check_interval)

    def start(self):
        """Starts the worker as a background asyncio task."""
        if not self._worker_task or self._worker_task.done():
            self._worker_task = asyncio.create_task(self.run_worker())

    def stop(self):
        """Stops the worker task."""
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None
            logger.info("Adaptive Deployment Service worker stopped.")


adaptive_service = AdaptiveDeploymentService()

# You would then call adaptive_service.start() in the main.py lifespan manager.