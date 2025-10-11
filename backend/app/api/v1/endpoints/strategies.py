"""
AuraQuant - API Endpoints for Strategy Management and Backtesting
"""
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body

from app.api import deps
from app.models.user import User
from app.schemas.backtest import BacktestRequest, BacktestResponse, StrategyInfo, BacktestPerformanceResults
from app.trading_strategies import STRATEGY_REGISTRY
from app.services.market_service import unified_market_service
from app.services.backtesting_service import BacktestingService

router = APIRouter()


@router.get("/", response_model=List[StrategyInfo])
async def get_available_strategies(current_user: User = Depends(deps.get_current_active_user)):
    """
    Get a list of all available trading strategies from the registry.
    """
    strategies_list = []
    for id, details in STRATEGY_REGISTRY.items():
        strategies_list.append(StrategyInfo(
            id=id,
            name=details["name"],
            description=details["description"],
            default_params=details["default_params"]
        ))
    return strategies_list


@router.post("/run-backtest", response_model=BacktestResponse)
async def run_backtest(
        request: BacktestRequest,
        current_user: User = Depends(deps.get_current_active_user)
):
    """
    Run a new backtest for a given strategy and parameters.
    """
    # 1. Validate Strategy ID
    strategy_details = STRATEGY_REGISTRY.get(request.strategy_id)
    if not strategy_details:
        raise HTTPException(status_code=404, detail="Strategy not found.")

    strategy_class = strategy_details["class"]

    # 2. Fetch Historical Data
    try:
        start_dt = datetime.fromisoformat(request.start_date)
        end_dt = datetime.fromisoformat(request.end_date)

        klines = await unified_market_service.get_historical_klines(
            exchange_name=request.exchange,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start_dt=start_dt,
            end_dt=end_dt
        )
        if not klines:
            raise HTTPException(status_code=400, detail="No historical data found for the given symbol and date range.")

        # Convert to Pandas DataFrame for the backtester
        data_df = pd.DataFrame([k.model_dump() for k in klines])
        data_df['volume'] = data_df['tick_volume']
        data_df['time'] = pd.to_datetime(data_df['time'], unit='s')

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {e}")

    # 3. Run the Backtest
    try:
        backtester = BacktestingService(
            strategy_class=strategy_class,
            data=data_df,
            params=request.parameters,
            initial_capital=100000.0,  # Can be made a request parameter
            commission_pct=0.00075  # Binance spot commission
        )
        results = backtester.run()

        # Convert NaN/Infinity to None for valid JSON response
        performance_dict = results["performance"]
        for key, value in performance_dict.items():
            if pd.isna(value) or np.isinf(value):
                performance_dict[key] = None

        # Format the response using our Pydantic schemas
        return BacktestResponse(
            strategy_name=strategy_details["name"],
            symbol=request.symbol,
            timeframe=request.timeframe,
            performance=BacktestPerformanceResults(**performance_dict),
            equity_curve={str(k): v for k, v in results["equity_curve"].items()},
            trades=results["trades"],
            parameters=results["parameters"]
        )
    except Exception as e:
        # Log the full traceback for debugging
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"An error occurred during backtest execution: {e}")