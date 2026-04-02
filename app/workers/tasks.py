from loguru import logger

from app.workers.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_id: str, email: str) -> dict:
    """Simulate sending a welcome email.

    In a real application this would call SendGrid / SES / Postmark.
    """
    try:
        logger.info(f"Sending welcome email to {email} (user_id={user_id})")
        # Placeholder — replace with real email provider call
        return {"status": "sent", "user_id": user_id, "email": email}
    except Exception as exc:
        logger.error(f"Failed to send welcome email: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def cleanup_expired_tokens() -> dict:
    """Remove expired token blacklist entries from Redis."""
    import redis

    from app.config import settings

    r = redis.from_url(settings.REDIS_URL)
    pattern = "blacklist:*"
    cursor = 0
    cleaned = 0
    while True:
        cursor, keys = r.scan(cursor, match=pattern, count=100)
        for key in keys:
            ttl = r.ttl(key)
            if ttl == -1:  # no expiry set — clean up stale entries
                r.delete(key)
                cleaned += 1
        if cursor == 0:
            break
    logger.info(f"Token cleanup complete: removed {cleaned} entries")
    return {"cleaned": cleaned}
