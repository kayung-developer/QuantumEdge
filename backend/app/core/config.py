"""AuraQuant - Core Configuration Management

This module centralizes all application settings. It uses Pydantic's BaseSettings
to load configuration from environment variables and/or a .env file. This approach
ensures a single source of truth for configuration, promotes security by keeping
secrets out of the codebase, and provides type-safe settings.

To use this, create a .env file in the root of the backend directory.
Example .env file:"""

# --- PROJECT SETTINGS ---
PROJECT_NAME="AuraQuant"
PROJECT_VERSION="1.0.0"
DEBUG=True
API_V1_STR="/api/v1"

# --- SECURITY & JWT ---
# Generate with: openssl rand -hex 32
SECRET_KEY="a_very_long_and_secure_random_string_goes_here"
ACCESS_TOKEN_EXPIRE_MINUTES=60

# --- DATABASE ---
# For local development with SQLite:
SQLALCHEMY_DATABASE_URI="sqlite+aiosqlite:///./auraquant.db"
# For production with PostgreSQL:
# POSTGRES_SERVER="localhost"
# POSTGRES_PORT="5432"
# POSTGRES_USER="auraquant_user"
# POSTGRES_PASSWORD="strong_password_here"
# POSTGRES_DB="auraquant_db"
# The application will construct the full URI from the above variables.

# --- FIRST SUPERUSER ---
FIRST_SUPERUSER_EMAIL="admin@auraquant.com"
FIRST_SUPERUSER_PASSWORD="a_very_strong_initial_password"

# --- CORS ORIGINS ---
# Comma-separated list of allowed origins
BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000"

# --- THIRD-PARTY API KEYS & CREDENTIALS ---

# Exchange Connectivity (Example: Binance)
BINANCE_API_KEY="your_binance_api_key"
BINANCE_API_SECRET="your_binance_api_secret"
COINBASE_API_KEY="your_coinbase_api_key"
COINBASE_API_SECRET="your_coinbase_api_secret"

# Forex & Broker Connectivity (MetaTrader 5)
# These are the credentials for your MetaTrader 5 trading account.
MT5_LOGIN=12345678
MT5_PASSWORD="your_mt5_account_password"
MT5_SERVER="Your_Broker_Server_Name"

# TradingView Integration
# A secret key to validate incoming webhook alerts from TradingView.
TRADINGVIEW_WEBHOOK_SECRET="a_secure_random_string_to_validate_webhooks"

# FIX Protocol Configuration
# Path to the FIX configuration file
FIX_CONFIG_PATH="/app/config/fix_session.cfg"

# Payment Gateways
PAYSTACK_SECRET_KEY="your_paystack_secret_key"
PAYSTACK_PUBLIC_KEY="your_paystack_public_key"
PAYPAL_CLIENT_ID="your_paypal_client_id"
PAYPAL_CLIENT_SECRET="your_paypal_client_secret"
PAYPAL_MODE="sandbox" # "live" or "sandbox"

# Firebase Admin SDK
# Path to your Firebase service account key JSON file
FIREBASE_CREDENTIALS_PATH="/app/config/firebase-service-account.json"

# Alternative Data Sources
NEWS_API_KEY="your_newsapi_org_key"
X_API_KEY="your_x_twitter_api_key"
X_API_SECRET_KEY="your_x_twitter_api_secret"
X_ACCESS_TOKEN="your_x_twitter_access_token"
X_ACCESS_TOKEN_SECRET="your_x_twitter_access_token_secret"

# --- MONITORING & ALERTING ---
MLFLOW_TRACKING_URI="http://mlflow_server:5000"
ALERTING_SLACK_WEBHOOK_URL="https://hooks.slack.com/services"
ALERTING_TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
ALERTING_TELEGRAM_CHAT_ID="your_telegram_chat_id"


