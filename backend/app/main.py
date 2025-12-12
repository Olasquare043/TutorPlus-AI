from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import get_settings
from app.database import init_db
from app.middleware.cors import setup_cors
from app.utils.logger import setup_logger
from app.api.routes import auth_router, tutor_router, progress_router, mcq_router, admin_router
from app.services.ai_service import AIService
from app.services.rag_service import RAGService
import logging

logger = setup_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager for managing application startup and shutdown events.
    """
    logger.info(f"Starting TutorPlus AI in {settings.app_env} mode")
    init_db()
    logger.info("Database initialized")
    
    # Initialize AI Service
    try:
        AIService.initialize()
        logger.info("AI Service initialized")
    except Exception as e:
        logger.warning(f"AI Service initialization deferred: {str(e)}")
    
    # Initialize RAG Service
    try:
        RAGService.initialize()
        logger.info("RAG Service initialized")
    except Exception as e:
        logger.warning(f"RAG Service initialization failed: {str(e)}")
    
    yield  # application is running
    logger.info("Shutting down TutorPlus AI")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="TutorPlus AI",
        description="Multilingual AI-powered tutoring platform for Nigerian secondary school students",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    
    # Setup middleware
    setup_cors(app)

    # root
    @app.get("/", tags=["root"])
    async def root():
        return {"status":"ok", "message":"Welcome to TutorPlus AI"}
    
    # Health check
    @app.get("/health", tags=["health"])
    async def health_check():
        return {
            "status": "ok",
            "environment": settings.app_env,
            "debug": settings.debug,
        }
    
    # Include routers
    app.include_router(auth_router)
    app.include_router(tutor_router)
    app.include_router(progress_router)
    app.include_router(mcq_router)
    app.include_router(admin_router) 
    
    return app


app = create_app()