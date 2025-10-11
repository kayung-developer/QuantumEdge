"""
AuraQuant - Adapters Package
"""
from .mt5_adapter import MT5Adapter
from .binance_adapter import BinanceAdapter
from .fix_adapter import FixAdapter # Add the new FIX adapter

AVAILABLE_ADAPTERS = [
    MT5Adapter,
    BinanceAdapter,
    # FixAdapter is instantiated differently, so we don't add it here for auto-discovery.
    # It would be managed separately by the ConnectionManager based on user-configured accounts.
]