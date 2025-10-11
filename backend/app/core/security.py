"""
AuraQuant - Core Security Services

This module provides essential security functionalities for the application, including:
1.  Password Hashing: Using bcrypt, a strong and widely-trusted hashing algorithm,
    to securely store user passwords. We never store plain-text passwords.
2.  JWT Token Generation: Creating JSON Web Tokens (JWT) for user authentication
    after a successful login. These tokens are stateless and digitally signed.
3.  OAuth2 Password Bearer Scheme: A FastAPI dependency that extracts the JWT
    token from the "Authorization" header of incoming requests.

Security Best Practices Implemented:
-   Salting and hashing passwords with a computationally expensive algorithm (bcrypt).
-   Using a strong, environment-variable-managed secret key for signing JWTs.
-   Setting a reasonable expiration time for access tokens to limit their lifespan.
-   Standardizing the token retrieval mechanism using OAuth2PasswordBearer.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from cryptography.fernet import Fernet
from app.core.config import settings
import json

from app.core.config import settings

# 1. Password Hashing Setup
# -------------------------
# We use passlib's CryptContext to handle password hashing.
# By specifying bcrypt as the scheme, we ensure that passwords are
# securely salted and hashed. The 'auto' method will automatically
# handle hashing new passwords and verifying existing ones against the scheme.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This is the dependency that FastAPI will use to find the token in the request.
# It looks for an 'Authorization' header with a 'Bearer' token.
# The tokenUrl points to the endpoint where the client can obtain a token (the login endpoint).
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
# --- Fernet Symmetric Encryption for Credentials ---
# The ENCRYPTION_KEY should be a 32-byte URL-safe base64-encoded key.
# Generate with: Fernet.generate_key().decode() and store in your .env file
# Ensure ENCRYPTION_KEY is added to the Settings class in config.py
if not settings.ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is not set in the environment. Cannot encrypt/decrypt credentials.")
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

# 2. Password Verification and Hashing Functions
# ---------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain-text password against a hashed password.

    Args:
        plain_password: The password to check.
        hashed_password: The stored hashed password.

    Returns:
        True if the password is correct, otherwise False.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes a plain-text password.

    Args:
        password: The password to hash.

    Returns:
        The resulting hashed password as a string.
    """
    return pwd_context.hash(password)


# 3. JSON Web Token (JWT) Generation Function
# -------------------------------------------

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    """
    Creates a new JWT access token.

    The token contains a subject ('sub') claim, identifying who the token
    refers to (e.g., user ID or email), and an expiration ('exp') claim.

    Args:
        subject: The subject of the token (e.g., user's email or ID).
        expires_delta: The lifespan of the token. If None, it defaults to the
                       value from the application settings.

    Returns:
        The encoded JWT as a string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # The claims to include in the JWT payload.
    # 'exp': Expiration time (standard claim)
    # 'sub': Subject/principal (standard claim)
    to_encode = {"exp": expire, "sub": str(subject)}

    # Encode the payload with the secret key and algorithm from settings.
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    """
    Verifies a JWT token and returns its subject if valid.

    Args:
        token: The JWT token to verify.

    Returns:
        The subject of the token if verification is successful, otherwise None.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except JWTError:
        # This will catch any error during decoding, such as:
        # - ExpiredSignatureError
        # - InvalidTokenError
        return None