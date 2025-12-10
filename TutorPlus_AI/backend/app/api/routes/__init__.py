"""API Routes Package"""
from app.api.routes.auth import router as auth_router
from app.api.routes.tutor import router as tutor_router
from app.api.routes.progress import router as progress_router
from app.api.routes.mcq import router as mcq_router

__all__ = ["auth_router", "tutor_router", "progress_router", "mcq_router"]