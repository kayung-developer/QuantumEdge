"""
AuraQuant - Sandbox Backtest Execution Script
This script runs inside a secure, isolated Docker container.
"""
import sys
import json
import pandas as pd
import base64
import importlib.util


def run_backtest_from_code(user_code: str, data_df_json: str, params_json: str, symbol: str):
    """
    Dynamically loads a strategy from a string of code and runs a backtest.
    """
    try:
        # --- 1. Load the strategy class from the user's code string ---
        spec = importlib.util.spec_from_loader("user_strategy_module", loader=None)
        user_module = importlib.util.module_from_spec(spec)
        exec(user_code, user_module.__dict__)

        # Assume the user's code defines a class named "CustomStrategy"
        # that inherits from our base class.
        StrategyClass = user_module.CustomStrategy

        # --- 2. Prepare data and parameters ---
        from app.services.backtesting_service import BacktestingService

        data_df = pd.read_json(data_df_json, orient='split')
        params = json.loads(params_json)

        # --- 3. Run the backtest ---
        backtester = BacktestingService(
            strategy_class=StrategyClass,
            data=data_df,
            params=params,
            symbol=symbol
        )
        results = backtester.run()

        # --- 4. Output results as JSON to stdout ---
        # Convert datetime objects in trades to strings for JSON serialization
        for trade in results.get('trades', []):
            trade['entry_time'] = trade['entry_time'].isoformat() if trade.get('entry_time') else None
            trade['exit_time'] = trade['exit_time'].isoformat() if trade.get('exit_time') else None

        # Convert equity curve timestamps
        equity_curve_serializable = {
            str(k.to_pydatetime().isoformat()): v
            for k, v in results.get('equity_curve', {}).items()
        }
        results['equity_curve'] = equity_curve_serializable

        print(json.dumps({"success": True, "results": results}))

    except Exception as e:
        import traceback
        error_info = traceback.format_exc()
        print(json.dumps({"success": False, "error": str(e), "traceback": error_info}))


if __name__ == "__main__":
    """
    Reads inputs from command-line arguments, base64-decoded.
    This is a simple way to pass potentially complex strings into the container.
    """
    user_code_b64 = sys.argv[1]
    data_df_json_b64 = sys.argv[2]
    params_json_b64 = sys.argv[3]
    symbol_b64 = sys.argv[4]

    user_code = base64.b64decode(user_code_b64).decode('utf-8')
    data_df_json = base64.b64decode(data_df_json_b64).decode('utf-8')
    params_json = base64.b64decode(params_json_b64).decode('utf-8')
    symbol = base64.b64decode(symbol_b64).decode('utf-8')

    run_backtest_from_code(user_code, data_df_json, params_json, symbol)