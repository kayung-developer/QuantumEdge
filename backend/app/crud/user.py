"""
AuraQuant - CRUD Operations for the User Model

This module provides a dedicated class, `CRUDUser`, for handling all database
operations related to the `User` model. It inherits from the generic `CRUDBase`
class and extends it with user-specific functionality.

Key Features:
-   **Password Hashing**: Overrides the `create` and `update` methods to ensure that
    any plain-text password provided is securely hashed using the functions from
    `app.core.security` before being saved to the database. This is a critical
    security measure.

-   **Email-based Lookup**: Implements a `get_by_email` method to efficiently
    retrieve a user by their email address. This is essential for login,
    registration checks, and other user management tasks.

-   **Authentication Check**: Provides an `authenticate` method that encapsulates
    the logic for verifying a user's email and password, returning the user
    object only if the credentials are valid.

-   **Type-Specific**: It is specifically typed to work with the `User` model and
    the `UserCreate` and `UserUpdate` Pydantic schemas, providing static analysis
    benefits and reducing runtime errors.
"""

from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        """
        Retrieve a single user by their email address.
        """
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        """
        Create a new user, hashing the password before saving.
        """
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
            self,
            db: AsyncSession,
            *,
            db_obj: User,
            obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Update a user's details. If a password is provided, it will be hashed.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def authenticate(
            self, db: AsyncSession, *, email: str, password: str
    ) -> Optional[User]:
        """
        Authenticate a user by email and password.
        """
        user = await self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


# Create a single instance of the CRUDUser class to be used throughout the application.
crud_user = CRUDUser(User)