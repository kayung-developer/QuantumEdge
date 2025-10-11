"""
AuraQuant - API v1 Router Aggregator (with On-Chain Endpoints)
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    users, login, plans, payments,
    market_data, trade, ai, dashboard,
    strategies, adaptive, forge, signals,
    accounts, reports, portfolio, onchain, collaboration # Import the new onchain router
)

api_router = APIRouter()

# --- Register all endpoint routers ---
api_router.include_router(login.router, tags=["Login & Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["User Management"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["Account Management"])
api_router.include_router(plans.router, prefix="/plans", tags=["Subscription Plans"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments & Webhooks"])
api_router.include_router(market_data.router, prefix="/market", tags=["Market Data"])
api_router.include_router(trade.router, prefix="/trade", tags=["Trade Execution & Orchestration"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Services"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reporting & Exports"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio Intelligence"])

# Category: Advanced AI & Quantitative Tools
api_router.include_router(ai.router, prefix="/ai", tags=["AI & ML Services (CV)"])
api_router.include_router(signals.router, prefix="/signals", tags=["AI Trading Signals"])
api_router.include_router(strategies.router, prefix="/strategies", tags=["Strategy & Backtesting"])
api_router.include_router(forge.router, prefix="/forge", tags=["Strategy Forge (AutoML)"])
api_router.include_router(adaptive.router, prefix="/adaptive", tags=["Adaptive Deployment"])
api_router.include_router(onchain.router, prefix="/onchain", tags=["On-Chain Intelligence"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration & Social Trading"])