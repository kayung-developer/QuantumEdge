import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
from alembic import context

# --- CUSTOM ADDITIONS FOR AURAQUANT ---
# 1. Import your Base model from your application
from app.db.base import Base
# 2. Import all your models so that Base knows about them
from app.models.user import User
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.order import OrchestratedOrder
from app.models.risk import UserRiskProfile
from app.models.audit import AuditLog
from app.models.adaptive import AdaptivePortfolio
from app.models.autotrade import ForgeJob
from app.models.collaboration import TradeRoom, TradeRoomMember, ChatMessage, CopyTradeSubscription
from app.models.marketplace import MarketplaceStrategy, MarketplaceSubscription
from app.models.sentiment import SentimentData
from app.models.signal import AISignal
from app.models.account import TradingAccount

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# --- NEW: Set the database URL from environment variable ---
# This allows `alembic` to connect to the database defined in your .env file
# when you run migration commands.
config.set_main_option('sqlalchemy.url', os.getenv('SQLALCHEMY_DATABASE_URI'))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CUSTOM ADDITIONS FOR AURAQUANT ---
# 3. Set the target metadata for autogenerate
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()