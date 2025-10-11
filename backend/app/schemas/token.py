"""
AuraQuant - Pydantic Schemas for JWT Tokens

This module defines the schemas related to JSON Web Tokens (JWTs) used for
user authentication.

Schema Breakdown:
-   `Token`: This is the response model for the login endpoint. It defines the
    structure of the JSON object that is returned to a user upon successful
    authentication. It includes the access token itself and the token type,
    which is typically "bearer".

-   `TokenPayload`: This schema defines the structure of the data (the "payload")
    that is encoded within the JWT. It contains the standard `sub` (subject)
    claim, which we use to store the user's ID. This schema is used internally
    when decoding a token to validate its contents and identify the user.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the access token response.
    """
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """
    Schema for the JWT payload data.
    """
    sub: Optional[int] = None