"""Application entrypoint and FastAPI app factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pocket.app.api.v1.router import api_router
from pocket.app.core.config import get_settings
from pocket.app.core.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure database tables exist on startup for local development."""
    settings = get_settings()
    if settings.run_migrations_on_startup:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        lifespan=lifespan,
    )
    
    # CORS 미들웨어 추가 (가장 먼저 추가)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
