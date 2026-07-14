from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health", summary="Health check", description="Return OK if service is running.")
async def health_check():
    return {"status": "ok"}

@router.get("/ready", summary="Readiness check", description="Check dependencies (DB, Redis).")
async def readiness_check():
    # For now, just return ok; later add actual checks.
    return {"status": "ready"}
