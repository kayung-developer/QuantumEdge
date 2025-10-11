"""
AuraQuant - Pydantic Schemas for the User Model (Corrected Version)
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

# --- Base Schema ---
# Contains fields that are common to most User-related operations.
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    timezone: Optional[str] = "UTC"
    language: Optional[str] = "en"
    theme: Optional[str] = "system"

# --- Create Schema ---
# Used when creating a new user. Requires an email and password.
# THIS IS THE CLASS THE ERROR MESSAGE IS LOOKING FOR.
class UserCreate(UserBase):
    email: EmailStr
    password: str

# --- Update Schema ---
# Used when updating an existing user. All fields are optional.
class UserUpdate(UserBase):
    password: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    theme: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_two_factor_enabled: Optional[bool] = None

# --- Database Schemas ---
# These schemas represent the data as it is stored in the database.

class UserInDBBase(UserBase):
    """
    Base schema for user data as stored in the database.
    Includes fields that are managed by the database (id, created_at, etc.).
    """
    id: int
    created_at: datetime
    
    # The `from_attributes=True` setting (formerly `orm_mode`) allows Pydantic
    # to read the data from object attributes (like user.id) instead of a dict,
    # which is necessary for creating schemas from SQLAlchemy models.
    model_config = ConfigDict(from_attributes=True)

class User(UserInDBBase):
    """
    Properties to return to the client. This is the public-facing user model.
    It inherits all fields from UserInDBBase.
    Crucially, it does NOT include the hashed_password.
    """
    pass

class UserInDB(UserInDBBase):
    """
    Properties stored in the database.
    This schema includes the hashed_password and is only used internally
    within the application logic (e.g., for authentication).
    It should never be returned from an API endpoint.
    """
    hashed_password: str