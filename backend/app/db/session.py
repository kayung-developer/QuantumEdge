"""
AuraQuant - Database Session Management

This module is responsible for configuring the database engine and managing sessions.
It uses SQLAlchemy's async capabilities to interact with the database in a
non-blocking way, which is essential for a high-performance application like a
trading platform.

Key Components:
1.  `engine`: An instance of `create_async_engine`. This is the core connectivity
    interface to the database. It is configured once when the application starts.
    It uses the database URI specified in the application settings.

2.  `AsyncSessionLocal`: An `async_sessionmaker` factory. This factory is used to
    create new `AsyncSession` objects. Each session represents a single "conversation"
    with the database and is used to execute queries and manage transactions.

3.  `get_db()`: An asynchronous generator function designed to be used as a
    FastAPI dependency. For each API request that needs database access, this
    dependency will:
    -   Create a new `AsyncSession`.
    -   Yield the session to the endpoint function.
    -   Ensure the session is closed after the request is complete, even if an
        error occurs. This is a critical pattern for robust resource management.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import QueuePool

from app.core.config import settings

# Create the asynchronous engine for database connections.
# The engine is the starting point for any SQLAlchemy application. It's the
# 'home base' for the actual database and its DBAPI, delivered to the SQLAlchemy
# application through a connection pool.
#
# - `pool_pre_ping=True`: This setting enables a "pre-ping" feature that tests
#   the liveliness of a connection before it's checked out from the pool. This helps
#   to handle connections that may have been dropped by the database server.
# - `poolclass=QueuePool`: A standard connection pool implementation.
# - `echo=settings.DEBUG`: If in debug mode, SQLAlchemy will log all generated SQL
#   statements, which is very useful for debugging.
engine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_pre_ping=True,
    echo=settings.DEBUG,
    pool_size=10,        # Default is 5, increased for higher concurrency
    max_overflow=20      # Allows for temporary spikes in connection demand
)

# Create a configured "AsyncSession" class.
# This factory will create new AsyncSession objects when called.
# - `autocommit=False`: Ensures that we have to explicitly call `session.commit()`.
#   This is the standard and safest way to handle transactions.
# - `autoflush=False`: Prevents the session from automatically issuing SQL to the
#   database before a commit. This gives us more control over the transaction.
# - `bind=engine`: Associates this session factory with our database engine.
AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False # Prevents objects from being detached after commit,
                           # which can be useful in async contexts.
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.

    This is an async generator that yields a database session and ensures it's
    closed correctly after the request is handled.

    Yields:
        AsyncSession: The database session for the current request.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            # This block ensures that the session is closed, returning the
            # connection to the pool, regardless of whether the request
            # processing was successful or resulted in an error.
            await session.close()