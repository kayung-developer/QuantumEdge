"""
AuraQuant - Celery Worker for Distributed Backtesting
"""
import os
import pandas as pd
from datetime import datetime
from celery import Celery

# Import our existing services and components
from app.services.backtesting_service import BacktestingService
from app.trading_strategies import STRATEGY_REGISTRY

from datetime import timedelta
from skopt import gp_minimize
from skopt.space import Real, Integer
from skopt.utils import use_named_args

# Import the new schema for type hinting
from app.schemas.walkforward import WalkForwardJobCreate, WalkForwardChunkResult
# Import services (assuming they can be resolved)
from app.services.market_service import unified_market_service

# Note: For this to work, you might need to adjust Python paths or use a proper project structure
# that Celery can import from. Usually involves setting PYTHONPATH.
# For now, we assume the paths are resolvable.

# Configure Celery
# The broker is Redis, which we already set up for the orchestrator.
# The backend also uses Redis to store task results.
celery_app = Celery(
    "AuraQuantWorker",
    broker="redis://localhost:6379/1",
    backend="redis://localhost:6379/2",
    # Include the path to the app module so Celery can find tasks and imports
    include=['app.celery_worker']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(name="run_single_backtest_permutation")
def run_single_backtest_permutation(
        strategy_id: str,
        historical_data_json: str,
        parameters: dict
) -> dict:
    """
    A Celery task that runs one single backtest with a specific set of parameters.
    """
    strategy_details = STRATEGY_REGISTRY.get(strategy_id)
    if not strategy_details:
        return {"error": f"Strategy '{strategy_id}' not found."}

    data_df = pd.read_json(historical_data_json, orient='split')

    # The symbol is needed by the backtester for regime analysis
    # We can infer it from the config or pass it in. For now, assume a default.
    symbol = "BTCUSDT"  # This should ideally be passed in as an argument.

    backtester = BacktestingService(
        strategy_class=strategy_details["class"],
        data=data_df,
        params=parameters,
        symbol=symbol,
        initial_capital=100000.0,
        commission_pct=0.00075
    )

    try:
        results = backtester.run()
        return results["performance"]
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}


@celery_app.task(name="run_walk_forward_optimization", bind=True)
def run_walk_forward_optimization(self, config_dict: dict) -> dict:
    """
    A long-running Celery task to perform a full Walk-Forward Optimization.
    """
    config = WalkForwardJobCreate(**config_dict)

    total_start_date = datetime.fromisoformat(config.start_date)
    total_end_date = datetime.fromisoformat(config.end_date)

    # Initialize the ForgeService to access its helper methods
    forge = ForgeService()
    parameter_space = forge._get_parameter_space(config.strategy_id)

    # --- Data Fetching: Get all data for the entire period once ---
    try:
        # We need to run the async function in a sync context (Celery worker)
        import asyncio
        klines = asyncio.run(unified_market_service.get_historical_klines(
            exchange_name=config.exchange, symbol=config.symbol, timeframe=config.timeframe,
            start_dt=total_start_date, end_dt=total_end_date
        ))
        if not klines:
            raise ValueError("No data for the entire period.")

        full_df = pd.DataFrame([k.model_dump() for k in klines])
        full_df['time'] = pd.to_datetime(full_df['time'], unit='s')
        full_df.set_index('time', inplace=True)
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': f"Data fetching failed: {e}"})
        return {"error": f"Data fetching failed: {e}"}

    all_chunk_results = []
    current_date = total_start_date

    # --- Main Walk-Forward Loop ---
    while current_date + timedelta(days=config.training_period_days + config.testing_period_days) <= total_end_date:

        # Define the time windows for this chunk
        in_sample_start = current_date
        in_sample_end = in_sample_start + timedelta(days=config.training_period_days)
        out_of_sample_start = in_sample_end
        out_of_sample_end = out_of_sample_start + timedelta(days=config.testing_period_days)

        # Slice the main DataFrame for this chunk's data
        in_sample_data = full_df.loc[in_sample_start:in_sample_end]
        out_of_sample_data = full_df.loc[out_of_sample_start:out_of_sample_end]

        if in_sample_data.empty or out_of_sample_data.empty:
            current_date += timedelta(days=config.testing_period_days)
            continue

        # --- 1. In-Sample Optimization (using the ForgeService logic) ---
        @use_named_args(parameter_space)
        def objective(**params):
            # This runs a backtest on the IN-SAMPLE data
            # This part is synchronous for simplicity within the Celery task
            bt_service = BacktestingService(
                strategy_class=STRATEGY_REGISTRY[config.strategy_id]['class'],
                data=in_sample_data.reset_index(),
                params=params,
                symbol=config.symbol
            )
            perf = bt_service.run()['performance']
            score = perf.get(config.optimization_metric, 0.0)
            return -score if score is not None else 100.0

        # Run the optimizer
        opt_result = gp_minimize(objective, parameter_space, n_calls=25, random_state=0)  # Fewer calls for each chunk
        optimal_params = {dim.name: val for dim, val in zip(parameter_space, opt_result.x)}

        # --- 2. Out-of-Sample Validation ---
        # Run a final backtest on the UNSEEN out-of-sample data with the optimal parameters
        oos_backtester = BacktestingService(
            strategy_class=STRATEGY_REGISTRY[config.strategy_id]['class'],
            data=out_of_sample_data.reset_index(),
            params=optimal_params,
            symbol=config.symbol
        )
        oos_performance = oos_backtester.run()['performance']

        # Store the results for this chunk
        chunk_result = WalkForwardChunkResult(
            in_sample_start=in_sample_start, in_sample_end=in_sample_end,
            out_of_sample_start=out_of_sample_start, out_of_sample_end=out_of_sample_end,
            optimal_parameters=optimal_params,
            in_sample_performance=opt_result.fun * -1,  # The best score found
            out_of_sample_performance=oos_performance
        )
        all_chunk_results.append(chunk_result.model_dump())

        # Update task state for frontend progress tracking
        self.update_state(state='PROGRESS', meta={'chunks_completed': len(all_chunk_results)})

        # Move the window forward
        current_date += timedelta(days=config.testing_period_days)

    # --- 3. Aggregate Final Results ---
    # Combine the trades from all out-of-sample periods to get a final equity curve and performance
    # (This is a complex step, for now we return the chunked results)

    return {
        "status": "SUCCESS",
        "results": all_chunk_results,
    }