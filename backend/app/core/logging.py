import logging
import sys
from app.core.config import settings

def configure_logging() -> None:
    """
    Configure application logging.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    # Reduce noise from some libraries in non-debug mode
    if not settings.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("aioredis").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

# Configure logging on import
configure_logging()