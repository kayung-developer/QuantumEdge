"""
AuraQuant - SQLAlchemy Declarative Base

This module provides the base class for all SQLAlchemy models in the application.
Every database table will be represented by a class that inherits from the `Base`
class defined here.

SQLAlchemy's declarative extension allows us to define our database mappings
in a more Pythonic way, as classes. The `DeclarativeBase` class maintains a
catalog of classes and tables relative to that base - this is known as the
declarative base class.

Key Features:
-   `@as_declarative()`: A decorator that marks our `Base` class as the declarative
    base for our models.
-   Type Annotation Map: We are providing `type_annotation_map` to handle specific
    PostgreSQL types like `TIMESTAMP(timezone=True)` which are essential for
    storing timezone-aware datetimes, a critical requirement for a global trading
    platform.
-   `__tablename__`: An attribute that can be automatically generated from the
    class name, providing a consistent naming convention for database tables (e.g.,
    the class `UserAccount` would map to the table `user_account`).
"""

import re
from typing import Any, cast

from sqlalchemy import TIMESTAMP, BigInteger
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime, timezone

# Custom type for timezone-aware timestamps
# This ensures that all datetime objects stored in the database include timezone information.
# Using timezone.utc is a best practice for storing timestamps to avoid ambiguity.
TIMESTAMPAware = TIMESTAMP(timezone=True)
BigInt = BigInteger()


class CustomBase(AsyncAttrs, DeclarativeBase):
    """
    Custom base class for all SQLAlchemy models.

    - Includes `AsyncAttrs` to support async loading of relationships and attributes.
    - Provides an automatic `__tablename__` generation.
    - Defines a default `id` primary key column for all models.
    """
    id: Mapped[int]
    __name__: str

    # Provides a default type map for common Python types to SQL types.
    type_annotation_map = {
        datetime: TIMESTAMPAware,
        int: BigInt,
    }

    # This method automatically generates a table name in snake_case
    # from the model's class name.
    # For example, a class named `User` will have a table named `user`.
    # A class named `TradeOrder` will have a table named `trade_order`.
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        return name


# The `Base` object to be imported and inherited by all models.
Base: DeclarativeBase = cast(Any, CustomBase)