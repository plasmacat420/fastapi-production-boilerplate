import pytest


@pytest.mark.asyncio
async def test_rate_limit_exceeded(client):
    """Send 61 requests — the last ones should return 429."""
    last_status = None
    for _ in range(65):
        response = await client.get("/health")
        last_status = response.status_code
        if last_status == 429:
            break

    assert last_status == 429, (
        f"Expected 429 after exceeding rate limit of 60/minute, but got {last_status}"
    )
