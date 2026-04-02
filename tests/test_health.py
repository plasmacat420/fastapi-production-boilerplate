import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_ready(client):
    response = await client.get("/health/ready")
    # May be 200 or 503 depending on whether postgres/redis are available
    # In CI we use SQLite for the DB check, redis may not be available
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data
