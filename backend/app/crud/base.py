"""
AuraQuant - Generic CRUD Base Class

This module provides a reusable, generic base class for performing CRUD
(Create, Read, Update, Delete) operations on a SQLAlchemy model. This pattern
promotes code reuse and consistency across the application.

By using Python's `TypeVar` and `Generic`, we can create a type-safe class that
can be adapted to work with any specific model and its corresponding Pydantic
schemas for creation and updates.

Class `CRUDBase`:
-   `model`: The SQLAlchemy model class (e.g., `User`).
-   `get`: Retrieves a single object by its ID.
-   `get_multi`: Retrieves a list of objects with optional pagination (skip, limit).
-   `create`: Creates a new object in the database from a Pydantic schema.
-   `update`: Updates an existing database object with data from a Pydantic schema.
-   `remove`: Deletes an object from the database by its ID.

This generic implementation handles the core database interaction logic, allowing
specific CRUD classes (like `CRUDUser`) to inherit from it and only add or
override methods that are unique to that model (e.g., `get_by_email`).
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# Define Type Variables for generics
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        Get a single record by its primary key.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
            self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records with pagination.
        """
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record in the database.
        """
        # Convert Pydantic model to a dictionary
        obj_in_data = jsonable_encoder(obj_in)
        # Create a SQLAlchemy model instance
        db_obj = self.model(**obj_in_data)
        # Add the instance to the session and commit
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: ModelType,
            obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Update an existing record in the database.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # Use exclude_unset=True to only update fields that were actually provided
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        """
        Delete a record from the database by its ID.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj