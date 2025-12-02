"""FastAPI application entrypoint for TDIE."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from backend.api import bias, fingerprint, poison, tdie, train, validate
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle startup and shutdown events with structured logging.

    Using lifespan avoids deprecated ``on_event`` hooks and ensures predictable
    initialization when exercised through HTTPX transports in tests.
    """

    logger.info("TDIE API starting up")
    yield
    logger.info("TDIE API shutdown complete")


app = FastAPI(
    title="Training Data Integrity Engine",
    version="1.0.0",
    description="Synthetic-safe integrity checks for datasets aligned with NIST AI RMF and ISO/IEC 42001",
    lifespan=lifespan,
)

app.include_router(validate.router)
app.include_router(fingerprint.router)
app.include_router(poison.router)
app.include_router(bias.router)
app.include_router(tdie.router)
app.include_router(train.router)


@app.get("/health", response_class=PlainTextResponse)
def health() -> str:
    """Liveness probe for uptime monitoring and CI smoke checks."""

    return "ok"


@app.get("/logs")
def get_logs(lines: int = 200) -> list[str]:
    """Return the most recent log entries for quick operational debugging."""

    safe_line_limit = max(1, min(lines, 1000))
    log_path = Path("logs/tdie.log")
    if not log_path.exists():
        return []
    try:
        with log_path.open("r", encoding="utf-8") as f:
            content = f.readlines()
    except OSError as exc:
        logger.error("Unable to read log file: %s", exc)
        raise HTTPException(status_code=500, detail="Unable to read logs") from exc
    return content[-safe_line_limit:]
