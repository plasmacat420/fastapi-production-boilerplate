from datetime import datetime, timezone

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "ok",
        "version": settings.APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/ready")
async def readiness_check():
    db_status = "ok"
    redis_status = "ok"
    errors = []

    # Check DB
    try:
        from sqlalchemy import text

        from app.database import async_session_factory

        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {e}"
        errors.append("db")

    # Check Redis
    try:
        import redis.asyncio as aioredis

        from app.config import settings as cfg

        r = aioredis.from_url(cfg.REDIS_URL)
        await r.ping()
        await r.aclose()
    except Exception as e:
        redis_status = f"error: {e}"
        errors.append("redis")

    payload = {"status": "ready", "db": db_status, "redis": redis_status}
    if errors:
        payload["status"] = "degraded"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=payload
        )
    return payload