import os
from pathlib import Path
from typing import List, Optional, Union, Any

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Application settings class.
    Reads configuration from environment variables.
    """

    # --- MODEL CONFIGURATION ---
    # Specifies how Pydantic should behave.
    # We are telling it to be case-sensitive and to look for a .env file.
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        case_sensitive=True,
        extra='ignore'
    )

    # --- PROJECT METADATA ---
    PROJECT_NAME: str = "AuraQuant"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"

    # --- SECURITY & AUTHENTICATION (JWT) ---
    # This key is critical for signing JWT tokens. It must be kept secret.
    SECRET_KEY: str
    ENCRYPTION_KEY: str
    # Algorithm used for JWT signing. HS256 is a common choice.
    ALGORITHM: str = "HS256"
    # Defines how long the access token is valid in minutes.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- DATABASE CONFIGURATION ---
    # This section manages the database connection string.
    # It dynamically builds the URI for PostgreSQL if credentials are provided,
    # otherwise it defaults to a local SQLite database for ease of development.
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_PORT: Optional[int] = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None

    SQLALCHEMY_DATABASE_URI: Optional[Union[PostgresDsn, str]] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v

        values = info.data

        # Check if PostgreSQL environment variables are set
        if all(values.get(key) for key in ["POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]):
            return str(PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=values.get("POSTGRES_USER"),
                password=values.get("POSTGRES_PASSWORD"),
                host=values.get("POSTGRES_SERVER"),
                port=values.get("POSTGRES_PORT"),
                path=f"{values.get('POSTGRES_DB') or ''}",
            ))

        # Default to SQLite if PostgreSQL is not configured
        sqlite_path = os.path.join(BASE_DIR, "auraquant.db")
        return f"sqlite+aiosqlite:///{sqlite_path}"

    # --- FIRST SUPERUSER ---
    # These settings are used to create the initial admin user in the system.
    # This is typically done via a CLI command or an initial startup script.
    FIRST_SUPERUSER_EMAIL: str
    FIRST_SUPERUSER_PASSWORD: str

    # --- CORS (Cross-Origin Resource Sharing) ---
    # A list of origins that are allowed to make requests to this API.
    # Crucial for connecting the frontend application.
    BACKEND_CORS_ORIGINS: Union[str, List[AnyHttpUrl]]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> Union[List[str], str]:
        """
        This robust validator handles multiple input formats for CORS origins.
        """
        if isinstance(v, str):
            # If it's a string, split it by commas and strip whitespace.
            # This is the primary path for values from the .env file.
            stripped_val = v.strip()
            if not stripped_val:
                return []
            return [origin.strip() for origin in stripped_val.split(",")]
        if isinstance(v, list):
            # If it's already a list (e.g., from a different settings source),
            # just return it.
            return v

        # If it's neither a string nor a list, it's an invalid type.
        raise ValueError("Invalid type for BACKEND_CORS_ORIGINS. Must be a comma-separated string or a list.")

    # --- THIRD-PARTY API KEYS & CREDENTIALS ---
    # Storing API keys and credentials here ensures they are managed via
    # environment variables and not hardcoded in the application logic.

    # Crypto Exchanges
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    COINBASE_API_KEY: Optional[str] = None
    COINBASE_API_SECRET: Optional[str] = None
    # Add other exchanges as needed (e.g., KRAKEN, KUCOIN)

    # Forex & Brokers (MetaTrader 5)
    MT5_LOGIN: Optional[int] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None

    # TradingView Integration
    # Used to secure and validate incoming webhook alerts for automated trading.
    TRADINGVIEW_WEBHOOK_SECRET: Optional[str] = None

    # FIX Protocol (Financial Information eXchange)
    FIX_CONFIG_PATH: Optional[str] = None

    # Payment Systems
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_MODE: str = "sandbox"  # Can be 'live' or 'sandbox'

    # Google Firebase for features like push notifications or authentication
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None

    # Alternative Data Providers
    NEWS_API_KEY: Optional[str] = None
    # Twitter/X API v2 Credentials
    X_API_KEY: Optional[str] = None
    X_API_SECRET_KEY: Optional[str] = None
    X_ACCESS_TOKEN: Optional[str] = None
    X_ACCESS_TOKEN_SECRET: Optional[str] = None

    # --- MONITORING, OBSERVABILITY & ML OPS ---
    # URI for the MLflow tracking server to log experiments, models, and metrics.
    MLFLOW_TRACKING_URI: Optional[str] = "http://127.0.0.1:5000"
    ETHEREUM_RPC_URL: Optional[str] = None

    # Webhook URLs and tokens for sending alerts to communication platforms.
    ALERTING_SLACK_WEBHOOK_URL: Optional[str] = None
    ALERTING_TELEGRAM_BOT_TOKEN: Optional[str] = None
    ALERTING_TELEGRAM_CHAT_ID: Optional[str] = None


# Create a single, globally accessible instance of the settings.
# This instance will be imported by other parts of the application.
settings = Settings()