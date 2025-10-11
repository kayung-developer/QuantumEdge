"""
AuraQuant - Main Application Entrypoint (Definitive Final Version)
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Import all services and managers that have a lifecycle ---
from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import engine, AsyncSessionLocal
from app.db.base import Base
from app.core.connections import connection_manager
from app.core.redis_client import redis_client
from app.kafka_producer import kafka_producer
from app.services.order_orchestrator import orchestrator_service
from app.services.news_ingestion_service import news_ingestion_service
from app.services.sentiment_analysis_service import sentiment_analysis_service
from app.services.sentiment_storage_service import sentiment_storage_service  # Import the new service
from app.services.adaptive_service import adaptive_service
from app.services.cv_service import cv_service
# Import for initial superuser creation
from app import crud
from app.schemas.user import UserCreate
from fastapi import Request, Response
from app.services.telemetry_service import telemetry_service
from app.services.regime_service import regime_service
import time


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    The application's lifespan manager. This context manager handles all
    startup and shutdown events for the entire platform in the correct order.
    """
    # ========================================================================
    # --- APPLICATION STARTUP SEQUENCE ---
    # ========================================================================
    logger.info("--- AuraQuant Application Startup Sequence Initiated ---")

    # 1. Initialize core infrastructure connections
    await redis_client.connect()
    await kafka_producer.start()

    # 2. Initialize database and create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 3. Create the initial superuser if not present (bootstrap)
    async with AsyncSessionLocal() as db:
        user = await crud.crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
        if not user:
            logger.info("Initial superuser not found. Creating one...")
            await crud.crud_user.create(db, obj_in=UserCreate(
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            ))
            logger.info("Initial superuser created successfully.")

    # 4. Connect to all external trading exchanges concurrently
    await connection_manager.startup_all()

    # 5. Load the production ML model into memory
    cv_service.load_production_model()
    regime_service.load_all_models()

    # 6. Start all background service workers
    logger.info("Starting all background service workers...")
    orchestrator_service.start_worker()
    news_ingestion_service.start()
    sentiment_analysis_service.start()
    sentiment_storage_service.start()  # START THE SENTIMENT STORAGE WORKER
    adaptive_service.start()
    logger.info("All background workers have been started.")

    # Application is now running
    yield

    # ========================================================================
    # --- APPLICATION SHUTDOWN SEQUENCE ---
    # ========================================================================
    logger.info("--- AuraQuant Application Shutdown Sequence Initiated ---")

    # 1. Stop all background service workers to prevent new tasks
    logger.info("Stopping all background service workers...")
    adaptive_service.stop()
    sentiment_storage_service.stop()  # STOP THE SENTIMENT STORAGE WORKER
    sentiment_analysis_service.stop()
    news_ingestion_service.stop()
    orchestrator_service.stop_worker()
    logger.info("All background workers have been stopped.")

    # 2. Disconnect from external trading exchanges
    await connection_manager.shutdown_all()

    # 3. Disconnect from core infrastructure
    await kafka_producer.stop()
    await redis_client.disconnect()

    # 4. Dispose of the database connection pool
    await engine.dispose()
    logger.info("--- AuraQuant Shutdown Complete ---")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = (time.time() - start_time) * 1000

    # Record telemetry for the API call
    telemetry_service.record_api_request(
        endpoint=request.url.path,
        duration_ms=process_time,
        status_code=response.status_code
    )

    return response


# --- FastAPI App Initialization ---

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", status_code=200, include_in_schema=False)
def root():
    return {"status": "ok", "message": f"Welcome to {settings.PROJECT_NAME} API v{settings.PROJECT_VERSION}"}


# celery -A app.celery_worker.celery_app worker --loglevel=info
# pip install -e . && pip install -r requirements.txt
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# yarn dev - npm run dev