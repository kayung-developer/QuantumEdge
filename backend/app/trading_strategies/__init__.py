"""
AuraQuant - Trading Strategies Package and Registry
"""
from .strategy_base import Strategy
from .momentum_crossover import MomentumCrossover
from .bb_mean_reversion import BBMeanReversion
from .rsi_divergence import RSIDivergence
from .ichimoku_breakout import IchimokuBreakout
from .smc_order_block import SMCOrderBlock

# The Strategy Registry
# This maps a unique string key to the strategy's class.
# The API will use this to find and instantiate the requested strategy.
STRATEGY_REGISTRY = {
    "momentum_crossover": {
        "class": MomentumCrossover,
        "name": "Momentum Crossover",
        "description": "A trend-following strategy using EMA crossovers and RSI for momentum confirmation.",
        "default_params": {
            "fast_ema": 20, "slow_ema": 50, "rsi_len": 14,
            "rsi_buy_threshold": 55, "rsi_sell_threshold": 45,
            "atr_len": 14, "atr_multiplier_sl": 2.0, "risk_reward_ratio": 1.5
        }
    },
    "bb_mean_reversion": {
        "class": BBMeanReversion,
        "name": "Bollinger Band Mean Reversion",
        "description": "A mean-reversion strategy that trades on price extremes identified by Bollinger Bands.",
        "default_params": {"bb_len": 20, "bb_std": 2.0}
    },
    "rsi_divergence": {
        "class": RSIDivergence,
        "name": "RSI Divergence",
        "description": "A counter-trend strategy that identifies and trades divergences between price and the RSI oscillator.",
        "default_params": {"rsi_len": 14, "lookback": 30, "risk_reward_ratio": 2.0}
    },
    "ichimoku_breakout": {
        "class": IchimokuBreakout,
        "name": "Ichimoku Cloud Breakout",
        "description": "A comprehensive trend-following strategy based on breakouts and trend confirmation from the Ichimoku Kinko Hyo indicator.",
        "default_params": {"tenkan": 9, "kijun": 26, "senkou": 52, "risk_reward_ratio": 1.5}
    },
    "smc_order_block": {
        "class": "Smart Money Concepts (SMC)",
        "name": "SMC Order Block",
        "description": "An advanced price action strategy that trades on 'return-to-block' after a 'break of structure'.",
        "default_params": {"swing_lookback": 10, "risk_reward_ratio": 3.0}
    }
}