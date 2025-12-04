"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.internal import router as internal_router
from app.api.external import router as external_router
from app.core.config import get_settings
from app.schemas.api import HealthCheck

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Test Data Management Platform API. "
            "A full-stack AI agent chat tool with RAG capabilities."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(internal_router, prefix=settings.api_v1_prefix)
    app.include_router(external_router, prefix=settings.api_v1_prefix)

    @app.get("/", response_model=HealthCheck, tags=["health"])
    async def root() -> HealthCheck:
        """Root endpoint returning API health status."""
        return HealthCheck(
            status="healthy",
            version=settings.app_version,
            services={
                "api": "running",
                "knowledge_base": "available",
                "event_pipeline": "available",
            },
        )

    @app.get("/health", response_model=HealthCheck, tags=["health"])
    async def health_check() -> HealthCheck:
        """Health check endpoint for monitoring."""
        return HealthCheck(
            status="healthy",
            version=settings.app_version,
            services={
                "api": "running",
                "knowledge_base": "available",
                "event_pipeline": "available",
            },
        )

    logger.info(
        "Application started: %s v%s",
        settings.app_name,
        settings.app_version,
    )

    return app


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
