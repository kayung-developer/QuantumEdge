"""
AuraQuant - API Endpoint for User Authentication (Login)

This module provides the /login endpoint for the AuraQuant API. It handles
user authentication by verifying credentials and issuing JWT access tokens.

Key Functionality:
-   `/login/access-token`: This is the main endpoint for user login.
    -   It uses `OAuth2PasswordRequestForm` as a dependency, which means it
        expects the client to send the credentials in a standard form-data
        format (`username` and `password`).
    -   It uses the `crud_user.authenticate` method to securely check the
        provided email and password against the stored hashed password in the

        database.
    -   Upon successful authentication, it generates a new JWT access token
        using `security.create_access_token`.
    -   It also updates the `last_login_at` timestamp for the user, which is
        an important security and auditing feature.
    -   If authentication fails (e.g., wrong password, user not found), it
        returns a 400 Bad Request error with a clear message.

-   `/login/test-token`: A simple utility endpoint that requires a valid token.
    It's used for clients to easily verify if their current token is active
    and valid without performing any other action.
"""
from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token
from app.schemas import user as user_schema

router = APIRouter()


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
        db: AsyncSession = Depends(deps.get_db),
        form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud.crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Update last login time
    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=user_schema.User)
def test_token(current_user: User = Depends(deps.get_current_user)):
    """
    Test access token.
    """
    return current_user