"""
AuraQuant - API Endpoints for User Management

This module defines the API routes for all user-related operations, including
creating, reading, updating, and deleting users. It leverages the CRUD functions
for database interaction and the dependency injection system for authentication
and authorization.

API Structure:
-   A FastAPI `APIRouter` is used to group all user-related endpoints under the
    `/users` path prefix.
-   Endpoints are protected using dependencies from `app.api.deps`.
    -   Admin-level actions (listing all users, updating others) require
        `get_current_active_superuser`.
    -   User-specific actions (reading/updating one's own profile) require
        `get_current_active_user`.
-   Pydantic schemas are used for `response_model` to control what data is sent
    back to the client, preventing sensitive information like hashed passwords
    from being exposed.
-   Standard HTTP status codes are used to communicate the outcome of operations
    (e.g., 200 OK, 201 Created, 400 Bad Request, 404 Not Found).
-   Detailed docstrings and metadata (tags, summary) are provided for each
    endpoint, which FastAPI uses to generate interactive API documentation.
"""
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.api import deps
from app.models.user import User
from app.schemas import user as user_schema

router = APIRouter()


@router.get("/", response_model=List[user_schema.User])
async def read_users(
        db: AsyncSession = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all users.
    This is a protected endpoint, accessible only by superusers.
    """
    users = await crud.crud_user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def create_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_in: user_schema.UserCreate,
        # current_user: User = Depends(deps.get_current_active_superuser), # Optional: Uncomment to restrict user creation to superusers
) -> Any:
    """
    Create a new user.
    Can be configured to be open for public registration or restricted to superusers.
    """
    user = await crud.crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.crud_user.create(db, obj_in=user_in)
    return user


@router.get("/me", response_model=user_schema.User)
async def read_user_me(
        current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current logged-in user's details.
    """
    return current_user


@router.put("/me", response_model=user_schema.User)
async def update_user_me(
        *,
        db: AsyncSession = Depends(deps.get_db),
        password: str = Body(None),
        full_name: str = Body(None),
        email: str = Body(None),
        current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update current logged-in user's details.
    """
    current_user_data = user_schema.UserUpdate(
        full_name=current_user.full_name,
        email=current_user.email,
    ).model_dump()

    user_in = user_schema.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email

    user = await crud.crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=user_schema.User)
async def read_user_by_id(
        user_id: int,
        current_user: User = Depends(deps.get_current_active_superuser),
        db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by ID.
    Accessible only by superusers.
    """
    user = await crud.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=user_schema.User)
async def update_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_id: int,
        user_in: user_schema.UserUpdate,
        current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """

    Update a user's details by ID.
    Accessible only by superusers.
    """
    user = await crud.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await crud.crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=user_schema.User)
async def delete_user(
        *,
        db: AsyncSession = Depends(deps.get_db),
        user_id: int,
        current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a user by ID.
    Accessible only by superusers.
    """
    user = await crud.crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Superusers cannot delete themselves")

    deleted_user = await crud.crud_user.remove(db, id=user_id)
    return deleted_user