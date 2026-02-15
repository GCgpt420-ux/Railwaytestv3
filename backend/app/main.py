from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.catalog import router as catalog_router
from app.api.v1.endpoints.quiz import router as quiz_router
from app.api.v1.endpoints.users import router as users_router
from app.api.v1.endpoints.questions import router as questions_router
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.db.base import Base
from app.db.session import engine

logger = setup_logging()
logger.info("Starting TutorPAES API...")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        if settings.AUTO_CREATE_TABLES:
            logger.warning("AUTO_CREATE_TABLES enabled: running Base.metadata.create_all()")
            Base.metadata.create_all(bind=engine)
        else:
            logger.info("AUTO_CREATE_TABLES disabled: relying on Alembic migrations")
    except Exception:
        logger.exception("Database not ready during startup")
        raise
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(quiz_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(questions_router, prefix="/api/v1")