from fastapi import FastAPI
from app.core.logging import configure_logging  # noqa: F401
from app.core.config import settings
from app.api.v1.routers import health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}