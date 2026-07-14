from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health", summary="Health check", description="Return OK if service is running.")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT, "version": settings.VERSION}

@router.get("/ready", summary="Readiness check", description="Check dependencies (DB, Redis).")
async def readiness_check():
    # For now, just return ok; later add actual checks.
    return {"status": "ready"}
