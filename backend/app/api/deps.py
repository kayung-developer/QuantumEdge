"""
AuraQuant - API Dependencies

This module provides reusable dependencies for the FastAPI application, primarily
focused on authentication and authorization. Dependencies in FastAPI allow us to
run common logic before our endpoint functions, handling tasks like:
-   Authenticating a user.
-   Checking for specific permissions (e.g., is the user a superuser?).
-   Establishing and providing a database session.

These dependencies streamline the endpoint logic, making it cleaner, more readable,
and less prone to errors by centralizing common concerns.

Key Dependencies:
-   `get_db`: (Imported from `app.db.session`) Provides a database session to the
    endpoint and ensures it's closed afterward.

-   `get_current_user`: The core authentication dependency. It extracts the JWT
    token from the request's Authorization header, decodes it, and retrieves the
    corresponding user from the database. It raises an HTTP exception if the
    token is invalid, expired, or the user does not exist.

-   `get_current_active_user`: Builds upon `get_current_user` by adding a check
    to ensure the user's `is_active` flag is true. This is the most common
    dependency used for protecting endpoints that require a logged-in user.

-   `get_current_active_superuser`: Builds upon `get_current_active_user` by
    adding a check to ensure the user also has the `is_superuser` flag. This is
    used to protect administrative endpoints.
"""
from typing import Generator, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import settings
from app.crud import crud_user
from app.models.user import User
from app.schemas.token import TokenPayload
from app.db.session import get_db

# Reusable OAuth2 scheme, pointing to the login endpoint.
# This tells FastAPI how to extract the token.
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_current_user(
        db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Dependency to get the current user from a JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Pydantic model validation ensures the payload structure is correct.
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = await crud_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
        current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user.
    Raises an exception if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
        current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependency to get the current active superuser.
    Raises an exception if the user is not a superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail = "The user doesn't have enough privileges")
        return current_user