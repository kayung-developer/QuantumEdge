"""
AuraQuant - AutoML Strategy Forging Service
"""
import pandas as pd
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from celery import group
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

from app.celery_worker import run_single_backtest_permutation
from app.crud.forge import crud_forge_job  # Assumes this is created
from app.models.autotrade import ForgeJob, ForgeJobStatus
from app.trading_strategies import STRATEGY_REGISTRY
from app.services.market_service import unified_market_service


class ForgeService:

    def _get_parameter_space(self, strategy_id: str):
        """
        Defines the search space for each strategy's parameters.
        This is crucial for the optimization algorithm.
        """
        # Example for Momentum Crossover
        if strategy_id == "momentum_crossover":
            return [
                Integer(5, 30, name='fast_ema'),
                Integer(35, 100, name='slow_ema'),
                Real(1.0, 3.0, name='risk_reward_ratio'),
                Integer(50, 70, name='rsi_buy_threshold')
            ]
        # You would define spaces for other optimizable strategies here
        raise ValueError(f"No parameter space defined for strategy '{strategy_id}'")

    async def launch_forge_job(self, db: AsyncSession, *, user_id: int, config: dict) -> ForgeJob:
        """
        Creates the job in the DB and starts the asynchronous optimization task.
        """
        # 1. Create the ForgeJob in the database
        new_job = await crud_forge_job.create(db, obj_in={
            "user_id": user_id,
            "status": ForgeJobStatus.PENDING,
            **config
        })

        # 2. Launch the main optimization task in the background (non-blocking)
        asyncio.create_task(self.run_optimization(job_id=new_job.id, config=config))

        return new_job

    async def run_optimization(self, job_id, config: dict):
        """
        The main asynchronous task that manages the Bayesian Optimization process.
        """
        from app.db.session import AsyncSessionLocal  # For async task

        strategy_id = config['strategy_id']
        space = self._get_parameter_space(strategy_id)

        # --- Update Job Status to RUNNING ---
        async with AsyncSessionLocal() as db:
            await crud_forge_job.update(db, db_obj_id=job_id, obj_in={"status": ForgeJobStatus.RUNNING})

        try:
            # --- Fetch and Prepare Data Once ---
            klines = await unified_market_service.get_historical_klines(
                exchange_name="Binance",  # Should be from config
                symbol=config['symbol'],
                timeframe=config['timeframe'],
                start_dt=config['start_date'],
                end_dt=config['end_date']
            )
            data_df = pd.DataFrame([k.model_dump() for k in klines])
            data_df['volume'] = data_df['tick_volume']
            data_df['time'] = pd.to_datetime(data_df['time'], unit='s')
            # Serialize DataFrame to pass to Celery workers
            historical_data_json = data_df.to_json(orient='split')

            # --- Define the Objective Function for the Optimizer ---
            # This function will be called by gp_minimize. It takes a set of
            # parameters and must return a score to be minimized.
            @use_named_args(space)
            def objective(**params):
                # --- THIS IS THE KEY CHANGE ---
                # We get the task by its registered name from the Celery app instance.
                # This removes the need to import the task directly.
                task = celery_app.signature(
                    "run_single_backtest_permutation",
                    args=[
                        strategy_id,
                        historical_data_json,
                        params
                    ]
                )
                result = task.delay().get(timeout=300)

                if "error" in result or not result: return 100.0
                sharpe = result.get(config['optimization_metric'], 0.0)
                return -sharpe if sharpe is not None else 100.0

            n_calls = 50
            result = gp_minimize(objective, space, n_calls=n_calls, random_state=0)

            best_params = {dim.name: val for dim, val in zip(space, result.x)}

            final_task_sig = celery_app.signature(
                "run_single_backtest_permutation",
                args=[
                    strategy_id,
                    historical_data_json,
                    best_params
                ]
            )
            best_performance_stats = final_task_sig.delay().get(timeout=300)

            async with AsyncSessionLocal() as db:
                update_data = {
                    "status": ForgeJobStatus.COMPLETED,
                    "completed_at": datetime.now(timezone.utc),
                    "best_parameters": best_params,
                    "best_performance": best_performance_stats
                }
                await crud_forge_job.update(db, db_obj_id=job_id, obj_in=update_data)

        except Exception as e:
            async with AsyncSessionLocal() as db:
                await crud_forge_job.update(db, db_obj_id=job_id, obj_in={"status": ForgeJobStatus.FAILED})
            print(f"Forge Job {job_id} failed: {e}")


forge_service = ForgeService()