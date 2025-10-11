"""
AuraQuant - LLM Tool Definitions
"""
from langchain.tools import tool
from datetime import datetime, timedelta
import pandas as pd

from app.services.market_service import unified_market_service
from app.services.backtesting_service import BacktestingService
from app.trading_strategies import STRATEGY_REGISTRY
from app.schemas.backtest import BacktestPerformanceResults


# --- Tool 1: Get Historical Market Data ---
@tool
def get_historical_market_data(symbol: str, timeframe: str, days_ago: int) -> str:
    """
    Fetches historical OHLCV market data for a specific symbol, timeframe,
    and a number of days into the past from today. Returns the data as a JSON string.
    """
    try:
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=days_ago)
        # Assume a default exchange for simplicity in the tool
        exchange = "Binance"

        # This needs to be async, but LangChain's Tool class is sync.
        # We run the async function in a new event loop.
        import asyncio
        klines = asyncio.run(unified_market_service.get_historical_klines(
            exchange_name=exchange,
            symbol=symbol,
            timeframe=timeframe,
            start_dt=start_dt,
            end_dt=end_dt
        ))
        if not klines:
            return f"No data found for {symbol} on {exchange}."

        df = pd.DataFrame([k.model_dump() for k in klines])
        return df.to_json(orient='records')
    except Exception as e:
        return f"Error fetching data: {e}"


# --- Tool 2: Run a Backtest ---
@tool
def run_strategy_backtest(strategy_id: str, symbol: str, timeframe: str, start_date: str, end_date: str) -> str:
    """
    Runs a backtest for a given strategy, symbol, timeframe, and date range.
    Returns a JSON string of the performance summary.
    """
    try:
        strategy_details = STRATEGY_REGISTRY.get(strategy_id)
        if not strategy_details:
            return f"Strategy '{strategy_id}' not found. Available strategies are: {list(STRATEGY_REGISTRY.keys())}"

        # Fetch data for the backtest
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        exchange = "Binance"

        import asyncio
        klines = asyncio.run(unified_market_service.get_historical_klines(
            exchange_name=exchange, symbol=symbol, timeframe=timeframe,
            start_dt=start_dt, end_dt=end_dt
        ))
        if not klines:
            return f"No data found for {symbol} to run backtest."

        data_df = pd.DataFrame([k.model_dump() for k in klines])
        data_df['volume'] = data_df['tick_volume']
        data_df['time'] = pd.to_datetime(data_df['time'], unit='s')

        backtester = BacktestingService(
            strategy_class=strategy_details["class"],
            data=data_df,
            params=strategy_details["default_params"],
            symbol=symbol
        )
        results = backtester.run()

        # Return a clean summary
        performance = BacktestPerformanceResults(**results['performance'])
        return performance.model_dump_json()
    except Exception as e:
        return f"Error running backtest: {e}"


# A list of all tools the agent can use
llm_tools = [get_historical_market_data, run_strategy_backtest]

